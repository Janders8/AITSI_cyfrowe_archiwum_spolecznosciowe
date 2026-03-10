import { writable } from 'svelte/store';

// Plik służący jako pamięć globalna aplikacji
// PRzechowuje m.in. token JWT, rolę użytkownika i email użytkownika

// Zmienna przechowująca klucz JWT otrzymany z API backendu
export const tokenJWT = writable(null);

// Zmienna przechowująca przypisaną użytkownikowi rolę w bazie
export const rolaUzytkownika = writable("Gość");

// Zmienna przechowująca adres email z Google
export const emailUzytkownika = writable("");
