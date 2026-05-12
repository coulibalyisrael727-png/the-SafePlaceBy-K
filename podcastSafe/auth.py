from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect
from functools import wraps


def owner_required(view_func):
    """
    Décorateur pour vérifier que l'utilisateur est le propriétaire du site.
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        # Vérifier si l'utilisateur est superutilisateur (propriétaire du site)
        if not request.user.is_authenticated:
            return redirect('admin:login')
        
        if not request.user.is_superuser and request.user.username != 'admin':
            # Rediriger vers une page d'erreur si ce n'est pas le propriétaire
            return redirect('access_denied')
        
        return view_func(request, *args, **kwargs)
    
    return wrapped_view


def owner_and_staff_required(view_func):
    """
    Décorateur pour staff et propriétaire du site.
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('admin:login')
        
        if not (request.user.is_staff or request.user.is_superuser):
            return redirect('access_denied')
        
        return view_func(request, *args, **kwargs)
    
    return wrapped_view
