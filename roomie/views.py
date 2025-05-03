from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from core.models import Room, Message, RoomBooking, SupportTicket, TicketResponse, RoomContract, Subscription
from django.db.models import Count, Q, F
from reportlab.pdfgen import canvas
from io import BytesIO
from .forms import RoomieFormFactory, RoomieForms
from django.urls import reverse
from django.utils import timezone
User = get_user_model()  # Get the custom user model

def home(request):
    """
    Home page view to display featured rooms and all roommates.
    """
    # Fetch rooms that are available and have remaining capacity
    featured_rooms = Room.objects.annotate(
        approved_bookings=Count('bookings', filter=Q(bookings__status='approved'))
    ).filter(is_available=True).filter(bedrooms__gt=F('approved_bookings'))[:6]

    # Fetch all seekers (roommates)
    roommates = User.objects.filter(account_type='seeker')

    # Fetch subscription details for the logged-in user (if seeker)
    subscription = None
    if request.user.is_authenticated and hasattr(request.user, 'account_type') and request.user.account_type == 'seeker':
        subscription = Subscription.objects.filter(user=request.user).first()

    return render(request, 'home.html', {
        'featured_rooms': featured_rooms,
        'roommates': roommates,
        'subscription': subscription,
    })

def register(request):
    """
    Simplified user registration process with proper password handling.
    """
    if request.method == 'POST':
        form = RoomieForms.UserForm(request.POST, request.FILES)  # Handle form data and file uploads
        if form.is_valid():
            form.save()  # Save the user to the database
            messages.success(request, "Your account has been created successfully!")
            return redirect('login')  # Redirect to the login page
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RoomieForms.UserForm()  # Instantiate an empty form

    return render(request, 'register.html', {'form': form})

