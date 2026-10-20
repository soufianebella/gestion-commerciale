# Script PowerShell pour lancer Django
param(
    [string]$ServerHost = "127.0.0.1",
    [int]$Port = 8002
)

# Définir le titre de la fenêtre
$Host.UI.RawUI.WindowTitle = "Serveur Django - CommerGestion"

# Changer vers le répertoire du script
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ScriptPath

Write-Host "=== COMMERGESTION - SERVEUR DJANGO ===" -ForegroundColor Green
Write-Host "Démarrage du serveur sur http://$ServerHost`:$Port" -ForegroundColor Yellow
Write-Host "Ouvrez votre navigateur et allez sur : http://$ServerHost`:$Port" -ForegroundColor Cyan
Write-Host ""
Write-Host "Appuyez sur Ctrl+C pour arrêter le serveur" -ForegroundColor Red
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""

try {
    # Activer l'environnement virtuel
    if (Test-Path "Venv\Scripts\Activate.ps1") {
        Write-Host "Activation de l'environnement virtuel..." -ForegroundColor Yellow
        & "Venv\Scripts\Activate.ps1"
    } else {
        Write-Host "Environnement virtuel non trouvé. Vérifiez le chemin." -ForegroundColor Red
        Read-Host "Appuyez sur Entrée pour continuer"
        exit 1
    }

    # Démarrer le serveur Django
    Write-Host "Démarrage du serveur Django..." -ForegroundColor Green
    python manage.py runserver "$ServerHost`:$Port"
}
catch {
    Write-Host "Erreur lors du démarrage du serveur : $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Appuyez sur Entrée pour fermer"
}
finally {
    Write-Host "Serveur arrêté." -ForegroundColor Yellow
    Read-Host "Appuyez sur Entrée pour fermer cette fenêtre"
}
