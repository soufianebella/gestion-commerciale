#!/usr/bin/env python
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
        print("\nServeur arrêté par l'utilisateur.")
    except Exception as e:
        print(f"Erreur lors du démarrage du serveur : {e}")
        input("Appuyez sur Entrée pour fermer...")
    finally:
        print("Serveur arrêté.")

if __name__ == "__main__":
    main()
