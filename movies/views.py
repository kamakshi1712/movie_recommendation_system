from django.shortcuts import render

def home(request):
    return render(request, "home.html")


def recommendations(request):
    recommendations = [
        {
            "title": "Toy Story 2 (1999)",
            "genres": "Adventure | Animation | Children | Comedy | Fantasy",
            "rating": 4.3,
        },
        {
            "title": "Monsters, Inc. (2001)",
            "genres": "Adventure | Animation | Children | Comedy",
            "rating": 4.2,
        },
        {
            "title": "Shrek (2001)",
            "genres": "Adventure | Animation | Comedy | Fantasy",
            "rating": 4.1,
        },
    ]

    return render(
        request,
        "recommendations.html",
        {"recommendations": recommendations},
    )