from orders_app.email_utils import send_welcome_email
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserLoginForm
from orders_app.email_utils import send_welcome_email

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Set the backend for the user
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            
            login(request, user)
            messages.success(request, f'Welcome {user.username}! Your account has been created successfully.')
            return redirect('products:home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'users_app/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Set the backend for the user
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                next_page = request.GET.get('next', 'products:home')
                return redirect(next_page)
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    
    return render(request, 'users_app/login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('products:home')

@login_required
def profile(request):
    return render(request, 'users_app/profile.html')
@login_required
def edit_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.phone_number = request.POST.get('phone_number', '')
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('users:profile')
    return render(request, 'users_app/edit_profile.html')
from django.contrib.auth import update_session_auth_hash

@login_required
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        if not request.user.check_password(old_password):
            messages.error(request, 'Current password is incorrect.')
        elif new_password1 != new_password2:
            messages.error(request, 'New passwords do not match.')
        elif len(new_password1) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
        else:
            request.user.set_password(new_password1)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Password changed successfully!')
            return redirect('users:profile')
    
    return render(request, 'users_app/change_password.html')
def social_login_simulate(request, provider):
    """Simulate social login for demo purposes"""
    # For demo, automatically login as a demo user
    from django.contrib.auth.models import User
    user, created = User.objects.get_or_create(
        username=f'{provider}_demo_user',
        defaults={
            'email': f'{provider}@demo.com',
            'first_name': provider.capitalize(),
            'last_name': 'User'
        }
    )
    login(request, user)
    messages.success(request, f'Successfully logged in with {provider.capitalize()}!')
    return redirect('/')