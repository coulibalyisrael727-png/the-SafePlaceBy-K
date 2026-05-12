#!/usr/bin/env python
"""
Script de diagnostic pour le push GitHub
"""
import subprocess
import os
import sys

def run_command(cmd, description):
    """Exécuter une commande et retourner le résultat"""
    print(f"\n🔍 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd="c:\\Users\\couli\\Desktop\\Nouveau dossier (3)")
        print(f"✅ Commande: {cmd}")
        print(f"📤 Sortie: {result.stdout.strip()}")
        if result.stderr:
            print(f"❌ Erreur: {result.stderr.strip()}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def main():
    """Diagnostic complet du problème GitHub"""
    print("🚀 Diagnostic du push GitHub - Projet SafePlace")
    print("=" * 50)
    
    # Vérifier l'état Git
    run_command("git status", "Vérification du statut Git")
    
    # Vérifier les remotes
    run_command("git remote -v", "Vérification des remotes")
    
    # Vérifier la configuration du remote
    run_command("git config --get remote.origin.url", "URL du remote origin")
    
    # Vérifier les branches
    run_command("git branch -a", "Vérification des branches")
    
    # Vérifier le dernier commit
    run_command("git log --oneline -1", "Dernier commit")
    
    print("\n" + "=" * 50)
    print("📋 Instructions manuelles si le push échoue:")
    print("1. Vérifiez que le dépôt existe: https://github.com/coulibr/Projet-SafePlaceBy-K")
    print("2. Si le dépôt n'existe pas, créez-le manuellement")
    print("3. Si le dépôt existe, vérifiez les permissions")
    print("4. Essayez avec HTTPS: git push https://github.com/coulibr/Projet-SafePlaceBy-K.git main")
    
    print("\n🔧 Commandes alternatives:")
    print("git push -f origin main  # Force push")
    print("git push origin main --set-upstream  # Upstream explicite")
    
    # Test de connexion simple
    print("\n🌐 Test de connexion à GitHub...")
    try:
        import urllib.request
        response = urllib.request.urlopen("https://github.com/coulibr/Projet-SafePlaceBy-K")
        if response.getcode() == 200:
            print("✅ Dépôt accessible via HTTP")
        else:
            print(f"❌ Code HTTP: {response.getcode()}")
    except Exception as e:
        print(f"❌ Erreur de connexion: {str(e)}")
        print("💡 Le dépôt n'existe probablement pas encore")

if __name__ == "__main__":
    main()
