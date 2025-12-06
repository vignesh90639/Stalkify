// =======================
// Global Variables
// =======================
let predictionChart = null;

// =======================
// AI PRICE PREDICTOR
// =======================
async function runPrediction() {
  const symbol = document.getElementById('predict-symbol').value.trim().toUpperCase();
  const days = parseInt(document.getElementById('predict-days').value) || 30;

  if (!symbol) {
    showNotification('Please enter a stock symbol', 'error');
    return;
  }

  if (symbol.length > 5) {
    showNotification('Stock symbol is too long', 'error');
    return;
  }

  if (days < 1 || days > 365) {
    showNotification('Days must be between 1 and 365', 'error');
    return;
  }

  // Show loading
  const loadingElem = document.getElementById('loading-prediction');
  const resultsElem = document.getElementById('prediction-results');
  
  if (loadingElem) loadingElem.style.display = 'block';
  if (resultsElem) resultsElem.style.display = 'none';

  try {
    const response = await fetch('/api/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ symbol, days })
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();

    if (data.error) {
      showNotification('Error: ' + data.error, 'error');
      return;
    }

    displayPrediction(data);
    showNotification('Prediction generated successfully!', 'success');
  } catch (error) {
    console.error('Prediction error:', error);
    showNotification('Failed to generate prediction: ' + error.message, 'error');
  } finally {
    if (loadingElem) loadingElem.style.display = 'none';
  }
}

function displayPrediction(data) {
  // Update stats
  document.getElementById('prediction-title').textContent = `${data.symbol} Price Prediction`;
  document.getElementById('current-price').textContent = `$${data.current_price}`;
  
  const trend = data.predicted_trend;
  const trendElement = document.getElementById('predicted-trend');
  trendElement.textContent = trend.charAt(0).toUpperCase() + trend.slice(1);
  trendElement.style.color = trend === 'upward' ? '#00ff00' : '#ff4444';

  const lastPrediction = data.predictions[data.predictions.length - 1];
  const targetElement = document.getElementById('target-price');
  targetElement.textContent = `$${lastPrediction.price}`;
  
  const priceChange = lastPrediction.price - data.current_price;
  targetElement.style.color = priceChange >= 0 ? '#00ff00' : '#ff4444';

  // Show results
  document.getElementById('prediction-results').style.display = 'block';

  // Create chart
  createPredictionChart(data);
}

function createPredictionChart(data) {
  const ctx = document.getElementById('predictionChart');
  
  // Destroy existing chart
  if (predictionChart) {
    predictionChart.destroy();
  }

  const labels = data.predictions.map(p => p.date);
  const prices = data.predictions.map(p => p.price);

  predictionChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: `${data.symbol} Predicted Price`,
        data: prices,
        borderColor: data.predicted_trend === 'upward' ? '#00ff00' : '#ff4444',
        backgroundColor: data.predicted_trend === 'upward' 
          ? 'rgba(0, 255, 0, 0.1)' 
          : 'rgba(255, 68, 68, 0.1)',
        borderWidth: 3,
        tension: 0.4,
        fill: true,
        pointBackgroundColor: '#00ffff',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 3,
        pointHoverRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          labels: { 
            color: '#00ffff', 
            font: { size: 14, family: 'Poppins' } 
          }
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          titleColor: '#00ffff',
          bodyColor: '#fff',
          borderColor: '#00ffff',
          borderWidth: 1,
          callbacks: {
            label: function(context) {
              return `Price: $${context.parsed.y.toFixed(2)}`;
            }
          }
        }
      },
      scales: {
        x: {
          ticks: { 
            color: '#aaa',
            maxRotation: 45,
            minRotation: 45
          },
          grid: { color: 'rgba(255, 255, 255, 0.05)' }
        },
        y: {
          ticks: { 
            color: '#aaa',
            callback: function(value) {
              return '$' + value.toFixed(2);
            }
          },
          grid: { color: 'rgba(255, 255, 255, 0.05)' }
        }
      }
    }
  });
}

