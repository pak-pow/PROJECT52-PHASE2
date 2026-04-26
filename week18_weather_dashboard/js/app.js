import { fetchWeather } from './api.js';

async function init() {
    console.log("Pinging Open-Meteo...");
    const weatherData = await fetchWeather();
    console.log(weatherData);
}

document.addEventListener("DOMContentLoaded", init);