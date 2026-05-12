"""
Episode model for SafePlace application
"""
from django.db import models
from .category import Category


class Episode(models.Model):
    """Model for podcast and video episodes"""
    TYPE_CHOICES = [('podcast', 'Podcast'), ('video', 'Vidéo')]

    title = models.CharField(max_length=200)
    description = models.TextField()
    episode_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='podcast')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    audio_url = models.URLField(blank=True)
    video_url = models.URLField(blank=True)
    duration = models.CharField(max_length=10, blank=True)
    host = models.CharField(max_length=100, blank=True, default='The SafePlace by K')
    cover_color = models.CharField(max_length=7, default='#00261b')
    views_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Épisode"
        verbose_name_plural = "Épisodes"
