from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from movies import views


urlpatterns = [

    path(
        'admin/',
        admin.site.urls
    ),

    path(
        '',
        views.home,
        name='home'
    ),

    path(
        'dashboard/',
        views.dashboard,
        name='dashboard'
    ),

    path(
        'recommendations/',
        views.recommendations,
        name='recommendations'
    ),

    # Day 19 - Advanced Search
    path(
        'advanced-search/',
        views.advanced_search,
        name='advanced_search'
    ),

    # Day 19 - Movie Comparison
    path(
        'compare/',
        views.compare_movies,
        name='compare_movies'
    ),

    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='login.html'
        ),
        name='login'
    ),

    path(
        'logout/',
        auth_views.LogoutView.as_view(
            next_page='login'
        ),
        name='logout'
    ),

    path(
        'register/',
        views.register,
        name='register'
    ),

    path(
        'history/',
        views.search_history,
        name='search_history'
    ),

    path(
        'favorites/',
        views.favorites,
        name='favorites'
    ),

    path(
        'add-favorite/',
        views.add_favorite,
        name='add_favorite'
    ),

    path(
        'remove-favorite/<int:favorite_id>/',
        views.remove_favorite,
        name='remove_favorite'
    ),

    path(
        'watchlist/',
        views.watchlist,
        name='watchlist'
    ),

    path(
        'add-watchlist/',
        views.add_watchlist,
        name='add_watchlist'
    ),

    path(
    'remove-watchlist/<int:watchlist_id>/',
    views.remove_watchlist,
    name='remove_watchlist'
    ),

]