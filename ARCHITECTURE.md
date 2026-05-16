# Architecture Profile: The SafePlace by K

This document provides a comprehensive technical overview of the platform's architecture, designed for consumption by an AI coding assistant.

## 1. Overview
**The SafePlace by K** is a Christian podcast and media platform. It has been refactored from a monolithic Django application into a **decoupled architecture** to allow independent hosting and scaling of the Creator Dashboard.

## 2. Decoupled Architecture
The system is split into two primary components:

### A. Backend Service (`podcastSafe`)
- **Role**: Core business logic, data persistence, and public-facing site.
- **Technology**: Django 6.0+, Django REST Framework (DRF).
- **Primary Responsibilities**:
    - Managing Podcasts, Episodes, Live Streams, and Categories.
    - User Authentication and Community Registration.
    - Payment Integrations (Stripe, Wave CI).
    - Providing REST APIs for the Dashboard.
- **Hosting**: Designed for containerized hosting (Render, Railway, Fly.io, or VPS via Docker).

### B. Dashboard Service (`dashboard-service`)
- **Role**: Admin/Creator Studio for managing content and viewing analytics.
- **Technology**: Independent Django project (currently) moving towards a Static/SPA model for Netlify.
- **Primary Responsibilities**:
    - Content publishing (Episodes, Videos).
    - Live stream management.
    - Donation tracking and Message management.
    - Analytics visualization.
- **Hosting**: **Netlify**. It uses a `netlify.toml` configuration to proxy API requests to the backend service.

## 3. Communication & Flux de Données
- **API REST** : Le Dashboard consomme les données via DRF (Django REST Framework).
- **Sécurité** : Authentification par clé API (`DASHBOARD_API_KEY`) et tokens de session.
- **CORS** : Le Backend autorise explicitement l'URL Netlify du Dashboard.
- **Redirection** : `https://site-principal.com/dashboard/` redirige l'utilisateur vers `https://dashboard.netlify.app`.

## 4. Configuration (Variables d'Environnement)

### Backend (`podcastSafe`)
| Variable | Description | Valeur par défaut |
|---|---|---|
| `DJANGO_SECRET_KEY` | Clé secrète Django | (Générée) |
| `POSTGRES_DB` | Nom de la base de données | `safeplace_db` |
| `DASHBOARD_NETLIFY_URL` | URL de production du dashboard | `https://...netlify.app` |
| `MAIN_API_URL` | Base URL de l'API (pour les liens) | `https://api.site.com/v1/` |

### Dashboard (`dashboard-service`)
| Variable | Description | Valeur par défaut |
|---|---|---|
| `MAIN_API_URL` | Point d'entrée de l'API Backend | `http://localhost:8000/api/v1/` |
| `DASHBOARD_API_KEY` | Clé de sécurité partagée | `safeplace_secret_...` |

## 5. Directory Structure (Root)
```text
.
├── Safeplace/              # Configuration globale du projet Django
├── podcastSafe/            # Application Backend principale (API + Core)
├── dashboard-service/      # Microservice Dashboard (Frontend)
│   ├── dashboard/          # Logique du dashboard (Vues, Templates)
│   ├── dashboard_project/  # Paramètres du microservice
│   └── netlify.toml        # Configuration du déploiement Netlify
├── docker-compose.yml      # Orchestration locale
└── ARCHITECTURE.md         # Ce document
```

## 6. Stratégie de Déploiement

### Backend
1. **GitHub** : Push sur la branche `main`.
2. **Hébergeur** (ex: Railway) : Détection du `Dockerfile` à la racine.
3. **Services** : Provisionnement automatique de PostgreSQL et Redis.

### Dashboard (Netlify)
1. **GitHub** : Dépôt séparé `dashboard-safeplace`.
2. **Netlify** : Connecté au dépôt.
3. **Redirects** : Utilisation du `netlify.toml` pour rediriger `/api/*` vers le Backend afin d'éviter les problèmes de CORS en développement/production.

---
*Generated for AI Handoff - 2026-05-15*
