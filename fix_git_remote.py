#!/usr/bin/env python
"""
Script pour corriger la configuration du remote Git
"""
import subprocess
import os

def run_git_command(cmd_args):
    """Exécuter une commande Git de manière sécurisée et retourner le résultat"""
    try:
        # Utiliser une liste au lieu de shell=True pour éviter l'injection
        result = subprocess.run(
            cmd_args, 
            capture_output=True, 
            text=True, 
            cwd="c:\\Users\\couli\\Desktop\\Nouveau dossier (3)",
            timeout=30  # Timeout pour éviter les blocages
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "Command timeout", 1
    except Exception as e:
        return "", str(e), 1

def main():
    """Corriger la configuration du remote Git"""
    print("🔧 Correction de la configuration Git pour le dépôt SafePlace")
    
    # Étape 1: Supprimer toutes les configurations de remote
    print("\n1️⃣ Suppression des anciennes configurations...")
    stdout, stderr, code = run_git_command(["git", "config", "--remove-section", "remote"])
    if code == 0:
        print("✅ Anciennes configurations supprimées")
    else:
        print(f"⚠️ Erreur suppression: {stderr}")
    
    # Étape 2: Ajouter le nouveau remote correct
    print("\n2️⃣ Ajout du nouveau remote...")
    stdout, stderr, code = run_git_command(["git", "remote", "add", "origin", "https://github.com/kingBen-j/SafePlaceBy-k.git"])
    if code == 0:
        print("✅ Remote ajouté correctement")
    else:
        print(f"❌ Erreur ajout remote: {stderr}")
        return
    
    # Étape 3: Vérifier la configuration
    print("\n3️⃣ Vérification de la configuration...")
    stdout, stderr, code = run_git_command(["git", "remote", "-v"])
    if code == 0:
        print("✅ Configuration actuelle:")
        print(stdout)
    else:
        print(f"❌ Erreur vérification: {stderr}")
        return
    
    # Étape 4: Tenter le push
    print("\n4️⃣ Tentative de push...")
    stdout, stderr, code = run_git_command(["git", "push", "-u", "origin", "main"])
    if code == 0:
        print("🎉 Push réussi!")
        print("✅ Votre projet est maintenant sur GitHub!")
        print("📍 URL: https://github.com/kingBen-j/SafePlaceBy-k")
    else:
        print(f"❌ Erreur de push: {stderr}")
        print("\n💡 Solutions possibles:")
        print("1. Vérifiez que le dépôt existe: https://github.com/kingBen-j/SafePlaceBy-k")
        print("2. Si le dépôt n'existe pas, créez-le manuellement")
        print("3. Vérifiez vos permissions GitHub")
        print("4. Essayez avec un token d'accès si nécessaire")

if __name__ == "__main__":
    main()
