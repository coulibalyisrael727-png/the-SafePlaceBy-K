# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /build

# Installer les dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    postgresql-client-common \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copier requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Installer les runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client-common \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copier les dépendances Python du builder
COPY --from=builder /root/.local /root/.local

# Copier l'application
COPY . .

# Ajouter /root/.local/bin au PATH
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Créer des répertoires nécessaires
RUN mkdir -p /app/staticfiles /app/media

# Exposer le port
EXPOSE 8000

# Commande de démarrage
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "Safeplace.wsgi:application"]
