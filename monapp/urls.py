from django.contrib import admin
from django.urls import path
from . import views
from .views import ResultsView, DropUrlView, MaListeView



urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('', views.home, name='home'),
    path('search/', DropUrlView.as_view(), name='search'),
    path('accueil/', views.accueil, name='accueil'),
    path('results/', ResultsView.as_view(), name='results'),
    path('malist/', views.malist, name='malist'),
    path('ma-liste/', MaListeView.as_view(), name='malist'),
    path('ajouter_liste/', views.ajouter_liste, name='ajouter_liste'),
    path('supprimer/<int:pk>/', views.SupprimerFilmListeView.as_view(), name='supprimer_liste'),
]
