from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Sum, Q, Avg
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import logging

from .models import Episode, Donation, Category, LiveStream, Subscription, ContactMessage

logger = logging.getLogger(__name__)

class IsDashboardOrAdmin(BasePermission):
    """Autorise l'accès si la requête contient la clé API du Dashboard ou si l'utilisateur est admin."""
    def has_permission(self, request, view):
        api_key = request.META.get('HTTP_X_API_KEY')
        expected_key = getattr(settings, 'DASHBOARD_API_KEY', 'safeplace_secret_dashboard_key_2026')
        if api_key == expected_key:
            return True
        return request.user and request.user.is_authenticated



# ──────────────────────────────────────────────
# Dashboard Data
# ──────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsDashboardOrAdmin])
def dashboard_data(request):
    """API endpoint pour fournir les données du dashboard"""
    try:
        total_episodes = Episode.objects.count()
        total_donations = Donation.objects.filter(status='completed').aggregate(
            total=Sum('amount')
        )['total'] or 0
        total_messages = ContactMessage.objects.count()
        unread_messages = ContactMessage.objects.filter(is_read=False).count()
        active_lives = LiveStream.objects.filter(status='live').count()
        total_subscribers = Subscription.objects.filter(is_active=True).count()

        # Épisodes récents
        recent_episodes = Episode.objects.order_by('-created_at')[:5]
        recent_episodes_data = [
            {
                'id': ep.id,
                'title': ep.title,
                'description': (ep.description or '')[:100],
                'created_at': ep.created_at.strftime('%Y-%m-%d'),
                'status': 'published' if ep.is_published else 'draft',
                'views': ep.views_count,
                'episode_type': ep.episode_type,
            }
            for ep in recent_episodes
        ]

        # Donations récentes
        recent_donations = Donation.objects.filter(status='completed').order_by('-created_at')[:5]
        recent_donations_data = [
            {
                'id': d.id,
                'name': d.name or 'Anonyme',
                'email': d.email,
                'amount': float(d.amount),
                'created_at': d.created_at.strftime('%Y-%m-%d'),
            }
            for d in recent_donations
        ]

        # Messages récents
        recent_messages = ContactMessage.objects.order_by('-created_at')[:5]
        recent_messages_data = [
            {
                'id': m.id,
                'name': m.name,
                'email': m.email,
                'subject': m.subject,
                'created_at': m.created_at.strftime('%Y-%m-%d'),
                'read': m.is_read,
            }
            for m in recent_messages
        ]

        # Stats 30 derniers jours
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_stats = {
            'new_episodes': Episode.objects.filter(created_at__gte=thirty_days_ago).count(),
            'recent_donations_amount': float(
                Donation.objects.filter(status='completed', created_at__gte=thirty_days_ago)
                .aggregate(total=Sum('amount'))['total'] or 0
            ),
            'active_streams': LiveStream.objects.filter(status='live').count(),
        }

        data = {
            'stats': {
                'total_episodes': total_episodes,
                'total_donations': float(total_donations),
                'total_messages': total_messages,
                'unread_messages': unread_messages,
                'active_lives': active_lives,
                'total_subscribers': total_subscribers,
            },
            'recent_data': {
                'recent_episodes': recent_episodes_data,
                'recent_donations': recent_donations_data,
                'recent_messages': recent_messages_data,
            },
            'recent_stats': recent_stats,
            'last_updated': timezone.now().isoformat(),
        }

        return Response(data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error in dashboard_data API: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ──────────────────────────────────────────────
# Episodes
# ──────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsDashboardOrAdmin])
def episodes_api(request):
    """Liste des épisodes avec pagination et filtrage"""
    try:
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        status_filter = request.GET.get('status', '')
        search = request.GET.get('search', '')
        episode_type = request.GET.get('type', '')

        queryset = Episode.objects.all()

        if status_filter == 'published':
            queryset = queryset.filter(is_published=True)
        elif status_filter == 'draft':
            queryset = queryset.filter(is_published=False)

        if episode_type:
            queryset = queryset.filter(episode_type=episode_type)

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )

        total = queryset.count()
        start = (page - 1) * page_size
        episodes = queryset.order_by('-created_at')[start:start + page_size]

        episodes_data = [
            {
                'id': ep.id,
                'title': ep.title,
                'description': (ep.description or '')[:200],
                'episode_type': ep.episode_type,
                'category': ep.category.name if ep.category else None,
                'category_id': ep.category_id,
                'is_published': ep.is_published,
                'audio_url': ep.audio_url,
                'video_url': ep.video_url,
                'duration': ep.duration,
                'cover_color': ep.cover_color,
                'views': ep.views_count,
                'created_at': ep.created_at.strftime('%Y-%m-%d'),
            }
            for ep in episodes
        ]

        return Response({
            'episodes': episodes_data,
            'pagination': {
                'page': page, 'page_size': page_size,
                'total': total, 'pages': (total + page_size - 1) // page_size
            }
        })

    except Exception as e:
        logger.error(f"Error in episodes_api: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsDashboardOrAdmin])
def episode_create(request):
    """Créer un épisode depuis le dashboard"""
    try:
        data = request.data
        title = (data.get('title') or '').strip()
        description = (data.get('description') or '').strip()
        episode_type = data.get('episode_type', 'podcast')
        category_id = data.get('category_id')
        audio_url = (data.get('audio_url') or '').strip()
        video_url = (data.get('video_url') or '').strip()
        duration = (data.get('duration') or '').strip()
        cover_color = data.get('cover_color', '#00261b')

        if not title or not description:
            return Response({'error': 'Titre et description obligatoires'}, status=400)

        category = None
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                pass

        episode = Episode.objects.create(
            title=title,
            description=description,
            episode_type=episode_type,
            category=category,
            audio_url=audio_url,
            video_url=video_url,
            duration=duration,
            cover_color=cover_color,
            is_published=True,
        )

        return Response({
            'success': True,
            'episode': {
                'id': episode.id,
                'title': episode.title,
                'created_at': episode.created_at.strftime('%Y-%m-%d'),
            }
        }, status=201)

    except Exception as e:
        logger.error(f"Error in episode_create: {str(e)}")
        return Response({'error': str(e)}, status=500)


@api_view(['DELETE'])
@permission_classes([IsDashboardOrAdmin])
def episode_delete(request, pk):
    """Supprimer un épisode"""
    try:
        episode = Episode.objects.get(id=pk)
        episode.delete()
        return Response({'success': True})
    except Episode.DoesNotExist:
        return Response({'error': 'Épisode non trouvé'}, status=404)
    except Exception as e:
        logger.error(f"Error in episode_delete: {str(e)}")
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsDashboardOrAdmin])
def categories_api(request):
    """Liste des catégories"""
    cats = Category.objects.all()
    return Response({
        'categories': [{'id': c.id, 'name': c.name, 'icon': c.icon} for c in cats]
    })


