document.addEventListener("DOMContentLoaded", () => {
    // Catégories initiales
    const categories = {};

    // Liste des catégories et leurs endpoints
    const categoryEndpoints = [
        { name: "Action", url: "/main/action" },
        { name: "Comedy", url: "/main/comedy" },
        { name: "Sci-Fi", url: "/main/Sci-Fi" },
        { name: "Horror", url: "/main/Horror" },
        { name: "Children", url: "/main/Children" }
    ];

    // Tableau de requêtes fetch pour chaque catégorie
    const fetchPromises = categoryEndpoints.map(endpoint =>
        fetch(endpoint.url)
            .then(response => response.json())
            .then(data => {
                if (data.length > 0) {
                    categories[endpoint.name] = data; // Ajouter les films à la catégorie
                } else {
                    console.warn(`Aucun film trouvé pour ${endpoint.name}.`);
                }
            })
            .catch(error => console.error(`Erreur lors de la récupération des films ${endpoint.name} :`, error))
    );

    // Attendre que toutes les requêtes soient terminées
    Promise.all(fetchPromises)
        .then(() => {
            // Créer les sliders une fois toutes les catégories remplies
            const main = document.querySelector("main");
            Object.keys(categories).forEach((category) => {
                const slider = createSlider(category, categories[category]);
                main.appendChild(slider);
            });
        })
        .catch(error => console.error("Erreur globale lors de la récupération des films :", error));

    // Fonction pour créer un slider dynamique
    const createSlider = (categoryName, films) => {
        const sliderContainer = document.createElement("div");
        sliderContainer.classList.add("slider-film");

        sliderContainer.innerHTML = `
            <h2 class="slider-title">${categoryName} Movies</h2>
            <div class="slider-container">
                <button class="slider-btn left-btn">&#8249;</button>
                <div class="slider-track"></div>
                <button class="slider-btn right-btn">&#8250;</button>
            </div>
        `;

        const sliderTrack = sliderContainer.querySelector(".slider-track");

        films.forEach((film) => {
            const filmDiv = document.createElement("div");
            filmDiv.classList.add("film-item");
        
            // Générer le chemin d'image en fonction de movieId
            const basePath = `static/ressources/${film.movieId}`;
            let imagePath = `${basePath}.jpg`; // Par défaut en jpg
        
            // Vérifier si une image avec l'extension .jpg ou .jpeg existe
            if (!doesImageExist(imagePath)) {
                imagePath = `${basePath}.jpeg`;
                if (!doesImageExist(imagePath)) {
                    imagePath = "static/ressources/default.jpg"; // Image par défaut si aucune n'existe
                }
            }
        
            // Créer l'élément HTML pour le film
            filmDiv.innerHTML = `
                <img src="${imagePath}" alt="${film.title}">
                <h3>${film.title}</h3>
            `;
        
            sliderTrack.appendChild(filmDiv);
        });
        
        // Fonction pour vérifier si une image existe
        function doesImageExist(url) {
            const http = new XMLHttpRequest();
            http.open("HEAD", url, false); // Vérifie l'existence en mode synchrone
            http.send();
            return http.status === 200; // Retourne vrai si l'image existe
        }
        

        // Ajouter la logique des boutons
        let currentIndex = 0;
        const leftBtn = sliderContainer.querySelector(".left-btn");
        const rightBtn = sliderContainer.querySelector(".right-btn");

        const updateSlider = () => {
            const slideWidth = sliderTrack.children[0].offsetWidth + 20; // Largeur d'un élément + marge
            sliderTrack.style.transform = `translateX(-${currentIndex * slideWidth}px)`;
        };

        leftBtn.addEventListener("click", () => {
            if (currentIndex > 0) {
                currentIndex--;
                updateSlider();
            }
        });

        rightBtn.addEventListener("click", () => {
            if (currentIndex < films.length - 3) {
                currentIndex++;
                updateSlider();
            }
        });

        return sliderContainer;
    };
});
