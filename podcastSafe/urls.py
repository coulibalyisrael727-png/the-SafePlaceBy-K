from django.urls import path
from . import views

# Nouvelle section dashboard (accès hors site principal)
from .dashboard_urls import urlpatterns as dashboard_urlpatterns

urlpatterns = [
    path('', views.home, name='home'),
    path('podcasts/', views.podcasts, name='podcasts'),
    path('videos/', views.videos, name='videos'),
    path('podcasts/<int:pk>/', views.podcast_detail, name='podcast_detail'),
    path('live/', views.live, name='live'),
    # (dashboard interne retiré → utiliser le dashboard-service sur port 8001)

    path('abonnements/', views.donate, name='subscriptions'),
    path('inscription/', views.register, name='register'),
    path('donate/', views.subscriptions, name='donate'),
    path('api/subscription/create/', views.create_subscription, name='create_subscription'),
    path('api/donation/create/', views.create_donation, name='create_donation'),
    path('api/donation/pledge-notify/', views.pledge_donation_notify, name='pledge_donation_notify'),
    path('api/donation/confirm/', views.confirm_donation, name='confirm_donation'),
    path('api/stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),

    path('apropos/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('access-denied/', views.access_denied, name='access_denied'),
    path('loading/', views.loading, name='loading'),
    
]

# Ajoute les routes dashboard hors site principal
urlpatterns += list(dashboard_urlpatterns)


