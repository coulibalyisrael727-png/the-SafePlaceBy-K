from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('podcastSafe.urls')),
    # API endpoints for dashboard microservice
    path('api/v1/', include('podcastSafe.api_urls')),
]
