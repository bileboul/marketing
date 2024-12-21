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
    # Envoi des titres à la page web
    return render_template('users.html')

@app.route('/main')
def main():
    return render_template('main.html')

import random

@app.route('/main/recommendation')
def get_recommendation():
    """
    Retourne des recommandations basées sur les deux genres les plus présents 
    dans les favoris de l'utilisateur, avec un mélange aléatoire des résultats.
    """
    # Chemin du fichier des favoris
    favorites_file = "user1/favorite.csv"
    try:
        # Charger les favoris
        favorites_df = pd.read_csv(favorites_file)
    except FileNotFoundError:
        # Si aucun favori n'est trouvé, retourner 5 films aléatoires comme fallback
        return jsonify(df.sample(n=5, random_state=random.randint(0, 1000)).to_dict(orient='records'))

    # Extraire les genres des films favoris
    favorite_movies = df[df['movieId'].isin(favorites_df['movieId'])]
    genre_counts = {}

    # Compter l'occurrence de chaque genre dans les favoris
    for genres in favorite_movies['genres'].dropna():
        for genre in genres.split('|'):
            genre_counts[genre] = genre_counts.get(genre, 0) + 1

    # Trouver les deux genres les plus fréquents
    top_genres = sorted(genre_counts, key=genre_counts.get, reverse=True)[:2]
    print(top_genres)

    if not top_genres:
        return jsonify([])  # Aucun genre trouvé, retourner une liste vide

    # Filtrer les films ayant au moins un des deux genres les plus présents
    recommended_movies = df[
        df['genres'].apply(lambda x: any(genre in top_genres for genre in str(x).split('|')))
    ]

    # Exclure les films déjà favoris
    recommended_movies = recommended_movies[~recommended_movies['movieId'].isin(favorites_df['movieId'])]

    # Mélanger les films recommandés et limiter à 5
    recommended_movies = recommended_movies.sample(
        n=min(len(recommended_movies), 5),  # Assurez-vous de ne pas dépasser la taille réelle des données
        random_state=random.randint(0, 1000)  # Random seed pour mélange aléatoire
    )

    return jsonify(recommended_movies.to_dict(orient='records'))




@app.route('/main/action')
def get_action_movies():
    # Filtrer les films d'action
    action_movies = df[df['genres'].str.contains('Action', na=False)]
    
    # Retourner en JSON directement avec jsonify
    return jsonify(action_movies.iloc[1:20].to_dict(orient='records'))

@app.route('/main/comedy')
def get_comedy_movies():
    comedy_movies = df[df['genres'].str.contains('Comedy', na=False)]
    return jsonify(comedy_movies.iloc[1:20].to_dict(orient='records'))

@app.route('/main/Sci-Fi')
def get_Scifi_movies():
    scify_movies = df[df['genres'].str.contains('Sci-Fi', na=False)]
    return jsonify(scify_movies.iloc[1:20].to_dict(orient='records'))


@app.route('/main/Horror')
def get_horror_movies():
    horror_movies = df[df['genres'].str.contains('Horror', na=False)]
    return jsonify(horror_movies.iloc[1:20].to_dict(orient='records'))

@app.route('/main/Children')
def get_children_movies():
    children_movies = df[df['genres'].str.contains('Children', na=False)]
    return jsonify(children_movies.iloc[1:20].to_dict(orient='records'))

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/test/json')
def test_json():
    # Convertir le dataframe en JSON brut
    json_data = df.to_json(orient='records')
    return jsonify(json_data)

@app.route('/test/title/<string:title>')
def get_movie_by_title(title):
    # Filtrer les données par titre
    filtered_df = df[df['title'].str.contains(title, case=False, na=False)]

    if not filtered_df.empty:
        # Convertir en JSON et retourner correctement avec jsonify
        return jsonify(filtered_df.to_dict(orient='records'))
    else:
        return jsonify([])  # Retourner une liste vide si aucun film n'est trouvé
    

