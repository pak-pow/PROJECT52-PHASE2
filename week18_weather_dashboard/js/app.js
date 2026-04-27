import { fetchWeather } from "./api.js";
import { renderWeather, renderChart } from "./ui.js";

async function init() {
  console.log("App initialized. Pinging Open-Meteo...");

  const weatherData = await fetchWeather();

  if (weatherData) {
    renderWeather(weatherData);
    renderChart(weatherData);
  } else {
    console.error("Failed to load weather data.");
  }
}

document.addEventListener("DOMContentLoaded", init);
