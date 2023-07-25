from collections import Counter

class Comment:
    def __init__(self, points_forts):
        self.points_forts = points_forts

comments = [
    Comment(['bon', 'film', 'pixar', 'amour', 'impossible']),
    Comment(['film', 'bien', 'adorer', 'univers', 'conseiller']),
    Comment(['film', 'bien', 'pixar', 'test', 'a']),
    Comment(['film', 'bien', 'adorer', 'pixar', 'cjdj'])
]

# Extraction des mots clés les plus fréquents pour les points forts
points_forts = []
for comment in comments:
    points_forts.extend(comment.points_forts)

top_points_forts = Counter(points_forts).most_common(3)
if top_points_forts:
    top_keywords = []
    for keyword, count in top_points_forts:
        top_keywords.append(keyword)
        if len(top_keywords) == 3:
            break

# Affichage des mots clés les plus fréquents
print(top_keywords)