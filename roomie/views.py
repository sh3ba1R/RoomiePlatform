from django.shortcuts import render, redirect, HttpResponse
from .models import RoommateProfile
from .forms import RoomForm, RoommateProfileForm

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required

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
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
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
        form = AuthenticationForm()
    return render(request, "login.html", {'form': form})

def list_room(request):
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
