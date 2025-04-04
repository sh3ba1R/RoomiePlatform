from django.shortcuts import render, HttpResponse


def home(request):
    return render(request, "home.html")

def register(request):
    return render(request, "register.html")

def user_login(request):
    return render(request, "login.html")

def list_room(request):
    return render(request, "list_room.html")

def find_roommate(request):
    return render(request, "find_roommate.html")
