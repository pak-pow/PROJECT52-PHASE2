// ==========================================
// 🖥️ UI CONTROLLER (Interface Logic Only)
// ==========================================

export function renderWeather(data) {
  const card = document.getElementById("weather-card");

  if (!data) {
    card.innerHTML = `<p style="color: red;">Failed to load weather data.</p>`;
    return;
  }

  // 1. Extract the Daily Data (Index 0 is "Today")
  const maxTemp = data.daily.temperature_2m_max[0];
  const minTemp = data.daily.temperature_2m_min[0];
  const sunrise = new Date(data.daily.sunrise[0]).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
  const sunset = new Date(data.daily.sunset[0]).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  // 2. Extract the Current Hourly Data
  // We get the current hour (0-23) to find the exact temperature right now
  const currentHour = new Date().getHours();
  const currentTemp = data.hourly.temperature_2m[currentHour];
  const chanceOfRain = data.hourly.precipitation_probability[currentHour];

  card.innerHTML = `
        <div class="weather-main">
            <h2>${currentTemp}°C</h2>
            <p>High: ${maxTemp}°C | Low: ${minTemp}°C</p>
        </div>
        
        <div class="weather-details">
            <div>
                <strong>🌧️ Rain Chance</strong>
                <span>${chanceOfRain}%</span>
            </div>
            <div>
                <strong>🌅 Sunrise</strong>
                <span>${sunrise}</span>
            </div>
            <div>
                <strong>🌇 Sunset</strong>
                <span>${sunset}</span>
            </div>
        </div>
    `;
}