# ──────────────────────────────────────────────
# Donations
# ──────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsDashboardOrAdmin])
def donations_api(request):
    """Liste des donations avec stats"""
    try:
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        status_filter = request.GET.get('status', '')

        queryset = Donation.objects.all()
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        total = queryset.count()
        start = (page - 1) * page_size
        donations = queryset.order_by('-created_at')[start:start + page_size]

        donations_data = [
            {
                'id': d.id,
                'name': d.name or 'Anonyme',
                'email': d.email,
                'amount': float(d.amount),
                'message': d.message,
                'status': d.status,
                'created_at': d.created_at.strftime('%Y-%m-%d'),
            }
            for d in donations
        ]

        completed = Donation.objects.filter(status='completed')
        stats = {
            'total_amount': float(completed.aggregate(total=Sum('amount'))['total'] or 0),
            'total_count': completed.count(),
            'this_month': float(
                completed.filter(created_at__month=timezone.now().month)
                .aggregate(total=Sum('amount'))['total'] or 0
            ),
            'average': float(completed.aggregate(avg=Avg('amount'))['avg'] or 0),
            'donor_count': completed.values('email').distinct().count(),
            'pending_count': Donation.objects.filter(status='pending').count(),
        }

        return Response({
            'donations': donations_data,
            'stats': stats,
            'pagination': {
                'page': page, 'page_size': page_size,
                'total': total, 'pages': (total + page_size - 1) // page_size
            }
        })

    except Exception as e:
        logger.error(f"Error in donations_api: {str(e)}")
        return Response({'error': str(e)}, status=500)


