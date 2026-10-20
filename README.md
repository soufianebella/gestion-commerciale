# Gestion Commerciale — CommerGestion

Application web Django de gestion commerciale (clients, articles, stock, ventes / factures, commandes) avec génération de factures PDF, interface Bootstrap 5 + Crispy Forms.

> Projet développé pour **E.K.K.C.F** — Ouagadougou, Burkina Faso.

## Fonctionnalités

- **Tableau de bord** : aperçu des ventes, dernière vente
- **Clients** : CRUD complet (créer, lister, détail, modifier, supprimer)
- **Fournisseurs** : gestion des fournisseurs
- **Articles / Catalogue** : CRUD, codes produits uniques, prix par défaut, stock initial / actuel, alertes stock faible
- **Stock** : suivi, modification, alertes
- **Ventes / Factures** : création avec lignes multiples (formset), calcul auto des totaux, décrément du stock, détail, modification, suppression, **export PDF**
- **Commandes** : création et suivi
- **Authentification** : connexion / déconnexion (vues Django `LoginView` / `LogoutView`)
- **Interface FR** : `LANGUAGE_CODE = fr-fr`, fuseau `Africa/Ouagadougou`, Bootstrap 5

## Stack technique

- Python 3.x + Django 5.2.4
- SQLite (dev) via `db.sqlite3`
- `django-crispy-forms` + `crispy-bootstrap5`
- `xhtml2pdf` pour les factures PDF
- `pytz`, `sqlparse`, `asgiref`, `tzdata`
- Lancement local sur `http://127.0.0.1:8002`

## Structure du projet

```
commergestion-code/
├── kiemde/              # Config Django (settings, urls, wsgi)
│   ├── settings.py
│   └── urls.py
├── gestions/            # App métier : models, views, forms, urls
│   ├── models.py        # Client, Fournisseur, Article, Vente, LigneVente, Commande
│   ├── views.py
│   ├── forms.py
│   └── urls.py
├── templates/           # Templates HTML (base, listes, formulaires, facture PDF)
├── static/              # CSS / JS / images
├── manage.py
├── django_launcher.py   # Lanceur Python (serveur :8002)
├── launch_django.ps1    # Lanceur PowerShell
├── script.bat           # Lanceur batch Windows
├── create_exe.py        # Build .exe via PyInstaller
├── requirements.txt
└── db.sqlite3           # Base dev (non versionnée, voir .gitignore)
```

## Installation en local

```powershell
# 1. Cloner
git clone https://github.com/soufianebella/gestion-commerciale.git
cd gestion-commerciale

# 2. Créer et activer un venv
python -m venv Venv
.\Venv\Scripts\Activate.ps1

# 3. Installer les dépendances
pip install -r requirements.txt
# Si requirements.txt est vide, au minimum :
# pip install Django==5.2.4 django-crispy-forms crispy-bootstrap5 xhtml2pdf pytz

# 4. Migrations
python manage.py migrate

# 5. Créer un admin
python manage.py createsuperuser

# 6. Lancer
python manage.py runserver 127.0.0.1:8002
# ou
.\launch_django.ps1
# ou
python django_launcher.py
```

Ouvre ensuite http://127.0.0.1:8002
- Admin : http://127.0.0.1:8002/admin/

## Variables / config à adapter

Dans `kiemde/settings.py` :
- `SECRET_KEY` : **à changer en prod** (utiliser variable d'env)
- `DEBUG = True` : passer à `False` en prod
- `ALLOWED_HOSTS` : à remplir en prod
- `COMPANY_INFO` : nom, adresse, téléphone, email, RCCM / IFU

Ne commite jamais `db.sqlite3`, `.env`, ni les `.exe`.

## Build Windows (.exe)

```powershell
python create_exe.py
# L'exécutable sort dans dist/
```

Nécessite `pyinstaller` + `favicon.ico` si tu veux l'icône.

## Dépôt GitHub

```powershell
git init
git add .
git commit -m "Initial commit - gestion-commerciale"
git branch -M main
git remote add origin https://github.com/soufianebella/gestion-commerciale.git
git push -u origin main
```

## Auteur

**soufianebella** — https://github.com/soufianebella