def get_movie_id_by_title(df, title):
    """
    Récupère l'ID d'un film à partir de son titre sans tenir compte de l'année entre parenthèses.
    
    :param df: pd.DataFrame - Le DataFrame contenant les films (avec colonnes "movieId" et "title").
    :param title: str - Le titre du film recherché (sans l'année).
    :return: int ou None - L'ID du film si trouvé, sinon None.
    """
    # Supprimer l'année entre parenthèses des titres du DataFrame
    df['clean_title'] = df['title'].str.replace(r"\s*\(\d{4}\)$", "", regex=True)

    # Supprimer l'année entre parenthèses du titre fourni
    clean_title = re.sub(r"\s*\(\d{4}\)$", "", title)

    # Recherche insensible à la casse
    result = df[df['clean_title'].str.contains(clean_title, case=False, na=False)]
    if not result.empty:
        return result.iloc[0]['movieId']  # Retourne l'ID du premier résultat trouvé
    return None


@app.route('/get_movie_id', methods=['GET'])
def get_movie_id():
    title = request.args.get('title')  # Récupérer le titre depuis les paramètres de l'URL

    if not title:
        return jsonify({"error": "Title parameter is required"}), 400

    movie_id = get_movie_id_by_title(df, title)

    if movie_id:
        return jsonify({"movieId": int(movie_id), "title": title})
    else:
        return jsonify({"error": f"Movie with title '{title}' not found"}), 404

    
@app.route('/is_favorite/<movieId>', methods=['GET'])
def is_favorite(movieId,user="user1"):
    favorites_df = pd.read_csv(user+'/favorite.csv')
    movieId = int(movieId)
    
    # Vérifiez si le titre du film existe dans le CSV
    is_fav = movieId in favorites_df['movieId'].values
    
    # Retournez un JSON indiquant si le film est favori
    return jsonify({"is_favorite": is_fav})

@app.route('/get_description/<int:movieId>', methods=['GET'])
def get_description(movieId):
    """
    Retourne la description d'un film en fonction de son movieId.
    """
    movie = df[df['movieId'] == movieId]
    if not movie.empty:
        # Retourne la description du film
        description = movie.iloc[0]['description']
        return jsonify({"movieId": movieId, "description": description})
    else:
        # Retourne une erreur si le movieId n'existe pas
        return jsonify({"error": f"Movie with ID {movieId} not found"}), 404


@app.route('/toggle_favorite', methods=['POST'])
def toggle_favorite(user="1"):
    data = request.get_json()  # Récupérez les données du corps de la requête
    movieId = data.get('movieId')  # Récupérez le movieId
    print(movieId)
    if not movieId:
        return jsonify({"error": "Movie ID is required"}), 400

    # Définir le chemin du fichier CSV
    user_folder = 'user'+user
    os.makedirs(user_folder, exist_ok=True)  # Créez le dossier si nécessaire
    favorites_file = os.path.join(user_folder, 'favorite.csv')
    print(favorites_file)

    # Charger ou initialiser le DataFrame
    if os.path.exists(favorites_file):
        favorites_df = pd.read_csv(favorites_file)
    else:
        favorites_df = pd.DataFrame(columns=['movieId'])

    # Ajouter ou supprimer le favori
    if int(movieId) in favorites_df['movieId'].astype(int).values:
        # Supprimer si déjà favori
        favorites_df = favorites_df[favorites_df['movieId'].astype(int) != int(movieId)]
        action = "removed"
    else:
        # Ajouter comme favori
        new_favorite = {"movieId": int(movieId)}
        favorites_df = pd.concat([favorites_df, pd.DataFrame([new_favorite])], ignore_index=True)
        action = "added"

    # Enregistrez les modifications dans le fichier CSV
    favorites_df.to_csv(favorites_file, index=False)

    return jsonify({"success": True, "action": action, "movieId": movieId})

if __name__ == '__main__':
    app.run(debug=True, port=5000)


