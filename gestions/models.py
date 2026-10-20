# gestion/models.py (ou invoices/models.py, selon le nom de votre application)

from django.db import models
from django.contrib.auth.models import User # Pour lier les ventes à un utilisateur
import datetime # Pour les dates par défaut

class Client(models.Model):
    """
    Représente un client de l'entreprise.
    Chaque client est unique et peut être associé à plusieurs ventes.
    """
    nom = models.CharField(max_length=255, verbose_name="Nom du client")
    adresse = models.TextField(blank=True, null=True, verbose_name="Adresse")
    telephone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Téléphone")

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ['nom'] # Trie les clients par ordre alphabétique du nom par défaut

    def __str__(self):
        return self.nom
    
    
    # Fournisseur

class Fournisseur(models.Model):
    nom = models.CharField(max_length=200, unique=True, verbose_name="Nom du Fournisseur")
    contact = models.CharField(max_length=100, blank=True, null=True, verbose_name="Contact (Téléphone/Email)")
    adresse = models.TextField(blank=True, null=True, verbose_name="Adresse")

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"    

class Article(models.Model):
    designation = models.CharField(max_length=200, verbose_name="Désignation du Produit")
    code_produit = models.CharField(max_length=50, unique=True, verbose_name="Code Produit ")
    stock_initial = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Stock Initial")
    stock_actuel = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Stock Actuel")
    prix_unitaire_defaut = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix Unitaire ")
    # Si vous avez un modèle Fournisseur, ce serait une ForeignKey
    fournisseur = models.CharField(max_length=200, null=True, blank=True, verbose_name="Fournisseur ")
    # ... ajoutez d'autres champs si nécessaire, ex: stock_actuel, description, etc.

    def __str__(self):
        return self.designation

    def get_absolute_url(self):
        # Utile pour rediriger après création/modification
        from django.urls import reverse
        return reverse('detail_article', kwargs={'pk': self.pk})

    def get_stock_status(self):
        """
        Retourne le statut du stock pour les alertes
        """
        if self.stock_actuel > 5:
            return "OK"
        else:
            return "Stock faible"

    def get_stock_status_class(self):
        """
        Retourne la classe CSS pour le statut du stock
        """
        if self.stock_actuel > 5:
            return "text-success"
        else:
            return "text-danger"

    def save(self, *args, **kwargs):
        """
        Surcharge la méthode save pour initialiser le stock_actuel si c'est une nouvelle instance
        """
        if not self.pk:  # Nouvelle instance
            self.stock_actuel = self.stock_initial
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"



class Vente(models.Model):
    """
    Représente une facture ou un bon de vente global.
    Une Vente est liée à un Client et peut contenir plusieurs Lignes de Vente.
    Son ID sera le numéro de facture.
    """
    client = models.ForeignKey(Client, on_delete=models.PROTECT, verbose_name="Client",blank=True, null=True)
    date_vente = models.DateField(default=datetime.date.today, verbose_name="Date de la Vente")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes / Commentaires")
    enregistre_par = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Enregistré par"
    )
    # Le prix total de la facture est calculé dynamiquement
    # On le stocke pour faciliter les requêtes et les affichages rapides,
    # mais il est redondant et doit être mis à jour après chaque modification des lignes.
    total_facture_ht = models.DecimalField(
        max_digits=10, decimal_places=0, default=0, verbose_name="Total Facture HT (FCFA)", editable=False
    )

    class Meta:
        verbose_name = "Vente / Facture"
        verbose_name_plural = "Ventes / Factures"
        # Trie les ventes par date la plus récente, puis par ID (numéro de facture)
        ordering = ['-date_vente', '-id']

    def __str__(self):
        # Formatage du numéro de facture sur 5 chiffres (ex: 00001)
        return f"Facture N°{self.id:05d} - {self.client.nom} ({self.date_vente.strftime('%d/%m/%Y')})"

    def calculer_total_facture(self):
        """
        Calcule le prix total de cette facture en additionnant les totaux de toutes ses lignes.
        """
        # Utilise .aggregate pour une somme efficace sur la base de données
        return self.lignes_vente.aggregate(total=models.Sum('prix_total_ligne'))['total'] or 0

    def save(self, *args, **kwargs):
        """
        Surcharge la méthode save pour s'assurer que le total de la facture est à jour.
        Cela est crucial pour que `total_facture_ht` reflète les modifications des lignes.
        """
        # Sauvegarde d'abord l'instance Vente (si nouvelle) pour obtenir son PK/ID.
        # Nécessaire avant de pouvoir interroger les LigneVente associées.
        super().save(*args, **kwargs)
        
        # Ensuite, on recalcule et met à jour le total basé sur les lignes existantes.
        # Utilise update_fields pour une sauvegarde partielle et éviter les boucles infinies.
        self.total_facture_ht = self.calculer_total_facture()
        super().save(update_fields=['total_facture_ht']) # Sauvegarde uniquement ce champ

