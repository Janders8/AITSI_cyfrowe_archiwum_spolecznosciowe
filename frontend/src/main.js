import { mount } from 'svelte'
import App from './App.svelte'
import './index.css'

// Główny plik wejściowy. 
// Szuka w index.html elementu z id="app" i montuje w nim aplikację Svelte
// (z pliku App.svelte).
const app = mount(App, {
  target: document.getElementById('app'),
})

export default app