def user_login(request):
    """
    Handle user authentication process.

    This view function processes user login requests. When accessed via GET, it displays
    the login form. When submitted via POST, it validates the credentials and authenticates
    the user.

    Args:
        request (HttpRequest): The HTTP request object containing metadata about the request.

    Returns:
        HttpResponse: Renders the login page with the authentication form. 
                      If credentials are valid, redirects to home page.

    Notes:
        - Uses custom LoginForm from RoomieForms via the factory pattern
        - On failed authentication, adds an error message to the form
        - On successful login, redirects to 'home.html'
    """
    # Create a form factory instance
    form_factory = RoomieFormFactory()
    
    if request.method == 'POST':
        # Use the factory to create a login form with request and POST data
        form = form_factory.create_login_form(request=request, data=request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('dashboard')  # Redirect to dashboard after login
            else:
                form.add_error(None, 'Invalid username or password')
    else:
        # Use the factory to create an empty login form
        form = form_factory.create_login_form(request=request)
        
    return render(request, "login.html", {'form': form})

@login_required
def dashboard(request):
    """
    Display personalized dashboard for authenticated users.
    
    This view shows an overview of the user's account activity,
    with different content depending on the account type (seeker or provider).
    """
    user = request.user
    
    # Get unread messages count
    unread_messages = Message.objects.filter(recipient=user, is_read=False).count()
    
    # Get recent messages 
    recent_messages = Message.objects.filter(recipient=user).order_by('-timestamp')[:5]
    
    context = {
        'unread_messages': unread_messages,
        'recent_messages': recent_messages,
        'profile_views': 0,  # Placeholder for future profile view tracking feature
    }
    
    # Add recommended content based on user type
    if user.account_type == 'seeker':
        # Get recommended rooms for seekers
        recommended_rooms = Room.objects.filter(is_available=True).order_by('?')[:3]
        context['recommended_rooms'] = recommended_rooms
    else:
        # Get potential roommates for providers
        recommended_roommates = User.objects.filter(account_type='seeker').order_by('?')[:3]
        context['recommended_roommates'] = recommended_roommates
    
    return render(request, 'dashboard.html', context)

@login_required
def list_room(request):
    """
    Allow providers to list a room.
    """
    if request.user.account_type != 'provider':
        messages.error(request, "Only room providers can list rooms.")
        return redirect('home')  # Redirect unauthorized users to the home page

    if request.method == 'POST':
        form = RoomieForms.RoomForm(request.POST, request.FILES)
        if form.is_valid():
            room = form.save(commit=False)
            room.provider = request.user  # Assign the logged-in user as the room provider
            room.save()
            messages.success(request, "Your room has been listed successfully!")
            return redirect('user_profile', user_id=request.user.id)  # Redirect to user profile to see the listed room
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RoomieForms.RoomForm()

    return render(request, 'list_room.html', {'form': form, 'provider': request.user})

def find_roommate(request):
    """
    View to search and filter potential roommates based on user preferences.
    """
    # Start with all users
    roommates = User.objects.all()
    
    # Filter by account type
    account_type = request.GET.get('account_type', '')
    if account_type:
        roommates = roommates.filter(account_type=account_type)
    else:
        # Default to showing seekers if no specific filter is applied
        roommates = roommates.filter(account_type='seeker')
    
    # Search by name, username, or bio
    search_query = request.GET.get('search', '')
    if search_query:
        roommates = roommates.filter(
            Q(username__icontains=search_query) | 
            Q(first_name__icontains=search_query) | 
            Q(last_name__icontains=search_query) | 
            Q(bio__icontains=search_query)
        )
    
    # Filter by location
    location = request.GET.get('location', '')
    if location:
        roommates = roommates.filter(location__icontains=location)
    
    # Filter by budget range if provided - safely check if field exists
    min_budget = request.GET.get('min_budget', '')
    max_budget = request.GET.get('max_budget', '')
    
    if min_budget and hasattr(User, 'budget'):
        roommates = roommates.filter(budget__gte=min_budget)
    if max_budget and hasattr(User, 'budget'):
        roommates = roommates.filter(budget__lte=max_budget)
    
    # Filter by interests or lifestyle - safely check if field exists
    lifestyle = request.GET.get('lifestyle', '')
    if lifestyle and hasattr(User, 'lifestyle_preferences'):
        roommates = roommates.filter(lifestyle_preferences__icontains=lifestyle)
    
    # Filter by availability - safely check if field exists
    is_available = request.GET.get('is_available', '')
    if is_available and hasattr(User, 'is_available'):
        roommates = roommates.filter(is_available=is_available == 'true')
    
    # Pagination
    paginator = Paginator(roommates, 9)  # Show 9 roommates per page
    page = request.GET.get('page')
    roommates = paginator.get_page(page)
    
    return render(request, "find_roommate.html", {'roommates': roommates})

def send_message(request, user_id):
    """
    View to send a message to a specific user.
    """
    recipient = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = RoomieForms.MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.recipient = recipient
            message.save()
            messages.success(request, "Message sent successfully!")
            return redirect('find_roommate')  # Redirect to the roommate list or another page
    else:
        form = RoomieForms.MessageForm()

    return render(request, 'send_message.html', {'form': form, 'recipient': recipient})

def user_profile(request, user_id):
    """
    View to display the profile of a specific user.
    """
    user = get_object_or_404(User, id=user_id)  # Fetch the user by ID or return a 404 if not found
    return render(request, 'user_profile.html', {'user': user})

@login_required
def messages_view(request, user_id):
    """
    View to display incoming messages for the logged-in user.
    """
    if request.user.id != user_id:
        return HttpResponse("Unauthorized", status=401)  # Prevent access to other users' messages

    # Get all messages for the user
    messages = Message.objects.filter(recipient=request.user).order_by('-timestamp')
    
    # If a message_id is provided in GET parameters, mark that message as read
    message_id = request.GET.get('mark_read')
    if message_id:
        try:
            message = Message.objects.get(message_id=message_id, recipient=request.user)
            message.is_read = True
            message.save()
            # Return a JSON response for AJAX calls
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
        except Message.DoesNotExist:
            # Return error for AJAX calls
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Message not found'}, status=404)
    
    return render(request, 'messages.html', {'messages': messages})

def logout_view(request):
    """
    Custom logout view to handle GET requests.
    """
    logout(request)
    return redirect('home')  # Redirect to the home page after logout

@login_required
def mark_message_read(request, user_id, message_id):
    """
    AJAX view to mark a message as read/unread.
    """
    if request.user.id != user_id:
        return JsonResponse({"error": "Unauthorized"}, status=401)
    
    try:
        message = Message.objects.get(message_id=message_id, recipient=request.user)
        message.is_read = not message.is_read  # Toggle the read status
        message.save()
        return JsonResponse({"status": "success", "is_read": message.is_read})
    except Message.DoesNotExist:
        return JsonResponse({"error": "Message not found"}, status=404)

def room_detail(request, room_id):
    """
    View to display the details of a specific room.
    """
    room = get_object_or_404(Room, room_id=room_id)
    return render(request, 'room_detail.html', {'room': room})

def filter_rooms(request):
    """
    View to filter and display rooms based on user input.
    """
    rooms = Room.objects.all()

    # Get filter parameters from the request
    location = request.GET.get('location', '')
    room_type = request.GET.get('room_type', '')
    min_rent = request.GET.get('min_rent', '')
    max_rent = request.GET.get('max_rent', '')

    # Apply filters
    if location:
        rooms = rooms.filter(location__icontains=location)
    if room_type:
        rooms = rooms.filter(room_type=room_type)
    if min_rent:
        rooms = rooms.filter(rent__gte=min_rent)
    if max_rent:
        rooms = rooms.filter(rent__lte=max_rent)

    return render(request, 'filter_rooms.html', {'rooms': rooms})

@login_required
def book_room(request, room_id):
    """
    Allow seekers to book a room.
    """
    room = get_object_or_404(Room, room_id=room_id)

    # Ensure only seekers can book rooms
    if request.user.account_type != 'seeker':
        return redirect('home')

    if request.method == 'POST':
        form = RoomieForms.RoomBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.room = room
            booking.seeker = request.user
            booking.save()
            return redirect('room_detail', room_id=room.room_id)
    else:
        form = RoomieForms.RoomBookingForm()

    return render(request, 'book_room.html', {'room': room, 'form': form})

@login_required
def delete_room(request, room_id):
    """
    Allow providers to delete their room listings.
    """
    room = get_object_or_404(Room, room_id=room_id)

    # Ensure only the provider who owns the room can delete it
    if request.user != room.provider:
        messages.error(request, "You are not authorized to delete this room.")
        return redirect('user_profile', user_id=request.user.id)

    if request.method == 'POST':
        room.delete()
        messages.success(request, "Room listing deleted successfully.")
        return redirect('user_profile', user_id=request.user.id)

    return render(request, 'confirm_delete_room.html', {'room': room})

@login_required
def toggle_availability(request):
    """Toggle the availability status of a user."""
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            
            # Ensure the user can only toggle their own availability
            if str(request.user.id) != str(user_id):
                return JsonResponse({
                    'success': False,
                    'error': 'You can only toggle your own availability status.'
                })
            
            # Toggle the availability status
            request.user.is_available = not request.user.is_available
            request.user.save()
            
            return JsonResponse({
                'success': True,
                'is_available': request.user.is_available,
                'message': 'Your availability status has been updated.'
            })
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False, 
                'error': 'Invalid JSON data.'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method.'
    })

@login_required
def edit_profile(request):
    """Edit user profile information."""
    if request.method == 'POST':
        # Handle profile update
        if 'profile_photo' in request.FILES:
            request.user.profile_photo = request.FILES['profile_photo']
        
        # Update user fields
        request.user.email = request.POST.get('email', request.user.email)
        request.user.first_name = request.POST.get('first_name', request.user.first_name)
        request.user.last_name = request.POST.get('last_name', request.user.last_name)
        request.user.gender = request.POST.get('gender', request.user.gender)
        request.user.location = request.POST.get('location', request.user.location)
        request.user.bio = request.POST.get('bio', request.user.bio)
        
        # Parse birthdate if provided
        birthdate = request.POST.get('birthdate')
        if birthdate:
            from datetime import datetime
            try:
                request.user.birthdate = datetime.strptime(birthdate, '%Y-%m-%d')
            except ValueError:
                pass
        
        # Update availability
        request.user.is_available = 'is_available' in request.POST
        
        # Save user
        request.user.save()
        
        # Redirect to profile page with success message
        from django.contrib import messages
        messages.success(request, 'Your profile has been updated successfully!')
        return redirect('user_profile', user_id=request.user.id)
    
    # Display edit profile form
    return render(request, 'edit_profile.html', {'user': request.user})

