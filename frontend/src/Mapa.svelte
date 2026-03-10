<script>
    import { onMount } from "svelte";

    // Miejsce na funkcję od która informuje o zmianie współrzędnych mapy modół główny
    export let poZmianieMapy = (koordynaty) => {};

    // Lista zdjęć z API do wyświetlenia na mapie
    export let materialy = [];

    // Referencja do div'a w HTML, wewnątrz którego umieszczona zostanie mapa
    let divMiejscNaMape;

    // Zmienna przechowująca obiekt z kodem mapy
    let instancjaMapy;

    // Grupa znaczników
    let warstwaMarkerow;

    // Początkowe współrzędne mapy
    const startLat = 52.23;
    const startLng = 21.01;
    const startZoom = 13;

    onMount(() => {
        // Tworzenie instancji mapy
        instancjaMapy = window.L.map(divMiejscNaMape).setView(
            [startLat, startLng],
            startZoom,
        );

        // Podkład mapy, wybrano darmowy OpenStreetMap
        window.L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
            maxZoom: 19,
            attribution:
                '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        }).addTo(instancjaMapy);

        // Stworzenie pustej warstwy pinesek
        warstwaMarkerow = window.L.layerGroup().addTo(instancjaMapy);

        // Kiedy użytkownik skończy przesuwać mapę
        instancjaMapy.on("moveend", () => {
            // Pobranie aktualnych krawędzi okna mapy (Bounding Box)
            const graniceMapy = instancjaMapy.getBounds();

            // Przekazanie współrzędnych do modułu głównego
            poZmianieMapy({
                min_lat: graniceMapy.getSouth(),
                max_lat: graniceMapy.getNorth(),
                min_lng: graniceMapy.getWest(),
                max_lng: graniceMapy.getEast(),
            });
        });

        // Wysłanie wstępnych koordynatów obszarowych na start
        const graniceStartowe = instancjaMapy.getBounds();
        poZmianieMapy({
            min_lat: graniceStartowe.getSouth(),
            max_lat: graniceStartowe.getNorth(),
            min_lng: graniceStartowe.getWest(),
            max_lng: graniceStartowe.getEast(),
        });
    });

    // Ten kod wywoła się sam zawsze kiedy podmienione zostaną materiały
    $: if (warstwaMarkerow && materialy) {
        // Zdejmij wszystkie stare pineski
        warstwaMarkerow.clearLayers();

        // Pętla przez listę nowych materiałów wyświetlanych na mapie
        materialy.forEach((material) => {
            // Tylko te z lokalizacją
            if (material.location_lat && material.location_lng) {
                // Rysowanie markera z pozycją
                const znacznik = window.L.marker([
                    material.location_lat,
                    material.location_lng,
                ]);

                // Generowanie Miniaturkę Popupową widoczną po kliknięciu
                const okienkoHTML = `
                    <div style="text-align: center; max-width: 150px;">
                        <img src="http://localhost:8000/uploads/${material.filename}" alt="${material.title}" style="width: 100%; border-radius: 4px; margin-bottom: 5px;" />
                        <b>${material.title}</b><br/>
                        <span style="font-size: 0.8em; color: gray;">${material.category}</span>
                    </div>
                `;

                // Dodawanie chmurki do warstwy Pinezek
                znacznik.bindPopup(okienkoHTML).addTo(warstwaMarkerow);
            }
        });
    }
</script>

<!-- Kontener dla mapy -->
<div class="card shadow-sm mb-4">
    <div class="card-header">
        <h5 class="card-title fw-bold m-0">
            Wyszukiwanie Współrzędnych Przestrzenne
        </h5>
    </div>
    <div class="card-body p-0">
        <!-- Leaflet potrzebuje, aby div miał określoną z góry wysokość, inaczej
          mapa zniknie z ekranu (minimum 400 pikseli) -->
        <div
            bind:this={divMiejscNaMape}
            style="height: 400px; width: 100%; z-index: 1;"
        ></div>
    </div>
    <div class="card-footer text-muted small">
        Przesuń mapę i oddal by wyszukać okoliczne archiwa (Zasięg automatyczny)
    </div>
</div>
