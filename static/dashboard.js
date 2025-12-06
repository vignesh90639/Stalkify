// =======================
// DOM Elements
// =======================
const tbody = document.querySelector("#stocks-table tbody");
const searchInput = document.getElementById('search');
const filterSelect = document.getElementById('filter');
const aiContainer = document.querySelector('.ai-cards');
const hrCard = document.getElementById("highest-risk-card");
const totalStocks = document.getElementById("total-stocks");
const topAISignal = document.getElementById("top-ai-signal");
const highRiskCount = document.getElementById("high-risk-count");
const buySignals = document.getElementById("buy-signals");

// =======================
// Fetch Stocks and AI Data
// =======================
async function fetchStocksAndAI() {
  try {
    showLoading();
    
    const [stocksRes, aiRes] = await Promise.all([
      fetch('/api/get_stocks'),
      fetch('/api/get_ai_data')
    ]);
    
    const stocks = await stocksRes.json();
    const aiData = await aiRes.json();

    updateStocksTable(stocks);
    updateAICards(aiData);
    updateOverview(stocks, aiData);
    highlightAISignals();
    filterStocks();
  } catch (err) {
    console.error('Error fetching data:', err);
    showError();
  }
}

// =======================
// Update Stocks Table
// =======================
function updateStocksTable(stocks) {
  if (!stocks || stocks.length === 0) {
    tbody.innerHTML = '<tr><td colspan="12" class="loading-row"><i class="fas fa-exclamation-circle"></i> No stocks found</td></tr>';
    return;
  }

  tbody.innerHTML = '';
  stocks.forEach(stock => {
    const tr = document.createElement('tr');
    tr.style.cursor = 'pointer';
    tr.onclick = () => window.location.href = `/company/${stock.symbol}`;
    
    const changePercent = parseFloat(stock.change_percent);
    const changeClass = changePercent >= 0 ? 'positive' : 'negative';
    const changeIcon = changePercent >= 0 ? '▲' : '▼';
    
    tr.innerHTML = `
      <td><strong>${stock.name}</strong></td>
      <td><span class="symbol-badge">${stock.symbol}</span></td>
      <td class="price">$${parseFloat(stock.current_price).toFixed(2)}</td>
      <td class="${changeClass}">${changeIcon} ${Math.abs(changePercent).toFixed(2)}%</td>
      <td><span class="risk-badge ${stock.risk_level.toLowerCase()}">${stock.risk_level}</span></td>
      <td>${formatNumber(stock.market_cap) || '-'}</td>
      <td>${stock.pe_ratio ? parseFloat(stock.pe_ratio).toFixed(2) : '-'}</td>
      <td>${stock.dividend_yield ? (parseFloat(stock.dividend_yield) * 100).toFixed(2) + '%' : '-'}</td>
      <td>$${stock.high_52week ? parseFloat(stock.high_52week).toFixed(2) : '-'}</td>
      <td>$${stock.low_52week ? parseFloat(stock.low_52week).toFixed(2) : '-'}</td>
      <td>${formatNumber(stock.volume) || '-'}</td>
      <td onclick="event.stopPropagation()">
        <button onclick="updateStock('${stock.symbol}')" title="Refresh ${stock.symbol}">
          <i class="fas fa-sync-alt"></i>
        </button>
      </td>
    `;
    
    tbody.appendChild(tr);
  });
}

// =======================
// Update AI Cards
// =======================
function updateAICards(aiData) {
  if (!aiData || aiData.length === 0) {
    aiContainer.innerHTML = '<div class="loading-card"><i class="fas fa-exclamation-circle"></i> No AI data available</div>';
    return;
  }

  aiContainer.innerHTML = '';
  aiData.forEach(stock => {
    const div = document.createElement('div');
    div.classList.add('ai-card');
    
    const sentimentIcon = getSentimentIcon(stock.sentiment);
    const scoreColor = getScoreColor(stock.score);
    
    div.innerHTML = `
      <h3><i class="fas fa-chart-line"></i> ${stock.name} (${stock.symbol})</h3>
      <p><strong>AI Score:</strong> <span style="color: ${scoreColor}">${stock.score}/100</span></p>
      <p><strong>Sentiment:</strong> ${sentimentIcon} ${stock.sentiment}</p>
      <p><strong>Risk:</strong> <span class="risk-badge ${stock.ai_risk.toLowerCase()}">${stock.ai_risk}</span></p>
    `;
    
    aiContainer.appendChild(div);
  });
}

