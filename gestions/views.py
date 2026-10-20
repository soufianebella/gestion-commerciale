# views.py

from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.forms import inlineformset_factory
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.conf import settings
from .models import Article

# Pour la génération de PDF
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
import xhtml2pdf.pisa as pisa
import os

# Importez vos modèles et formulaires refactorisés
from .models import Client, Article, Vente, LigneVente, Commande
from .forms import ClientForm, ArticleForm, VenteForm, LigneVenteForm, CommandeForm

@login_required(login_url='vue_connexion')
def accueil(request):
    return render(request, 'index.html')

@login_required(login_url='vue_connexion')
def tableau_de_bord_gestion(request):
    """
    Vue du tableau de bord de gestion, offrant un aperçu rapide.
    """
    total_ventes = Vente.objects.count()
    derniere_vente = Vente.objects.order_by('-date_vente').first()
    context = {
        'total_ventes': total_ventes,
        'derniere_vente': derniere_vente,
    }
    return render(request, 'gestion.html', context)

def apropos(request):
    """
    Affiche la page "À propos" de l'application.
    """
    return render(request, 'apropos.html')

def article_json(request, pk):
    article = get_object_or_404(Article, pk=pk)
    data = {
        'id': article.id,
        'designation': article.designation,
        'code_produit': article.code_produit,
        'prix_unitaire_defaut': float(article.prix_unitaire_defaut),
    }
    return JsonResponse(data)

class ListeVentes(LoginRequiredMixin, ListView):
    model = Vente
    template_name = 'liste_ventes.html'
    context_object_name = 'ventes'
    ordering = ['-date_vente', '-id']
    login_url = 'vue_connexion'

class DetailVente(LoginRequiredMixin, DetailView):
    model = Vente
    template_name = 'detail_vente.html'
    context_object_name = 'vente'
    login_url = 'vue_connexion'

# --- Vue pour créer ou modifier une Vente (facture) ---

@login_required(login_url='vue_connexion')
def creer_ou_modifier_vente(request, pk=None):
    """
    Gère la création et la modification d'une vente (facture) et de ses lignes.
    """
    instance_vente = get_object_or_404(Vente, pk=pk) if pk else None
    
    # Le related_name 'lignes_de_vente' est utilisé ici, tel que défini dans models.py
    FormsetLigneVente = inlineformset_factory(
        Vente,
        LigneVente,
        form=LigneVenteForm,
        extra=1,
        can_delete=True,
        # Pas besoin de spécifier les 'fields' ici si ils sont tous dans LigneVenteForm.Meta.fields
    )

    if request.method == 'POST':
        form_vente = VenteForm(request.POST, instance=instance_vente)
        formset_lignes = FormsetLigneVente(
            request.POST,
            request.FILES, # Toujours inclure request.FILES si vos formulaires peuvent gérer des fichiers (même si ce n'est pas le cas ici)
            instance=instance_vente,
            prefix='lignes'
        )

        if form_vente.is_valid() and formset_lignes.is_valid():
            vente = form_vente.save(commit=False)
            if not vente.pk:
                vente.enregistre_par = request.user
            vente.save() # Sauvegarde la vente principale pour obtenir son PK

            # IMPORTANT : La méthode .save() du formset gère tout :
            # - Création de nouvelles instances (avec `vente` comme ForeignKey)
            # - Mise à jour des instances existantes
            # - Suppression des instances cochées pour suppression
            # Puisque LigneVente.save() gère déjà le calcul du prix total de la ligne
            # et le déclenchement de Vente.save() pour le total de la facture,
            # et que LigneVenteForm transmet maintenant les données correctement,
            # un simple appel à formset_lignes.save() suffit.
            formset_lignes.instance = vente # Assure que le formset est lié à l'instance vente
            formset_lignes.save() # Enregistre toutes les lignes et gère les suppressions

            messages.success(request, f"Facture N°{vente.id:05d} sauvegardée")
            return redirect('detail_vente', pk=vente.pk)
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
            # Pour le débogage, afficher les erreurs dans les logs
            print("Erreurs Formulaire Vente:", form_vente.errors)
            print("Erreurs Formset Lignes:", formset_lignes.errors)
            if formset_lignes.non_form_errors():
                print("Erreurs non-form:", formset_lignes.non_form_errors())
            for i, form in enumerate(formset_lignes.forms):
                if form.errors:
                    print(f"Erreurs ligne {i}:", form.errors)
    else:
        form_vente = VenteForm(instance=instance_vente)
        formset_lignes = FormsetLigneVente(
            instance=instance_vente,
            prefix='lignes'
        )

    context = {
        'form_vente': form_vente,
        'formset_lignes': formset_lignes,
        'vente': instance_vente,
        'action': 'Modifier' if pk else 'Créer',
    }
    return render(request, 'formulaire_vente.html', context)


