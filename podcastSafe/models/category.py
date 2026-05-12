"""
Category model for SafePlace application
"""
from django.db import models


class Category(models.Model):
    """Model for categorizing episodes and content"""
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, default='church')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Catégories"
        ordering = ['name']
