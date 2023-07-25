from django.contrib.auth.models import User
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login
from .scraping import scraping, extract_film_name
from django.views.generic import TemplateView, View
from .models import Comment, Film
from collections import Counter

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password1']
        confirm_password = request.POST['password2']
        
        # Vérifications supplémentaires et traitement des données
        
        if password == confirm_password:
            # Création d'un nouvel utilisateur
            user = User.objects.create_user(username=username, email=email, password=password)
            # Effectuer d'autres actions, comme enregistrer des informations supplémentaires dans le profil de l'utilisateur
            
            # Redirection vers la page de connexion après l'enregistrement réussi
            return redirect('login')
        else:
            # Gérer le cas où les mots de passe ne correspondent pas
            error_message = "Les mots de passe ne correspondent pas."
            return render(request, 'register.html', {'error_message': error_message})
    
    return render(request, 'register.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password1']

        # Vérifier les informations d'identification de l'utilisateur
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Connexion de l'utilisateur
            login(request, user)
            return redirect('accueil')  # Rediriger vers la page d'accueil après la connexion réussie
        else:
            # Gérer le cas où les informations d'identification sont incorrectes
            error_message = "Les informations d'identification sont incorrectes."
            return render(request, 'login.html', {'error_message': error_message})

    return render(request, 'login.html')

def home(request):
    return render(request, 'home.html')

class DropUrlView(TemplateView):
    template_name = 'search.html'

    def post(self, request, *args, **kwargs):
        url = request.POST.get('url')
        comments = scraping(url)

        # Récupérer le titre du film
        film_name = extract_film_name(url)

        # Redirection vers la vue ResultsView avec le titre du film en paramètre GET
        return redirect(reverse('results') + f'?film={film_name}')