@login_required
def my_bookings(request):
    """
    Display all bookings submitted by the seeker.
    """
    if request.user.account_type != 'seeker':
        return redirect('home')

    bookings = RoomBooking.objects.filter(seeker=request.user).select_related('room')
    booking_data = []

    for booking in bookings:
        contract = RoomContract.objects.filter(room=booking.room, seeker=booking.seeker).first()
        booking_data.append({
            'booking': booking,
            'contract': contract
        })

    return render(request, 'my_bookings.html', {'booking_data': booking_data})

@login_required
def manage_bookings(request):
    """
    Display all bookings for the provider's rooms.
    """
    if request.user.account_type != 'provider':
        return redirect('home')

    # Fetch all bookings for rooms owned by the provider
    bookings = RoomBooking.objects.filter(room__provider=request.user).select_related('room', 'seeker')

    # Add remaining capacity for each booking
    booking_data = []
    for booking in bookings:
        room = booking.room
        approved_bookings = RoomBooking.objects.filter(room=room, status='approved').count()
        remaining_capacity = room.bedrooms - approved_bookings
        booking_data.append({
            'booking': booking,
            'remaining_capacity': remaining_capacity
        })

    return render(request, 'manage_bookings.html', {'booking_data': booking_data})

@login_required
def update_booking_status(request, booking_id, status):
    """
    Allow providers to accept or reject a booking.
    """
    booking = get_object_or_404(RoomBooking, id=booking_id, room__provider=request.user)

    if status not in ['approved', 'rejected']:
        messages.error(request, "Invalid status update.")
        return redirect('manage_bookings')

    if status == 'approved' and not RoomBooking.can_accept_booking(booking.room):
        messages.error(request, f"Cannot approve booking. Maximum capacity of {booking.room.bedrooms} bedrooms reached.")
        return redirect('manage_bookings')

    booking.status = status
    booking.save()

    # Create a RoomContract if approved
    if status == 'approved':
        RoomContract.objects.create(
            room=booking.room,
            seeker=booking.seeker,
            provider=booking.room.provider,
            start_date=booking.start_date,
            end_date=booking.end_date,
            rent_amount=booking.room.rent,
            status='active',
        )
        messages.success(request, f"Booking for {booking.room.title} has been approved, and a contract has been created.")
    elif status == 'rejected':
        messages.error(request, f"Booking for {booking.room.title} has been rejected.")

    return redirect('manage_bookings')

@login_required
def support_home(request):
    """
    Main support page that directs users to appropriate support pages based on account type.
    """
    # Get recent tickets for the current user
    recent_tickets = None
    if request.user.is_authenticated:
        recent_tickets = SupportTicket.objects.filter(
            user=request.user
        ).order_by('-created_at')[:5]
    
    return render(request, 'support_home.html', {
        'recent_tickets': recent_tickets
    })

@login_required
def submit_support_ticket(request):
    """
    View for submitting a new support ticket.
    """
    # Determine ticket type based on query parameter or user account type
    ticket_type = request.GET.get('type', 'general')
    
    # For provider-specific support, check if user is a provider
    if ticket_type == 'provider' and request.user.account_type != 'provider':
        messages.error(request, "You must be a provider to access provider support.")
        return redirect('support_home')
    
    # For seeker-specific support, check if user is a seeker
    if ticket_type == 'seeker' and request.user.account_type != 'seeker':
        messages.error(request, "You must be a seeker to access seeker support.")
        return redirect('support_home')
    
    if request.method == 'POST':
        form = RoomieForms.SupportTicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.ticket_type = request.POST.get('ticket_type', 'general')
            ticket.category = request.POST.get('category', 'other')
            ticket.status = 'open'  # Default to open status
            ticket.save()
            
            messages.success(request, "Your support ticket has been submitted successfully. We'll get back to you soon.")
            return redirect('view_support_ticket_detail', ticket_id=ticket.id)
    else:
        form = RoomieForms.SupportTicketForm()
    
    return render(request, 'submit_support_ticket.html', {
        'form': form,
        'ticket_type': ticket_type
    })

@login_required
def view_support_tickets(request):
    """
    View for listing all support tickets submitted by the current user.
    """
    # Get all tickets for the current user with optional filtering
    status_filter = request.GET.get('status', '')
    type_filter = request.GET.get('type', '')
    
    tickets = SupportTicket.objects.filter(user=request.user)
    
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    
    if type_filter:
        tickets = tickets.filter(ticket_type=type_filter)
    
    tickets = tickets.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(tickets, 10)  # Show 10 tickets per page
    page = request.GET.get('page')
    tickets = paginator.get_page(page)
    
    return render(request, 'view_support_tickets.html', {
        'tickets': tickets
    })

@login_required
def view_support_ticket_detail(request, ticket_id):
    """
    View for displaying details of a specific support ticket.
    """
    # Get ticket if it belongs to the current user
    ticket = get_object_or_404(SupportTicket, id=ticket_id, user=request.user)
    
    return render(request, 'support_ticket_detail.html', {
        'ticket': ticket
    })

@login_required
def add_ticket_response(request, ticket_id):
    """
    View for adding a response to a support ticket.
    """
    ticket = get_object_or_404(SupportTicket, id=ticket_id, user=request.user)
    
    if request.method == 'POST':
        message = request.POST.get('message', '')
        if message:
            # Create new ticket response
            TicketResponse.objects.create(
                ticket=ticket,
                user=request.user,
                message=message,
                staff=False  # User response, not staff
            )
            
            # Update ticket status if it was resolved or closed
            if ticket.status in ['resolved', 'closed']:
                ticket.status = 'in_progress'
                ticket.save()
                
            messages.success(request, "Your response has been added to the ticket.")
        else:
            messages.error(request, "Response message cannot be empty.")
    
    return redirect('view_support_ticket_detail', ticket_id=ticket.id)

@login_required
def close_ticket(request, ticket_id):
    """
    View for marking a ticket as resolved.
    """
    ticket = get_object_or_404(SupportTicket, id=ticket_id, user=request.user)
    
    ticket.status = 'resolved'
    ticket.save()
    
    messages.success(request, "Ticket has been marked as resolved.")
    return redirect('view_support_ticket_detail', ticket_id=ticket.id)