// =======================
// Highlight AI Signals
// =======================
function highlightAISignals() {
  document.querySelectorAll(".ai-card").forEach(card => {
    const text = card.innerText.toLowerCase();
    
    if (text.includes("bullish")) {
      card.style.borderColor = "#00ff00";
    } else if (text.includes("bearish")) {
      card.style.borderColor = "#ff4444";
    } else if (text.includes("neutral")) {
      card.style.borderColor = "#ffbb33";
    }
  });
}

// =======================
// Update Overview Stats
// =======================
function updateOverview(stocks, aiData) {
  // Total stocks
  totalStocks.textContent = stocks.length;

  // High risk count
  const highRisk = stocks.filter(s => s.risk_level === "Bold").length;
  highRiskCount.textContent = highRisk;

  // Buy signals count
  const buyCount = stocks.filter(s => s.ai_signal === "BUY").length;
  buySignals.textContent = buyCount;

  // Top AI score
  if (aiData && aiData.length > 0) {
    const maxScore = Math.max(...aiData.map(d => d.score));
    topAISignal.textContent = maxScore;
  }
  
  // Highest risk stock
  const highestRisk = stocks.find(s => s.risk_level === "Bold") || stocks[0];
  
  if (highestRisk) {
    const changePercent = parseFloat(highestRisk.change_percent);
    const changeClass = changePercent >= 0 ? 'positive' : 'negative';
    const changeIcon = changePercent >= 0 ? '▲' : '▼';
    
    hrCard.innerHTML = `
      <div style="width: 100%; padding: 15px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
          <div>
            <h4 style="color: #00ffff; margin: 0;">${highestRisk.name}</h4>
            <p style="color: #aaa; margin: 5px 0;">${highestRisk.symbol}</p>
          </div>
          <span class="risk-badge ${highestRisk.risk_level.toLowerCase()}">${highestRisk.risk_level}</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div>
            <p style="color: #fff; font-size: 1.5rem; font-weight: bold; margin: 0;">
              $${parseFloat(highestRisk.current_price).toFixed(2)}
            </p>
            <p class="${changeClass}" style="margin: 5px 0;">
              ${changeIcon} ${Math.abs(changePercent).toFixed(2)}%
            </p>
          </div>
          <div style="text-align: right;">
            <p style="color: #aaa; margin: 5px 0; font-size: 0.85rem;">
              <i class="fas fa-signal"></i> ${highestRisk.ai_signal || 'N/A'}
            </p>
            <p style="color: #aaa; margin: 5px 0; font-size: 0.85rem;">
              ${highestRisk.confidence || 'N/A'} confidence
            </p>
          </div>
        </div>
      </div>
    `;
  } else {
    hrCard.innerHTML = '<p class="no-data"><i class="fas fa-check-circle"></i> No high-risk stocks found</p>';
  }
}

// =======================
// Filter/Search Stocks
// =======================
function filterStocks() {
  const searchText = searchInput.value.toLowerCase();
  const filter = filterSelect.value;

  Array.from(tbody.rows).forEach(row => {
    const name = row.cells[0]?.textContent.toLowerCase() || '';
    const symbol = row.cells[1]?.textContent.toLowerCase() || '';
    const risk = row.cells[4]?.textContent.trim() || '';

    const matchSearch = name.includes(searchText) || symbol.includes(searchText);
    const matchFilter = (filter === 'All') || (risk === filter);
    
    row.style.display = (matchSearch && matchFilter) ? '' : 'none';
  });
}

// Event listeners for filter/search
searchInput.addEventListener('input', filterStocks);
filterSelect.addEventListener('change', filterStocks);

// =======================
// Add Company
// =======================
async function addCompany() {
  const symbol = document.getElementById('company-symbol').value.trim().toUpperCase();
  
  if (!symbol) {
    showNotification("Please enter a stock symbol", "error");
    return;
  }
  
  try {
    const res = await fetch("/add_company", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: `symbol=${symbol}`
    });
    
    const data = await res.json();
    
    if (data.error) {
      showNotification(data.error, "error");
    } else {
      showNotification(data.message || "Stock added successfully!", "success");
      document.getElementById('company-symbol').value = '';
      fetchStocksAndAI();
    }
  } catch (err) {
    showNotification("Failed to add stock. Please try again.", "error");
  }
}

