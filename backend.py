from flask import Flask, render_template, jsonify, request
import pandas as pd
import os
import re

app = Flask(__name__, static_folder='static')
app._static_folder = 'templates/static'

# Chargement des données depuis le fichier CSV
df = pd.read_csv('moviesCopy.csv')

@app.route('/')
def chooseAccount():
    """
    Affiche la page d'accueil permettant de choisir un compte utilisateur.
    """
    return render_template('users.html')

@app.route('/main')
def main():
    """
    Affiche la page principale de l'application.
    """
    return render_template('main.html')

import random

@app.route('/main/recommendation')
def get_recommendation():
    """
    Retourne des recommandations basées sur les genres les plus fréquents 
    dans les favoris de l'utilisateur. Si aucun favori n'est trouvé, retourne
    des films aléatoires comme fallback.
    """
    favorites_file = "user1/favorite.csv"
    try:
        favorites_df = pd.read_csv(favorites_file)
    except FileNotFoundError:
        return jsonify(df.sample(n=5, random_state=random.randint(0, 1000)).to_dict(orient='records'))

    favorite_movies = df[df['movieId'].isin(favorites_df['movieId'])]
    genre_counts = {}
    for genres in favorite_movies['genres'].dropna():
        for genre in genres.split('|'):
            genre_counts[genre] = genre_counts.get(genre, 0) + 1

    top_genres = sorted(genre_counts, key=genre_counts.get, reverse=True)[:2]
    if not top_genres:
        return jsonify([])

    recommended_movies = df[
        df['genres'].apply(lambda x: any(genre in top_genres for genre in str(x).split('|')))
    ]
    recommended_movies = recommended_movies[~recommended_movies['movieId'].isin(favorites_df['movieId'])]
    recommended_movies = recommended_movies.sample(
        n=min(len(recommended_movies), 5),
        random_state=random.randint(0, 1000)
    )

    return jsonify(recommended_movies.to_dict(orient='records'))

@app.route('/main/action')
def get_action_movies():
    """
    Retourne une liste de films appartenant au genre Action.
    """
    action_movies = df[df['genres'].str.contains('Action', na=False)]
    return jsonify(action_movies.iloc[1:20].to_dict(orient='records'))

@app.route('/main/comedy')
def get_comedy_movies():
    """
    Retourne une liste de films appartenant au genre Comédie.
    """
    comedy_movies = df[df['genres'].str.contains('Comedy', na=False)]
    return jsonify(comedy_movies.iloc[1:20].to_dict(orient='records'))

@app.route('/main/Sci-Fi')
def get_scifi_movies():
    """
    Retourne une liste de films appartenant au genre Science-Fiction.
    """
    scify_movies = df[df['genres'].str.contains('Sci-Fi', na=False)]
    return jsonify(scify_movies.iloc[1:20].to_dict(orient='records'))

@app.route('/main/Horror')
def get_horror_movies():
    """
    Retourne une liste de films appartenant au genre Horreur.
    """
    horror_movies = df[df['genres'].str.contains('Horror', na=False)]
    return jsonify(horror_movies.iloc[1:20].to_dict(orient='records'))

@app.route('/main/Children')
def get_children_movies():
    """
    Retourne une liste de films appartenant au genre Enfants.
    """
    children_movies = df[df['genres'].str.contains('Children', na=False)]
    return jsonify(children_movies.iloc[1:20].to_dict(orient='records'))

@app.route('/test')
def test():
    """
    Affiche une page de test pour des expérimentations.
    """
    return render_template('test.html')

@app.route('/test/json')
def test_json():
    """
    Retourne toutes les données du fichier CSV sous forme de JSON.
    """
    json_data = df.to_json(orient='records')
    return jsonify(json_data)

@app.route('/test/title/<string:title>')
def get_movie_by_title(title):
    """
    Recherche un film par son titre et retourne les résultats correspondants.
    """
    filtered_df = df[df['title'].str.contains(title, case=False, na=False)]
    if not filtered_df.empty:
        return jsonify(filtered_df.to_dict(orient='records'))
    else:
        return jsonify([])

def get_movie_id_by_title(df, title):
    """
    Récupère l'ID d'un film à partir de son titre sans tenir compte de l'année.
    """
    df['clean_title'] = df['title'].str.replace(r"\s*\(\d{4}\)$", "", regex=True)
    clean_title = re.sub(r"\s*\(\d{4}\)$", "", title)
    result = df[df['clean_title'].str.contains(clean_title, case=False, na=False)]
    if not result.empty:
        return result.iloc[0]['movieId']
    return None

@app.route('/get_movie_id', methods=['GET'])
def get_movie_id():
    """
    Récupère l'ID d'un film via son titre fourni en paramètre de requête.
    """
    title = request.args.get('title')
    if not title:
        return jsonify({"error": "Title parameter is required"}), 400

    movie_id = get_movie_id_by_title(df, title)
    if movie_id:
        return jsonify({"movieId": int(movie_id), "title": title})
    else:
        return jsonify({"error": f"Movie with title '{title}' not found"}), 404

@app.route('/is_favorite/<movieId>', methods=['GET'])
def is_favorite(movieId, user="user1"):
    """
    Vérifie si un film est dans les favoris d'un utilisateur spécifique.
    """
    favorites_df = pd.read_csv(user+'/favorite.csv')
    movieId = int(movieId)
    is_fav = movieId in favorites_df['movieId'].values
    return jsonify({"is_favorite": is_fav})

@app.route('/get_description/<int:movieId>', methods=['GET'])
def get_description(movieId):
    """
    Retourne la description d'un film en fonction de son ID.
    """
    movie = df[df['movieId'] == movieId]
    if not movie.empty:
        description = movie.iloc[0]['description']
        return jsonify({"movieId": movieId, "description": description})
    else:
        return jsonify({"error": f"Movie with ID {movieId} not found"}), 404

@app.route('/toggle_favorite', methods=['POST'])
def toggle_favorite(user="1"):
    """
    Ajoute ou supprime un film des favoris de l'utilisateur.
    """
    data = request.get_json()
    movieId = data.get('movieId')
    if not movieId:
        return jsonify({"error": "Movie ID is required"}), 400

    user_folder = 'user' + user
    os.makedirs(user_folder, exist_ok=True)
    favorites_file = os.path.join(user_folder, 'favorite.csv')

    if os.path.exists(favorites_file):
        favorites_df = pd.read_csv(favorites_file)
    else:
        favorites_df = pd.DataFrame(columns=['movieId'])

    if int(movieId) in favorites_df['movieId'].astype(int).values:
        favorites_df = favorites_df[favorites_df['movieId'].astype(int) != int(movieId)]
        action = "removed"
    else:
        new_favorite = {"movieId": int(movieId)}
        favorites_df = pd.concat([favorites_df, pd.DataFrame([new_favorite])], ignore_index=True)
        action = "added"

    favorites_df.to_csv(favorites_file, index=False)
    return jsonify({"success": True, "action": action, "movieId": movieId})

if __name__ == '__main__':
    """
    Point d'entrée principal pour démarrer le serveur Flask.
    """
    app.run(debug=True, port=5000)