@login_required
def reopen_ticket(request, ticket_id):
    """
    View for reopening a closed or resolved ticket.
    """
    ticket = get_object_or_404(SupportTicket, id=ticket_id, user=request.user)
    
    if ticket.status in ['resolved', 'closed']:
        ticket.status = 'in_progress'
        ticket.save()
        messages.success(request, "Ticket has been reopened.")
    
    return redirect('view_support_ticket_detail', ticket_id=ticket.id)

@login_required
def submit_room_review(request, room_id):
    """
    Allow users to submit a review for a room.
    """
    room = get_object_or_404(Room, room_id=room_id)
    
    # Check if the user has stayed in this room (has an approved booking)
    has_booking = RoomBooking.objects.filter(
        room=room,
        seeker=request.user,
        status='approved'
    ).exists()
    
    if not has_booking:
        messages.error(request, "You can only review rooms you have booked.")
        return redirect('room_detail', room_id=room_id)
    
    # Check if user already reviewed this room
    from .models import Review
    existing_review = Review.objects.filter(
        reviewer=request.user,
        reviewed_room=room,
        review_type='room'
    ).first()
    
    if existing_review:
        messages.info(request, "You have already reviewed this room. You can edit your existing review.")
        return redirect('edit_review', review_id=existing_review.review_id)
    
    if request.method == 'POST':
        form = RoomieForms.ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer = request.user
            review.reviewed_room = room
            review.reviewed_user = None
            review.review_type = 'room'
            review.save()
            
            messages.success(request, "Your review has been submitted successfully.")
            return redirect('room_detail', room_id=room_id)
    else:
        form = RoomieForms.ReviewForm()
    
    return render(request, 'submit_review.html', {
        'form': form,
        'room': room,
        'review_type': 'room'
    })

@login_required
def submit_user_review(request, user_id):
    """
    Allow users to submit a review for another user.
    """
    user_to_review = get_object_or_404(User, id=user_id)
    
    # Don't allow users to review themselves
    if request.user.id == user_id:
        messages.error(request, "You cannot review yourself.")
        return redirect('user_profile', user_id=user_id)
    
    # Check if there was an interaction (booking) between the users
    interaction_exists = False
    
    if request.user.account_type == 'seeker':
        # Seeker reviewing a provider
        interaction_exists = RoomBooking.objects.filter(
            seeker=request.user,
            room__provider=user_to_review,
            status='approved'
        ).exists()
    else:
        # Provider reviewing a seeker
        interaction_exists = RoomBooking.objects.filter(
            seeker=user_to_review,
            room__provider=request.user,
            status='approved'
        ).exists()
    
    if not interaction_exists:
        messages.error(request, "You can only review users you have interacted with through bookings.")
        return redirect('user_profile', user_id=user_id)
    
    # Check if user already reviewed this person
    from .models import Review
    review_type = 'provider' if user_to_review.account_type == 'provider' else 'seeker'
    existing_review = Review.objects.filter(
        reviewer=request.user,
        reviewed_user=user_to_review,
        review_type=review_type
    ).first()
    
    if existing_review:
        messages.info(request, "You have already reviewed this user. You can edit your existing review.")
        return redirect('edit_review', review_id=existing_review.review_id)
    
    if request.method == 'POST':
        form = RoomieForms.ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer = request.user
            review.reviewed_user = user_to_review
            review.reviewed_room = None
            review.review_type = review_type
            review.save()
            
            messages.success(request, "Your review has been submitted successfully.")
            return redirect('user_profile', user_id=user_id)
    else:
        form = RoomieForms.ReviewForm()
    
    return render(request, 'submit_review.html', {
        'form': form,
        'user_to_review': user_to_review,
        'review_type': 'user'
    })

@login_required
def edit_review(request, review_id):
    """
    Allow users to edit their existing review.
    """
    from .models import Review
    review = get_object_or_404(Review, review_id=review_id, reviewer=request.user)
    
    if request.method == 'POST':
        form = RoomieForms.ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            
            if review.review_type == 'room':
                messages.success(request, "Your room review has been updated successfully.")
                return redirect('room_detail', room_id=review.reviewed_room.room_id)
            else:
                messages.success(request, "Your user review has been updated successfully.")
                return redirect('user_profile', user_id=review.reviewed_user.id)
    else:
        form = RoomieForms.ReviewForm(instance=review)
    
    context = {
        'form': form,
        'review': review,
        'edit_mode': True
    }
    
    if review.review_type == 'room':
        context['room'] = review.reviewed_room
    else:
        context['user_to_review'] = review.reviewed_user
        
    context['review_type'] = review.review_type
    
    return render(request, 'submit_review.html', context)

@login_required
def delete_review(request, review_id):
    """
    Allow users to delete their own reviews.
    """
    from .models import Review
    review = get_object_or_404(Review, review_id=review_id, reviewer=request.user)
    
    if request.method == 'POST':
        if review.review_type == 'room':
            room_id = review.reviewed_room.room_id
            review.delete()
            messages.success(request, "Your review has been deleted successfully.")
            return redirect('room_detail', room_id=room_id)
        else:
            user_id = review.reviewed_user.id
            review.delete()
            messages.success(request, "Your review has been deleted successfully.")
            return redirect('user_profile', user_id=user_id)
    
    # Determine return URL based on review type
    if review.review_type == 'room':
        return_url = reverse('room_detail', args=[review.reviewed_room.room_id])
    else:
        return_url = reverse('user_profile', args=[review.reviewed_user.id])
    
    return render(request, 'confirm_delete_review.html', {
        'review': review,
        'return_url': return_url
    })

