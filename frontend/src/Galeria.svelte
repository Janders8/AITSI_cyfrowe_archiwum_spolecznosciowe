<script>
    import { onMount } from "svelte";

    // Zmienna przechowująca pobrane zdjęcia z backendu
    let materialy = [];
    // Zmienna do obsługi ładowania
    let laduje = true;
    // Zmienna na ewentualne błędy przy pobieraniu
    let blad = null;

    // Wstrzyknięty "Prop" z wyższego komponentu (App.svelte)
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
            // Obiekt URL (punkt startowy API dla zasobów publicznych)
            const url = new URL("http://localhost:8000/materials/");

            // Doklejanie Parametrów do uderzenia do backendu
            // Np. zamieni słownik w "?search=Kosciol&category=Fotografia"
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
                // Konwersja by uniknąć błędów ułamków URL
                url.searchParams.append("min_lat", filtryPowiazane.min_lat);
                url.searchParams.append("max_lat", filtryPowiazane.max_lat);
                url.searchParams.append("min_lng", filtryPowiazane.min_lng);
                url.searchParams.append("max_lng", filtryPowiazane.max_lng);
            }

            // Właściwy Fetch pod wygenerowany z filtrów adres
            const odpowiedz = await fetch(url);

            if (!odpowiedz.ok) {
                // Jeżeli serwer odda 404
                if (odpowiedz.status === 404) {
                    materialy = [];
                    poPobraniuMaterialow([]);
                    // Return zatrzymuje dalsze przetwarzanie
                    return;
                }
                throw new Error(
                    "Wystąpił zewnętrzny błąd serwera przy pobieraniu zdjęć",
                );
            }

            // Rozpakowanie nadesłanej Listy w formacie Json
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

<div class="row row-cols-1 row-cols-md-3 g-4">
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
                Brak zdjęć w archiwach!
            </div>
        </div>
    {:else}
        <!-- Pętla po wszystkich zdjęciach -->
        {#each materialy as material}
            <div class="col">
                <div class="card h-100 shadow-sm">
                    <!-- Ładowanie obrazu z folderu uploads -->
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
                        <h5 class="card-title">{material.title}</h5>
                        <!-- Zadbanie by nie wyświetlało pustego podpisu -->
                        {#if material.description}
                            <p class="card-text text-truncate">
                                {material.description}
                            </p>
                        {/if}
                    </div>
                    <div class="card-footer bg-transparent">
                        <small class="text-body-secondary">
                            {material.category}
                        </small>
                    </div>
                </div>
            </div>
        {/each}
    {/if}
</div>
