from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('podcasts/', views.podcasts, name='podcasts'),
    path('videos/', views.videos, name='videos'),
    path('podcasts/<int:pk>/', views.podcast_detail, name='podcast_detail'),
    path('episodes/<int:pk>/download/', views.download_episode, name='episode_download'),
    path('live/', views.live, name='live'),
    path('publish/', views.publish_episode, name='publish_episode'),
    path('manage-live-streams/', views.manage_live_streams, name='manage_live_streams'),

    # Inscription communauté
    path('inscription/', views.register, name='register'),
    


   

    path('apropos/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('access-denied/', views.access_denied, name='access_denied'),
    path('loading/', views.loading, name='loading'),
]



