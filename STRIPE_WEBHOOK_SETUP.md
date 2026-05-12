# [CARD] Configuration du Webhook Stripe - The SafePlace by K

## [TARGET] Objectif
Configurer le webhook Stripe pour gérer automatiquement les paiements et les notifications.

## [LIST] Prérequis
- Compte Stripe (test ou production)
- Accès au dashboard Stripe
- URL publique de votre application

## [TOOLS] Étapes de Configuration

### 1. Créer le Webhook dans Stripe Dashboard

1. Connectez-vous à votre [Dashboard Stripe](https://dashboard.stripe.com/webhooks)
2. Cliquez sur "Ajouter un endpoint"
3. Configurez les paramètres:
   ```
   URL de l'endpoint: https://votre-domaine.com/api/stripe/webhook/
   Méthode HTTP: POST
   Version API: 2024-06-20 (ou plus récente)
   ```

### 2. Sélectionner les Événements

Cochez les événements suivants:
```
✅ payment_intent.succeeded     - Paiement réussi
✅ payment_intent.payment_failed - Paiement échoué
✅ payment_intent.canceled     - Paiement annulé
✅ invoice.payment_succeeded  - Facture payée (pour abonnements)
```

### 3. Obtenir la Clé Secrète du Webhook

1. Une fois le webhook créé, Stripe affichera une "clé secrète de signage"
2. Copiez cette clé (commence par `whsec_`)
3. Ajoutez-la à votre fichier `.env`:
   ```bash
   STRIPE_WEBHOOK_SECRET=whsec_votre_clé_secrète_ici
   ```

### 4. Configurer l'URL dans Django

Assurez-vous que l'URL est accessible:
```python
# podcastSafe/urls.py
path('api/stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),
```

## [SAFE] Sécurité

### Validation des Signatures
Le webhook valide automatiquement les signatures Stripe pour s'assurer que:
- Les requêtes viennent bien de Stripe
- Les données n'ont pas été modifiées
- Les attaques par rejeu sont évitées

### HTTPS Requis
- En production: HTTPS obligatoire
- En test: HTTP acceptable (avec ngrok ou tunnel similaire)

## [TEST] Tests Locaux

### Avec ngrok (recommandé)
```bash
# Installer ngrok
npm install -g ngrok

# Démarrer ngrok sur le port 8000
ngrok http 8000

# Copier l'URL HTTPS fournie
# Ex: https://abc123.ngrok.io
```

### Mettre à jour le webhook Stripe
1. Allez dans le dashboard Stripe
2. Modifiez votre webhook
3. Remplacez l'URL par: `https://votre-url-ngrok.io/api/stripe/webhook/`

### Tester le webhook
```bash
# Lancer le script de test
python test_stripe_payment.py

# Créer un paiement de test dans le dashboard Stripe
# Vérifier les logs de votre application
```

## [CHART] Monitoring

### Logs du Webhook
Le webhook logge automatiquement:
```python
# Succès
return JsonResponse({'status': 'success'}, status=200)

# Erreurs
return JsonResponse({'error': str(e)}, status=500)
```

### Événements Traités
- `payment_intent.succeeded`: Met la donation à 'completed'
- `payment_intent.payment_failed`: Met la donation à 'failed'

## [WARNING] Dépannage

### Erreur "Invalid signature"
```bash
# Vérifiez que STRIPE_WEBHOOK_SECRET est correct
echo $STRIPE_WEBHOOK_SECRET

# Doit commencer par whsec_
```

### Erreur "Invalid payload"
```bash
# Vérifiez que le webhook reçoit bien les données POST
# Test avec curl:
curl -X POST https://votre-domaine.com/api/stripe/webhook/ \
  -H "Content-Type: application/json" \
  -d '{"test": true}'
```

### Webhook non appelé
```bash
# Vérifiez l'URL dans le dashboard Stripe
# Testez l'accessibilité:
curl -I https://votre-domaine.com/api/stripe/webhook/

# Doit retourner 200 OK
```

## [RELOAD] Mise en Production

1. **Basculer en mode Live**:
   ```bash
   # Dans .env
   STRIPE_PUBLIC_KEY=pk_live_votre_clé_publique
   STRIPE_SECRET_KEY=sk_live_votre_clé_secrète
   ```

2. **Mettre à jour le webhook**:
   - Changer l'URL ngrok par votre domaine de production
   - Recréer le webhook si nécessaire
   - Mettre à jour la clé secrète

3. **Tester**:
   ```bash
   # Faire un don de test avec une vraie carte
   # Vérifier que le donation est bien marquée 'completed'
   ```

## [PHONE] Support

### Documentation Stripe
- [Webhooks Guide](https://stripe.com/docs/webhooks)
- [Payment Intents](https://stripe.com/docs/payments/payment-intents)
- [Testing](https://stripe.com/docs/testing)

### Événements Utiles
```json
{
  "type": "payment_intent.succeeded",
  "data": {
    "object": {
      "id": "pi_1234567890",
      "status": "succeeded",
      "amount": 1000,
      "currency": "eur",
      "metadata": {
        "donation_id": "123"
      }
    }
  }
}
```

---

**Le webhook est maintenant configuré!** [PARTY]

Les paiements seront traités automatiquement et les donations mises à jour en temps réel.
