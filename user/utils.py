import functools
from django.shortcuts import redirect

def anonymous_required(func, redirect_to=None):
    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(redirect_to or 'home')
        return func(request, *args, **kwargs)
    return wrapper
