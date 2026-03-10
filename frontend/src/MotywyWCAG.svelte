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
            // Standardowy Jasny tryb Bootstrapa
            korzenHTML.setAttribute("data-bs-theme", "light");
            korzenHTML.classList.remove("wysoki-kontrast");
        } else if (aktualnyMotyw === "dark") {
            // Wbudowany Tryb ciemny Bootstrapa
            korzenHTML.setAttribute("data-bs-theme", "dark");
            korzenHTML.classList.remove("wysoki-kontrast");
        } else if (aktualnyMotyw === "contrast") {
            // Tryb wysokiego kontrastu, nie jest wbudowany w Bootstrapa, więc należy dodać własną klasę
            // bazującą na trybie ciemnym
            korzenHTML.setAttribute("data-bs-theme", "dark");
            korzenHTML.classList.add("wysoki-kontrast");
        }

        // Zapiszmy wybór w LocalStorage przeglądarki, by nie resetowało się po odświeżeniu
        localStorage.setItem("zapisany_motyw_wcag", aktualnyMotyw);
    }

    // Kod odpalający się raz, przy wejściu na stronę
    onMount(() => {
        // Sprawdźmy czy wracający użytkownik nie miał już czegoś wybranego
        const zapisany = localStorage.getItem("zapisany_motyw_wcag");
        if (zapisany) {
            aktualnyMotyw = zapisany;
            zmienMotyw(); // Uruchom logikę nakładania od razu
        }
    });
</script>

<div class="d-flex align-items-center ms-3 me-3">
    <!-- Ikonka zmiany stylu -->
    <span class="text-light me-2 fw-bold">Motyw:</span>

    <!-- Selektor do wyboru -->
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
