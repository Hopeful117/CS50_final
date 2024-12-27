function dark_mode() {
    const Toogle_button = document.querySelectorAll("input.checkbox");
    const Statuses = document.querySelectorAll(".status");
    const top = document.getElementById("top");
    const nav_bar = document.querySelectorAll("a.nav-link");
    const duck = document.getElementById("duck");
    const bottom= document.getElementById("bottom");
    const h2 = document.querySelectorAll("h2");
    const body = document.querySelector("body");
    const lessontitle = document.querySelectorAll(".lesson-title");
    const words = document.querySelectorAll("h2.word");

 
    // Fonction pour appliquer le mode sombre ou clair
    function applyMode(isDarkMode) {
        if (isDarkMode) {
            top.style.backgroundColor = "Black";
            top.style.color = "White";
            duck.src = darkDuckUrl;
            bottom.style.color="White";
            body.style.background="Black"
            nav_bar.forEach((nav) => {
                nav.style.color = "White";
            });
            Statuses.forEach((status) => {
                status.innerHTML = "Dark Mode";
            
            });
            h2.forEach((title)=>{
                title.style.color ="White";
            });

            lessontitle.forEach((lesson)=>{
                lesson.style.color="White";
            });

            words.forEach((word)=>{
                word.style.color="Black";
                console.log("debug")
            });


           
        } else {
            top.style.backgroundColor = "White";
            top.style.color = "Black";
            duck.src = lightDuckUrl;
            bottom.style.color="Black";
            body.style.background='linear-gradient(90deg, rgba(0,80,242,1) 0%, rgba(255,255,255,1) 49%, rgba(255,0,0,1) 100%)'
            nav_bar.forEach((nav) => {
                nav.style.color = "Black";
            });
            Statuses.forEach((status) => {
                status.innerHTML = "Light Mode";
            });
            h2.forEach((title)=>{
                title.style.color ="Black";
            });

            lessontitle.forEach((lesson)=>{
                lesson.style.color="Black";
            });

        }
    }

    // Charger le mode sombre depuis localStorage
    const savedMode = localStorage.getItem("darkMode") === "true";
    applyMode(savedMode);
    Toogle_button.forEach((button) => {
        button.checked = savedMode; // Synchroniser l'état des boutons
    });

    // Ajouter un événement pour enregistrer les changements
    Toogle_button.forEach((button) => {
        button.addEventListener("change", (event) => {
            const isDarkMode = event.target.checked;
            applyMode(isDarkMode);
            localStorage.setItem("darkMode", isDarkMode); // Enregistrer dans localStorage
        });
    });
}

dark_mode();
