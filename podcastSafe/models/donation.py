"""
Donation model for SafePlace application
"""
from django.db import models


class Donation(models.Model):
    """Model for tracking donations and payments"""
    name = models.CharField(max_length=100, blank=True, verbose_name="Nom")
    email = models.EmailField(blank=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Montant")
    message = models.TextField(blank=True, verbose_name="Message")
    stripe_payment_intent = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Don {self.amount}€ - {self.name or 'Anonyme'}"

    class Meta:
        verbose_name = "Don"
        verbose_name_plural = "Dons"
        ordering = ['-created_at']
