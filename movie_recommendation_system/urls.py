from django.contrib import admin
from django.urls import path
from movies import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('recommendations/', views.recommendations, name='recommendations'),
]