from django.views.generic import TemplateView
import requests
from bs4 import BeautifulSoup
from .models import Comment
from transformers import pipeline
import re
from .models import Film


def extract_film_name(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Rechercher le titre dans la balise <title>
    title_element = soup.find('title')
    film_name = title_element.get_text()

    # Rechercher le titre dans la balise <meta>
    meta_element = soup.find('meta', property='og:title')
    if meta_element:
        meta_title = meta_element['content']
        # Utilisation d'une expression régulière pour extraire le nom du film
        pattern = r"(?:Avis sur le film|Critiques de la série)\s(.*)$"
        match = re.search(pattern, meta_title)
        if match:
            film_name = match.group(1)

    return film_name

def create_film_from_url(url):
    film_id = url.split('/')[-4].split('-')[-1]

    film_name = extract_film_name(url)

    details_url = f'https://www.allocine.fr/film/fichefilm_gen_cfilm={film_id}.html'

    response = requests.get(details_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    synopsis_element = soup.find('meta', property='og:description')
    if synopsis_element:
        synopsis = synopsis_element['content']
    else:
        synopsis = ''

    date_element = soup.find('span', class_='date')
    if date_element:
        date_text = date_element.get_text(strip=True)
        # La date est déjà sous forme de chaîne de caractères
        date_sortie = date_text
    else:
        date_sortie = None

    # Insérer les données dans la base de données
    film = Film(film=film_name, synopsis=synopsis, date_sortie=date_sortie)
    film.save()


import spacy

nlp = spacy.load("fr_core_news_sm")

def extract_keywords(comment_text):
    doc = nlp(comment_text)

    keywords = []

    for token in doc:
        if token.pos_ in ['NOUN', 'VERB', 'ADJ', 'ADV'] and not token.is_stop:
            keywords.append(token.lemma_)

    return keywords[:5]


def scraping(url):
    base_url = url + "?page="
    page_number = 1
    all_comments = []

    # Extraire le nom du film
    film_name = extract_film_name(url)
    create_film_from_url(url)  # Créer l'objet Film

    # Charger le modèle de sentiment pré-entraîné pour le français
    sentiment_classifier = pipeline('sentiment-analysis', model='nlptown/bert-base-multilingual-uncased-sentiment')

    while True:
        url = base_url + str(page_number)

        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        comment_elements = soup.find_all('div', {'class': 'content-txt review-card-content'})
        comments = [element.get_text(strip=True) for element in comment_elements]

        if not comments or comments == all_comments[-len(comments):]:
            break

        all_comments.extend(comments)

        page_number += 1

    # Limiter la longueur maximale de la séquence à 512 tokens
    MAX_SEQUENCE_LENGTH = 512

    # Ajouter les commentaires à la base de données avec leur positivité/négativité et le nom du film
    for comment_text in all_comments:
        # Tronquer la séquence si elle dépasse la limite
        truncated_comment = comment_text[:MAX_SEQUENCE_LENGTH]

        # Analyser le sentiment du commentaire tronqué
        result = sentiment_classifier(truncated_comment)
        sentiment = result[0]['label']

        # Extraire les mots-clés du commentaire
        keywords = extract_keywords(comment_text)

        # Créer un nouvel objet Comment avec le texte, le sentiment, les mots-clés et le nom du film
        if sentiment == '5 stars' or sentiment == '4 stars':
            points_faibles = None
            points_forts = keywords[:5]
        elif sentiment == '2 stars' or sentiment == '1 star':
            points_faibles = keywords[:5]
            points_forts = None
        else:
            points_faibles = None
            points_forts = None

        Comment.objects.create(content=comment_text, sentiment=sentiment, film=film_name,
                               points_faibles=points_faibles, points_forts=points_forts)

    return all_comments