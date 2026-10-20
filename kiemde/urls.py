# kiemde/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # AUTHENTICATION URLs (Doivent être définies en premier ou tôt)
    path('connexion/', auth_views.LoginView.as_view(template_name='vue_connexion.html'), name='vue_connexion'),
    path('deconnexion/', auth_views.LogoutView.as_view(next_page='vue_connexion'), name='vue_deconnexion'),

    # Include gestions app URLs
    path('', include('gestions.urls')), # C'est important que cette ligne soit là
]

# Servir les fichiers médias et statiques en mode développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)