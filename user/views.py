from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.contrib import messages
from user.forms import CustomLoginForm, CustomRegistrationForm

def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            print('here')
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, 'Login successful.')

                return redirect('chat-room')
            
            messages.error(request, 'Invalid username or password.')

    form = CustomLoginForm()
    return render(request, 'user/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'Logout successfully.')
    return redirect('login')

def registration_view(request):
    if request.method == 'GET':
        form = CustomRegistrationForm()
        return render(request, 'user/registration.html', {'form': form})
    
    if request.method == 'POST':
        form = CustomRegistrationForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            user.save()
            messages.success(request, 'You have signed up successfully.')
            login(request, user)
            return redirect('chat-room')
        
        return render(request, 'user/registration.html', {'form': form})
