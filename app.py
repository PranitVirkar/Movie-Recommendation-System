import streamlit as st
import pandas as pd
import pickle
import requests
import time

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry_strategy = Retry(
    total=3,
    status_forcelist=[429, 500, 502, 503, 504],
    backoff_factor=1  # wait 1s, then 2s, then 4s
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)

def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8d67f6914d2e74ff982eb67d3ed6d058&language=en-US"
        response = session.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        poster_path = data.get("poster_path")
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
        else:
            print(f"[INFO] No poster for movie ID {movie_id}")
            return "https://via.placeholder.com/500x750.png?text=No+Poster"
    except Exception as e:
        print(f"[ERROR] Failed to fetch poster for movie ID {movie_id}: {e}")
        return "https://via.placeholder.com/500x750.png?text=Error"

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []
    for i in movies_list:
        title = movies.iloc[i[0]].title
        movie_id = movies.iloc[i[0]].movie_id
        print(f"Fetching: {title} (ID: {movie_id})")
        recommended_movies.append(title)
        recommended_posters.append(fetch_poster(movie_id))
        time.sleep(0.3) 

    return recommended_movies, recommended_posters

movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl', 'rb'))

st.title('🎬 Movie Recommender System')

selected_movie_name = st.selectbox('Enter Name of Movie', movies['title'].values)

if st.button('Recommend'):
    names, posters = recommend(selected_movie_name)
    cols = st.columns(5)
    for i in range(len(cols)):
        with cols[i]:
            st.text(names[i])
            st.image(posters[i])