class LigneVente(models.Model):
    """
    Représente une ligne d'article individuelle sur une Vente (Facture).
    Les détails de l'article sont enregistrés *au moment de la vente*
    pour des raisons historiques (si le prix ou la désignation de l'article change plus tard).
    """
    vente = models.ForeignKey(Vente, on_delete=models.CASCADE, verbose_name="Vente / Facture", related_name="lignes_vente")
    
    # Lien optionnel vers un Article du catalogue
    # Permet de pré-remplir les champs, mais n'est pas obligatoire
    article = models.ForeignKey(
        Article, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Article du catalogue"
    )
    
    # Informations de la ligne, enregistrées telles qu'elles apparaissent sur la facture
    designation_facturee = models.CharField(
        max_length=255, verbose_name="Désignation Facturée",
        help_text="Description exacte de l'article telle qu'elle apparaît sur la facture."
    )
    code_produit_facture = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Code Produit Facturé",
        help_text="Code produit sur la facture. Rempli automatiquement si un article du catalogue est choisi."
    )
    quantite = models.DecimalField( # Utilise DecimalField pour la flexibilité (ex: 1.5 kg)
        max_digits=10, decimal_places=2, default=1, verbose_name="Quantité"
    )
    prix_unitaire_facture = models.DecimalField(
        max_digits=10, decimal_places=0, verbose_name="Prix Unitaire Facturé (FCFA)",
        help_text="Prix unitaire de l'article sur cette facture."
    )
    
    # Calculé automatiquement au moment de la sauvegarde de la ligne
    prix_total_ligne = models.DecimalField(
        max_digits=10, decimal_places=0, default=0, verbose_name="Prix Total de la Ligne (FCFA)", editable=False
    )

    class Meta:
        verbose_name = "Ligne de Vente"
        verbose_name_plural = "Lignes de Vente"

    def __str__(self):
        return f"{self.quantite} x {self.designation_facturee} @ {self.prix_unitaire_facture} FCFA"

    def clean(self):
        """
        Validation personnalisée pour s'assurer qu'au moins une désignation ou un article est fourni.
        """
        from django.core.exceptions import ValidationError
        if not self.article and not self.designation_facturee:
            raise ValidationError(
                "Vous devez soit sélectionner un article du catalogue, soit entrer une désignation manuellement."
            )

    def save(self, *args, **kwargs):
        """
        Surcharge la méthode save pour pré-remplir les champs si un article du catalogue est choisi
        et pour calculer le prix total de la ligne.
        """
        # Si un article du catalogue est choisi, pré-remplir les champs si eux-mêmes sont vides
        if self.article:
            if not self.designation_facturee:
                self.designation_facturee = self.article.designation
            if not self.code_produit_facture:
                self.code_produit_facture = self.article.code_produit
                
            # Utilise le prix par défaut de l'article uniquement si aucun prix n'a été spécifié pour la ligne
            if not self.prix_unitaire_facture:
                self.prix_unitaire_facture = self.article.prix_unitaire_defaut
        
        # Calcul du prix total de la ligne avant la sauvegarde
        self.prix_total_ligne = self.quantite * self.prix_unitaire_facture
        
        # Vérifier si c'est une nouvelle ligne de vente (pas de PK) pour diminuer le stock
        is_new_line = not self.pk
        
        super().save(*args, **kwargs)
        
        # Diminuer le stock de l'article si c'est une nouvelle ligne de vente
        if is_new_line and self.article:
            # Diminuer le stock actuel de la quantité vendue
            self.article.stock_actuel -= self.quantite
            # S'assurer que le stock ne devient pas négatif
            if self.article.stock_actuel < 0:
                self.article.stock_actuel = 0
            self.article.save()
        
        # Après la sauvegarde de la LigneVente, déclenche la sauvegarde de la Vente parente
        # pour s'assurer que le total de la facture est mis à jour.
        # La condition self.vente est pour éviter des erreurs si la ligne n'est pas encore liée à une vente.
        if self.vente:
            self.vente.save() # Cela va déclencher le save() de Vente, qui recalcule total_facture_ht


class Commande(models.Model):
    """
    Représente une commande. Ce modèle est laissé tel quel si les commandes
    sont des entités distinctes des ventes et ne gèrent pas de multiples lignes
    comme les factures.
    Si une commande doit également avoir plusieurs lignes d'articles,
    vous devrez la refactoriser de la même manière que Vente et LigneVente,
    en créant un modèle 'LigneCommande' et en ajustant le modèle Commande.
    """
    client = models.CharField(max_length=100, blank=True, null=True, verbose_name="Client")
    reference = models.CharField(max_length=100, verbose_name="Référence Commande")
    code_produit = models.CharField(max_length=50, verbose_name="Code Produit")
    quantite = models.PositiveIntegerField(verbose_name="Quantité")
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix Unitaire")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Date de la Commande")

    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ['-date']

    def prix_total(self):
        """Calcule le prix total de cette commande (si elle n'a qu'une ligne)."""
        return self.quantite * self.prix_unitaire

    def __str__(self):
        return f"Commande {self.reference} - {self.client or '-'}"