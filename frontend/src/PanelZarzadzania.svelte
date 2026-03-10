<script>
    import { onMount } from "svelte";
    import { tokenJWT, rolaUzytkownika } from "./store.js";

    // Komponent do dodawania i edycji materiałów przez Twórcę

    // ================= Zmienne stanu =================

    let tytul = "";
    let opis = "";
    let kategoria = "";
    let okres = "";
    let lat = "";
    let lng = "";
    let plik = null;

    let aktywnaZakladka = "dodaj";
    let mojeMaterialy = [];

    // Zmienna przechowująca ID materiału, który jest edytowany
    let edytowanyMaterialId = null;
    let edycjaTytul = "";
    let edycjaKategoria = "";
    let edycjaOpis = "";
    let edycjaOkres = "";

    // ================= Zmienne przechowujące dane =================

    // Funkcja wywoływana przy wyborze zdjęcia z dysku
    function obslugaPliku(event) {
        plik = event.target.files[0];
    }

    // Funkcja obsługująca kliknięcie "Wyślij" pod formularzem "Dodaj"
    async function wyslijFormularz(event) {
        // Żeby formularz nie odświeżał całej strony
        event.preventDefault();

        // Pakowanie pliku i danych przez zwykły FormData
        const formularzData = new FormData();

        formularzData.append("title", tytul);
        formularzData.append("category", kategoria);
        if (opis) formularzData.append("description", opis);
        if (okres) formularzData.append("historical_period", okres);
        if (lat) formularzData.append("location_lat", lat);
        if (lng) formularzData.append("location_lng", lng);
        formularzData.append("file", plik);

        try {
            // Polecenie POST do API
            const odpowiedz = await fetch("http://localhost:8000/materials/", {
                method: "POST",
                headers: {
                    // Token JWT od zalogowanego użytkownika
                    Authorization: `Bearer ${$tokenJWT}`,
                },
                body: formularzData,
            });

            // Sprawdzenie dopowiedzi
            if (odpowiedz.ok) {
                alert("Sukces! Materiał dodano do Archiwum.");
                // Resetowanie wartości formularza
                tytul = "";
                opis = "";
                okres = "";
                lat = "";
                lng = "";
                plik = null;
                // Odświeżenie listy, żeby nowy plik sie na niej pojawił
                pobierzMojeMaterialy();
            } else {
                // Komunikat błędu z backendu
                const blad = await odpowiedz.json();
                alert(`Odrzucono! Backend mówi: ${blad.detail}`);
            }
        } catch (error) {
            alert(`Wystąpił problem z połączeniem: ${error.message}`);
        }
    }

    // ================= Funkcje od pobierania i zarządzania materiałami =================

    // Funkcja pobierająca materiały zalogowanego twórcy
    async function pobierzMojeMaterialy() {
        if (!$tokenJWT) return; // Sprawdzenie tokena

        try {
            // URL zależy od roli - Twórca pobiera tylko swoje, Admin pobiera wszystkie z bazy danych
            const endpointUrl =
                $rolaUzytkownika === "Administrator"
                    ? "http://localhost:8000/materials/?limit=500" // TODO: jaki dać limit i czy dawać?
                    : "http://localhost:8000/materials/my";

            // Pobranie materiałów z API
            const odpowiedz = await fetch(endpointUrl, {
                method: "GET",
                headers: {
                    Authorization: `Bearer ${$tokenJWT}`,
                },
            });

            if (odpowiedz.ok) {
                // Przypisanie pobranej jsonowej tablicy ze zdjęciami do zmiennej
                mojeMaterialy = await odpowiedz.json();
            } else {
                console.error("Błąd podczas pobierania materiałów użytkownika");
            }
        } catch (error) {
            console.error("Błąd sieci", error);
        }
    }

    // Wywołanie pobierania zaraz po stworzeniu tego panelu
    onMount(() => {
        pobierzMojeMaterialy();
    });

    // Funkcja do usuwania autorskich wpisów bez przeładowania strony
    async function usunMaterial(id) {
        if (
            !confirm(
                "Czy na pewno chcesz na stałe usunąć to zdjęcie ze swojego archiwum?",
            )
        )
            return;

        try {
            const odpowiedz = await fetch(
                `http://localhost:8000/materials/${id}`,
                {
                    method: "DELETE",
                    headers: {
                        Authorization: `Bearer ${$tokenJWT}`,
                    },
                },
            );

            if (odpowiedz.ok) {
                // Usunięcie wpisu ze stanu
                mojeMaterialy = mojeMaterialy.filter((m) => m.id !== id);
                alert("Zdjęcie zostało usunięte z systemu!");
            } else {
                const blad = await odpowiedz.json();
                alert(`Odrzucono próbę usunięcia: ${blad.detail}`);
            }
        } catch (error) {
            alert(`Błąd połączenia: ${error.message}`);
        }
    }

    // ================= Funkcje od edycji materiałów =================

    // Otwiera mały formularz do wpisywania poprawek pod zdjęciem
    function zacznijEdycje(material) {
        edytowanyMaterialId = material.id;
        edycjaTytul = material.title;
        edycjaKategoria = material.category;
        edycjaOpis = material.description || "";
        edycjaOkres = material.historical_period || "";
    }

    function anulujEdycje() {
        // Zamknięcie małego formularza
        edytowanyMaterialId = null;
    }

    // Funkcja do fizycznego wysyłania zmian przez twórcę (same dane tekstowe).
    async function zapiszEdycje(id) {
        // Przygotowujemy zwykły obiekt JSON
        const noweDane = {
            title: edycjaTytul,
            category: edycjaKategoria,
            description: edycjaOpis,
            historical_period: edycjaOkres,
        };

        try {
            const odpowiedz = await fetch(
                `http://localhost:8000/materials/${id}`,
                {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${$tokenJWT}`,
                    },
                    body: JSON.stringify(noweDane),
                },
            );

            if (odpowiedz.ok) {
                const zaktualizowanyMaterial = await odpowiedz.json();
                // Odświeżenia widoku po przez nadpisanie starego wpisu nowym
                const index = mojeMaterialy.findIndex((m) => m.id === id);
                if (index !== -1) {
                    mojeMaterialy[index] = zaktualizowanyMaterial;
                }
                // Zamknięcie podglądu
                edytowanyMaterialId = null;
                alert("Zmiany w materiale zostały poprawie zapisane!");
            } else {
                const blad = await odpowiedz.json();
                alert("Błąd edycji: " + blad.detail);
            }
        } catch (error) {
            alert("Błąd połączenia: " + error.message);
        }
    }

    // ================= Funkcje administratora =================

    // Funkcja do blokowania użytkownika przez admina
    async function zablokujUzytkownika(userId) {
        if (
            !confirm("Ostrzeżenie! Czy na pewno chcesz zablokować użytkownika?")
        )
            return;

        try {
            const odpowiedz = await fetch(
                `http://localhost:8000/users/${userId}/block`,
                {
                    method: "PATCH",
                    headers: {
                        Authorization: `Bearer ${$tokenJWT}`,
                    },
                },
            );

            if (odpowiedz.ok) {
                alert("Konto zostało pomyślnie zablokowane.");
            } else {
                const blad = await odpowiedz.json();
                alert(`Błąd podczas blokowania: ${blad.detail}`);
            }
        } catch (error) {
            alert(`Błąd połączenia przy blokowaniu: ${error.message}`);
        }
    }
</script>

<div class="row justify-content-center mt-4">
    <div class="col-12 col-xl-10">
        <h3 class="mb-4">
            {$rolaUzytkownika === "Administrator"
                ? "Moderacja Cyfrowego Archiwum"
                : "Panel Twórcy Archiwum"}
        </h3>

        <!-- Zakładki Nawigacyjne z wykorzystaniem Bootstrapa 5 -->
        <ul class="nav nav-tabs mb-4">
            <li class="nav-item">
                <button
                    class="nav-link {aktywnaZakladka === 'dodaj'
                        ? 'active fw-bold'
                        : ''}"
                    on:click={() => (aktywnaZakladka = "dodaj")}
                >
                    Dodaj Material
                </button>
            </li>
            <li class="nav-item">
                <button
                    class="nav-link {aktywnaZakladka === 'zarzadzaj'
                        ? 'active fw-bold'
                        : ''}"
                    on:click={() => (aktywnaZakladka = "zarzadzaj")}
                >
                    {$rolaUzytkownika === "Administrator"
                        ? "Moderuj całe archiwum"
                        : "Zarządzaj własnymi zdjęciami"}
                </button>
            </li>
        </ul>

        <!-- Zakładka dodaj-->
        {#if aktywnaZakladka === "dodaj"}
            <div class="card shadow-sm border-0">
                <div class="card-body p-4">
                    <p class="text-muted small mb-4">
                        Wypełnij poniższy formularz, by dodać materiał do bazy
                        Archiwum. Pola z gwiazdką (*) są obowiązkowe.
                    </p>

                    <!-- Główny formularz -->
                    <form on:submit={wyslijFormularz}>
                        <!-- Pole: Tytuł -->
                        <div class="mb-3">
                            <label for="tytul" class="form-label"
                                >Tytuł materiału *</label
                            >
                            <input
                                type="text"
                                class="form-control"
                                id="tytul"
                                bind:value={tytul}
                                required
                                placeholder="np. Stary kościół"
                            />
                        </div>

                        <!-- Pole: Kategoria -->
                        <div class="mb-3">
                            <label for="kategoria" class="form-label"
                                >Kategoria *</label
                            >
                            <select
                                class="form-select"
                                id="kategoria"
                                bind:value={kategoria}
                            >
                                <option value="/Architektura/Sakralna/Koscioly/"
                                    >1.1 Kościoły</option
                                >
                                <option value="/Architektura/Sakralna/Synagogi/"
                                    >1.2 Synagogi</option
                                >
                                <option
                                    value="/Architektura/Mieszkalna/Kamienice/"
                                    >2.1 Kamienice</option
                                >
                                <option value="/Architektura/Mieszkalna/Bloki/"
                                    >2.2 Bloki Osiedlowe</option
                                >
                                <option
                                    value="/Architektura/Uzytecznosci_Publicznej/"
                                    >3. Użyteczność Publiczna</option
                                >
                                <option value="/Architektura/Przemyslowa/"
                                    >4. Obiekty Przemysłowe i Fabryki</option
                                >
                            </select>
                        </div>

                        <!-- Pole: Opis opcjonalny -->
                        <div class="mb-3">
                            <label for="opis" class="form-label"
                                >Szczegółowy opis (Opcjonalnie)</label
                            >
                            <textarea
                                class="form-control"
                                id="opis"
                                rows="3"
                                bind:value={opis}
                                placeholder="Opcjonalny opis zdjęcia"
                            ></textarea>
                        </div>

                        <!-- Pole: Okres Historyczny i Współrzędne  -->
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="okres" class="form-label"
                                    >Okres Historyczny (np. Lata 90.)</label
                                >
                                <input
                                    type="text"
                                    class="form-control"
                                    id="okres"
                                    bind:value={okres}
                                />
                            </div>
                            <div class="col-md-3 mb-3">
                                <label for="lat" class="form-label"
                                    >Szer. Geo. (Lat)</label
                                >
                                <input
                                    type="number"
                                    step="any"
                                    class="form-control"
                                    id="lat"
                                    bind:value={lat}
                                    placeholder="np. 52.23"
                                />
                            </div>
                            <div class="col-md-3 mb-3">
                                <label for="lng" class="form-label"
                                    >Dłg. Geo. (Lng)</label
                                >
                                <input
                                    type="number"
                                    step="any"
                                    class="form-control"
                                    id="lng"
                                    bind:value={lng}
                                    placeholder="np. 21.01"
                                />
                            </div>
                        </div>

                        <!-- Pole: Przesyłanie Pliku -->
                        <div class="mb-4 mt-2">
                            <label for="plik" class="form-label fw-bold"
                                >Wybierz plik (Zdjecie / Skan) *</label
                            >
                            <input
                                class="form-control form-control-lg"
                                type="file"
                                id="plik"
                                on:change={obslugaPliku}
                                required
                                accept="image/*"
                            />
                        </div>

                        <hr />
                        <!-- Przycisk Zapisz -->
                        <button
                            type="submit"
                            class="btn btn-primary btn-lg w-100 mt-2"
                        >
                            Wyślij na serwer Archiwum
                        </button>
                    </form>
                </div>
            </div>

            <!--Zakładka zarządzania-->
        {:else if aktywnaZakladka === "zarzadzaj"}
            <div class="card shadow-sm border-0">
                <div class="card-body py-4">
                    <button
                        class="btn btn-outline-secondary btn-sm mb-3"
                        on:click={pobierzMojeMaterialy}
                    >
                        Odśwież Listę
                    </button>

                    {#if mojeMaterialy.length === 0}
                        <div class="alert alert-info py-4 text-center">
                            Nie wgrałeś jeszcze żadnego zdjęcia do bazy
                            Cyfrowego Archiwum. Użyj zakładki obok by wgrać
                            pierwsze zdjęcie.
                        </div>
                    {:else}
                        <!-- Tabela z listą od Twórcy -->
                        <div class="table-responsive">
                            <table
                                class="table table-hover align-middle border"
                            >
                                <thead class="table-light">
                                    <tr>
                                        <th>Podgląd</th>
                                        <th>Tytuł</th>
                                        <th>Kategoria / Okres</th>
                                        <th class="text-end"
                                            >Operacje Autorskie</th
                                        >
                                    </tr>
                                </thead>
                                <tbody>
                                    <!-- Pętla dla każdego zdjęcia z serwera -->
                                    {#each mojeMaterialy as material}
                                        <tr>
                                            <td style="width: 120px;">
                                                <!-- Pobranie zdjęcia z serwera -->
                                                <img
                                                    src="http://localhost:8000/uploads/{material.filename}"
                                                    alt="Zdjęcie: {material.title}"
                                                    class="img-thumbnail"
                                                    style="height: 60px; width: 100px; object-fit: cover;"
                                                />
                                            </td>
                                            <td class="fw-bold"
                                                >{material.title}</td
                                            >
                                            <td>
                                                <div
                                                    class="small fw-bold text-success"
                                                    style="font-size: 0.75rem;"
                                                >
                                                    {material.category}
                                                </div>
                                                <span class="badge bg-secondary"
                                                    >{material.historical_period ||
                                                        "Nieznany"}</span
                                                >
                                                {#if $rolaUzytkownika === "Administrator" && material.owner}
                                                    <div
                                                        class="mt-1 small border-top pt-1 text-muted"
                                                        style="font-size: 0.70rem;"
                                                    >
                                                        Autor:
                                                        <b
                                                            >{material.owner
                                                                .name}</b
                                                        >
                                                        ({material.owner.email})
                                                    </div>
                                                {/if}
                                            </td>
                                            <!-- Panel z przyciskiem do usunięcia/modyfikacji -->
                                            <td class="text-end">
                                                <button
                                                    class="btn btn-warning btn-sm me-1"
                                                    on:click={() =>
                                                        zacznijEdycje(material)}
                                                    >Edytuj Wpis</button
                                                >
                                                <button
                                                    class="btn btn-danger btn-sm"
                                                    on:click={() =>
                                                        usunMaterial(
                                                            material.id,
                                                        )}>Usuń</button
                                                >
                                                {#if $rolaUzytkownika === "Administrator"}
                                                    <button
                                                        class="btn btn-dark btn-sm mt-1 w-100"
                                                        on:click={() =>
                                                            zablokujUzytkownika(
                                                                material.owner_id,
                                                            )}
                                                    >
                                                        Blokada użytkownika
                                                    </button>
                                                {/if}
                                            </td>
                                        </tr>

                                        <!-- Formularz do edycji-->
                                        {#if edytowanyMaterialId === material.id}
                                            <tr class="table-warning">
                                                <td colspan="4" class="p-3">
                                                    <div
                                                        class="border rounded p-3 bg-white shadow-sm"
                                                    >
                                                        <h6
                                                            class="text-muted fw-bold mb-3"
                                                        >
                                                            # Tryb Edycji
                                                            Metadanych
                                                        </h6>
                                                        <div class="row">
                                                            <div
                                                                class="col-md-6 mb-2"
                                                            >
                                                                <label
                                                                    for="edycjaTytulInput"
                                                                    class="form-label small"
                                                                    >Tytuł</label
                                                                >
                                                                <input
                                                                    id="edycjaTytulInput"
                                                                    type="text"
                                                                    class="form-control form-control-sm"
                                                                    bind:value={
                                                                        edycjaTytul
                                                                    }
                                                                />
                                                            </div>
                                                            <div
                                                                class="col-md-6 mb-2"
                                                            >
                                                                <label
                                                                    for="edycjaOkresInput"
                                                                    class="form-label small"
                                                                    >Okres</label
                                                                >
                                                                <input
                                                                    id="edycjaOkresInput"
                                                                    type="text"
                                                                    class="form-control form-control-sm"
                                                                    bind:value={
                                                                        edycjaOkres
                                                                    }
                                                                />
                                                            </div>
                                                            <div
                                                                class="col-12 mb-2"
                                                            >
                                                                <label
                                                                    for="edycjaOpisInput"
                                                                    class="form-label small"
                                                                    >Opis
                                                                    (opcjonalny)</label
                                                                >
                                                                <textarea
                                                                    id="edycjaOpisInput"
                                                                    class="form-control form-control-sm"
                                                                    rows="2"
                                                                    bind:value={
                                                                        edycjaOpis
                                                                    }
                                                                ></textarea>
                                                            </div>
                                                        </div>
                                                        <!-- Przyciski do zatwierdzenia lub anulowania edycji -->
                                                        <div
                                                            class="mt-2 text-end"
                                                        >
                                                            <button
                                                                class="btn btn-sm btn-secondary me-2"
                                                                on:click={anulujEdycje}
                                                                >Anuluj</button
                                                            >
                                                            <button
                                                                class="btn btn-sm btn-success"
                                                                on:click={() =>
                                                                    zapiszEdycje(
                                                                        material.id,
                                                                    )}
                                                                >Zapisz Poprawki</button
                                                            >
                                                        </div>
                                                    </div>
                                                </td>
                                            </tr>
                                        {/if}
                                    {/each}
                                </tbody>
                            </table>
                        </div>
                    {/if}
                </div>
            </div>
        {/if}
    </div>
</div>

<!-- ================= Style css ================= -->
<style>
    /* Usuwanie spinnerów z pól liczbowych (źle się sprawdzają we współrzędnych) */
    input[type="number"]::-webkit-inner-spin-button,
    input[type="number"]::-webkit-outer-spin-button {
        -webkit-appearance: none;
        margin: 0;
    }
    input[type="number"] {
        -moz-appearance: textfield; /* Dla działania na firefoxie */
        appearance: textfield;
    }
</style>
