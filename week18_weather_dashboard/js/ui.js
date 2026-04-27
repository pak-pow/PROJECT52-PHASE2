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

// ==========================================
// 📊 CHART CONTROLLER
// ==========================================
let weatherChart = null; 

export function renderChart(data) {
    const ctx = document.getElementById('hourlyChart').getContext('2d');
    const currentHourStr = new Date().toISOString().slice(0, 14) + "00"; 
    const currentIndex = data.hourly.time.findIndex(t => t.startsWith(currentHourStr));
    const startIndex = currentIndex !== -1 ? currentIndex : 0;
    
    const next12Hours = data.hourly.time.slice(startIndex, startIndex + 12);
    const next12Temps = data.hourly.temperature_2m.slice(startIndex, startIndex + 12);
    const formattedLabels = next12Hours.map(timeStr => {
        return new Date(timeStr).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    });
    if (weatherChart) {
        weatherChart.destroy();
    }
    weatherChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: formattedLabels,
            datasets: [{
                label: 'Temperature (°C)',
                data: next12Temps,
                borderColor: '#3b82f6', // Matches your --accent-blue
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 3,
                tension: 0.4, // Makes the line smooth and curvy
                fill: true,
                pointBackgroundColor: '#0f1115',
                pointBorderColor: '#3b82f6',
                pointHoverBackgroundColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false } // Hides the legend for a cleaner look
            },
            scales: {
                x: {
                    grid: { display: false, color: '#2d3139' },
                    ticks: { color: '#9ca3af' }
                },
                y: {
                    grid: { color: '#2d3139' },
                    ticks: { color: '#9ca3af', stepSize: 1 }
                }
            }
        }
    });
}