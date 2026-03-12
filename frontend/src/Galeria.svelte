<script>
    // Komponent odpowiedzialny za wyświetlanie zdjęć z bazy na stronie głównej.
    // Pobiera materiały z API na podstawie filtrów (tekst, kategoria, współrzędne mapy)
    // i rysuje je w formie grida.

    import { onMount } from "svelte";

    // Zmienna przechowująca pobrane zdjęcia z backendu
    let materialy = [];
    // Zmienna do obsługi ładowania
    let laduje = true;
    // Zmienna na ewentualne błędy przy pobieraniu
    let blad = null;

    // Prop z App.svelte
    export let aktywneFiltry = {
        search: "",
        category: "",
        historical_period: "",
    };

    // Callback by poinformować jakie materiały wyciągnięto z bazy
    export let poPobraniuMaterialow = (mat) => {};

    // Funkcja pobierająca, podmieniona na bycie niezależną
    async function pobierzZdjecia(filtryPowiazane) {
        // Reset stanów
        laduje = true;
        blad = null;

        try {
            // URL do API
            const url = new URL("http://localhost:8000/materials/");

            // Dodanie parametrów do URL
            if (filtryPowiazane.search)
                url.searchParams.append("search", filtryPowiazane.search);
            if (filtryPowiazane.category)
                url.searchParams.append("category", filtryPowiazane.category);
            if (filtryPowiazane.historical_period)
                url.searchParams.append(
                    "historical_period",
                    filtryPowiazane.historical_period,
                );

            // Filtr współrzędnych
            if (
                filtryPowiazane.min_lat !== undefined &&
                filtryPowiazane.min_lat !== null
            ) {
                // Konwersja by uniknąć błędów ułamków w URL
                url.searchParams.append("min_lat", filtryPowiazane.min_lat);
                url.searchParams.append("max_lat", filtryPowiazane.max_lat);
                url.searchParams.append("min_lng", filtryPowiazane.min_lng);
                url.searchParams.append("max_lng", filtryPowiazane.max_lng);
            }

            // Zapytanie do API
            const odpowiedz = await fetch(url);

            if (!odpowiedz.ok) {
                // Jeżeli serwer odda 404
                if (odpowiedz.status === 404) {
                    materialy = [];
                    poPobraniuMaterialow([]);

                    return;
                }
                throw new Error("Wystąpił błąd serwera przy pobieraniu zdjęć");
            }

            // Odpakowanie listy zdjęć
            materialy = await odpowiedz.json();
            poPobraniuMaterialow(materialy);
        } catch (error) {
            blad = error.message;
        } finally {
            laduje = false;
        }
    }

    // Obserwator zmian w filtrach
    $: pobierzZdjecia(aktywneFiltry);
</script>

<div class="row row-cols-3 g-4">
    {#if laduje}
        <div class="col-12 text-center">
            <!-- Spinner reprezentujący ładowanie -->
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Ładowanie...</span>
            </div>
        </div>
    {:else if blad}
        <div class="col-12">
            <div class="alert alert-danger" role="alert">
                {blad}
            </div>
        </div>
    {:else if materialy.length === 0}
        <div class="col-12">
            <div class="alert alert-info" role="alert">
                Brak zdjęć z podanymi kryteriami.
            </div>
        </div>
    {:else}
        <!-- Pętla po wszystkich zdjęciach -->
        {#each materialy as material}
            <div class="col">
                <div class="card h-100 shadow-sm">
                    <!-- Ładowanie zdjęcia z folderu uploads -->
                    {#if material.filename}
                        <img
                            src={`http://localhost:8000/uploads/${material.filename}`}
                            class="card-img-top object-fit-cover"
                            alt={`Karta materiału: ${material.title}`}
                            style="height: 250px;"
                        />
                    {:else}
                        <!-- Na wypadek braku zdjęcia -->
                        <div
                            class="bg-secondary text-white text-center py-5 d-flex align-items-center justify-content-center"
                            style="height: 250px;"
                        >
                            [Brak Zdjęcia]
                        </div>
                    {/if}
                    <div class="card-body">
                        <h3 class="card-title h5">{material.title}</h3>
                        <!-- Zadbanie by nie wyświetlało pustego podpisu -->
                        {#if material.description}
                            <p class="card-text text-truncate">
                                {material.description}
                            </p>
                        {/if}
                    </div>
                    <div
                        class="card-footer bg-transparent d-flex justify-content-between align-items-center"
                    >
                        <small class="text-body-secondary">
                            {material.category}
                        </small>
                        {#if material.historical_period}
                            <span class="badge rounded-pill bg-info text-dark">
                                {material.historical_period}
                            </span>
                        {/if}
                    </div>
                </div>
            </div>
        {/each}
    {/if}
</div>
