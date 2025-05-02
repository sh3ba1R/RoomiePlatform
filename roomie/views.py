from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth import authenticate, login, get_user_model,logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from core.models import Room, Message, RoomBooking, SupportTicket, TicketResponse, RoomContract,Subscription
from django.db.models import Count, Q, F
from reportlab.pdfgen import canvas
from io import BytesIO
from .forms import RoomieFormFactory, RoomieForms
from django.urls import reverse
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
    contract = get_object_or_404(RoomContract, id=contract_id, seeker=request.user)

    # Generate PDF
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.drawString(100, 800, f"Room Contract")
    pdf.drawString(100, 780, f"Room: {contract.room.title}")
    pdf.drawString(100, 760, f"Seeker: {contract.seeker.username}")
    pdf.drawString(100, 740, f"Provider: {contract.provider.username}")
    pdf.drawString(100, 720, f"Start Date: {contract.start_date}")
    pdf.drawString(100, 700, f"End Date: {contract.end_date}")
    pdf.drawString(100, 680, f"Rent: ${contract.rent_amount}/month")
    pdf.save()

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="contract_{contract.id}.pdf"'
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