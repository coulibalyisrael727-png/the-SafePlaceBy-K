from django.urls import path
from django.contrib.auth import views as auth_views

from dashboard import views

urlpatterns = [
    # Dashboard home
    path('', views.dashboard_home, name='dashboard_home'),

    # Content management
    path('video-export/', views.video_export, name='video_export'),
    path('publish/', views.episode_publishing, name='episode_publishing'),
    path('episodes/<int:pk>/delete/', views.episode_delete, name='episode_delete'),

    # Live streams
    path('lives/', views.live_management, name='live_management'),
    path('lives/<int:pk>/delete/', views.live_delete, name='live_delete'),

    # Donations
    path('donations/', views.donation_management, name='donation_management'),

    # Messages
    path('messages/', views.message_management, name='message_management'),
    path('messages/<int:pk>/<str:action>/', views.message_action, name='message_action'),
    path('messages/mark-all-read/', views.mark_all_messages_read, name='mark_all_messages_read'),

    # Analytics
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),

    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='dashboard/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # Health check
    path('health/', views.health_check, name='health_check'),
]
