from django.contrib import admin
# Importez tous vos modèles
from .models import Client, Article, Fournisseur, Vente, LigneVente, Commande 

# Enregistrez chaque modèle ici
admin.site.register(Client)
admin.site.register(Article)
admin.site.register(Fournisseur) # Si vous voulez gérer les fournisseurs aussi
admin.site.register(Vente)
admin.site.register(LigneVente)
admin.site.register(Commande)
