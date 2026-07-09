from django.contrib import admin
from .models import Movie, SearchHistory

admin.site.register(Movie)
admin.site.register(SearchHistory)