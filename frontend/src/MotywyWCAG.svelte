<script>
    // Skrypt do zmiany motywów wizualnych (jasny, ciemny, wysoki kontrast)

    import { onMount } from "svelte";

    // Aktualny motyw
    let aktualnyMotyw = "light";

    // Funkcja wywoływana po zmianie opcji w pasku wyboru
    function zmienMotyw() {
        // referencja do znacznika HTML strony (by efekt był widoczny w całym projekcie)
        const korzenHTML = document.documentElement;

        if (aktualnyMotyw === "light") {
            // Jasny tryb Bootstrapa
            korzenHTML.setAttribute("data-bs-theme", "light");
            korzenHTML.classList.remove("wysoki-kontrast");
        } else if (aktualnyMotyw === "dark") {
            // Tryb ciemny Bootstrapa
            korzenHTML.setAttribute("data-bs-theme", "dark");
            korzenHTML.classList.remove("wysoki-kontrast");
        } else if (aktualnyMotyw === "contrast") {
            // Tryb wysokiego kontrastu, nie jest wbudowany w Bootstrapa, więc dodano własną klasę
            // bazującą na trybie ciemnym
            korzenHTML.setAttribute("data-bs-theme", "dark");
            korzenHTML.classList.add("wysoki-kontrast");
        }

        // Zapisanie motywu w LocalStorage przeglądarki, by nie resetowało się po odświeżeniu
        localStorage.setItem("zapisany_motyw_wcag", aktualnyMotyw);
    }

    onMount(() => {
        // Sprawdzenie zapisanego motywu
        const zapisany = localStorage.getItem("zapisany_motyw_wcag");
        if (zapisany) {
            aktualnyMotyw = zapisany;
            zmienMotyw();
        }
    });
</script>

<div class="d-flex align-items-center ms-3 me-3">
    <span class="text-light me-2 fw-bold">Motyw:</span>

    <!-- lista do wyboru motywu -->
    <select
        class="form-select form-select-sm bg-dark text-light border-secondary"
        bind:value={aktualnyMotyw}
        on:change={zmienMotyw}
        aria-label="Wybór motywu kolorystycznego"
    >
        <option value="light">Tryb Jasny</option>
        <option value="dark">Tryb Ciemny</option>
        <option value="contrast">Wysoki Kontrast</option>
    </select>
</div>
