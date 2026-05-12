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
    # (ancien studio exposé) -> gardé pour compatibilité
    path('studio/', views.dashboard, name='dashboard'),
    path('studio/publish/', views.publish_episode, name='publish_episode'),
    path('studio/live-streams/', views.manage_live_streams, name='manage_live_streams'),

    path('abonnements/', views.subscriptions, name='subscriptions'),
    path('donate/', views.donate, name='donate'),
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


