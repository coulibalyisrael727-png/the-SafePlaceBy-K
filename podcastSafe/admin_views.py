from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse


@login_required
def dashboard_admin(request):
    # Page tableau de contrôle (prototype minimal)
    # La vraie logique pourra être branchée sur les modèles Episode/LiveStream.
    return render(request, 'dashboard_admin.html')

