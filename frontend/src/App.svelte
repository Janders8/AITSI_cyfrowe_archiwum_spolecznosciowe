<script>
    // Importowanie bibliotek i pamięci globalnej aplikacji
    import { onMount } from "svelte";
    import { tokenJWT, rolaUzytkownika, emailUzytkownika } from "./store.js";
    import Galeria from "./Galeria.svelte";
    import PanelZarzadzania from "./PanelZarzadzania.svelte";
    import Wyszukiwarka from "./Wyszukiwarka.svelte";
    import Mapa from "./Mapa.svelte";
    import MotywyWCAG from "./MotywyWCAG.svelte";

    let imieProjektu = "Cyfrowe Archiwum Społecznościowe";

    // Zmienna przechowująca informację, w której zakładce obecnie znajduje się strona
    let aktywnaStrona = "galeria";

    // Stan filtrów, domyślnie puste
    let aktywneFiltry = {
        search: "",
        category: "",
        historical_period: "",
        min_lat: null,
        max_lat: null,
        min_lng: null,
        max_lng: null,
    };

    // Zmienna przechowująca materiały pobrane przez galerię do pokazania na mapie
    let pobraneMaterialy = [];

    // Zmiana filtrów od Wyszukiwarki
    function obslugujZmianeFiltrow(nowePolaFiltracyjnie) {
        // Łączenie filtrów tekstowych z filtrami współrzędnych
        aktywneFiltry = { ...aktywneFiltry, ...nowePolaFiltracyjnie };
    }

    // Aktualizacja obszaru z Mapy
    function obslugujZmianeMapy(koordynaty) {
        aktywneFiltry = { ...aktywneFiltry, ...koordynaty };
    }

    // Odbiór listy zdjęć od komponentu Galerii
    function obslugujPobraneMaterialy(materialy) {
        pobraneMaterialy = materialy;
    }

    // Funkcja ułatwiająca zmianę zakładek w HTML
    function zmienStrone(nowaStrona) {
        aktywnaStrona = nowaStrona;
    }

    // Klucz google id do logowania, pobierany z pliku konfiguracyjnego .env
    const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID;

    function rysujPrzyciskGoogle() {
        // Funkcja będzie co 100 milisekund sprawdzać, czy skrypt Google zdążył się już wgrać
        const probaRenderowania = setInterval(() => {
            const pojemnik = document.getElementById("googleButtonContainer");
            if (window.google && pojemnik) {
                // Zatrzymanie licznika po wyrenderowaniu przycisku
                clearInterval(probaRenderowania);

                // Konfiguracja panelu logowania Google
                window.google.accounts.id.initialize({
                    client_id: GOOGLE_CLIENT_ID,
                    callback: obslugaLogowaniaGoogle,
                });

                // Wyczyść pojemnik HTML po wylogowaniu
                pojemnik.innerHTML = "";

                // Generowanie przycisku wewnątrz div
                window.google.accounts.id.renderButton(pojemnik, {
                    theme: "outline",
                    size: "large",
                    text: "signin_with",
                });
            }
        }, 100); // próbuj co 0.1s aż się uda, po czym przestań.
    }

    onMount(() => {
        rysujPrzyciskGoogle();
    });

    // Funkcja odbierająca token z serwerów Google
    async function obslugaLogowaniaGoogle(googleResponse) {
        try {
            // Przekazanie tokenu do API
            const odpowiedz = await fetch("http://localhost:8000/auth/google", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ credential: googleResponse.credential }),
            });

            if (odpowiedz.ok) {
                const dane_z_backendu = await odpowiedz.json();

                // Zapis tokenu JWT do pamięci aplikacji
                $tokenJWT = dane_z_backendu.access_token;

                // Odkodowanie tokena z użyciem atob(), by wyświetlić na pasku Imię i Rolę
                const rozkodowane = JSON.parse(atob($tokenJWT.split(".")[1]));
                $emailUzytkownika = rozkodowane.sub;
                $rolaUzytkownika = rozkodowane.role;

                alert(
                    `Zalogowano jako: ${$emailUzytkownika} (Rola: ${$rolaUzytkownika})`,
                );
            } else {
                const b = await odpowiedz.json();
                alert(`Odmowa dostępu przez Archiwum: ${b.detail}`);
            }
        } catch (blad) {
            alert(`Błąd sieci z weryfikacją: ${blad}`);
        }
    }

    // Funkcja Wyloguj, po prostu czyści klucze
    function wyloguj() {
        $tokenJWT = null;
        $rolaUzytkownika = "Przeglądający";
        $emailUzytkownika = "";
        // Zmiana strony na galerię (dla bezpieczeństwa)
        aktywnaStrona = "galeria";

        // Ponowne wyrenderowanie przycisku zaloguj
        // 50ms opóźnienia jest by div na przycisk zdążył się pojawić
        setTimeout(rysujPrzyciskGoogle, 50);
    }
