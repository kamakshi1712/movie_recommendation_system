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


@login_required
def home(request):

    recent_movies = (
        SearchHistory.objects.filter(user=request.user)
        .order_by("-searched_at")
        .values_list("movie_title", flat=True)
        .distinct()[:5]
    )

    return render(
        request,
        "home.html",
        {
            "recent_movies": recent_movies,
        },
    )


@login_required
def dashboard(request):

    total_searches = SearchHistory.objects.filter(
        user=request.user
    ).count()

    total_favorites = FavoriteMovie.objects.filter(
        user=request.user
    ).count()

    recent_movies = SearchHistory.objects.filter(
        user=request.user
    ).order_by("-searched_at")[:5]

    return render(
        request,
        "dashboard.html",
        {
            "total_searches": total_searches,
            "total_favorites": total_favorites,
            "recent_movies": recent_movies,
        },
    )


@login_required
def recommendations(request):

    try:
        movie_name = request.GET.get("movie", "").strip()

        recent_movies = (
            SearchHistory.objects.filter(user=request.user)
            .order_by("-searched_at")
            .values_list("movie_title", flat=True)
            .distinct()[:5]
        )

        if not movie_name:
            return render(
                request,
                "home.html",
                {
                    "error": "Please enter a movie name.",
                    "movie_name": "",
                    "recent_movies": recent_movies,
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
                    "recent_movies": recent_movies,
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
                        "runtime": movie_details["runtime"],
                        "language": movie_details["language"],
                        "released": movie_details["released"],
                        "plot": movie_details["plot"],
                        "imdb_rating": movie_details["imdb_rating"],
                        "genre": movie_details["genre"],
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
                "recent_movies": recent_movies,
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