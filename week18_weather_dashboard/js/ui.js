export function renderWeather(data, locationName) {
  const weatherContainer = document.getElementById("current-weather");

  if (!data) {
    weatherContainer.innerHTML = `<p style="color: #ef4444;">Failed to load weather data.</p>`;
    return;
  }

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

  const currentHour = new Date().getHours();
  const currentTemp = data.hourly.temperature_2m[currentHour];
  const chanceOfRain = data.hourly.precipitation_probability[currentHour];
  weatherContainer.innerHTML = `
        <div class="weather-main">
            <h3>📍 ${locationName}</h3>
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

let weatherChart = null;

export function renderChart(data) {
  const ctx = document.getElementById("hourlyChart").getContext("2d");

  // 🔥 MUCH CLEANER TIME LOGIC:
  // Because the API returns hours 0-23 for today, the current hour IS the index!
  const startIndex = new Date().getHours();

  const next12Hours = data.hourly.time.slice(startIndex, startIndex + 12);
  const next12Temps = data.hourly.temperature_2m.slice(
    startIndex,
    startIndex + 12,
  );

  const formattedLabels = next12Hours.map((timeStr) => {
    return new Date(timeStr).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
  });

  if (weatherChart) {
    weatherChart.destroy();
  }

  weatherChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: formattedLabels,
      datasets: [
        {
          label: "Temperature (°C)",
          data: next12Temps,
          borderColor: "#3b82f6",
          backgroundColor: "rgba(59, 130, 246, 0.1)",
          borderWidth: 3,
          tension: 0.4,
          fill: true,
          pointBackgroundColor: "#0f1115",
          pointBorderColor: "#3b82f6",
          pointHoverBackgroundColor: "#fff",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
      },
      scales: {
        x: {
          grid: { display: false, color: "#2d3139" },
          ticks: { color: "#9ca3af" },
        },
        y: {
          grid: { color: "#2d3139" },
          ticks: { color: "#9ca3af", stepSize: 1 },
        },
      },
    },
  });
}

function getWeatherIcon(code) {
  if (code === 0) return "☀️"; // Clear sky
  if (code >= 1 && code <= 3) return "⛅"; // Partly cloudy
  if (code >= 45 && code <= 48) return "🌫️"; // Fog
  if (code >= 51 && code <= 67) return "🌧️"; // Rain
  if (code >= 71 && code <= 77) return "❄️"; // Snow
  if (code >= 95 && code <= 99) return "⛈️"; // Thunderstorm
  return "☁️";
}

export function renderWeeklyForecast(data) {
  const weeklyContainer = document.getElementById("weekly-forecast");
  weeklyContainer.innerHTML = ""; // Clear any old data out first

  // Loop through all 7 days of data
  for (let i = 0; i < 7; i++) {
    const dateString = data.daily.time[i]; // e.g., "2026-04-30"
    const maxTemp = Math.round(data.daily.temperature_2m_max[i]);
    const minTemp = Math.round(data.daily.temperature_2m_min[i]);
    const weatherCode = data.daily.weather_code[i];

    // Convert the raw date string into a friendly day name (Mon, Tue, Wed)
    // We add "T00:00:00" to prevent timezone bugs where it shifts a day backward
    const dayName = new Date(dateString + "T00:00:00").toLocaleDateString('en-US', { weekday: 'short' });
    
    // Get the matching emoji
    const icon = getWeatherIcon(weatherCode);

    // Inject the HTML for this specific day into our container
    weeklyContainer.innerHTML += `
        <div class="daily-card">
            <span class="day-name">${dayName}</span>
            <span style="font-size: 1.5rem; margin: 0.25rem 0;">${icon}</span>
            <span class="day-temp">${maxTemp}°</span>
            <span style="font-size: 0.85rem; color: var(--text-muted);">${minTemp}°</span>
        </div>
    `;
  }
}

export function renderAdvancedMetrics(data){

  // index 0 is always today
  const maxWind = Math.round(data.daily.wind_speed_10m_max[0]);
  const uvIndex = Math.round(data.daily.uv_index_max[0]);

  const totalRain = data.daily.precipitation_sum[0].toFixed(1);
  
  const sunrise = new Date(data.daily.sunrise[0]);
  const sunset = new Date(data.daily.sunset[0]);

  const diffMs = sunset - sunrise;
  const diffHrs = Math.floor(diffMs / (1000 * 60 * 60));
  const diffMins = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
  const daylightStr = `${diffHrs}h ${diffMins}m`;

  document.getElementById("metric-wind").innerText = maxWind;
  document.getElementById("metric-uv").innerText = uvIndex;
  document.getElementById("metric-rain").innerText = totalRain;
  document.getElementById("metric-sun").innerText = daylightStr;
}

