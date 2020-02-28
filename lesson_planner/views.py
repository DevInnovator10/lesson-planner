from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .forms import SignUpForm
from lesson_plans.models import UserProfile
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # role = form.cleaned_data['role']

            # First check if the username already exists
            if User.objects.filter(username=username).exists():
                form.add_error('username', 'Username already taken.')
                return render(request, 'signup.html', {'form': form})

            # Create the user
            user = User.objects.create_user(username=username, email=email, password=password)

            # Only create profile if it doesn't already exist
            # UserProfile.objects.create(user=user, role=role)

            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

def home_screen(request):
    return render(request, 'home.html')