class SupprimerVente(LoginRequiredMixin, DeleteView):
    model = Vente
    template_name = 'confirmer_suppression_vente.html'
    success_url = reverse_lazy('liste_ventes')
    login_url = 'vue_connexion'

    def form_valid(self, form):
        messages.success(self.request, f"La facture N°{self.object.id:05d} a été supprimée.")
        return super().form_valid(form)


# --- Vues pour les Commandes ---

class ListeCommandes(LoginRequiredMixin, ListView):
    model = Commande
    template_name = 'liste_commandes.html'
    context_object_name = 'commandes'
    ordering = ['-date']
    login_url = 'vue_connexion'

@login_required(login_url='vue_connexion')
def creer_ou_modifier_commande(request, pk=None):
    instance_commande = None
    if pk:
        instance_commande = get_object_or_404(Commande, pk=pk)

    form_commande = CommandeForm(request.POST or None, instance=instance_commande)
    if request.method == 'POST' and form_commande.is_valid():
        form_commande.save()
        messages.success(request, "La commande a été sauvegardée avec succès.")
        return redirect('liste_commandes')

    context = {
        'form_commande': form_commande,
        'commande': instance_commande,
        'action': 'Modifier' if pk else 'Créer',
    }
    return render(request, 'formulaire_commande.html', context)

class SupprimerCommande(LoginRequiredMixin, DeleteView):
    model = Commande
    template_name = 'confirmer_suppression_commande.html'
    success_url = reverse_lazy('liste_commandes')
    login_url = 'vue_connexion'

    def form_valid(self, form):
        messages.success(self.request, "La commande a été supprimée avec succès.")
        return super().form_valid(form)


# --- Vue pour la génération de Facture PDF ---

@login_required(login_url='vue_connexion')
def generer_facture_pdf(request, pk):
    """
    Génère le document PDF d'une facture (Vente) spécifique.
    """
    vente = get_object_or_404(Vente, pk=pk)

    context = {
        'vente': vente,
        'entreprise': settings.COMPANY_INFO,
    }

    template = get_template('gestions/facture_pdf_template.html')
    html = template.render(context)

    reponse = HttpResponse(content_type='application/pdf')
    reponse['Content-Disposition'] = f'inline; filename="facture_{vente.id:05d}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=reponse)

    if pisa_status.err:
        messages.error(request, "Une erreur est survenue lors de la génération du PDF.")
        return HttpResponse("Une erreur est survenue lors de la génération du PDF. <pre>" + html + "</pre>")
    return reponse

# --- Vues pour les Clients ---

