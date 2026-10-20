from django.urls import path
from . import views

urlpatterns = [
    # --- Vues d'Accueil et Authentification ---
    path('', views.accueil, name='accueil'), # Renommé de 'index'
    path('tableau-de-bord/', views.tableau_de_bord_gestion, name='tableau_de_bord_gestion'), # Renommé de 'gestion'
    path('a-propos/', views.apropos, name='apropos'), # Reste le même

    # --- Vues pour les Ventes (Factures) ---
    path('ventes/', views.ListeVentes.as_view(), name='liste_ventes'), # Affiche la liste des factures
    path('ventes/creer/', views.creer_ou_modifier_vente, name='creer_vente'), # Formulaire de création de facture
    path('ventes/<int:pk>/', views.DetailVente.as_view(), name='detail_vente'), # Détails d'une facture spécifique
    path('ventes/<int:pk>/modifier/', views.creer_ou_modifier_vente, name='modifier_vente'), # Formulaire de modification
    path('ventes/<int:pk>/supprimer/', views.SupprimerVente.as_view(), name='supprimer_vente'), # Confirmation de suppression
    path('ventes/<int:pk>/pdf/', views.generer_facture_pdf, name='generer_facture_pdf'), # Génération de PDF
    
    # --- Vues pour les Clients ---
    path('clients/', views.ListeClients.as_view(), name='liste_clients'),
    path('clients/creer/', views.CreerClient.as_view(), name='creer_client'),
    path('clients/<int:pk>/', views.DetailClient.as_view(), name='detail_client'),
    path('clients/<int:pk>/modifier/', views.ModifierClient.as_view(), name='modifier_client'),
    path('clients/<int:pk>/supprimer/', views.SupprimerClient.as_view(), name='supprimer_client'),

    # --- Vues pour les Articles du Catalogue ---
    path('articles/', views.ListeArticles.as_view(), name='liste_articles'),
    path('articles/creer/', views.CreerArticle.as_view(), name='creer_article'),
    path('articles/<int:pk>/', views.DetailArticle.as_view(), name='detail_article'),
    path('articles/<int:pk>/modifier/', views.ModifierArticle.as_view(), name='modifier_article'),
    path('articles/<int:pk>/supprimer/', views.SupprimerArticle.as_view(), name='supprimer_article'),
    path('articles/<int:pk>/json/', views.detail_article_json, name='detail_article_json'), # Endpoint pour AJAX

    # --- Vues pour les Commandes (si distinctes des Ventes) ---
    path('commandes/', views.ListeCommandes.as_view(), name='liste_commandes'),
    path('commandes/creer/', views.creer_ou_modifier_commande, name='creer_commande'),
    # Ajoutez d'autres vues de commande si nécessaire (détail, modifier, supprimer)
    # path('commandes/<int:pk>/', views.DetailCommande.as_view(), name='detail_commande'),
    # path('commandes/<int:pk>/modifier/', views.ModifierCommande.as_view(), name='modifier_commande'),
    # path('commandes/<int:pk>/supprimer/', views.SupprimerCommande.as_view(), name='supprimer_commande'),

    # URLs pour la gestion du stock
    path('stock/', views.gestion_stock, name='gestion_stock'),
    path('stock/alertes/', views.alertes_stock, name='alertes_stock'),
    path('stock/<int:pk>/modifier/', views.modifier_stock, name='modifier_stock'),
]