</script>

<!-- Pasek nawigacyjny u góry strony -->
<nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
    <div class="container">
        <a class="navbar-brand" href="#">{imieProjektu}</a>
        <button
            class="navbar-toggler"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#navbarText"
            aria-controls="navbarText"
            aria-expanded="false"
            aria-label="Przełącz nawigację"
        >
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarText">
            <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                <li class="nav-item">
                    <!-- Klasa 'active' pogrubia tekst aktywnej zakładki -->
                    <a
                        class="nav-link {aktywnaStrona === 'galeria'
                            ? 'active'
                            : ''}"
                        href="#"
                        on:click={() => zmienStrone("galeria")}
                    >
                        Kolekcja Zdjęć
                    </a>
                </li>
                <li class="nav-item">
                    <a
                        class="nav-link {aktywnaStrona === 'tworca'
                            ? 'active'
                            : ''}"
                        href="#"
                        on:click={() => zmienStrone("tworca")}
                    >
                        Panel Twórcy / Admina
                    </a>
                </li>
            </ul>

            <!-- Dodany na pasku przycisku zmiany motywu -->
            <MotywyWCAG />

            <span class="navbar-text">
                <!-- Logika Wyświetlania Profilu w Svelte -->
                {#if $tokenJWT}
                    <!-- Użytkownik jest zalogowany -->
                    <span class="me-3 text-light"
                        >Zalogowany(a): <strong
                            >{$emailUzytkownika} ({$rolaUzytkownika})</strong
                        ></span
                    >
                    <button
                        class="btn btn-sm btn-outline-light"
                        on:click={wyloguj}>Wyloguj</button
                    >
                {:else}
                    <!-- Jeśli nie, wyświetl pusty pojemnik na guzik Google -->
                    <div id="googleButtonContainer"></div>
                {/if}
            </span>
        </div>
    </div>
</nav>

<main class="container mb-5">
    <div class="row mt-4 mb-3">
        <div class="col-12">
            <h2 class="mb-3">Najnowsze materiały w zbiorach</h2>
            <p class="text-muted">
                Przeglądaj zebrane fotografie i dokumenty obrazujące historię
                okolicy.
            </p>
        </div>
    </div>

    <!-- Warunek by wyświetlać odpowiednią stronę -->
    {#if aktywnaStrona === "galeria"}
        <!-- Interaktywna mapa Leaflet -->
        <Mapa poZmianieMapy={obslugujZmianeMapy} materialy={pobraneMaterialy} />

        <!-- Przesłanie funkcji do komponentu Wyszukiwarka -->
        <Wyszukiwarka poZmianieFiltru={obslugujZmianeFiltrow} />

        <Galeria
            {aktywneFiltry}
            poPobraniuMaterialow={obslugujPobraneMaterialy}
        />
    {:else if aktywnaStrona === "tworca"}
        <div class="row">
            <div class="col-12">
                <!-- Zabezpieczenie panelu Twórcy -->
                {#if $rolaUzytkownika === "Twórca" || $rolaUzytkownika === "Administrator"}
                    <PanelZarzadzania />
                {:else}
                    <div class="alert alert-warning text-center mt-5 shadow-sm">
                        <h4>Odmowa dostępu</h4>
                        <p>
                            Musisz zalogować się jako Twórca lub Administrator
                            używając konta Google na pasku nawigacji, by uzyskać
                            dostęp do panelu przesyłania.
                        </p>
                    </div>
                {/if}
            </div>
        </div>
    {/if}
</main>
