from django.db import models
from django.shortcuts import reverse

class Comment(models.Model):
    content = models.TextField()
    sentiment = models.CharField(max_length=10)  # 'positif' ou 'négatif'
    film = models.CharField(max_length=100)
    points_forts = models.TextField(null=True)
    points_faibles = models.TextField(null=True)

class Film(models.Model):
    film = models.CharField(max_length=255)
    synopsis = models.TextField()
    date_sortie = models.CharField(max_length=255, null=True)
    ajoute_a_liste = models.BooleanField(default=False)

    def __str__(self):
        return self.film
    def delete_url(self):
        return reverse('supprimer_liste', args=[self.pk])