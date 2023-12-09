import base64
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.shortcuts import redirect, render
from django.contrib import messages
from user.forms import LoginForm, RegistrationForm, ProfileUpdateForm
from user.utils import anonymous_required
from user.tasks import upload_image

@login_required(login_url=reverse_lazy('login'))
def update_user_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES)

        if form.is_valid():
            if 'image' in request.FILES:
                image_file = request.FILES['image']

                if image_file.size > 1024*1024:
                    messages.error(request, 'Image size must be 1 megabyte or less.')
                    return redirect(reverse_lazy('chat-room'))

                picture = image_file.read()
                byte = base64.b64encode(picture)
                data = {
                    'picture': byte.decode('utf-8'),
                    'user': request.user
                }

                upload_image.delay(data=data)
                messages.success(request, 'Image uploading.')

            if request.POST.get('username'):
                request.user.username = request.POST['username']
                request.user.save()

            return redirect(reverse_lazy('chat-room'))

@anonymous_required(redirect_to=reverse_lazy('chat-room'))
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

                return redirect(reverse_lazy('chat-room'))
            
            messages.error(request, 'Invalid username or password.')

    form = LoginForm()
    return render(request, 'user/login.html', {'form': form})

@login_required(login_url=reverse_lazy('login'))
def logout_view(request):
    logout(request)
    messages.success(request, 'Logout successfully.')
    return redirect('login')

@anonymous_required(redirect_to=reverse_lazy('chat-room'))
def registration_view(request):
    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            user.save()
            messages.success(request, 'You have signed up successfully.')
            login(request, user)
            return redirect(reverse_lazy('chat-room'))
        
        return render(request, 'user/registration.html', {'form': form})

    form = RegistrationForm()
    return render(request, 'user/registration.html', {'form': form})
