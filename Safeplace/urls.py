from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponseRedirect
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('podcastSafe.urls')),
    # Redirection vers le microservice dashboard (Netlify)
    path('dashboard/', lambda request: HttpResponseRedirect(settings.DASHBOARD_NETLIFY_URL)),
    # API endpoints for dashboard microservice
    path('api/v1/', include('podcastSafe.api_urls')),
]