class ListeClients(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'liste_clients.html'
    context_object_name = 'clients'
    ordering = ['nom']
    login_url = 'vue_connexion'

class DetailClient(LoginRequiredMixin, DetailView):
    model = Client
    template_name = 'detail_client.html'
    context_object_name = 'client'
    login_url = 'vue_connexion'

class CreerClient(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'formulaire_client.html'
    success_url = reverse_lazy('liste_clients')
    login_url = 'vue_connexion'

    def form_valid(self, form):
        messages.success(self.request, "Client ajouté avec succès.")
        return super().form_valid(form)

class ModifierClient(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'formulaire_client.html'
    success_url = reverse_lazy('liste_clients')
    login_url = 'vue_connexion'

    def form_valid(self, form):
        messages.success(self.request, "Client mis à jour avec succès.")
        return super().form_valid(form)

class SupprimerClient(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = 'confirmer_suppression_client.html'
    success_url = reverse_lazy('liste_clients')
    login_url = 'vue_connexion'

    def form_valid(self, form):
        messages.success(self.request, "Client supprimé avec succès.")
        return super().form_valid(form)

# --- Vues pour les Articles du Catalogue ---

class ListeArticles(LoginRequiredMixin, ListView):
    model = Article
    template_name = 'liste_articles.html'
    context_object_name = 'articles'
    ordering = ['designation']
    login_url = 'vue_connexion'

class DetailArticle(LoginRequiredMixin, DetailView):
    model = Article
    template_name = 'detail_article.html'
    context_object_name = 'article'
    login_url = 'vue_connexion'

@login_required(login_url='vue_connexion')
def detail_article_json(request, pk):
    article = get_object_or_404(Article, pk=pk)
    data = {
        'id': article.id,
        'designation': article.designation,
        'code_produit': article.code_produit,
        'prix_unitaire_defaut': str(article.prix_unitaire_defaut),
    }
    return JsonResponse(data)

class CreerArticle(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'formulaire_article.html'
    success_url = reverse_lazy('liste_articles')
    login_url = 'vue_connexion'

    def form_valid(self, form):
        messages.success(self.request, "Article ajouté avec succès.")
        return super().form_valid(form)

class ModifierArticle(LoginRequiredMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'formulaire_article.html'
    success_url = reverse_lazy('liste_articles')
    login_url = 'vue_connexion'

    def form_valid(self, form):
        messages.success(self.request, "Article mis à jour avec succès.")
        return super().form_valid(form)

class SupprimerArticle(LoginRequiredMixin, DeleteView):
    model = Article
    template_name = 'confirmer_suppression_article.html'
    success_url = reverse_lazy('liste_articles')
    login_url = 'vue_connexion'

    def form_valid(self, form):
        messages.success(self.request, "Article supprimé avec succès.")
        return super().form_valid(form)
    
class ModifierVente(UpdateView):
    model = Vente
    form_class = VenteForm
    template_name = 'gestions/modifier_vente.html' # Vérifiez ce chemin, il semble spécifique
    context_object_name = 'vente'

    def get_success_url(self):
        return reverse_lazy('detail_vente', kwargs={'pk': self.object.pk})

@login_required
def gestion_stock(request):
    """
    Vue pour afficher la gestion du stock avec les alertes
    """
    articles = Article.objects.all().order_by('designation')
    
    # Séparer les articles par statut de stock
    articles_ok = [article for article in articles if article.stock_actuel > 5]
    articles_alerte = [article for article in articles if article.stock_actuel <= 5]
    
    context = {
        'articles_ok': articles_ok,
        'articles_alerte': articles_alerte,
        'total_articles': articles.count(),
        'articles_en_alerte': len(articles_alerte),
    }
    
    return render(request, 'gestions/gestion_stock.html', context)

@login_required
def alertes_stock(request):
    """
    Vue pour afficher uniquement les alertes de stock faible
    """
    articles_alerte = Article.objects.filter(stock_actuel__lte=5).order_by('designation')
    
    context = {
        'articles_alerte': articles_alerte,
        'total_alertes': articles_alerte.count(),
    }
    
    return render(request, 'gestions/alertes_stock.html', context)

@login_required
def modifier_stock(request, pk):
    """
    Vue pour modifier le stock d'un article
    """
    article = get_object_or_404(Article, pk=pk)
    
    if request.method == 'POST':
        nouveau_stock = request.POST.get('stock_actuel')
        if nouveau_stock:
            try:
                article.stock_actuel = float(nouveau_stock)
                article.save()
                messages.success(request, f'Stock de {article.designation} mis à jour avec succès.')
                return redirect('gestion_stock')
            except ValueError:
                messages.error(request, 'Veuillez entrer un nombre valide.')
    
    context = {
        'article': article,
    }
    
    return render(request, 'gestions/modifier_stock.html', context)