@login_required
def reply_to_review(request, review_id):
    """
    Allow room providers or reviewed users to reply to reviews about them.
    """
    from .models import Review, ReviewReply
    review = get_object_or_404(Review, review_id=review_id)
    
    # Verify the user is authorized to reply to this review
    can_reply = False
    if review.review_type == 'room':
        # Only the room provider can reply to room reviews
        can_reply = (request.user == review.reviewed_room.provider)
    else:
        # Only the reviewed user can reply to user reviews
        can_reply = (request.user == review.reviewed_user)
    
    if not can_reply:
        messages.error(request, "You are not authorized to reply to this review.")
        return redirect('home')
    
    # Check if a reply already exists
    existing_reply = ReviewReply.objects.filter(review=review).first()
    if existing_reply:
        messages.info(request, "You've already replied to this review. You can edit your existing reply.")
        return redirect('edit_review_reply', reply_id=existing_reply.reply_id)
    
    if request.method == 'POST':
        form = RoomieForms.ReviewReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.review = review
            reply.author = request.user
            reply.save()
            
            if review.review_type == 'room':
                messages.success(request, "Your reply has been submitted successfully.")
                return redirect('room_detail', room_id=review.reviewed_room.room_id)
            else:
                messages.success(request, "Your reply has been submitted successfully.")
                return redirect('user_profile', user_id=review.reviewed_user.id)
    else:
        form = RoomieForms.ReviewReplyForm()
    
    return render(request, 'reply_to_review.html', {
        'form': form,
        'review': review
    })

@login_required
def edit_review_reply(request, reply_id):
    """
    Allow users to edit their reply to a review.
    """
    from .models import ReviewReply
    reply = get_object_or_404(ReviewReply, reply_id=reply_id, author=request.user)
    review = reply.review
    
    if request.method == 'POST':
        form = RoomieForms.ReviewReplyForm(request.POST, instance=reply)
        if form.is_valid():
            form.save()
            
            if review.review_type == 'room':
                messages.success(request, "Your reply has been updated successfully.")
                return redirect('room_detail', room_id=review.reviewed_room.room_id)
            else:
                messages.success(request, "Your reply has been updated successfully.")
                return redirect('user_profile', user_id=review.reviewed_user.id)
    else:
        form = RoomieForms.ReviewReplyForm(instance=reply)
    
    return render(request, 'reply_to_review.html', {
        'form': form,
        'review': review,
        'reply': reply,
        'edit_mode': True
    })

@login_required
def delete_review_reply(request, reply_id):
    """
    Allow users to delete their reply to a review.
    """
    from .models import ReviewReply
    reply = get_object_or_404(ReviewReply, reply_id=reply_id, author=request.user)
    review = reply.review
    
    if request.method == 'POST':
        if review.review_type == 'room':
            room_id = review.reviewed_room.room_id
            reply.delete()
            messages.success(request, "Your reply has been deleted successfully.")
            return redirect('room_detail', room_id=room_id)
        else:
            user_id = review.reviewed_user.id
            reply.delete()
            messages.success(request, "Your reply has been deleted successfully.")
            return redirect('user_profile', user_id=user_id)
    
    # Determine return URL based on review type
    if review.review_type == 'room':
        return_url = reverse('room_detail', args=[review.reviewed_room.room_id])
    else:
        return_url = reverse('user_profile', args=[review.reviewed_user.id])
    
    return render(request, 'confirm_delete_reply.html', {
        'reply': reply,
        'review': review,
        'return_url': return_url
    })

def room_reviews(request, room_id):
    """
    Display all reviews for a specific room.
    """
    room = get_object_or_404(Room, room_id=room_id)
    
    from .models import Review
    reviews = Review.objects.filter(reviewed_room=room, review_type='room').order_by('-created_at')
    
    # Pagination for reviews
    paginator = Paginator(reviews, 10)  # Show 10 reviews per page
    page = request.GET.get('page')
    reviews = paginator.get_page(page)
    
    # Calculate review statistics
    review_count = reviews.count()
    average_rating = 0
    rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    rating_percentages = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    
    if review_count > 0:
        # Calculate average rating
        total_rating = sum(review.rating for review in reviews)
        average_rating = total_rating / review_count
        
        # Count ratings by star level
        for review in reviews:
            if review.rating in rating_counts:
                rating_counts[review.rating] += 1
        
        # Calculate percentages
        for rating in rating_counts:
            if review_count > 0:
                rating_percentages[rating] = (rating_counts[rating] / review_count) * 100
    
    return render(request, 'reviews/room_reviews.html', {
        'room': room,
        'reviews': reviews,
        'review_count': review_count,
        'average_rating': average_rating,
        'rating_counts': rating_counts,
        'rating_percentages': rating_percentages
    })

def user_reviews(request, user_id):

    """
    Display all reviews for a specific user.
    """
    user = get_object_or_404(User, id=user_id)
    
    from .models import Review
    # If the user is a provider, we want to show provider reviews
    # If the user is a seeker, we want to show seeker reviews
    review_type = 'provider' if user.account_type == 'provider' else 'seeker'
    reviews = Review.objects.filter(reviewed_user=user, review_type=review_type).order_by('-created_at')
    
    # Pagination for reviews
    paginator = Paginator(reviews, 10)  # Show 10 reviews per page
    page = request.GET.get('page')
    reviews = paginator.get_page(page)
    
    # Calculate review statistics
    review_count = reviews.count()
    average_rating = 0
    rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    rating_percentages = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    
    if review_count > 0:
        # Calculate average rating
        total_rating = sum(review.rating for review in reviews)
        average_rating = total_rating / review_count
        
        # Count ratings by star level
        for review in reviews:
            if review.rating in rating_counts:
                rating_counts[review.rating] += 1
        
        # Calculate percentages
        for rating in rating_counts:
            if review_count > 0:
                rating_percentages[rating] = (rating_counts[rating] / review_count) * 100
    
    return render(request, 'reviews/user_reviews.html', {
        'user_profile': user,
        'reviews': reviews,
        'review_count': review_count,
        'average_rating': average_rating,
        'rating_counts': rating_counts,
        'rating_percentages': rating_percentages
    })

def submit_review(request):
    if request.method == 'POST':
        form = RoomieForms.ReviewForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your review has been submitted successfully.")
            redirect_url = request.POST.get('redirect_url', '/')
            return redirect(redirect_url)
    else:
        form = RoomieForms.ReviewForm()

    return render(request, 'submit_review.html', {'form': form})

