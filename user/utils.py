import functools
from django.shortcuts import redirect

def anonymous_required(redirect_to=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                return redirect(redirect_to or 'home')
            return func(request, *args, **kwargs)
        return wrapper
    return decorator

def generate_image_name(instance):
    return f'user_{instance.email}'
