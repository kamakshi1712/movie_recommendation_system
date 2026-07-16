from django.shortcuts import render, redirect
import pandas as pd

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

from .models import SearchHistory, FavoriteMovie

from .services.recommender import (
    load_dataset,
    preprocess_data,
    generate_similarity_matrix,
    recommend_movies,
)

from .services.omdb import get_movie_details

from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    return render(request, "home.html")



@login_required
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

        SearchHistory.objects.create(
            user=request.user,
            movie_title=movie_name,
        )

        recommendations = []

        full_dataset = pd.read_csv("master_dataset.csv")

        for title in recommended_titles:

            movie = full_dataset[full_dataset["title"] == title]

            if not movie.empty:

                movie_details = get_movie_details(title)

                recommendations.append(
                    {
                        "title": title,
                        "genres": movie.iloc[0]["genres"],
                        "rating": round(movie["rating"].mean(), 1),
                        "total_ratings": int(movie["rating"].count()),
                        "poster": movie_details["poster"],
                        "year": movie_details["year"],
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


def register(request):

    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("login")

    else:
        form = UserCreationForm()

    return render(
        request,
        "register.html",
        {
            "form": form,
        },
    )


@login_required
def search_history(request):

    history = SearchHistory.objects.filter(
        user=request.user
    ).order_by("-searched_at")

    return render(
        request,
        "history.html",
        {
            "history": history,
        },
    )


@login_required
def add_favorite(request):

    if request.method == "POST":

        FavoriteMovie.objects.get_or_create(
            user=request.user,
            title=request.POST.get("title"),
            genres=request.POST.get("genres"),
            poster=request.POST.get("poster"),
            rating=request.POST.get("rating"),
        )

    return redirect(request.META.get("HTTP_REFERER", "/"))


@login_required
def favorites(request):

    favorites = FavoriteMovie.objects.filter(
        user=request.user
    ).order_by("-added_at")

    return render(
        request,
        "favorites.html",
        {
            "favorites": favorites,
        },
    )


@login_required
def remove_favorite(request, favorite_id):

    favorite = FavoriteMovie.objects.get(
        id=favorite_id,
        user=request.user,
    )

    favorite.delete()

    return redirect("favorites")