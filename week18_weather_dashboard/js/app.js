import { fetchWeather } from './api.js';
import { renderWeather } from './ui.js';

async function init() {
    console.log("App initialized. Pinging Open-Meteo...");
    
    // 1. Fetch the data
    const weatherData = await fetchWeather();
    
    // 2. Send the data to the UI to be drawn on the screen
    renderWeather(weatherData); 
}

// Start the engine when the HTML is fully loaded
document.addEventListener("DOMContentLoaded", init);