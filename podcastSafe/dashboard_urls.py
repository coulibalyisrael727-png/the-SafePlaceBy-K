from django.urls import path

from . import admin_views

app_name = 'dashboard'

urlpatterns = [
    # Ne pas exposer l'accès depuis le site principal: chemin à part.
    path('dashboard/', admin_views.dashboard_admin, name='dashboard_admin'),
]