// =======================
// Update Stock
// =======================
async function updateStock(symbol) {
  try {
    const res = await fetch("/update_stock", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: `symbol=${symbol}`
    });
    
    const data = await res.json();
    
    if (data.error) {
      showNotification(data.error, "error");
    } else {
      showNotification(data.message || "Stock updated!", "success");
      fetchStocksAndAI();
    }
  } catch (err) {
    showNotification("Failed to update stock.", "error");
  }
}

// =======================
// Add AI Analysis
// =======================
async function addAIAnalysis() {
  const symbol = document.getElementById('ai-symbol').value.trim().toUpperCase();
  const score = document.getElementById('ai-score').value;
  const sentiment = document.getElementById('ai-sentiment').value.trim();
  const ai_risk = document.getElementById('ai-risk').value;
  
  if (!symbol || !score || !sentiment || !ai_risk) {
    showNotification("Please fill in all fields", "error");
    return;
  }
  
  if (score < 0 || score > 100) {
    showNotification("Score must be between 0 and 100", "error");
    return;
  }
  
  try {
    const res = await fetch("/add_ai_analysis", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: `symbol=${symbol}&score=${score}&sentiment=${sentiment}&ai_risk=${ai_risk}`
    });
    
    const data = await res.json();
    
    if (data.error) {
      showNotification(data.error, "error");
    } else {
      showNotification(data.message || "AI analysis saved!", "success");
      // Clear form
      document.getElementById('ai-symbol').value = '';
      document.getElementById('ai-score').value = '';
      document.getElementById('ai-sentiment').value = '';
      fetchStocksAndAI();
    }
  } catch (err) {
    showNotification("Failed to save AI analysis.", "error");
  }
}

// =======================
// Portfolio Chart (Chart.js)
// =======================
let portfolioChart = null;

async function loadPortfolioPerformance() {
  try {
    const response = await fetch('/api/portfolio_performance');
    const data = await response.json();
    
    if (data.error) {
      console.error('Portfolio error:', data.error);
      return;
    }
    
    // Extract labels and values
    const labels = data.map(d => d.date);
    const values = data.map(d => d.value);
    
    // Calculate performance percentage
    const firstValue = values[0];
    const lastValue = values[values.length - 1];
    const changePercent = ((lastValue - firstValue) / firstValue * 100).toFixed(2);
    
    const portfolioChartCtx = document.getElementById('portfolioChart');
    
    if (portfolioChart) {
      portfolioChart.destroy();
    }
    
    portfolioChart = new Chart(portfolioChartCtx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: `Portfolio Value (${changePercent >= 0 ? '+' : ''}${changePercent}%)`,
          data: values,
          borderColor: changePercent >= 0 ? '#00ff00' : '#ff4444',
          backgroundColor: changePercent >= 0 ? 'rgba(0, 255, 0, 0.1)' : 'rgba(255, 68, 68, 0.1)',
          borderWidth: 2,
          tension: 0.4,
          fill: true,
          pointBackgroundColor: '#00ffff',
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
          pointRadius: 2,
          pointHoverRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: {
            labels: { color: '#00ffff', font: { size: 12, family: 'Poppins' } }
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleColor: '#00ffff',
            bodyColor: '#fff',
            borderColor: '#00ffff',
            borderWidth: 1,
            callbacks: {
              label: function(context) {
                return `Value: $${context.parsed.y.toLocaleString()}`;
              }
            }
          }
        },
        scales: {
          x: {
            ticks: { 
              color: '#aaa',
              maxRotation: 45,
              minRotation: 45,
              autoSkip: true,
              maxTicksLimit: 10
            },
            grid: { color: 'rgba(255, 255, 255, 0.05)' }
          },
          y: {
            ticks: { 
              color: '#aaa',
              callback: function(value) {
                return '$' + value.toLocaleString();
              }
            },
            grid: { color: 'rgba(255, 255, 255, 0.05)' }
          }
        }
      }
    });
  } catch (error) {
    console.error('Error loading portfolio:', error);
  }
}

