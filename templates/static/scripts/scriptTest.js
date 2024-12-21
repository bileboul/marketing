fetch('/test/json') // Appeler la route JSON
    .then(response => response.json()) // Convertir la réponse en JSON
    .then(data => {
        // Afficher le JSON brut dans la balise <pre>
        document.getElementById('json-output').textContent = JSON.stringify(data, null, 4);
    })
    .catch(error => console.error('Erreur lors de la récupération du JSON :', error));


fetch('/test/title/Inception') // Rechercher un film contenant "Inception"
    .then(response => response.json()) // Convertir la réponse en JSON
    .then(data => {
        console.log("Données récupérées :", data); // Vérifier le contenu de "data"
        
        if (Array.isArray(data) && data.length > 0) {
            const movieInfoContainer = document.getElementById('movie-info');

            data.forEach(movie => {
                const titleParagraph = document.createElement('p');
                titleParagraph.textContent = `Titre : ${movie.title}`;

                const genreParagraph = document.createElement('p');
                genreParagraph.textContent = `Genres : ${movie.genres}`;

                movieInfoContainer.appendChild(titleParagraph);
                movieInfoContainer.appendChild(genreParagraph);
            });
        } else {
            console.error("Aucun film trouvé ou données incorrectes !");
        }
    })
    .catch(error => console.error('Erreur :', error));