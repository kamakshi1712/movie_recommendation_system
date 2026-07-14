import requests

API_KEY = "1d5c4e3f"


def get_movie_details(movie_title):
    clean_title = movie_title.split("(")[0].strip()
    url = f"https://www.omdbapi.com/?t={clean_title}&apikey={API_KEY}"

    try:
        response = requests.get(url)
        data = response.json()

        if data.get("Response") == "True":
            return {
                "poster": data.get("Poster"),
                "year": data.get("Year"),
            }

    except Exception:
        pass

    return {
        "poster": None,
        "year": "N/A",
    }