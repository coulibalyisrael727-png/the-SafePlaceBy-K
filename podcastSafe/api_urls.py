from django.urls import path
from . import api_views

app_name = 'api'

urlpatterns = [
    # Dashboard overview
    path('dashboard-data/', api_views.dashboard_data, name='dashboard_data'),

    # Analytics
    path('analytics/', api_views.analytics_data, name='analytics'),

    # Episodes
    path('episodes/', api_views.episodes_api, name='episodes_api'),
    path('episodes/create/', api_views.episode_create, name='episode_create'),
    path('episodes/<int:pk>/delete/', api_views.episode_delete, name='episode_delete'),
    path('categories/', api_views.categories_api, name='categories_api'),

    # Live Streams
    path('livestreams/', api_views.livestreams_api, name='livestreams_api'),
    path('livestreams/create/', api_views.livestream_create, name='livestream_create'),
    path('livestreams/<int:pk>/update/', api_views.livestream_update, name='livestream_update'),
    path('livestreams/<int:pk>/delete/', api_views.livestream_delete, name='livestream_delete'),

    # Messages
    path('messages/', api_views.messages_api, name='messages_api'),
    path('messages/<int:pk>/read/', api_views.message_mark_read, name='message_mark_read'),
    path('messages/<int:pk>/delete/', api_views.message_delete, name='message_delete'),
    path('messages/mark-all-read/', api_views.message_mark_all_read, name='message_mark_all_read'),

  
]
