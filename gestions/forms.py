# forms.py

from django import forms
from .models import Client, Article, Vente, LigneVente, Commande

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['nom', 'adresse', 'telephone']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['designation', 'code_produit', 'prix_unitaire_defaut', 'stock_initial', 'fournisseur']
        widgets = {
            'designation': forms.TextInput(attrs={'class': 'form-control'}),
            'code_produit': forms.TextInput(attrs={'class': 'form-control'}),
            'prix_unitaire_defaut': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock_initial': forms.NumberInput(attrs={'class': 'form-control'}),
            'fournisseur': forms.TextInput(attrs={'class': 'form-control'}),
        }

class VenteForm(forms.ModelForm):
    class Meta:
        model = Vente
        fields = ['client', 'date_vente', 'notes']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-control select2'}),
            'date_vente': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class LigneVenteForm(forms.ModelForm):
    # Ces champs sont déclarés ici avec les NOMS EXACTS des champs de votre modèle LigneVente.
    # C'est crucial pour que Django sache où stocker les données.
    code_produit_facture = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'readonly': 'readonly'
    }))
    designation_facturee = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'readonly': 'readonly'
    }))
    # Le prix unitaire dans votre modèle a 0 décimales (`decimal_places=0`),
    # donc `step: '1'` est plus cohérent ici.
    prix_unitaire_facture = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'readonly': 'readonly',
        'step': '1' # Ajusté pour correspondre à decimal_places=0 dans le modèle
    }))

    class Meta:
        model = LigneVente
        # Les 'fields' doivent utiliser les NOMS EXACTS des champs du modèle, y compris les suffixes "_facture".
        fields = ['article', 'code_produit_facture', 'designation_facturee', 'quantite', 'prix_unitaire_facture']
        widgets = {
            'article': forms.Select(attrs={
                'class': 'form-control select-article',
                'data-placeholder': 'Sélectionnez un article'
            }),
            'quantite': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1', # Assurez-vous que la quantité minimale est 1 si c'est une ligne valide.
                'step': '1'
            }),
            # Pas besoin de répéter les widgets pour _facture ici, car ils sont déclarés au-dessus.
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Assurez-vous que le champ 'article' a une option vide
        self.fields['article'].empty_label = "Sélectionnez un article"
        
        # Initialisation des champs du formulaire avec les valeurs de l'instance si elle existe.
        if self.instance and self.instance.pk:
            # L'initialisation se fait avec les valeurs réelles de l'instance de modèle
            # vers les champs du formulaire qui ont les MÊMES NOMS.
            self.fields['code_produit_facture'].initial = self.instance.code_produit_facture
            self.fields['designation_facturee'].initial = self.instance.designation_facturee
            self.fields['prix_unitaire_facture'].initial = self.instance.prix_unitaire_facture
        else:
            # Pour les nouvelles lignes, assurez-vous que les champs en lecture seule sont vides
            self.fields['code_produit_facture'].initial = ''
            self.fields['designation_facturee'].initial = ''
            self.fields['prix_unitaire_facture'].initial = ''

    def clean(self):
        cleaned_data = super().clean()
        article = cleaned_data.get('article')
        quantite = cleaned_data.get('quantite')
        designation = cleaned_data.get('designation_facturee')

        if not article and not designation:
            raise forms.ValidationError(
                "Vous devez soit sélectionner un article du catalogue, soit entrer une désignation manuellement."
            )

        # Vérification du stock
        if article:
            if article.stock_actuel <= 0:
                raise forms.ValidationError(f"Stock épuisé pour l'article '{article.designation}' ! Impossible de vendre.")
            if quantite and quantite > article.stock_actuel:
                raise forms.ValidationError(f"Stock insuffisant pour l'article '{article.designation}' (stock actuel : {article.stock_actuel}) !")

        # Conversion du prix unitaire si besoin (déjà présent)
        prix_unitaire = cleaned_data.get('prix_unitaire_facture')
        if prix_unitaire:
            try:
                cleaned_data['prix_unitaire_facture'] = int(float(prix_unitaire))
            except Exception:
                raise forms.ValidationError("Le prix unitaire doit être un nombre entier.")
        return cleaned_data

    def save(self, commit=True):
        """
        Surcharge la méthode save pour pré-remplir les champs si un article du catalogue est choisi
        et pour calculer le prix total de la ligne.
        """
        instance = super().save(commit=False)
        
        # Si un article du catalogue est choisi, pré-remplir les champs si eux-mêmes sont vides
        if instance.article:
            if not instance.designation_facturee:
                instance.designation_facturee = instance.article.designation
            if not instance.code_produit_facture:
                instance.code_produit_facture = instance.article.code_produit
                
            # Utilise le prix par défaut de l'article uniquement si aucun prix n'a été spécifié pour la ligne
            if not instance.prix_unitaire_facture:
                instance.prix_unitaire_facture = instance.article.prix_unitaire_defaut
        
        if commit:
            instance.save()
        
        return instance

class CommandeForm(forms.ModelForm):
    class Meta:
        model = Commande
        fields = ['client', 'reference', 'quantite', 'prix_unitaire']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-control'}),
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control'}),
            'prix_unitaire': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
        }