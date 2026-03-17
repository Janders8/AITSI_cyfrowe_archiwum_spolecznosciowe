<script>
    // Główny komponent aplikacji frontendowej.
    // Wyświetla pasek nawigacji, obsługuje logowanie Google i przełączanie widoków (Galeria / Panel Twórcy).
    // Łączy ze sobą filtry z Wyszukiwarki i Mapy i przekazuje je do Galerii.

    // Importowanie bibliotek i pamięci globalnej
    import { onMount } from "svelte";
    import { tokenJWT, rolaUzytkownika, emailUzytkownika } from "./store.js";
    import Galeria from "./Galeria.svelte";
    import PanelZarzadzania from "./PanelZarzadzania.svelte";
    import Wyszukiwarka from "./Wyszukiwarka.svelte";
    import Mapa from "./Mapa.svelte";
    import MotywyWCAG from "./MotywyWCAG.svelte";

    let nazwaStrony = "Cyfrowe Archiwum Społecznościowe";

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

    // Callback przechwytujący wywołanie funkcji przez Wyszukiwarkę
    function obslugujZmianeFiltrow(nowePolaFiltracyjnie) {
        // Łączenie filtrów tekstowych z filtrami współrzędnych
        aktywneFiltry = { ...aktywneFiltry, ...nowePolaFiltracyjnie };
    }

    // Callback przechwytujący wywołanie od mapy z jej obszarem
    function obslugujZmianeMapy(koordynaty) {
        aktywneFiltry = { ...aktywneFiltry, ...koordynaty };
    }

    // Callback przechwytujący od galerii przefiltrowaną listę zdjęć pobranych z BD
    function obslugujPobraneMaterialy(materialy) {
        pobraneMaterialy = materialy;
    }

    // Funkcja od zmiany zakładek w HTML
    function zmienStrone(nowaStrona) {
        aktywnaStrona = nowaStrona;
    }

    // Klucz google id do logowania, pobierany z pliku konfiguracyjnego .env
    const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID;

    function rysujPrzyciskGoogle() {
        // Funkcja będzie co 100 milisekund sprawdzać, czy skrypt Google zdążył się już wgrać
        const probaRenderowania = setInterval(() => {
            const pojemnik = document.getElementById("googleButtonContainer");
            if (window["google"] && pojemnik) {
                // Zatrzymanie licznika po wyrenderowaniu przycisku
                clearInterval(probaRenderowania);

                // Konfiguracja panelu logowania Google
                window["google"].accounts.id.initialize({
                    client_id: GOOGLE_CLIENT_ID,
                    callback: obslugaLogowaniaGoogle,
                });

                // Wyczyść pojemnik HTML po wylogowaniu
                pojemnik.innerHTML = "";

                // Generowanie przycisku wewnątrz diva
                window["google"].accounts.id.renderButton(pojemnik, {
                    theme: "outline",
                    size: "large",
                    text: "signin_with",
                });
            }
        }, 100); // próbuj co 0.1s
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

                // Odkodowanie tokena, by wyświetlić na pasku Imię i Rolę
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

    // Funkcja Wyloguj, po prostu czyści zmienne
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

<!-- Pasek nawigacyjny -->
<nav class="navbar navbar-dark bg-dark mb-4">
    <div class="container d-flex align-items-center">
        <a class="navbar-brand" href="/">{nazwaStrony}</a>
        <ul class="navbar-nav d-flex flex-row me-auto gap-3">
            <li class="nav-item">
                <!-- Klasa 'active' pogrubia tekst aktywnej zakładki -->
                <a
                    class="nav-link {aktywnaStrona === 'galeria'
                        ? 'active'
                        : ''}"
                    href="/#galeria"
                    on:click|preventDefault={() => zmienStrone("galeria")}
                >
                    Kolekcja Zdjęć
                </a>
            </li>
            <li class="nav-item">
                <a
                    class="nav-link {aktywnaStrona === 'tworca'
                        ? 'active'
                        : ''}"
                    href="/#tworca"
                    on:click|preventDefault={() => zmienStrone("tworca")}
                >
                    Panel Twórcy / Admina
                </a>
            </li>
        </ul>

        <!-- Dodany na pasku przycisku zmiany motywu -->
        <MotywyWCAG />

        <span class="navbar-text">
            <!-- Wyświetlanieinformacji o zalogowanym użytkowniku lub przycisku do zalogowania -->
            {#if $tokenJWT}
                <!-- Użytkownik jest zalogowany -->
                <span class="me-3 text-light"
                    >Zalogowany(a): <strong
                        >{$emailUzytkownika} ({$rolaUzytkownika})</strong
                    ></span
                >
                <button class="btn btn-sm btn-outline-light" on:click={wyloguj}
                    >Wyloguj</button
                >
            {:else}
                <!-- Jeśli nie, wyświetl pojemnik na przycisk Google -->
                <div id="googleButtonContainer"></div>
            {/if}
        </span>
    </div>
</nav>

<main class="container mb-5">
    <div class="row mt-4 mb-3">
        <div class="col-12">
            <h1 class="mb-3">Najnowsze materiały w zbiorach</h1>
            <p class="text-muted">
                Przeglądaj zebrane fotografie i dokumenty obrazujące historię
                okolicy.
            </p>
        </div>
    </div>

    <!-- Wyświetlanie odpowiedniej strony -->
    {#if aktywnaStrona === "galeria"}
        <!-- Mapa Leaflet -->
        <Mapa poZmianieMapy={obslugujZmianeMapy} materialy={pobraneMaterialy} />

        <!-- Wyszukiwarka -->
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
