from django.contrib.auth import authenticate, login , logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect

def login_page(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == "POST":
        email_or_username = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember') == 'on'

        # Check if input is email
        if '@' in email_or_username:
            try:
                user_obj = User.objects.get(email=email_or_username)
                username = user_obj.username
            except User.DoesNotExist:
                messages.error(request, 'No account found with this email address')
                return redirect('login')
        else:
            # It's a username
            username = email_or_username
            if User.objects.filter(username=username).exists():
                print(f"🔍 Found user by username: {username}")
            else:
                print(f"🔍 No user found with username: {username}")
                messages.error(request, 'No account found with this username')
                return redirect('login')

        # Authenticate user
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            
            # Remember me functionality
            if not remember_me:
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(1209600)
                
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('home')
        else:
            messages.error(request, 'Invalid password')
            return redirect('login')

    return render(request, 'login_page.html')



def register(request):
    if request.method == "POST":
        fname = request.POST.get('fname')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if user already exists
        if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already taken')
            return redirect('register')
        
        try:
            # Create user with both username and email
            user = User.objects.create_user(
                username=email,      # Username bhi email hi rakhenge
                email=email,         # Email field set karein
                first_name=fname,
                password=password
            )
            
            messages.success(request, 'Your account created successfully! Please login.')
            return redirect('login')  # Register ke baad login page redirect karein
            
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return redirect('register')

    return render(request, 'register.html')


def logout_page(request):
    logout(request)
    return redirect('login')