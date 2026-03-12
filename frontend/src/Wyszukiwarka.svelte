<script>
    // Formularz do filtrowania zdjęć po frazie, kategorii i okresie historycznym.
    // Po zatwierdzeniu przekazuje wybrane filtry do komponentu App.svelte.

    // Miejsce na funkcję przekazaną z zewnątrz, służy do zgłaszania zmian filtrów
    export let poZmianieFiltru = (_filtry) => {};

    // Zmienne formularza filtrującego
    let search = "";
    let category = "";
    let historical_period = "";

    // Funkcja wywoływana, gdy użytkownik zatwierdzi formularz wyszukiwania
    function wyszukaj(event) {
        // Zapobieganie domyślnemu odświeżaniu całej strony
        event.preventDefault();

        // Wywołanie funkcji przekazanej z zewnątrz, z nowymi wartościami
        poZmianieFiltru({
            search: search,
            category: category,
            historical_period: historical_period,
        });
    }

    // Funkcja resetująca pola i zgłaszająca wyczyszczenie
    function wyczysc() {
        search = "";
        category = "";
        historical_period = "";

        // Puste wartości, prośba o całą galerię
        poZmianieFiltru({
            search: "",
            category: "",
            historical_period: "",
        });
    }
</script>

<div class="card shadow-sm mb-4">
    <div class="card-body">
        <h2 class="card-title fw-bold mb-3">Wyszukiwarka w Archiwum</h2>

        <!-- Główny Formularz z filtrami. Po wysłaniu uruchamia funkcję wyszukaj() -->
        <form on:submit={wyszukaj} class="row g-3">
            <!-- Wyszukiwanie w Tytule/Opisie -->
            <div class="col-md-5">
                <label for="szukanaFraza" class="form-label text-muted small"
                    >Szukana fraza</label
                >
                <input
                    type="text"
                    id="szukanaFraza"
                    class="form-control"
                    placeholder="Wpisz słowo kluczowe np. Kościół..."
                    bind:value={search}
                />
            </div>

            <!-- Rozwijana lista -->
            <div class="col-md-3">
                <label for="kategoriaSelect" class="form-label text-muted small"
                    >Kategoria</label
                >
                <select
                    id="kategoriaSelect"
                    class="form-select"
                    bind:value={category}
                >
                    <!-- Pusta kategoria traktowana jest jako podanie wszystkich wyników -->

                    <!-- Przy rzowoju projektu wypadałoby zrobić te kategorie dynamicznie, 
                    na podstawie dostępnych kategorii w API -->
                    <option value="">Wszystkie</option>
                    <option value="/Architektura/"
                        >-- Cała Architektura --</option
                    >
                    <option value="/Architektura/Sakralna/"
                        >1. Budynki Sakralne (Wszystkie)</option
                    >
                    <option value="/Architektura/Sakralna/Koscioly/"
                        >-- 1.1 Kościoły</option
                    >
                    <option value="/Architektura/Sakralna/Synagogi/"
                        >-- 1.2 Synagogi</option
                    >
                    <option value="/Architektura/Mieszkalna/"
                        >2. Budynki Mieszkalne (Wszystkie)</option
                    >
                    <option value="/Architektura/Mieszkalna/Kamienice/"
                        >-- 2.1 Kamienice</option
                    >
                    <option value="/Architektura/Mieszkalna/Bloki/"
                        >-- 2.2 Bloki Osiedlowe</option
                    >
                    <option value="/Architektura/Uzytecznosci_Publicznej/"
                        >3. Użyteczność Publiczna</option
                    >
                    <option value="/Architektura/Przemyslowa/"
                        >4. Architektura Przemysłowa</option
                    >
                </select>
            </div>

            <!-- Okres historyczny -->
            <div class="col-md-4">
                <label for="okresCzasu" class="form-label text-muted small"
                    >Okres Historyczny</label
                >
                <input
                    type="text"
                    id="okresCzasu"
                    class="form-control"
                    placeholder="np. Lata 90."
                    bind:value={historical_period}
                />
            </div>

            <!-- Przyciski wyszukiwarki -->
            <div class="col-12 d-flex justify-content-end gap-2 mt-3">
                <button
                    type="button"
                    class="btn btn-secondary"
                    on:click={wyczysc}>Wyczyść Filtry</button
                >
                <button
                    type="submit"
                    class="btn btn-primary d-flex align-items-center"
                >
                    Zastosuj filtry
                </button>
            </div>
        </form>
    </div>
</div>
