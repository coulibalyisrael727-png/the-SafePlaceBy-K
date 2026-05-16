from django.shortcuts import redirect
from functools import wraps


def owner_required(view_func):
    """Accès uniquement au propriétaire (superuser / username admin)."""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('admin:login')

        if not request.user.is_superuser and request.user.username != 'admin':
            return redirect('access_denied')

        return view_func(request, *args, **kwargs)

    return wrapped_view


def subscriber_required(view_func):
    """Accès dashboard aux personnes inscrites (Subscription active via email)."""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('admin:login')

        email = getattr(request.user, 'email', None)
        if not email:
            return redirect('access_denied')

        # Import local pour éviter circular import
        from .models import Subscription

        sub = Subscription.objects.filter(email=email, is_active=True).first()
        if not sub:
            return redirect('access_denied')

        # utile dans les templates
        request.subscription = sub
        return view_func(request, *args, **kwargs)

    return wrapped_view


def owner_and_staff_required(view_func):
    """Accès staff ou propriétaire."""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('admin:login')

        if not (request.user.is_staff or request.user.is_superuser):
            return redirect('access_denied')

        return view_func(request, *args, **kwargs)

    return wrapped_view