@login_required
def download_contract(request, contract_id):
    # Get contract and verify that either the seeker or provider is accessing it
    contract = get_object_or_404(RoomContract, id=contract_id)
    
    # Security check - only the seeker or provider can access the contract
    if request.user != contract.seeker and request.user != contract.provider:
        messages.error(request, "You don't have permission to access this contract.")
        return redirect('home')

    # Get room and user information for the contract
    room = contract.room
    provider = contract.provider
    seeker = contract.seeker
    
    # Format dates for display
    start_date_str = contract.start_date.strftime("%B %d, %Y")
    end_date_str = contract.end_date.strftime("%B %d, %Y")
    today_str = timezone.now().strftime("%B %d, %Y")
    
    # Calculate contract duration in months
    contract_duration = (contract.end_date.year - contract.start_date.year) * 12 + (contract.end_date.month - contract.start_date.month)
    if contract_duration < 1:
        contract_duration = "Less than 1 month"
    else:
        contract_duration = f"{contract_duration} month{'s' if contract_duration > 1 else ''}"
    
    # Calculate total rent amount for the entire period
    total_rent = contract.rent_amount * int(contract.end_date.month - contract.start_date.month + (contract.end_date.year - contract.start_date.year) * 12)
    
    # Generate PDF
    buffer = BytesIO()
    
    # Set up document with a professional look
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
    from reportlab.lib.units import inch
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.darkblue,
        spaceAfter=12,
        alignment=1  # Center
    )
    
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.darkblue,
        spaceAfter=6,
        spaceBefore=12
    )
    
    subheading_style = ParagraphStyle(
        'Subheading',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.darkblue,
        spaceAfter=6,
        spaceBefore=6
    )
    
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    )
    
    # Begin building the PDF content
    elements = []
    
    # Logo or header could be added here if available
    # elements.append(Image("path/to/logo.png", width=2*inch, height=0.5*inch))
    
    # Title
    elements.append(Paragraph(f"ROOM RENTAL AGREEMENT", title_style))
    elements.append(Spacer(1, 0.25*inch))
    
    # Contract ID and Date
    elements.append(Paragraph(f"Contract ID: {contract.id}", normal_style))
    elements.append(Paragraph(f"Date: {today_str}", normal_style))
    elements.append(Spacer(1, 0.25*inch))
    
    # Parties Information
    elements.append(Paragraph("PARTIES", heading_style))
    elements.append(Paragraph(f"This Room Rental Agreement (\"Agreement\") is entered into between:", normal_style))
    elements.append(Paragraph(f"<b>PROVIDER:</b> {provider.first_name} {provider.last_name} (\"Landlord\")", normal_style))
    elements.append(Paragraph(f"<b>SEEKER:</b> {seeker.first_name} {seeker.last_name} (\"Tenant\")", normal_style))
    elements.append(Spacer(1, 0.15*inch))
    
    # Property Details
    elements.append(Paragraph("PROPERTY", heading_style))
    elements.append(Paragraph(f"The Landlord agrees to rent to the Tenant, and the Tenant agrees to rent from the Landlord, the following property:", normal_style))
    elements.append(Paragraph(f"<b>Property:</b> {room.title}", normal_style))
    elements.append(Paragraph(f"<b>Address:</b> {room.location}", normal_style))
    elements.append(Paragraph(f"<b>Room Type:</b> {room.get_room_type_display()}", normal_style))
    elements.append(Paragraph(f"<b>Bedrooms:</b> {room.bedrooms}", normal_style))
    elements.append(Spacer(1, 0.15*inch))
    
    # Term
    elements.append(Paragraph("TERM", heading_style))
    elements.append(Paragraph(f"The term of this Agreement shall begin on {start_date_str} and end on {end_date_str}, for a duration of {contract_duration}.", normal_style))
    elements.append(Spacer(1, 0.15*inch))
    
    # Rent
    elements.append(Paragraph("RENT", heading_style))
    elements.append(Paragraph(f"The Tenant agrees to pay rent in the amount of ${contract.rent_amount} per month, payable on the 1st day of each month.", normal_style))
    elements.append(Paragraph(f"The total rent for the entire term of this Agreement is ${total_rent}.", normal_style))
    elements.append(Spacer(1, 0.15*inch))
    
    # Deposit
    elements.append(Paragraph("SECURITY DEPOSIT", heading_style))
    elements.append(Paragraph(f"The Tenant shall pay a security deposit of ${contract.rent_amount} upon signing this Agreement. This deposit will be returned within 30 days after the termination of this Agreement, less any deductions for damages beyond normal wear and tear.", normal_style))
    elements.append(Spacer(1, 0.15*inch))
    
    # Utilities
    elements.append(Paragraph("UTILITIES", heading_style))
    elements.append(Paragraph("The following utilities are included in the rent:", normal_style))
    elements.append(Paragraph("• Water", normal_style))
    elements.append(Paragraph("• Electricity", normal_style))
    elements.append(Paragraph("• Internet", normal_style))
    elements.append(Paragraph("The Tenant is responsible for any additional utilities not listed above.", normal_style))
    elements.append(Spacer(1, 0.15*inch))
    
    # House Rules
    elements.append(Paragraph("HOUSE RULES", heading_style))
    elements.append(Paragraph("The Tenant agrees to comply with all house rules, including but not limited to:", normal_style))
    elements.append(Paragraph("• No smoking inside the property", normal_style))
    elements.append(Paragraph("• Quiet hours from 10:00 PM to 7:00 AM", normal_style))
    elements.append(Paragraph("• No unauthorized guests staying overnight for more than 3 consecutive nights", normal_style))
    elements.append(Paragraph("• Keeping common areas clean and tidy", normal_style))
    elements.append(Spacer(1, 0.15*inch))
    
    # Termination
    elements.append(Paragraph("TERMINATION", heading_style))
    elements.append(Paragraph("Either party may terminate this Agreement with 30 days' written notice. Early termination by the Tenant may result in forfeiture of the security deposit unless a replacement tenant is found.", normal_style))
    elements.append(Spacer(1, 0.15*inch))
    
    # Signatures
    elements.append(Paragraph("SIGNATURES", heading_style))
    elements.append(Paragraph("By signing below, the parties acknowledge that they have read, understood, and agree to the terms of this Agreement.", normal_style))
    elements.append(Spacer(1, 0.25*inch))
    
    # Create signature table
    signature_data = [
        [Paragraph("<b>Landlord:</b>", normal_style), Paragraph("<b>Tenant:</b>", normal_style)],
        [Paragraph(f"{provider.first_name} {provider.last_name}", normal_style), Paragraph(f"{seeker.first_name} {seeker.last_name}", normal_style)],
        ["_______________________", "_______________________"],
        [Paragraph("Signature", normal_style), Paragraph("Signature", normal_style)],
        ["_______________________", "_______________________"],
        [Paragraph("Date", normal_style), Paragraph("Date", normal_style)],
    ]
    
    signature_table = Table(signature_data, colWidths=[2.5*inch, 2.5*inch])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.white),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    elements.append(signature_table)
    
    # Legal Notice
    elements.append(Spacer(1, 0.35*inch))
    elements.append(Paragraph("LEGAL NOTICE", subheading_style))
    elements.append(Paragraph("This document is a legally binding contract. If either party is unsure about any of the terms, they should seek legal advice before signing.", normal_style))
    
    # Add disclaimer about platform
    elements.append(Spacer(1, 0.25*inch))
    elements.append(Paragraph("This contract was generated by RoomiePlatform. RoomiePlatform is not responsible for the content of this agreement and does not provide legal advice.", ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.gray,
        alignment=1  # Center
    )))
    
    # Build the PDF
    doc.build(elements)
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Rental_Agreement_{contract.id}.pdf"'
    return response

