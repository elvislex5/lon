from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.shortcuts import redirect
from functools import wraps

def login_required_message(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            return function(request, *args, **kwargs)
        else:
            messages.warning(request, 'Veuillez vous connecter pour accéder à cette page.')
            return redirect('login')
    return wrap 