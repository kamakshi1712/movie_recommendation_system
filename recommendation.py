import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def load_dataset(file_path):
    return pd.read_csv(file_path)

def preprocess_data(data):
    data["genres"] = data["genres"].fillna("")
    return data

def generate_similarity_matrix(data):
    cv = CountVectorizer(stop_words="english")
    vectors = cv.fit_transform(data["genres"]).toarray()
    similarity = cosine_similarity(vectors)
    return similarity

def recommend_movies(movie_title, movies, similarity, num_recommendations=10):

    if movie_title not in movies["title"].values:
        return ["Movie not found in the dataset."]

    movie_index = movies[movies["title"] == movie_title].index[0]

    similarity_scores = list(enumerate(similarity[movie_index]))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)

    recommendations = []
    seen = set()

    for movie in similarity_scores[1:]:
        title = movies.iloc[movie[0]]["title"]

        if title not in seen:
            recommendations.append(title)
            seen.add(title)

        if len(recommendations) == num_recommendations:
            break

    return recommendations
