from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import RoommateProfile
from .forms import RoomForm, RoommateProfileForm,RoomieFormFactory
from core.models import RoommateProfile 





def home(request):
    return render(request, "home.html")

def register(request):
    """
    Handle user registration process.
    Renders the registration form for GET requests. For POST requests,
    validates the submitted data, creates a new user account, and logs in
    the user if validation passes.
    Parameters:
    ----------
    request : HttpRequest
        The HTTP request object
    Returns:
    -------
    HttpResponse
        Renders the registration page for GET requests
        Redirects to home page after successful registration
        Redirects back to registration page with error messages on validation failure
    Side effects:
    ------------
    - Creates a new User object in the database on successful registration
    - Logs in the user on successful registration
    - Displays error messages for validation failures (password mismatch, username taken)
    """
    register = "register.html"
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm = request.POST['confirm']

        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return redirect(register)

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect(register)

        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return redirect("home.html")  # Redirect to home after registering
    return render(request, register)

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
                return redirect('home.html')  # Redirect to home after login
            else:
                form.add_error(None, 'Invalid username or password')
    else:
        # Use the factory to create an empty login form
        form = form_factory.create_login_form(request=request)
        
    return render(request, "login.html", {'form': form})

def list_room(request):
    """
    Handle the room listing process through form submission.

    This view function manages both the display of the room listing form (GET)
    and the processing of room data (POST). Upon successful submission, the room
    is associated with the current user as the owner.

    Args:
        request: HttpRequest object containing metadata about the request

    Returns:
        HttpResponse: Renders list_room.html with the form for GET requests,
                      or redirects to 'home' after successful POST submission
    """
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.owner = request.user
            room.save()
            return redirect('home')
    else:
        form = RoomForm()
    return render(request, "list_room.html", {'form': form})

def find_roommate(request):
    """
    Handle the creation and updating of roommate profiles.
    This view function manages the process of creating a new roommate profile or updating 
    an existing one. It handles both GET and POST requests:
    - GET: Displays the roommate profile form (pre-populated if profile exists)
    - POST: Processes the submitted form, saves the profile, and redirects to home
    Parameters:
        request (HttpRequest): The HTTP request object containing metadata about the request
    Returns:
        HttpResponse: Renders the 'find_roommate.html' template with the form on GET requests
                      or redirects to 'home' on successful POST requests
    """
    try:
        profile = RoommateProfile.objects.get(user=request.user)
    except RoommateProfile.DoesNotExist:
        profile = None

    if request.method == 'POST':
        form = RoommateProfileForm(request.POST, instance=profile)
        if form.is_valid():
            roommate_profile = form.save(commit=False)
            roommate_profile.user = request.user
            roommate_profile.save()
            return redirect('home')
    else:
        form = RoommateProfileForm(instance=profile)
    
    return render(request, 'find_roommate.html', {'form': form})