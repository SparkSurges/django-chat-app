from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.shortcuts import redirect, render
from django.contrib import messages
from user.forms import LoginForm, RegistrationForm
from user.utils import anonymous_required

@anonymous_required(redirect_to=reverse('chat-room'))
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, 'Login successful.')

                return redirect(reverse('chat-room'))
            
            messages.error(request, 'Invalid username or password.')

    form = LoginForm()
    return render(request, 'user/login.html', {'form': form})

@login_required(login_url=reverse('login'))
def logout_view(request):
    logout(request)
    messages.success(request, 'Logout successfully.')
    return redirect('login')

@anonymous_required(redirect_to=reverse('chat-room'))
def registration_view(request):
    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            user.save()
            messages.success(request, 'You have signed up successfully.')
            login(request, user)
            return redirect(reverse('chat-room'))
        
        return render(request, 'user/registration.html', {'form': form})

    form = RegistrationForm()
    return render(request, 'user/registration.html', {'form': form})