# ──────────────────────────────────────────────
# Live Streams
# ──────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsDashboardOrAdmin])
def livestreams_api(request):
    """Liste des live streams"""
    try:
        streams = LiveStream.objects.all().order_by('-created_at')
        data = [
            {
                'id': s.id,
                'title': s.title,
                'description': s.description,
                'platform': s.platform,
                'platform_display': s.get_platform_display(),
                'stream_url': s.stream_url,
                'embed_url': s.embed_url,
                'status': s.status,
                'status_display': s.get_status_display(),
                'viewers_count': s.viewers_count,
                'scheduled_at': s.scheduled_at.strftime('%Y-%m-%d %H:%M') if s.scheduled_at else None,
                'created_at': s.created_at.strftime('%Y-%m-%d'),
            }
            for s in streams
        ]
        return Response({
            'livestreams': data,
            'platforms': [{'value': k, 'label': v} for k, v in LiveStream.PLATFORM_CHOICES],
            'statuses': [{'value': k, 'label': v} for k, v in LiveStream.STATUS_CHOICES],
        })
    except Exception as e:
        logger.error(f"Error in livestreams_api: {str(e)}")
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsDashboardOrAdmin])
def livestream_create(request):
    """Créer un live stream"""
    try:
        data = request.data
        title = (data.get('title') or '').strip()
        if not title:
            return Response({'error': 'Titre obligatoire'}, status=400)

        stream = LiveStream.objects.create(
            title=title,
            description=(data.get('description') or '').strip(),
            platform=data.get('platform', 'youtube'),
            stream_url=(data.get('stream_url') or '').strip(),
            embed_url=(data.get('embed_url') or '').strip(),
            status=data.get('status', 'scheduled'),
        )
        return Response({'success': True, 'id': stream.id}, status=201)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['PUT'])
@permission_classes([IsDashboardOrAdmin])
def livestream_update(request, pk):
    """Mettre à jour un live stream"""
    try:
        stream = LiveStream.objects.get(id=pk)
        data = request.data
        for field in ['title', 'description', 'platform', 'stream_url', 'embed_url', 'status']:
            val = data.get(field)
            if val is not None:
                setattr(stream, field, val.strip() if isinstance(val, str) else val)
        stream.save()
        return Response({'success': True})
    except LiveStream.DoesNotExist:
        return Response({'error': 'Live non trouvé'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['DELETE'])
@permission_classes([IsDashboardOrAdmin])
def livestream_delete(request, pk):
    """Supprimer un live stream"""
    try:
        LiveStream.objects.get(id=pk).delete()
        return Response({'success': True})
    except LiveStream.DoesNotExist:
        return Response({'error': 'Live non trouvé'}, status=404)


# ──────────────────────────────────────────────
# Messages (Contact)
# ──────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsDashboardOrAdmin])
def messages_api(request):
    """Liste des messages de contact"""
    try:
        status_filter = request.GET.get('status', '')
        priority = request.GET.get('priority', '')
        search = request.GET.get('search', '')

        queryset = ContactMessage.objects.all()
        if status_filter == 'read':
            queryset = queryset.filter(is_read=True)
        elif status_filter == 'unread':
            queryset = queryset.filter(is_read=False)
        if priority:
            queryset = queryset.filter(priority=priority)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(subject__icontains=search) | Q(email__icontains=search)
            )

        messages_list = queryset.order_by('-created_at')
        data = [
            {
                'id': m.id,
                'name': m.name,
                'email': m.email,
                'subject': m.subject,
                'message': m.message,
                'priority': m.priority,
                'read': m.is_read,
                'created_at': m.created_at.strftime('%Y-%m-%d'),
            }
            for m in messages_list
        ]

        stats = {
            'total': ContactMessage.objects.count(),
            'unread': ContactMessage.objects.filter(is_read=False).count(),
            'high_priority': ContactMessage.objects.filter(priority='high').count(),
            'read': ContactMessage.objects.filter(is_read=True).count(),
        }

        return Response({'messages': data, 'stats': stats})
    except Exception as e:
        logger.error(f"Error in messages_api: {str(e)}")
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsDashboardOrAdmin])
def message_mark_read(request, pk):
    """Marquer un message comme lu"""
    try:
        msg = ContactMessage.objects.get(id=pk)
        msg.is_read = True
        msg.save()
        return Response({'success': True})
    except ContactMessage.DoesNotExist:
        return Response({'error': 'Message non trouvé'}, status=404)


