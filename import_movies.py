import os
import django
import pandas as pd

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movie_recommendation_system.settings")
django.setup()

from movies.models import Movie

df = pd.read_csv("master_dataset.csv")

movies = df[["movieId", "title", "genres"]].drop_duplicates()

for _, row in movies.iterrows():
    Movie.objects.get_or_create(
        movie_id=row["movieId"],
        defaults={
            "title": row["title"],
            "genres": row["genres"]
        }
    )

print("Movies imported successfully!")