from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth import authenticate, login, get_user_model,logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from core.models import Room, Message, RoomBooking
from django.db.models import Count, Q, F


from .forms import RoomieFormFactory,RoomieForms

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

    return render(request, 'home.html', {
        'featured_rooms': featured_rooms,
        'roommates': roommates,
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
                return redirect('home')  # Fixed Redirect to home after login
            else:
                form.add_error(None, 'Invalid username or password')
    else:
        # Use the factory to create an empty login form
        form = form_factory.create_login_form(request=request)
        
    return render(request, "login.html", {'form': form})

@login_required
def list_room(request):
    """
    Allow providers to list a room.
    """
    if request.user.account_type != 'provider':
        return redirect('home')  # Redirect seekers or unauthorized users to the home page

    if request.method == 'POST':
        form = RoomieForms.RoomForm(request.POST, request.FILES)
        if form.is_valid():
            room = form.save(commit=False)
            room.provider = request.user  # Assign the logged-in user as the room provider
            room.save()
            return redirect('home')  # Redirect to the home page after successful submission
    else:
        form = RoomieForms.RoomForm()

    return render(request, 'list_room.html', {'form': form, 'provider': request.user})



def find_roommate(request):
    roommates = User.objects.filter(account_type='seeker')  # Fetch only seekers
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
def my_bookings(request):
    """
    Display all bookings submitted by the seeker.
    """
    if request.user.account_type != 'seeker':
        return redirect('home')

    bookings = RoomBooking.objects.filter(seeker=request.user).select_related('room')
    return render(request, 'my_bookings.html', {'bookings': bookings})

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

    # Notify the seeker
    if status == 'approved':
        messages.success(request, f"Booking for {booking.room.title} has been approved.")
    elif status == 'rejected':
        messages.error(request, f"Booking for {booking.room.title} has been rejected.")

    return redirect('manage_bookings')