@api_view(['DELETE'])
@permission_classes([IsDashboardOrAdmin])
def message_delete(request, pk):
    """Supprimer un message"""
    try:
        ContactMessage.objects.get(id=pk).delete()
        return Response({'success': True})
    except ContactMessage.DoesNotExist:
        return Response({'error': 'Message non trouvé'}, status=404)


@api_view(['POST'])
@permission_classes([IsDashboardOrAdmin])
def message_mark_all_read(request):
    """Marquer tous les messages comme lus"""
    ContactMessage.objects.filter(is_read=False).update(is_read=True)
    return Response({'success': True})


# ──────────────────────────────────────────────
# Subscriptions
# ──────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsDashboardOrAdmin])
def subscriptions_api(request):
    """Liste des abonnements"""
    try:
        subs = Subscription.objects.all().order_by('-created_at')
        data = [
            {
                'id': s.id,
                'first_name': s.first_name,
                'last_name': s.last_name,
                'email': s.email,
                'notify_podcasts': s.notify_podcasts,
                'notify_live': s.notify_live,
                'notify_videos': s.notify_videos,
                'is_active': s.is_active,
                'created_at': s.created_at.strftime('%Y-%m-%d'),
            }
            for s in subs
        ]
        stats = {
            'total': Subscription.objects.count(),
            'active': Subscription.objects.filter(is_active=True).count(),
        }
        return Response({'subscriptions': data, 'stats': stats})
    except Exception as e:
        return Response({'error': str(e)}, status=500)


# ──────────────────────────────────────────────
# Analytics
# ──────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsDashboardOrAdmin])
def analytics_data(request):
    """Analytics détaillées"""
    try:
        days = int(request.GET.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)

        # Top épisodes
        top_episodes = Episode.objects.order_by('-views_count')[:10]

        # Totaux
        total_views = Episode.objects.aggregate(total=Sum('views_count'))['total'] or 0
        total_donations = float(
            Donation.objects.filter(status='completed').aggregate(total=Sum('amount'))['total'] or 0
        )
        total_subs = Subscription.objects.filter(is_active=True).count()

        # Par catégorie
        categories = Category.objects.annotate(
            episode_count=Count('episode')
        ).order_by('-episode_count')[:5]

        data = {
            'total_views': total_views,
            'total_donations': total_donations,
            'total_subscribers': total_subs,
            'total_episodes': Episode.objects.count(),
            'top_episodes': [
                {'id': ep.id, 'title': ep.title, 'views': ep.views_count, 'type': ep.episode_type}
                for ep in top_episodes
            ],
            'categories': [
                {'name': c.name, 'count': c.episode_count}
                for c in categories
            ],
            'period_days': days,
        }

        return Response(data)
    except Exception as e:
        logger.error(f"Error in analytics_data: {str(e)}")
        return Response({'error': str(e)}, status=500)
