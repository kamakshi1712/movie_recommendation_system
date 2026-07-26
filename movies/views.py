from django.shortcuts import render, redirect
import pandas as pd

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

from .models import SearchHistory, FavoriteMovie, WatchlistMovie

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
@login_required
def advanced_search(request):

    genre = request.GET.get("genre", "").strip()
    year = request.GET.get("year", "").strip()
    rating = request.GET.get("rating", "").strip()
    language = request.GET.get("language", "").strip()

    searched = any([genre, year, rating, language])
    results = []

    if searched:
        try:
            dataset = pd.read_csv("master_dataset.csv")

            # Keep one record for each movie
            movies = (
                dataset[["title", "genres"]]
                .drop_duplicates()
                .reset_index(drop=True)
            )

            # Apply genre first to reduce unnecessary API calls
            if genre:
                movies = movies[
                    movies["genres"].str.contains(
                        genre,
                        case=False,
                        na=False,
                        regex=False,
                    )
                ]

            # Limit candidates so OMDb requests remain manageable
            movies = movies.head(100)

            for _, movie in movies.iterrows():

                details = get_movie_details(movie["title"])

                movie_year = details.get("year", "N/A")
                movie_language = details.get("language", "N/A")
                imdb_rating = details.get("imdb_rating", "N/A")

                # Release Year filter
                if year and str(movie_year) != year:
                    continue

                # Language filter
                if language:
                    if language.lower() not in str(movie_language).lower():
                        continue

                # IMDb Rating filter
                if rating:
                    try:
                        if imdb_rating == "N/A":
                            continue

                        if float(imdb_rating) < float(rating):
                            continue

                    except (ValueError, TypeError):
                        continue

                results.append(
                    {
                        "title": movie["title"],
                        "genre": details.get("genre") or movie["genres"],
                        "year": movie_year,
                        "imdb_rating": imdb_rating,
                        "language": movie_language,
                        "poster": details.get("poster"),
                    }
                )

                # Enough results for the page
                if len(results) == 12:
                    break

        except Exception:
            results = []

    return render(
        request,
        "advanced_search.html",
        {
            "movies": results,
            "searched": searched,
            "selected_genre": genre,
            "selected_year": year,
            "selected_rating": rating,
            "selected_language": language,
        },
    )
@login_required
def compare_movies(request):

    movie1_name = request.GET.get("movie1", "").strip()
    movie2_name = request.GET.get("movie2", "").strip()

    movie1 = None
    movie2 = None
    error = None

    if movie1_name or movie2_name:

        if not movie1_name or not movie2_name:
            error = "Please enter both movie names."

        else:
            details1 = get_movie_details(movie1_name)
            details2 = get_movie_details(movie2_name)

            if details1["year"] == "N/A" or details2["year"] == "N/A":
                error = "One or both movies could not be found. Please check the movie names."

            else:
                movie1 = {
                    "title": movie1_name,
                    "poster": details1["poster"],
                    "genre": details1["genre"],
                    "year": details1["year"],
                    "runtime": details1["runtime"],
                    "imdb_rating": details1["imdb_rating"],
                    "language": details1["language"],
                    "plot": details1["plot"],
                }

                movie2 = {
                    "title": movie2_name,
                    "poster": details2["poster"],
                    "genre": details2["genre"],
                    "year": details2["year"],
                    "runtime": details2["runtime"],
                    "imdb_rating": details2["imdb_rating"],
                    "language": details2["language"],
                    "plot": details2["plot"],
                }

    return render(
        request,
        "compare_movies.html",
        {
            "movie1": movie1,
            "movie2": movie2,
            "movie1_name": movie1_name,
            "movie2_name": movie2_name,
            "error": error,
        },
    )
@login_required
def add_watchlist(request):

    if request.method == "POST":

        WatchlistMovie.objects.get_or_create(
            user=request.user,
            title=request.POST.get("title"),
            defaults={
                "genres": request.POST.get("genres"),
                "poster": request.POST.get("poster"),
                "imdb_rating": request.POST.get("imdb_rating") or None,
                "year": request.POST.get("year"),
            },
        )

    return redirect(request.META.get("HTTP_REFERER", "/"))


@login_required
def watchlist(request):

    movies = WatchlistMovie.objects.filter(
        user=request.user
    ).order_by("-added_at")

    return render(
        request,
        "watchlist.html",
        {
            "watchlist": movies,
        },
    )


@login_required
def remove_watchlist(request, watchlist_id):

    movie = WatchlistMovie.objects.get(
        id=watchlist_id,
        user=request.user,
    )

    movie.delete()

    return redirect("watchlist")