import requests
import logging
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings

logger = logging.getLogger(__name__)

API_URL = getattr(settings, 'MAIN_API_URL', 'http://127.0.0.1:8000/api/v1/')
SITE_URL = getattr(settings, 'MAIN_SITE_URL', 'http://127.0.0.1:8000')
DASHBOARD_API_KEY = getattr(settings, 'DASHBOARD_API_KEY', 'safeplace_secret_dashboard_key_2026')

def _get_headers():
    return {
        'Accept': 'application/json',
        'X-API-KEY': DASHBOARD_API_KEY,
    }

def _api_get(path, request, params=None):
    """Helper: GET request to main app API using the logged-in user's session."""
    url = f"{API_URL}{path}"
    try:
        resp = requests.get(
            url, params=params, timeout=10,
            headers=_get_headers(),
        )
        if resp.status_code == 200:
            return resp.json(), True
        elif resp.status_code in (401, 403):
            return {'error': 'Non autorisé — vérifiez vos identifiants API'}, False
        else:
            return {'error': f'Erreur API ({resp.status_code})'}, False
    except requests.ConnectionError:
        return {'error': 'Impossible de joindre l\'application principale (port 8000)'}, False
    except requests.Timeout:
        return {'error': 'Timeout — l\'application principale ne répond pas'}, False
    except Exception as e:
        logger.error(f"API GET error: {e}")
        return {'error': str(e)}, False


def _api_post(path, request, data=None, files=None):
    """Helper: POST/PUT/DELETE request to main app API."""
    url = f"{API_URL}{path}"
    try:
        resp = requests.post(
            url, json=data, files=files, timeout=30,
            headers=_get_headers(),
        )
        if resp.status_code in (200, 201):
            return resp.json(), True
        else:
            try:
                err = resp.json().get('error', f'Erreur API ({resp.status_code})')
            except Exception:
                err = f'Erreur API ({resp.status_code})'
            return {'error': err}, False
    except requests.ConnectionError:
        return {'error': 'Impossible de joindre l\'application principale'}, False
    except requests.Timeout:
        return {'error': 'Timeout API'}, False
    except Exception as e:
        logger.error(f"API POST error: {e}")
        return {'error': str(e)}, False


def _api_method(method, path, request, data=None):
    """Helper: arbitrary HTTP method to main app API."""
    url = f"{API_URL}{path}"
    try:
        resp = getattr(requests, method.lower())(
            url, json=data, timeout=15,
            headers=_get_headers(),
        )
        if resp.status_code in (200, 201, 204):
            try:
                return resp.json(), True
            except Exception:
                return {}, True
        else:
            try:
                err = resp.json().get('error', f'Erreur ({resp.status_code})')
            except Exception:
                err = f'Erreur ({resp.status_code})'
            return {'error': err}, False
    except Exception as e:
        return {'error': str(e)}, False


# ──────────────────────────────────────────────
# Dashboard Home
# ──────────────────────────────────────────────

@login_required
def dashboard_home(request):
    """Vue principale du dashboard — données réelles depuis l'API"""
    api_data, connected = _api_get('dashboard-data/', request)

    context = {
        'page_title': 'Tableau de Bord',
        'api_connected': connected,
        'stats': api_data.get('stats', {}),
        'recent_data': api_data.get('recent_data', {}),
        'recent_stats': api_data.get('recent_stats', {}),
        'error_message': api_data.get('error') if not connected else None,
    }

    return render(request, 'dashboard/home.html', context)


# ──────────────────────────────────────────────
# Video Export
# ──────────────────────────────────────────────

@login_required
def video_export(request):
    """Export vidéo vers le site principal"""
    if request.method == 'POST':
        data = {
            'title': request.POST.get('title', ''),
            'description': request.POST.get('description', ''),
            'episode_type': 'video',
            'video_url': request.POST.get('video_url', ''),
            'category_id': request.POST.get('category') or None,
            'cover_color': request.POST.get('cover_color', '#00261b'),
        }

        result, success = _api_post('episodes/create/', request, data=data)

        if success:
            messages.success(request, f'Vidéo "{data["title"]}" exportée avec succès!')
            return redirect('dashboard_home')
        else:
            messages.error(request, result.get('error', 'Erreur lors de l\'export'))

    # Charger les catégories
    cats_data, _ = _api_get('categories/', request)
    categories = cats_data.get('categories', [])

    return render(request, 'dashboard/video_export.html', {
        'categories': categories,
    })


# ──────────────────────────────────────────────
# Episode Publishing
# ──────────────────────────────────────────────

@login_required
def episode_publishing(request):
    """Publier un épisode (podcast ou vidéo)"""
    if request.method == 'POST':
        data = {
            'title': request.POST.get('title', ''),
            'description': request.POST.get('description', ''),
            'episode_type': request.POST.get('episode_type', 'podcast'),
            'audio_url': request.POST.get('audio_url', ''),
            'video_url': request.POST.get('video_url', ''),
            'duration': request.POST.get('duration', ''),
            'category_id': request.POST.get('category') or None,
            'cover_color': request.POST.get('cover_color', '#00261b'),
        }

        result, success = _api_post('episodes/create/', request, data=data)

        if success:
            messages.success(request, f'Épisode "{data["title"]}" publié avec succès!')
            return redirect('dashboard_home')
        else:
            messages.error(request, result.get('error', 'Erreur lors de la publication'))

    # Charger les catégories
    cats_data, _ = _api_get('categories/', request)
    categories = cats_data.get('categories', [])

    return render(request, 'dashboard/publish_episode.html', {
        'categories': categories,
        'main_api_url': API_URL,
    })


