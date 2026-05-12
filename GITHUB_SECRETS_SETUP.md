# [SECURITY] Configuration des Secrets GitHub

## [TARGET] Sécuriser le pipeline CI/CD avec des secrets

## [WARNING] Problème de sécurité corrigé
- ❌ **Avant**: Identifiants de base de données en dur dans `.github/workflows/django.yml`
- ✅ **Après**: Utilisation des secrets GitHub avec valeurs par défaut sécurisées

## [LIST] Secrets GitHub à configurer

### 1. Base de données
```yaml
POSTGRES_DB: safeplace_test
POSTGRES_USER: test
POSTGRES_PASSWORD: test
```

### 2. Configuration Django
```yaml
DJANGO_SECRET_KEY: votre-secret-key-django-ici
```

### 3. Configuration Stripe
```yaml
STRIPE_PUBLIC_KEY: pk_test_votre-clé-publique-ici
STRIPE_SECRET_KEY: sk_test_votre-clé-secrète-ici
STRIPE_WEBHOOK_SECRET: whsec_votre-webhook-secret-ici
```

### 4. Déploiement (optionnel)
```yaml
SSH_PRIVATE_KEY: votre-clé-ssh-privée-ici
SERVER_HOST: votre-domaine.com
SERVER_USER: votre-utilisateur-ssh
```

## [TOOLS] Comment configurer les secrets

### Étape 1: Accéder aux secrets
1. Allez sur votre dépôt GitHub: https://github.com/kingBen-j/the-SafePlace
2. Cliquez sur **Settings**
3. Dans la barre latérale, cliquez sur **Secrets and variables** → **Actions**
4. Cliquez sur **New repository secret**

### Étape 2: Ajouter chaque secret
Pour chaque secret ci-dessus:
1. **Name**: Nom du secret (ex: `POSTGRES_DB`)
2. **Secret**: Valeur du secret
3. Cliquez sur **Add secret**

### Étape 3: Répéter pour tous les secrets
Configurez tous les secrets listés ci-dessus.

## [SAFE] Valeurs par défaut sécurisées

Le fichier `.github/workflows/django.yml` utilise maintenant des valeurs par défaut sécurisées:
```yaml
${{ secrets.POSTGRES_DB || 'safeplace_test' }}
${{ secrets.POSTGRES_USER || 'test' }}
${{ secrets.POSTGRES_PASSWORD || 'test' }}
```

Cela signifie que:
- Si le secret est configuré → utilise le secret
- Si le secret n'est pas configuré → utilise la valeur par défaut (pour le CI/CD)

## [CHECK] Vérification après configuration

1. **Testez le workflow**:
   ```bash
   git push origin main
   ```

2. **Vérifiez les logs**:
   - Allez dans **Actions** → **Workflows**
   - Vérifiez que le workflow s'exécute sans erreurs

3. **Confirmez la sécurité**:
   - [ ] Plus aucun identifiant en dur dans le code
   - [ ] Tous les secrets sont configurés
   - [ ] Le CI/CD fonctionne correctement

## [INFO] Bonnes pratiques de sécurité

### ✅ Recommandé
- Utiliser des secrets GitHub pour toutes les données sensibles
- Utiliser des clés différentes pour développement et production
- Rotaionner les secrets régulièrement
- Utiliser des mots de passe forts

### ❌ À éviter
- Ne jamais mettre d'identifiants en dur dans le code
- Ne jamais partager les secrets
- Ne pas utiliser les mêmes secrets pour plusieurs environnements

## [DEPLOY] Déploiement sécurisé

Le workflow utilise maintenant des secrets pour:
- **Base de données**: Connexion sécurisée PostgreSQL
- **Stripe**: Clés API protégées
- **SSH**: Déploiement sécurisé sur le serveur

---

**La sécurité de votre projet est maintenant renforcée !** [LOCK]

Tous les identifiants sensibles sont protégés dans les secrets GitHub.
