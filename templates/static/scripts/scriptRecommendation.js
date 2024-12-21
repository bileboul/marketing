document.addEventListener("DOMContentLoaded", () => {
    // Récupérer le conteneur des recommandations
    const recommendationsContainer = document.getElementById("recommendations");

    // Fonction pour vérifier si une image existe
    const doesImageExist = (url) => {
        return new Promise((resolve) => {
            const img = new Image();
            img.onload = () => resolve(true);
            img.onerror = () => resolve(false);
            img.src = url;
        });
    };

    // Fonction pour créer un film avec un background dynamique
    const createFilmItem = async (movie) => {
        const movieDiv = document.createElement("div");
        movieDiv.classList.add("film-item");

        // Définir le chemin d'image
        const jpgPath = `/static/ressources/${movie.movieId}.jpg`;
        const jpegPath = `/static/ressources/${movie.movieId}.jpeg`;

        // Vérifier quelle image existe
        let imagePath = jpgPath;
        if (!(await doesImageExist(jpgPath))) {
            if (await doesImageExist(jpegPath)) {
                imagePath = jpegPath;
            } else {
                imagePath = "/static/ressources/default.jpg"; // Image par défaut
            }
        }

        // Définir le style de fond dynamiquement
        movieDiv.style.background = `url('${imagePath}') no-repeat center/cover`;

        // Ajouter le contenu du film
        const contentDiv = document.createElement("div");
        contentDiv.classList.add("content");
        contentDiv.innerHTML = `<h3>${movie.title}</h3>`;
        movieDiv.appendChild(contentDiv);

        return movieDiv;
    };

    // Requête pour récupérer les films recommandés
    fetch('/main/recommendation')
        .then((response) => response.json())
        .then(async (data) => {
            if (data.length > 0) {
                for (const movie of data) {
                    const movieDiv = await createFilmItem(movie);
                    recommendationsContainer.appendChild(movieDiv);
                }
            } else {
                recommendationsContainer.innerHTML =
                    "<p>No recommended movies at the moment.</p>";
            }
        })
        .catch((error) => {
            console.error("Erreur lors de la récupération des recommandations :", error);
            recommendationsContainer.innerHTML =
                "<p>Unable to load recommendations at the moment.</p>";
        });
});
