from django.urls import path
from user.views import (
    login_view, 
    registration_view, 
    logout_view,
    update_user_view
)

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', registration_view, name='register'),
    path('upload-image/', update_user_view, name='update-profile')
]