import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OMDB_API_KEY")



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
                "runtime": data.get("Runtime"),
                "language": data.get("Language"),
                "released": data.get("Released"),
                "plot": data.get("Plot"),
                "imdb_rating": data.get("imdbRating"),
                "genre": data.get("Genre"),
            }

    except Exception:
        pass

    return {
        "poster": None,
        "year": "N/A",
        "runtime": "N/A",
        "language": "N/A",
        "released": "N/A",
        "plot": "Not Available",
        "imdb_rating": "N/A",
        "genre": "N/A",
    }