@login_required
def subscription_plans(request):
    plans = [
        {'name': 'Free', 'price': 0, 'features': ['Basic access to rooms']},
        {'name': 'Monthly', 'price': 10, 'features': ['Priority room access', 'Unlimited messaging']},
        {'name': 'Yearly', 'price': 100, 'features': ['All features of Monthly', 'Discounted price']},
    ]
    return render(request, 'subscription_plans.html', {'plans': plans})

def faq_page(request):
    """
    Render the FAQ page.
    """
    return render(request, 'faq.html')

def faq(request):
    """
    Displays the Frequently Asked Questions page.
    """
    # Define FAQ categories and questions
    faq_categories = {
        'general': {
            'title': 'General Questions',
            'questions': [
                {
                    'question': 'What is Roomie Platform?',
                    'answer': 'Roomie Platform is a comprehensive service that connects people looking for rooms (seekers) with those who have rooms to offer (providers). Our platform makes it easy to find compatible roommates and suitable living spaces based on preferences, location, and budget.'
                },
                {
                    'question': 'Is it free to use Roomie Platform?',
                    'answer': 'Basic features are free for all users. Room seekers may choose to upgrade to premium plans for additional features like priority listing, advanced filters, and unlimited messaging. Room providers can list their properties for free, with optional promotional features available for a fee.'
                },
                {
                    'question': 'How do I get started?',
                    'answer': 'Simply register for an account, specify whether you\'re looking for a room or have a room to offer, complete your profile with your preferences and details, and start browsing or listing rooms! Check our User Guide for detailed instructions.'
                },
                {
                    'question': 'What areas does Roomie Platform cover?',
                    'answer': 'We currently operate in major cities across the country, with plans to expand to more locations soon. You can search for any location to see available listings in that area.'
                }
            ]
        },
        'account': {
            'title': 'Account & Profile',
            'questions': [
                {
                    'question': 'How do I change my account type (seeker/provider)?',
                    'answer': 'You can change your account type in the Account Settings page. Go to your profile, click on Account Settings, and then select the new account type under the "Account Type" section.'
                },
                {
                    'question': 'Can I have both seeker and provider profiles?',
                    'answer': 'Currently, you can only have one account type active at a time. If you need to both seek and provide rooms, you\'ll need to switch your account type as needed in your Account Settings.'
                },
                {
                    'question': 'How do I update my profile information?',
                    'answer': 'To update your profile, go to Account Settings, select the Profile tab, and update any information you\'d like to change. Don\'t forget to click the Save Changes button when you\'re done.'
                },
                {
                    'question': 'How can I delete my account?',
                    'answer': 'To delete your account, go to Account Settings, select the Privacy tab, and scroll down to the Account Deletion section. Follow the instructions to permanently delete your account. Please note that this action cannot be undone.'
                }
            ]
        },
        'seekers': {
            'title': 'For Room Seekers',
            'questions': [
                {
                    'question': 'How do I find rooms that match my preferences?',
                    'answer': 'Use our advanced search filters to narrow down listings based on location, price range, room type, amenities, and more. You can also set up alerts to be notified when new listings matching your criteria become available.'
                },
                {
                    'question': 'How do I contact a room provider?',
                    'answer': 'You can send a message to any room provider by clicking the "Contact" button on their room listing. This opens our secure messaging system where you can ask questions and discuss details. All communications are initially kept within the platform for safety.'
                },
                {
                    'question': 'What should I consider before booking a room?',
                    'answer': 'Before booking, we recommend: thoroughly reviewing the listing details, asking the provider questions about the property and living arrangements, checking reviews from previous tenants, verifying the location meets your needs, understanding all costs involved, and if possible, arranging a virtual or in-person viewing of the space.'
                },
                {
                    'question': 'How does the booking process work?',
                    'answer': 'Once you find a room you\'re interested in, you can submit a booking request through the platform. The provider will review your request and profile, and either approve or decline. If approved, you\'ll receive confirmation details and next steps for finalizing the arrangement.'
                }
            ]
        },
        'providers': {
            'title': 'For Room Providers',
            'questions': [
                {
                    'question': 'How do I list a room?',
                    'answer': 'To list a room, click on "List a Room" in the navigation menu or dashboard. Fill out the required information about your property, upload photos, set your price and availability, and define your preferences for potential roommates. Once submitted, your listing will be reviewed and published.'
                },
                {
                    'question': 'What makes a good room listing?',
                    'answer': 'Effective listings include: clear, high-quality photos of the room and common areas; detailed, honest descriptions of the space and amenities; accurate pricing information including any additional costs; specific house rules and expectations; and information about the neighborhood and nearby facilities or transportation.'
                },
                {
                    'question': 'How do I manage booking requests?',
                    'answer': 'All booking requests will appear in your dashboard under "Manage Bookings." You can review each seeker\'s profile before deciding to accept or decline their request. Once approved, you\'ll be connected with the seeker to finalize arrangements.'
                },
                {
                    'question': 'Can I set specific roommate preferences?',
                    'answer': 'Yes, you can specify preferences such as gender, age range, lifestyle factors (smoking, pets, etc.), and other criteria for potential roommates. These preferences will help match you with compatible seekers.'
                }
            ]
        },
        'safety': {
            'title': 'Safety & Security',
            'questions': [
                {
                    'question': 'How does Roomie Platform ensure user safety?',
                    'answer': 'We implement various safety measures including: user verification processes, secure messaging within the platform, review and rating systems, reporting features for suspicious activity, and educational resources on roommate safety best practices.'
                },
                {
                    'question': 'Should I meet potential roommates in person?',
                    'answer': 'While we recommend eventually meeting in person before finalizing any living arrangement, we suggest first communicating thoroughly through our platform. When meeting in person, choose public locations for initial meetings, let someone know where you\'re going, and trust your instincts if something feels wrong.'
                },
                {
                    'question': 'How are payments handled?',
                    'answer': 'For security, initial deposits and first payments can be processed through our secure system. For ongoing rent payments, users typically arrange their own payment methods after establishing trust. Never send payments outside the platform to someone you haven\'t met or verified.'
                },
                {
                    'question': 'What should I do if I encounter a problem user?',
                    'answer': 'If you encounter any suspicious or inappropriate behavior, use the "Report User" feature on their profile. Our moderation team will investigate all reports promptly. For immediate safety concerns, please contact local authorities first, then inform our support team.'
                }
            ]
        },
        'technical': {
            'title': 'Technical Support',
            'questions': [
                {
                    'question': 'I can\'t log in to my account. What should I do?',
                    'answer': 'First, verify you\'re using the correct email and password. You can use the "Forgot Password" link to reset your password if needed. If you still can\'t access your account, contact our support team with your account details for assistance.'
                },
                {
                    'question': 'How do I report a bug or technical issue?',
                    'answer': 'You can report technical issues through the Support section in your account menu. Provide as much detail as possible, including what you were trying to do, what happened, and any error messages you received. Screenshots are always helpful.'
                },
                {
                    'question': 'Is my personal information secure?',
                    'answer': 'Yes, we take data security seriously. We use encryption for sensitive data, implement strict access controls, and never share your personal information with third parties without your consent. You can review our Privacy Policy for more details on how we protect and use your data.'
                },
                {
                    'question': 'Which browsers are supported?',
                    'answer': 'Roomie Platform works best on recent versions of Chrome, Firefox, Safari, and Edge. We recommend keeping your browser updated for the best experience and security.'
                }
            ]
        }
    }
    
    context = {
        'page_title': 'Frequently Asked Questions',
        'faq_categories': faq_categories
    }
    return render(request, 'faq.html', context)