// =======================
// Helper Functions
// =======================
function formatNumber(num) {
  if (!num) return null;
  
  if (num >= 1e12) return (num / 1e12).toFixed(2) + 'T';
  if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
  if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
  if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
  
  return num.toLocaleString();
}

function getSentimentIcon(sentiment) {
  const s = sentiment.toLowerCase();
  if (s.includes('bullish')) return '📈';
  if (s.includes('bearish')) return '📉';
  return '📊';
}

function getScoreColor(score) {
  if (score >= 80) return '#00ff00';
  if (score >= 60) return '#ffbb33';
  return '#ff4444';
}

function showLoading() {
  tbody.innerHTML = '<tr><td colspan="12" class="loading-row"><i class="fas fa-spinner fa-spin"></i> Loading stock data...</td></tr>';
  aiContainer.innerHTML = '<div class="loading-card"><i class="fas fa-spinner fa-spin"></i> Loading AI insights...</div>';
}

function showError() {
  tbody.innerHTML = '<tr><td colspan="12" class="loading-row"><i class="fas fa-exclamation-triangle"></i> Error loading data. Please try again.</td></tr>';
  aiContainer.innerHTML = '<div class="loading-card"><i class="fas fa-exclamation-triangle"></i> Error loading AI data.</div>';
}

function showNotification(message, type = 'info') {
  // Simple alert for now - you can enhance this with a toast notification
  alert(message);
}

// =======================
// Auto-refresh every 2 minutes
// =======================
let lastRefreshTime = Date.now();

function updateRefreshTimer() {
  const elapsed = Math.floor((Date.now() - lastRefreshTime) / 1000);
  const remaining = 120 - elapsed;
  
  if (remaining > 0) {
    const minutes = Math.floor(remaining / 60);
    const seconds = remaining % 60;
    updateRefreshButtonText(`${minutes}:${seconds.toString().padStart(2, '0')}`);
  }
}

function updateRefreshButtonText(time) {
  const btn = document.querySelector('.refresh-btn');
  if (btn) {
    const icon = '<i class="fas fa-sync-alt"></i>';
    if (time) {
      btn.innerHTML = `${icon} Refresh (${time})`;
    } else {
      btn.innerHTML = `${icon} Refresh`;
    }
  }
}

async function refreshData() {
  lastRefreshTime = Date.now();
  updateRefreshButtonText();
  await fetchStocksAndAI();
}

// =======================
// Admin: Trigger server-side batch refresh
// =======================
async function adminRefresh(btn) {
  try {
    if (btn) {
      btn.disabled = true;
      btn.dataset.orig = btn.innerHTML;
      btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Starting...';
    }

    const res = await fetch('/admin/refresh_stocks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    });
    const data = await res.json();

    if (res.status === 202 || data.message) {
      showNotification('Server refresh started (background). It may take a few minutes to populate.', 'info');
      // schedule a client-side refresh after a short delay to pick up new cached data
      setTimeout(() => { fetchStocksAndAI(); }, 8000);
    } else {
      showNotification(data.error || 'Failed to start server refresh', 'error');
    }
  } catch (err) {
    console.error('Admin refresh error:', err);
    showNotification('Failed to trigger server refresh', 'error');
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = btn.dataset.orig || '<i class="fas fa-play-circle"></i> Server Refresh';
    }
  }
}

setInterval(refreshData, 120000);
setInterval(updateRefreshTimer, 1000);

// =======================
// Fetch and Display News
// =======================
async function fetchNews() {
  try {
    const response = await fetch('/api/news');
    const news = await response.json();
    displayNews(news);
  } catch (error) {
    console.error('Error fetching news:', error);
    document.getElementById('news-grid').innerHTML = '<div class="loading-card"><i class="fas fa-exclamation-circle"></i> Failed to load news</div>';
  }
}

