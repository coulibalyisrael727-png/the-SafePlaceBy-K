from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, default='church')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Catégories"


class Episode(models.Model):
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


class LiveStream(models.Model):
    PLATFORM_CHOICES = [
        ('youtube', 'YouTube'),
        ('facebook', 'Facebook'),
        ('tiktok', 'TikTok'),
        ('instagram', 'Instagram'),
        ('spotify', 'Spotify'),
    ]
    STATUS_CHOICES = [
        ('live', 'En Direct'),
        ('scheduled', 'Programmé'),
        ('ended', 'Terminé'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    stream_url = models.URLField(blank=True)
    embed_url = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    viewers_count = models.IntegerField(default=0)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.get_platform_display()})"

    class Meta:
        verbose_name = "Live Stream"


class Donation(models.Model):
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


class Subscription(models.Model):
    """Modèle pour les abonnements gratuits aux notifications"""
    NOTIFICATION_CHOICES = [
        ('podcasts', 'Nouveaux Podcasts'),
        ('live', 'Émissions Live'),
        ('videos', 'Nouvelles Vidéos'),
    ]
    
    first_name = models.CharField(max_length=100, verbose_name="Prénom")
    last_name = models.CharField(max_length=100, blank=True, verbose_name="Nom")
    email = models.EmailField(unique=True, verbose_name="Adresse e-mail")
    
    # Notifications préférées
    notify_podcasts = models.BooleanField(default=True, verbose_name="Notifier pour les podcasts")
    notify_live = models.BooleanField(default=True, verbose_name="Notifier pour les lives")
    notify_videos = models.BooleanField(default=False, verbose_name="Notifier pour les vidéos")
    
    is_active = models.BooleanField(default=True, verbose_name="Abonnement actif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    class Meta:
        verbose_name = "Abonnement"
        verbose_name_plural = "Abonnements"
        ordering = ['-created_at']