@login_required
def episode_delete(request, pk):
    """Supprimer un épisode"""
    result, success = _api_method('delete', f'episodes/{pk}/delete/', request)
    
    if success:
        messages.success(request, 'Épisode supprimé avec succès!')
    else:
        messages.error(request, result.get('error', 'Erreur lors de la suppression'))
    
    return redirect('episode_publishing')


# ──────────────────────────────────────────────
# Donations
# ──────────────────────────────────────────────

@login_required
def donation_management(request):
    """Gestion des donations — données réelles"""
    status_filter = request.GET.get('status', '')
    api_data, connected = _api_get('donations/', request, params={'status': status_filter} if status_filter else None)

    context = {
        'donations': api_data.get('donations', []),
        'donation_stats': api_data.get('stats', {}),
        'api_connected': connected,
        'error_message': api_data.get('error') if not connected else None,
    }
    return render(request, 'dashboard/donations.html', context)


# ──────────────────────────────────────────────
# Messages
# ──────────────────────────────────────────────

@login_required
def message_management(request):
    """Gestion des messages de contact — données réelles"""
    status_filter = request.GET.get('status', '')
    priority = request.GET.get('priority', '')
    search = request.GET.get('search', '')

    params = {}
    if status_filter:
        params['status'] = status_filter
    if priority:
        params['priority'] = priority
    if search:
        params['search'] = search

    api_data, connected = _api_get('messages/', request, params=params if params else None)

    context = {
        'messages_list': api_data.get('messages', []),
        'msg_stats': api_data.get('stats', {}),
        'api_connected': connected,
        'error_message': api_data.get('error') if not connected else None,
    }
    return render(request, 'dashboard/messages.html', context)


@login_required
def message_action(request, pk, action):
    """Actions sur un message (lire/supprimer)"""
    if action == 'read':
        result, ok = _api_method('post', f'messages/{pk}/read/', request)
    elif action == 'delete':
        result, ok = _api_method('delete', f'messages/{pk}/delete/', request)
    else:
        messages.error(request, 'Action inconnue')
        return redirect('message_management')

    if ok:
        messages.success(request, 'Action effectuée')
    else:
        messages.error(request, result.get('error', 'Erreur'))

    return redirect('message_management')


@login_required
def mark_all_messages_read(request):
    """Marquer tous les messages comme lus"""
    result, ok = _api_method('post', 'messages/mark-all-read/', request)
    if ok:
        messages.success(request, 'Tous les messages ont été marqués comme lus')
    else:
        messages.error(request, result.get('error', 'Erreur'))
    return redirect('message_management')


# ──────────────────────────────────────────────
# Live Management
# ──────────────────────────────────────────────

@login_required
def live_management(request):
    """Gestion des live streams — données réelles"""
    if request.method == 'POST':
        data = {
            'title': request.POST.get('title', ''),
            'description': request.POST.get('description', ''),
            'platform': request.POST.get('platform', 'youtube'),
            'stream_url': request.POST.get('stream_url', ''),
            'embed_url': request.POST.get('embed_url', ''),
            'status': request.POST.get('status', 'scheduled'),
        }
        result, ok = _api_post('livestreams/create/', request, data=data)
        if ok:
            messages.success(request, f'Live "{data["title"]}" créé avec succès!')
        else:
            messages.error(request, result.get('error', 'Erreur'))
        return redirect('live_management')

    api_data, connected = _api_get('livestreams/', request)

    context = {
        'livestreams': api_data.get('livestreams', []),
        'platforms': api_data.get('platforms', []),
        'statuses': api_data.get('statuses', []),
        'api_connected': connected,
        'error_message': api_data.get('error') if not connected else None,
    }
    return render(request, 'dashboard/lives.html', context)


@login_required
def live_delete(request, pk):
    """Supprimer un live stream"""
    result, ok = _api_method('delete', f'livestreams/{pk}/delete/', request)
    if ok:
        messages.success(request, 'Live supprimé')
    else:
        messages.error(request, result.get('error', 'Erreur'))
    return redirect('live_management')


# ──────────────────────────────────────────────
# Analytics
# ──────────────────────────────────────────────

@login_required
def analytics_dashboard(request):
    """Tableau de bord analytics — données réelles"""
    days = request.GET.get('days', 30)
    api_data, connected = _api_get('analytics/', request, params={'days': days})

    context = {
        'analytics': api_data if connected else {},
        'api_connected': connected,
        'error_message': api_data.get('error') if not connected else None,
        'selected_days': days,
    }
    return render(request, 'dashboard/analytics.html', context)


# ──────────────────────────────────────────────
# Health Check
# ──────────────────────────────────────────────

def health_check(request):
    """Health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'dashboard-microservice',
        'version': '2.0.0',
        'main_api_url': API_URL,
    })
