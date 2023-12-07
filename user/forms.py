from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from user.models import Contact, CustomUser

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'username'}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'password'}
        )
    )

class RegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser  
        fields = ['username', 'email', 'password1', 'password2']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'picture']

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['username', 'email']
        labels = {'email': 'contact'}
