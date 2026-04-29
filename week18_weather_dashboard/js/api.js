const BASE_URL = "https://api.open-meteo.com/v1/forecast";
const GEOCODE_URL = "https://geocoding-api.open-mateo.com/v1/search";

export async function fetchCoordinates(city) {
  try {
    const response = await fetch(
      `${GEOCODE_URL}?name=${city}&count=1&language=en&format=json`,
    );
    if (!response.ok) throw new Error("Geocoding failed");
    const data = await response.json();

    // returns null if searched no city or fake
    if (!data.results || data.results.length === 0) return null;

    return {
      lat: data.results[0].latitude,
      lon: data.results[0].longitude,
      name: data.results[0].name,
      country: data.results[0].country,
    };

  } catch (error) {
    console.error("Geocoding Error:", error);
    return null;
  }
}

export async function fetchWeather() {
  try {
    // This exactly matches the checkboxes in your new screenshots
    const params = new URLSearchParams({
      latitude: 13.4088,
      longitude: 122.5615,

      // Hourly Variables
      hourly: "temperature_2m,precipitation_probability,precipitation",

      // Daily Variables
      daily:
        "weather_code,temperature_2m_max,temperature_2m_min,sunrise,sunset,uv_index_max,precipitation_sum,wind_speed_10m_max",

      // Settings
      timezone: "auto",
    });

    const response = await fetch(`${BASE_URL}?${params.toString()}`);

    if (!response.ok) {
      throw new Error(`HTTP Error: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("API Fetch Failed:", error);
    return null;
  }
}