// =======================
// WHAT-IF SIMULATOR
// =======================
async function runSimulation() {
  const symbol = document.getElementById('sim-symbol').value.trim().toUpperCase();
  const shares = parseInt(document.getElementById('sim-shares').value) || 100;
  const scenarioType = document.getElementById('sim-scenario').value;
  const timeHorizon = document.getElementById('sim-timeframe').value;

  if (!symbol) {
    showNotification('Please enter a stock symbol', 'error');
    return;
  }

  if (symbol.length > 5) {
    showNotification('Stock symbol is too long', 'error');
    return;
  }

  if (shares < 1) {
    showNotification('Please enter at least 1 share', 'error');
    return;
  }

  // Show loading
  const loadingElem = document.getElementById('loading-sim');
  const resultsElem = document.getElementById('sim-results');

  if (loadingElem) loadingElem.style.display = 'block';
  if (resultsElem) resultsElem.innerHTML = '';

  try {
    const response = await fetch('/api/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        symbol,
        shares,
        scenario_type: scenarioType,
        time_horizon: timeHorizon
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    if (data.error) {
      if (resultsElem) {
        resultsElem.innerHTML = `<div class="error-message"><i class="fas fa-exclamation-triangle"></i> ${data.error}</div>`;
      }
      console.error('Simulation error:', data.error);
      return;
    }

    displaySimulation(data);
  } catch (error) {
    console.error('Simulation fetch error:', error);
    if (resultsElem) {
      resultsElem.innerHTML = `<div class="error-message"><i class="fas fa-exclamation-circle"></i> Failed to run simulation: ${error.message}</div>`;
    }
  } finally {
    if (loadingElem) loadingElem.style.display = 'none';
  }
}

function displaySimulation(data) {
  const resultsContainer = document.getElementById('sim-results');
  
  const profitLossClass = data.profit_loss >= 0 ? 'profit' : 'loss';
  const profitLossIcon = data.profit_loss >= 0 ? '📈' : '📉';
  
  resultsContainer.innerHTML = `
    <div class="results-grid">
      <div class="result-item">
        <div class="result-label">Scenario</div>
        <div class="result-value">${formatScenarioName(data.scenario)}</div>
      </div>
      
      <div class="result-item">
        <div class="result-label">Shares Held</div>
        <div class="result-value">${data.shares}</div>
      </div>
      
      <div class="result-item">
        <div class="result-label">Current Price</div>
        <div class="result-value">$${data.current_price}</div>
      </div>
      
      <div class="result-item">
        <div class="result-label">Simulated Price</div>
        <div class="result-value">$${data.simulated_price}</div>
      </div>
      
      <div class="result-item">
        <div class="result-label">Price Change</div>
        <div class="result-value ${profitLossClass}">
          ${data.price_change >= 0 ? '+' : ''}$${data.price_change}
        </div>
      </div>
      
      <div class="result-item">
        <div class="result-label">Percent Change</div>
        <div class="result-value ${profitLossClass}">
          ${data.percent_change >= 0 ? '+' : ''}${data.percent_change}%
        </div>
      </div>
      
      <div class="result-item highlight">
        <div class="result-label">Current Portfolio Value</div>
        <div class="result-value">$${data.current_value.toLocaleString()}</div>
      </div>
      
      <div class="result-item highlight">
        <div class="result-label">Simulated Portfolio Value</div>
        <div class="result-value">$${data.simulated_value.toLocaleString()}</div>
      </div>
      
      <div class="result-item highlight" style="grid-column: 1 / -1;">
        <div class="result-label">Profit/Loss ${profitLossIcon}</div>
        <div class="result-value ${profitLossClass}" style="font-size: 2rem;">
          ${data.profit_loss >= 0 ? '+' : ''}$${data.profit_loss.toLocaleString()}
        </div>
      </div>
    </div>
    
    <div class="recommendation-box">
      <h4><i class="fas fa-robot"></i> AI Recommendation</h4>
      <p>${data.recommendation}</p>
      <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(0, 255, 255, 0.2);">
        <small style="color: #aaa;">
          <i class="fas fa-shield-alt"></i> Risk Score: ${data.risk_score}/100
          ${getRiskEmoji(data.risk_score)}
        </small>
      </div>
    </div>
  `;
}

// =======================
// QUICK SCENARIOS
// =======================
function loadQuickScenario(scenarioType) {
  // Set the scenario type
  document.getElementById('sim-scenario').value = scenarioType;
  
  // Update scenario info
  updateScenarioInfo();
  
  // Scroll to simulator section
  document.querySelector('#scenarios').scrollIntoView({ behavior: 'smooth' });
  
  // Focus on symbol input if empty
  const symbolInput = document.getElementById('sim-symbol');
  if (!symbolInput.value) {
    symbolInput.focus();
  }
}

// =======================
// UPDATE SCENARIO INFO
// =======================
function updateScenarioInfo() {
  const scenarioType = document.getElementById('sim-scenario').value;
  const infoBox = document.getElementById('scenario-info');

  const scenarios = {
    'market_crash': {
      text: 'Simulates a severe market downturn with a -20% decline across all sectors (based on 1987 crash and 2020 COVID crash)'
    },
    'bull_market': {
      text: 'Simulates a strong market rally with +25% gains driven by investor confidence (average bull market returns)'
    },
    'recession': {
      text: 'Simulates an economic recession with -15% market decline and reduced spending (typical recession impact)'
    },
    'tech_boom': {
      text: 'Simulates a technology sector boom with +30% gains from innovation (2020-2021 tech rally)'
    },
    'rate_hike': {
      text: 'Simulates the impact of interest rate increases with -8% market adjustment (Fed rate hike effects)'
    },
    'volatility': {
      text: 'Simulates high market volatility with unpredictable swings but no net change (choppy market conditions)'
    },
    'inflation': {
      text: 'Simulates high inflation environment with -10% purchasing power impact (inflation concerns)'
    },
    'deflation': {
      text: 'Simulates deflation scenario with -12% economic slowdown (rare deflation events)'
    },
    'war': {
      text: 'Simulates geopolitical crisis with -18% market panic and uncertainty (Gulf War, Ukraine invasion)'
    },
    'recovery': {
      text: 'Simulates economic recovery with +20% post-crisis market bounce (post-2008 recovery)'
    }
  };

  const scenario = scenarios[scenarioType] || scenarios['market_crash'];

  infoBox.innerHTML = `
    <i class="fas fa-info-circle"></i>
    <p>${scenario.text}</p>
  `;
}

// =======================
// HELPER FUNCTIONS
// =======================
function formatScenarioName(scenario) {
  return scenario
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

function getRiskEmoji(riskScore) {
  if (riskScore < 30) return '✅ Low Risk';
  if (riskScore < 60) return '⚠️ Moderate Risk';
  return '🚨 High Risk';
}

// =======================
// COMPARE MULTIPLE SCENARIOS
// =======================
async function runComparison() {
  const symbol = document.getElementById('compare-symbol').value.trim().toUpperCase();
  const shares = parseInt(document.getElementById('compare-shares').value) || 100;

  if (!symbol) {
    showNotification('Please enter a stock symbol', 'error');
    return;
  }

  if (symbol.length > 5) {
    showNotification('Stock symbol is too long', 'error');
    return;
  }

  if (shares < 1) {
    showNotification('Please enter at least 1 share', 'error');
    return;
  }

  const resultsContainer = document.getElementById('comparison-results');
  resultsContainer.innerHTML = '<div class="loading-card"><i class="fas fa-spinner fa-spin"></i> Comparing scenarios...</div>';

  const scenariosToCompare = ['market_crash', 'bull_market', 'recession', 'tech_boom', 'recovery'];
  const results = [];

  for (const scenarioType of scenariosToCompare) {
    try {
      const response = await fetch('/api/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol,
          shares,
          scenario_type: scenarioType
        })
      });

      if (!response.ok) {
        console.warn(`HTTP error for ${scenarioType}! status: ${response.status}`);
        continue;
      }

      const data = await response.json();
      if (data && !data.error) {
        results.push(data);
      } else if (data && data.error) {
        console.warn(`API error for ${scenarioType}:`, data.error);
      }
    } catch (error) {
      console.error(`Error simulating ${scenarioType}:`, error);
    }
  }

  displayComparison(results);
}

