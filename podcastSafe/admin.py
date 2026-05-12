from django.contrib import admin
from .models import Episode, Category, LiveStream, Donation


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon']


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ['title', 'episode_type', 'category', 'host', 'duration', 'views_count', 'is_published', 'created_at']
    list_filter = ['episode_type', 'category', 'is_published']
    search_fields = ['title', 'description', 'host']
    list_editable = ['is_published']


@admin.register(LiveStream)
class LiveStreamAdmin(admin.ModelAdmin):
    list_display = ['title', 'platform', 'status', 'viewers_count', 'scheduled_at']
    list_filter = ['platform', 'status']
    search_fields = ['title']


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ['name', 'amount', 'email', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['name', 'email']