class ResultsView(TemplateView):
    template_name = 'results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        film_name = self.request.GET.get('film', '')  # Récupère le nom du film à partir des paramètres GET
        comments = Comment.objects.all()

        if film_name:
            comments = comments.filter(film=film_name)

        context['comments'] = comments
        context['count_5_4_stars'] = comments.filter(sentiment__in=['5 stars', '4 stars']).count()
        context['count_3_stars'] = comments.filter(sentiment='3 stars').count()
        context['count_2_1_stars'] = comments.filter(sentiment__in=['2 stars', '1 star']).count()

        total_comments = context['count_5_4_stars'] + context['count_3_stars'] + context['count_2_1_stars']
        context['percentage_5_4_stars'] = (context['count_5_4_stars'] / total_comments) * 100
        context['percentage_3_stars'] = (context['count_3_stars'] / total_comments) * 100
        context['percentage_2_1_stars'] = (context['count_2_1_stars'] / total_comments) * 100

        context['film_name'] = film_name

        # Récupération des points forts et points faibles de tous les commentaires
        points_forts = []
        points_faibles = []
        for comment in comments:
            sentiment = comment.sentiment
            if sentiment in ['5 stars', '4 stars']:
                points_forts.extend(eval(comment.points_forts))  # Convertir la chaîne de caractères en liste
            elif sentiment in ['2 stars', '1 star']:
                points_faibles.extend(eval(comment.points_faibles))  # Convertir la chaîne de caractères en liste

        dictionnaire_cinema = {
    "scénario": ["scénario", "intrigue", "script", "histoire"],
    "réalisation": ["réalisation", "mise en scène", "direction"],
    "acting": ["acting", "interprétation", "jeu d'acteur"],
    "acteur": ["acteur", "comédien", "interprète"],
    "personnages": ["personnages", "protagonistes", "figures"],
    "musique": ["musique", "bande sonore", "partition"],
    "animation": ["animation", "dessin animé", "animé"],
    "long": ["long", "durée", "étiré"],
    "ennuyant": ["ennuyant", "lent", "monotone"],
    "images": ["images", "visuels", "cinématographie"],
    "effets spéciaux": ["effets spéciaux", "effets visuels", "trucages"],
    "montage": ["montage", "assemblage", "édition"],
    "réalisme": ["réalisme", "authenticité", "crédibilité"],
    "captivant": ["captivant", "saisissant", "envoûtant"],
    "émouvant": ["émouvant", "touchant", "bouleversant"],
    "innovant": ["innovant", "novateur", "original"],
    "fascinant": ["fascinant", "intrigant", "envoûtant"],
    "convaincant": ["convaincant", "persuasif", "crédible"],
    "révélateur": ["révélateur", "éclairant", "significatif"],
    "réflexif": ["réflexif", "pensif", "introspectif"],
    "époustouflant": ["époustouflant", "impressionnant", "magique"],
    "réussi": ["réussi", "accompli", "abouti"],
    "impactant": ["impactant", "marquant", "percutant"],
    "remarquable": ["remarquable", "notable", "exceptionnel"],
    "poignant": ["poignant", "émotionnel", "touchant"],
    "pertinent": ["pertinent", "relevé", "adéquat"],
    "profond": ["profond", "intense", "profondément"],
    "engageant": ["engageant", "captivant", "impliquant"],
    "éblouissant": ["éblouissant", "éclatant", "spectaculaire"],
    "subtil": ["subtil", "délicat", "fin"],
    "surprenant": ["surprenant", "inattendu", "imprévisible"],
    "brillant": ["brillant", "éclatant", "génial"],
    "décevant": ["décevant", "déception", "insatisfaisant"],
    "ennuyeux": ["ennuyeux", "lassant", "rébarbatif"],
    "incohérent": ["incohérent", "incompréhensible", "confus"],
    "faible": ["faible", "médiocre", "insuffisant"],
    "prévisible": ["prévisible", "cliché", "banal"],
    "raté": ["raté", "manqué", "échec"],
    "ennui": ["ennui", "monotonie", "lassitude"],
    "maladroit": ["maladroit", "malhabile", "gauche"],
    "superficiel": ["superficiel", "surface", "creux"],
    "inintéressant": ["inintéressant", "fade", "sans intérêt"],
    "ridicule": ["ridicule", "risible", "absurde"],
    "stéréotypé": ["stéréotypé", "cliché", "conventionnel"],
    "confus": ["confus", "embrouillé", "incompréhensible"],
}

        allowed_keywords = []
        for keywords_list in dictionnaire_cinema.values():
            allowed_keywords.extend(keywords_list)

        # Extraction des mots les plus fréquents parmi les points forts
        top_points_forts = Counter([keyword for keyword in points_forts if keyword in allowed_keywords]).most_common(3)
        top_keywords_forts = [keyword for keyword, count in top_points_forts]

        # Extraction des mots les plus fréquents parmi les points faibles
        top_points_faibles = Counter([keyword for keyword in points_faibles if keyword in allowed_keywords]).most_common(3)
        top_keywords_faibles = [keyword for keyword, count in top_points_faibles]

        # Remplacement des mots manquants dans les points forts
        if len(top_keywords_forts) < 3:
            missing_keywords = set(allowed_keywords) - set(top_keywords_forts)
            additional_keywords = Counter(points_forts).most_common(3 - len(top_keywords_forts))
            for keyword, count in additional_keywords:
                if keyword in missing_keywords:
                    top_keywords_forts.append(keyword)

        # Remplacement des mots manquants dans les points faibles
        if len(top_keywords_faibles) < 3:
            missing_keywords = set(allowed_keywords) - set(top_keywords_faibles)
            additional_keywords = Counter(points_faibles).most_common(3 - len(top_keywords_faibles))
            for keyword, count in additional_keywords:
                if keyword in missing_keywords:
                    top_keywords_faibles.append(keyword)

        context['top_points_forts'] = top_keywords_forts
        context['top_points_faibles'] = top_keywords_faibles

        return context
        
    

def malist(request):
    return render(request, 'malist.html')

def accueil(request):
    return render(request, 'accueil.html')

class MaListeView(TemplateView):
    template_name = 'malist.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        films_a_liste = Film.objects.filter(ajoute_a_liste=True)
        context['films_a_liste'] = films_a_liste
        return context
    
def ajouter_liste(request):
    if request.method == 'POST':
        film_name = request.POST.get('film_name')

        film = Film.objects.get(film=film_name)
        film.ajoute_a_liste = True
        film.save()

        return redirect('malist')
    
class SupprimerFilmListeView(View):
    def post(self, request, pk):
        film = Film.objects.get(pk=pk)
        film.ajoute_a_liste = False
        film.save()
        return redirect('ma_liste')