function displayComparison(results) {
  const resultsContainer = document.getElementById('comparison-results');

  if (results.length === 0) {
    showNotification('Could not fetch comparison data. Please try again.', 'error');
    resultsContainer.innerHTML = '<div class="no-results"><i class="fas fa-exclamation-circle"></i><p>No comparison data available</p></div>';
    return;
  }
  
  showNotification('Comparison completed successfully!', 'success');

  let html = '<div class="comparison-grid">';

  results.forEach(result => {
    const profitLossClass = result.profit_loss >= 0 ? 'profit' : 'loss';
    
    html += `
      <div class="scenario-comparison-card">
        <h4>${formatScenarioName(result.scenario)}</h4>
        <div class="comparison-value ${profitLossClass}">
          ${result.profit_loss >= 0 ? '+' : ''}$${result.profit_loss.toLocaleString()}
        </div>
        <div class="comparison-change ${profitLossClass}">
          ${result.percent_change >= 0 ? '+' : ''}${result.percent_change}%
        </div>
        <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(0,255,255,0.2);">
          <small style="color: #aaa;">Final Value: $${result.simulated_value.toLocaleString()}</small>
        </div>
      </div>
    `;
  });

  html += '</div>';
  resultsContainer.innerHTML = html;
}

// =======================
// NOTIFICATION SYSTEM
// =======================
function showNotification(message, type = 'info') {
  // Remove existing notification if present
  const existing = document.getElementById('notification');
  if (existing) existing.remove();
  
  const notif = document.createElement('div');
  notif.id = 'notification';
  notif.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 16px 24px;
    border-radius: 10px;
    font-weight: 600;
    z-index: 9999;
    animation: slideIn 0.3s ease-out;
    max-width: 400px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  `;
  
  const colors = {
    success: { bg: 'rgba(0, 200, 100, 0.9)', text: '#fff', icon: '✓' },
    error: { bg: 'rgba(255, 70, 70, 0.9)', text: '#fff', icon: '✕' },
    info: { bg: 'rgba(0, 150, 255, 0.9)', text: '#fff', icon: 'ℹ' }
  };
  
  const style = colors[type] || colors.info;
  notif.style.backgroundColor = style.bg;
  notif.style.color = style.text;
  notif.textContent = `${style.icon} ${message}`;
  
  document.body.appendChild(notif);
  
  setTimeout(() => {
    notif.style.animation = 'slideOut 0.3s ease-out';
    setTimeout(() => notif.remove(), 300);
  }, 4000);
}

// =======================
// INITIALIZE
// =======================
document.addEventListener('DOMContentLoaded', () => {
  updateScenarioInfo();

  // Check for URL parameter to pre-select scenario
  const urlParams = new URLSearchParams(window.location.search);
  const scenarioParam = urlParams.get('scenario');
  if (scenarioParam) {
    // Pre-select the scenario and update info
    const scenarioSelect = document.getElementById('sim-scenario');
    if (scenarioSelect) {
      scenarioSelect.value = scenarioParam;
      updateScenarioInfo();
    }

    // Show notification
    showNotification(`Scenario "${formatScenarioName(scenarioParam)}" selected!`, 'info');
  }

  // Add enter key listeners
  document.getElementById('predict-symbol').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') runPrediction();
  });

  document.getElementById('sim-symbol').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') runSimulation();
  });

  document.getElementById('compare-symbol').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') runComparison();
  });
});
