document.addEventListener("DOMContentLoaded", () => {
    const popup = document.getElementById("movie-popup");
    const favoriteBtn = document.getElementById("popup-button-fav");

    // Gestion dynamique des films cliqués
    document.querySelector("main").addEventListener("click", (event) => {
        const filmItem = event.target.closest(".film-item");
        if (filmItem) {
            const title = filmItem.querySelector("h3").textContent;
            const image = filmItem.querySelector("img").src;

            // Mettre à jour les informations initiales du pop-up
            popup.querySelector("#popup-title").textContent = title;
            popup.querySelector("#popup-image").src = image;
            popup.querySelector("#popup-description").textContent = "Chargement de la description...";

            // Récupérer le movieId via l'API
            fetch(`/get_movie_id?title=${encodeURIComponent(title)}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Erreur HTTP : ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    const movieId = data.movieId;
                    console.log(`Movie ID pour '${title}' : ${movieId}`);

                    // Mettre à jour l'état du bouton en fonction des favoris
                    fetch(`/is_favorite/${movieId}`)
                        .then(response => response.json())
                        .then(data => {
                            if (data.is_favorite) {
                                favoriteBtn.textContent = "FAVORI";
                                favoriteBtn.classList.add("favorited");
                            } else {
                                favoriteBtn.textContent = "ADD FAVORITES";
                                favoriteBtn.classList.remove("favorited");
                            }
                        })
                        .catch(error => console.error("Erreur lors de la vérification des favoris :", error));

                    // Ajouter le movieId en tant que dataset sur le bouton
                    favoriteBtn.dataset.movieId = movieId;

                    // Récupérer la description via l'API
                    return fetch(`/get_description/${movieId}`);
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Erreur HTTP : ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    // Mettre à jour la description dans le pop-up
                    const description = data.description || "Description non disponible.";
                    popup.querySelector("#popup-description").textContent = description;
                })
                .catch(error => {
                    console.error("Erreur lors de la récupération de la description :", error);
                    popup.querySelector("#popup-description").textContent = "Erreur lors de la récupération de la description.";
                });

            // Afficher le pop-up
            popup.classList.remove("hidden");
            popup.classList.add("active");
        }
    });

    // Ajouter un gestionnaire d'événement au bouton "Add to Favorites"
    favoriteBtn.addEventListener("click", () => {
        const movieId = favoriteBtn.dataset.movieId;

        if (!movieId) {
            console.error("Movie ID introuvable !");
            return;
        }

        // Envoyer une requête pour basculer l'état du favori
        fetch('/toggle_favorite', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ movieId: movieId }) // Envoyer le movieId
        })
        .then(response => response.json())
        .then(data => {
            // Mettre à jour l'état du bouton en fonction de l'ajout ou de la suppression
            if (favoriteBtn.classList.contains("favorited")) {
                favoriteBtn.classList.remove("favorited");
                favoriteBtn.textContent = "ADD FAVORITES";
            } else {
                favoriteBtn.classList.add("favorited");
                favoriteBtn.textContent = "FAVORI";
            }
        })
        .catch(error => console.error("Erreur lors de la mise à jour des favoris :", error));
    });

    // Fermer le pop-up
    document.getElementById("close-popup").addEventListener("click", () => {
        popup.classList.add("hidden");
        popup.classList.remove("active");
    });
});
