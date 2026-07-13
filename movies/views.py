from django.shortcuts import render
import pandas as pd

from .services.recommender import (
    load_dataset,
    preprocess_data,
    generate_similarity_matrix,
    recommend_movies,
)


def home(request):
    return render(request, "home.html")


def recommendations(request):

    try:
        movie_name = request.GET.get("movie", "").strip()

        if not movie_name:
            return render(
                request,
                "home.html",
                {
                    "error": "Please enter a movie name.",
                    "movie_name": "",
                },
            )

        movies = load_dataset("master_dataset.csv")
        movies = movies[["title", "genres"]].drop_duplicates().reset_index(drop=True)
        movies = preprocess_data(movies)

        similarity = generate_similarity_matrix(movies)

        recommended_titles = recommend_movies(
            movie_name,
            movies,
            similarity,
        )

        if recommended_titles == ["Movie not found in the dataset."]:
            return render(
                request,
                "home.html",
                {
                    "error": "Movie not found.",
                    "movie_name": movie_name,
                },
            )

        recommendations = []

        full_dataset = pd.read_csv("master_dataset.csv")

        for title in recommended_titles:

            movie = full_dataset[full_dataset["title"] == title]

            if not movie.empty:

                recommendations.append(
                    {
                        "title": title,
                        "genres": movie.iloc[0]["genres"],
                        "rating": round(movie["rating"].mean(), 1),
                        "total_ratings": int(movie["rating"].count()),
                    }
                )

        return render(
            request,
            "recommendations.html",
            {
                "recommendations": recommendations,
                "movie_name": movie_name,
            },
        )

    except Exception:
        return render(
            request,
            "home.html",
            {
                "error": "Something went wrong. Please try again.",
                "movie_name": "",
            },
        )