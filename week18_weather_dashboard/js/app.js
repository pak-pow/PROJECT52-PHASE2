import { fetchWeather, fetchCoordinates } from "./api.js";
import { renderWeather, renderChart } from "./ui.js";

async function loadWeather(lat, lon, locationName) {
  const weatherContainer = document.getElementById("current-weather");
  weatherContainer.innerHTML = `<p id="loading-text">Fetching live data for ${locationName}...</p>`;
  const weatherData = await fetchWeather(lat, lon);

  if (weatherData) {
    renderWeather(weatherData, locationName);
    renderChart(weatherData);
  }
}

async function handleSearch() {
  const cityInput = document.getElementById("city-input").value.trim();
  if (!cityInput) return;

  const weatherContainer = document.getElementById("current-weather");
  weatherContainer.innerHTML = `<p id="loading-text">Searching for coordinates...</p>`;
  
  const location = await fetchCoordinates(cityInput);

  if (location) {
    const locationName = `${location.name}, ${location.country}`;
    await loadWeather(location.lat, location.lon, locationName);
  
  } else {
    weatherContainer.innerHTML = `<p style="color: #ef4444;">City not found. Please try again.</p>`;
  }
}

function init() {
  console.log("System Online. Geocoding Engine Active.");
  document.getElementById("search-btn").addEventListener("click", handleSearch);
  document.getElementById("city-input").addEventListener("keypress", (e) => {
    if (e.key === "Enter") handleSearch();
  });

  loadWeather(13.4088, 122.5615, "Pagbilao, Philippines");
}

document.addEventListener("DOMContentLoaded", init);
