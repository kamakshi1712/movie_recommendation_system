from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from movies import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.home, name='home'),
    path('recommendations/', views.recommendations, name='recommendations'),

    path(
        'login/',
        auth_views.LoginView.as_view(template_name='login.html'),
        name='login'
    ),

    path(
        'logout/',
        auth_views.LogoutView.as_view(next_page='login'),
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
]