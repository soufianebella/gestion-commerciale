"""
Script pour créer un exécutable à partir du script batch
Utilise PyInstaller pour créer un .exe autonome
"""

import os
import sys
import subprocess
import shutil

def create_launcher_script():
    """Crée un script Python qui lance Django"""
    launcher_content = '''#!/usr/bin/env python
"""
Launcher pour l'application Django CommerGestion
"""
import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def main():
    # Obtenir le répertoire du script
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    print("=== COMMERGESTION - SERVEUR DJANGO ===")
    print("Démarrage du serveur sur http://127.0.0.1:8002")
    print("Ouvrez votre navigateur et allez sur : http://127.0.0.1:8002")
    print("")
    print("Appuyez sur Ctrl+C pour arrêter le serveur")
    print("=========================================")
    print("")
    
    try:
        # Activer l'environnement virtuel
        venv_python = script_dir / "Venv" / "Scripts" / "python.exe"
        if venv_python.exists():
            print("Activation de l'environnement virtuel...")
            # Utiliser l'interpréteur Python de l'environnement virtuel
            python_cmd = str(venv_python)
        else:
            print("Environnement virtuel non trouvé. Utilisation de Python système...")
            python_cmd = sys.executable
        
        # Démarrer le serveur Django
        print("Démarrage du serveur Django...")
        subprocess.run([python_cmd, "manage.py", "runserver", "127.0.0.1:8002"])
        
    except KeyboardInterrupt:
        print("\\nServeur arrêté par l'utilisateur.")
    except Exception as e:
        print(f"Erreur lors du démarrage du serveur : {e}")
        input("Appuyez sur Entrée pour fermer...")
    finally:
        print("Serveur arrêté.")

if __name__ == "__main__":
    main()
'''
    
    with open("django_launcher.py", "w", encoding="utf-8") as f:
        f.write(launcher_content)
    
    print("Script launcher créé : django_launcher.py")

def install_pyinstaller():
    """Installe PyInstaller si nécessaire"""
    try:
        import PyInstaller
        print("PyInstaller déjà installé")
    except ImportError:
        print("Installation de PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])

def create_exe():
    """Crée l'exécutable avec PyInstaller"""
    print("Création de l'exécutable...")
    
    # Commande PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",  # Un seul fichier exécutable
        "--windowed",  # Pas de console (optionnel, enlever si vous voulez voir la console)
        "--name=CommerGestion",  # Nom de l'exécutable
        "--icon=favicon.ico",  # Icône (si disponible)
        "django_launcher.py"
    ]
    
    subprocess.run(cmd)
    print("Exécutable créé dans le dossier 'dist'")

def main():
    print("=== CRÉATION D'UN EXÉCUTABLE POUR COMMERGESTION ===")
    
    # Créer le script launcher
    create_launcher_script()
    
    # Installer PyInstaller
    install_pyinstaller()
    
    # Créer l'exécutable
    create_exe()
    
    print("\\n=== TERMINÉ ===")
    print("L'exécutable se trouve dans le dossier 'dist'")
    print("Vous pouvez le déplacer où vous voulez et l'exécuter directement.")

if __name__ == "__main__":
    main()