function displayNews(newsArray) {
  const newsGrid = document.getElementById('news-grid');
  
  if (!newsArray || newsArray.length === 0) {
    newsGrid.innerHTML = '<div class="loading-card"><i class="fas fa-newspaper"></i> No news available at the moment</div>';
    return;
  }
  
  newsGrid.innerHTML = '';
  
  newsArray.forEach(item => {
    const newsCard = document.createElement('div');
    newsCard.classList.add('news-card');

    const source = item.source || (item.link ? (() => { try { return new URL(item.link).hostname.replace('www.', ''); } catch(e){ return 'Unknown'; } })() : 'Unknown');
    const time = item.time || 'Recently';
    const link = item.link || '#';
    const title = item.title || 'Untitled';
    const desc = item.description || 'No description available';
    
    const sourceIcon = getSourceIcon(source);
    const truncatedDesc = desc.length > 120 ? desc.substring(0, 120) + '...' : desc;

    newsCard.innerHTML = `
      <div class="news-header">
        <span class="news-source">
          <i class="${sourceIcon}"></i> ${source}
        </span>
        <span class="news-time"><i class="fas fa-clock"></i> ${time}</span>
      </div>
      <h3 class="news-title"><a href="${link}" target="_blank" rel="noopener noreferrer">${title}</a></h3>
      <p class="news-description">${truncatedDesc}</p>
      <div class="news-meta">
        <small><i class="fas fa-briefcase"></i> ${source} • ${time}</small>
      </div>
    `;

    newsCard.addEventListener('click', () => {
      if (link !== '#') {
        window.open(link, '_blank');
      }
    });

    newsGrid.appendChild(newsCard);
  });
}

function getSourceIcon(source) {
  const sourceMap = {
    'bloomberg.com': 'fas fa-landmark',
    'cnbc.com': 'fas fa-tv',
    'reuters.com': 'fas fa-newspaper',
    'ft.com': 'fas fa-book',
    'wsj.com': 'fas fa-scroll',
    'marketwatch.com': 'fas fa-chart-line',
    'yahoo.com': 'fas fa-y',
    'google.com': 'fas fa-search',
    'bbc.com': 'fas fa-broadcast-tower',
    'default': 'fas fa-newspaper'
  };
  
  const normalizedSource = source.toLowerCase();
  for (const key in sourceMap) {
    if (normalizedSource.includes(key)) {
      return sourceMap[key];
    }
  }
  return sourceMap['default'];
}

// =======================
// Initialize on page load
// =======================
window.onload = () => {
  lastRefreshTime = Date.now();
  fetchStocksAndAI();
  fetchNews();
  loadPortfolioPerformance();

  // Trigger server-side refresh immediately when dashboard loads
  // This ensures fresh data is loaded proactively
  setTimeout(() => {
    adminRefresh(null, true); // Silent refresh on load
  }, 2000); // Wait 2 seconds for initial load to complete
};

// =======================
// Enhanced admin refresh for silent loading
// =======================
async function adminRefresh(btn, silent = false) {
  try {
    if (btn && !silent) {
      btn.disabled = true;
      btn.dataset.orig = btn.innerHTML;
      btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Starting...';
    }

    const res = await fetch('/admin/refresh_stocks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    });
    const data = await res.json();

    if (res.status === 202 || data.message) {
      if (!silent) {
        showNotification('Server refresh started (background). It may take a few minutes to populate.', 'info');
      }
      console.log('Server refresh triggered on dashboard load');
      // Schedule a client-side refresh after delay to pick up new cached data
      setTimeout(() => {
        fetchStocksAndAI();
        if (!silent) {
          showNotification('Dashboard data refreshed!', 'success');
        }
      }, 10000); // Wait 10 seconds for server refresh to complete
    } else {
      if (!silent) {
        showNotification(data.error || 'Failed to start server refresh', 'error');
      }
    }
  } catch (err) {
    console.error('Admin refresh error:', err);
    if (!silent) {
      showNotification('Failed to trigger server refresh', 'error');
    }
  } finally {
    if (btn && !silent) {
      btn.disabled = false;
      btn.innerHTML = btn.dataset.orig || '<i class="fas fa-play-circle"></i> Server Refresh';
    }
  }
}

// =======================
// QUICK SCENARIOS
// =======================
function loadQuickScenario(scenarioType) {
  // Redirect to simulator page with the selected scenario
  window.location.href = `/simulator?scenario=${scenarioType}`;
}

// =======================
// Add CSS for positive/negative changes
// =======================
const style = document.createElement('style');
style.textContent = `
  .positive { color: #00ff00; }
  .negative { color: #ff4444; }
  .symbol-badge {
    background: rgba(0, 255, 255, 0.1);
    padding: 4px 8px;
    border-radius: 5px;
    color: #00ffff;
    font-weight: 600;
  }
`;
document.head.appendChild(style);