def user_guide(request):
    """
    Displays the User Guide page with instructions on how to use the platform.
    """
    context = {
        'page_title': 'User Guide',
    }
    return render(request, 'user_guide.html', context)

def account_settings(request):
    """
    Displays and handles the account settings page where users can manage their account.
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Get user notification settings if they exist (could be expanded in a real implementation)
    notification_settings = {
        'email_notifications': True,
        'message_notifications': True,
        'booking_notifications': True,
        'marketing_notifications': False,
    }
    
    context = {
        'page_title': 'Account Settings',
        'notification_settings': notification_settings,
        'user': request.user,
    }
    return render(request, 'account_settings.html', context)

def update_profile(request):
    """
    Handles updates to user profile information.
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        # Process form submission for profile updates
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.location = request.POST.get('location', user.location)
        user.bio = request.POST.get('bio', user.bio)
        user.save()
        
        messages.success(request, 'Profile information updated successfully.')
        return redirect('account_settings')
    
    return redirect('account_settings')

def update_preferences(request):
    """
    Handles updates to user preferences.
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        # Process form submission for preference updates
        # This is a simplified example
        messages.success(request, 'Preferences updated successfully.')
        return redirect('account_settings')
    
    return redirect('account_settings')

def update_privacy(request):
    """
    Handles updates to privacy settings.
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        # Process form submission for privacy settings
        # This is a simplified example
        messages.success(request, 'Privacy settings updated successfully.')
        return redirect('account_settings')
    
    return redirect('account_settings')

def update_notifications(request):
    """
    Handles updates to notification settings.
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        # Get notification preferences from form
        email_notifications = 'email_notifications' in request.POST
        message_notifications = 'message_notifications' in request.POST
        booking_notifications = 'booking_notifications' in request.POST
        marketing_notifications = 'marketing_notifications' in request.POST
        
        # In a real implementation, you would save these to the user's profile
        # This is a simplified example
        
        messages.success(request, 'Notification settings updated successfully.')
        return redirect('account_settings')
    
    return redirect('account_settings')

def change_password(request):
    """
    Handles password change requests.
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validate current password
        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('account_settings')
        
        # Validate new password
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return redirect('account_settings')
        
        # Update password
        request.user.set_password(new_password)
        request.user.save()
        
        # Update session to prevent logout
        update_session_auth_hash(request, request.user)
        
        messages.success(request, 'Password changed successfully.')
        return redirect('account_settings')
    
    return redirect('account_settings')

def update_profile_photo(request):
    """
    Handles profile photo updates.
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST' and request.FILES.get('profile_photo'):
        user = request.user
        user.profile_photo = request.FILES['profile_photo']
        user.save()
        
        messages.success(request, 'Profile photo updated successfully.')
        return redirect('account_settings')
    
    return redirect('account_settings')

def update_account_type(request):
    """
    Handles account type changes (e.g., from seeker to provider or vice versa).
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        account_type = request.POST.get('account_type')
        if account_type in ['seeker', 'provider']:
            user = request.user
            user.account_type = account_type
            user.save()
            
            messages.success(request, f'Account type updated to {user.get_account_type_display()}.')
        else:
            messages.error(request, 'Invalid account type selected.')
        
        return redirect('account_settings')
    
    return redirect('account_settings')

def delete_account(request):
    """
    Handles account deletion requests.
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        # Verify confirmation
        confirmation = request.POST.get('confirmation')
        if confirmation != 'DELETE':
            messages.error(request, 'Incorrect confirmation text. Account not deleted.')
            return redirect('account_settings')
        
        # Delete the user account
        user = request.user
        logout(request)
        user.delete()
        
        messages.success(request, 'Your account has been permanently deleted.')
        return redirect('home')
    
    return redirect('account_settings')