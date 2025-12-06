// Company Details JavaScript

let companyData = null;
let tvChart = null;
let currentPeriod = '1y';

// Load company data on page load
window.onload = async () => {
  await loadCompanyData();
};

// Fetch company details
async function loadCompanyData() {
  try {
    const response = await fetch(`/api/company/${symbol}`);
    const data = await response.json();
    
    if (data.error) {
      alert('Error loading company data: ' + data.error);
      return;
    }
    
    companyData = data;
    displayCompanyData(data);
    createTradingViewChart(data.history);
    
    // Hide loading, show content
    document.getElementById('loading-screen').style.display = 'none';
    document.getElementById('company-content').style.display = 'block';
  } catch (error) {
    console.error('Error:', error);
    alert('Failed to load company data');
  }
}

// Create TradingView Lightweight Chart
function createTradingViewChart(history) {
  const chartContainer = document.getElementById('tradingview-chart');
  chartContainer.innerHTML = ''; // Clear previous chart
  
  // Create chart with dark theme
  const chart = LightweightCharts.createChart(chartContainer, {
    layout: {
      background: { color: '#1a1a1a' },
      textColor: '#aaa',
    },
    width: chartContainer.offsetWidth,
    height: 500,
    timeScale: {
      timeVisible: true,
      secondsVisible: false,
    },
    grid: {
      hStyle: 'rgba(255, 255, 255, 0.05)',
      vLines: { color: 'rgba(255, 255, 255, 0.05)' },
    },
  });
  
  // Prepare candlestick data
  const candleData = [];
  for (let i = 0; i < history.length; i++) {
    const h = history[i];
    candleData.push({
      time: h.date,
      open: h.open,
      high: h.high,
      low: h.low,
      close: h.close,
    });
  }
  
  // Create candlestick series
  const candlestickSeries = chart.addCandlestickSeries({
    upColor: '#26a69a',
    downColor: '#ef5350',
    borderVisible: false,
    wickUpColor: '#26a69a',
    wickDownColor: '#ef5350',
  });
  
  candlestickSeries.setData(candleData);
  
  // Auto-scale
  chart.timeScale().fitContent();
  
  // Add volume indicator (optional)
  const volumeData = history.map(h => ({
    time: h.date,
    value: h.volume,
  }));
  
  const volumeSeries = chart.addHistogramSeries({
    color: '#26a69a',
    priceFormat: { type: 'volume' },
  });
  
  volumeSeries.setData(volumeData);
  
  tvChart = { chart, candlestickSeries, volumeSeries };
  
  // Handle window resize
  window.addEventListener('resize', () => {
    if (chartContainer.offsetWidth > 0) {
      chart.applyOptions({ width: chartContainer.offsetWidth });
    }
  });
}

// Display company data
function displayCompanyData(data) {
  // Company Header
  document.getElementById('company-name').textContent = data.name;
  document.getElementById('current-price').textContent = `$${data.current_price?.toFixed(2) || '0.00'}`;
  
  // Price change
  const change = data.current_price - data.previous_close;
  const changePercent = ((change / data.previous_close) * 100).toFixed(2);
  const priceChangeEl = document.getElementById('price-change');
  priceChangeEl.textContent = `${change >= 0 ? '+' : ''}$${change.toFixed(2)} (${change >= 0 ? '+' : ''}${changePercent}%)`;
  priceChangeEl.className = `price-change ${change >= 0 ? 'positive' : 'negative'}`;
  
  // Quick Stats
  document.getElementById('stat-open').textContent = `$${data.open?.toFixed(2) || '-'}`;
  document.getElementById('stat-high').textContent = `$${data.day_high?.toFixed(2) || '-'}`;
  document.getElementById('stat-low').textContent = `$${data.day_low?.toFixed(2) || '-'}`;
  document.getElementById('stat-volume').textContent = formatNumber(data.volume);
  document.getElementById('stat-marketcap').textContent = formatMarketCap(data.market_cap);
  document.getElementById('stat-pe').textContent = data.pe_ratio?.toFixed(2) || '-';
  
  // Company Info
  document.getElementById('info-sector').textContent = data.sector || 'N/A';
  document.getElementById('info-industry').textContent = data.industry || 'N/A';
  document.getElementById('info-employees').textContent = formatNumber(data.employees) || 'N/A';
  
  const websiteEl = document.getElementById('info-website');
  if (data.website && data.website !== 'N/A') {
    websiteEl.href = data.website;
    websiteEl.textContent = data.website;
  } else {
    websiteEl.textContent = 'N/A';
    websiteEl.removeAttribute('href');
  }
  
  document.getElementById('company-desc').textContent = data.description;
  
  // Financial Metrics
  document.getElementById('metric-52high').textContent = `$${data['52week_high']?.toFixed(2) || '0.00'}`;
  document.getElementById('metric-52low').textContent = `$${data['52week_low']?.toFixed(2) || '0.00'}`;
  document.getElementById('metric-eps').textContent = `$${data.eps?.toFixed(2) || '0.00'}`;
  document.getElementById('metric-dividend').textContent = data.dividend_yield ? `${(data.dividend_yield * 100).toFixed(2)}%` : 'N/A';
  document.getElementById('metric-beta').textContent = data.beta?.toFixed(2) || 'N/A';
  document.getElementById('metric-avgvol').textContent = formatNumber(data.avg_volume);
  
  // Historical Data Table
  displayHistoricalData(data.history.slice(-30).reverse());
}

// Display historical data table
function displayHistoricalData(history) {
  const tbody = document.getElementById('history-tbody');
  tbody.innerHTML = '';
  
  history.forEach(row => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${row.date}</td>
      <td>$${row.open}</td>
      <td>$${row.high}</td>
      <td>$${row.low}</td>
      <td>$${row.close}</td>
      <td>${formatNumber(row.volume)}</td>
    `;
    tbody.appendChild(tr);
  });
}

// Change chart period
async function changeChartPeriod(period) {
  currentPeriod = period;
  
  // Remove active class from all buttons
  document.querySelectorAll('.chart-btn').forEach(btn => {
    btn.classList.remove('active');
  });
  
  // Add active class to clicked button
  event.target.classList.add('active');
  
  // Filter existing data based on period
  let filteredHistory = companyData.history;
  
  switch(period) {
    case '1mo':
      filteredHistory = companyData.history.slice(-30);
      break;
    case '3mo':
      filteredHistory = companyData.history.slice(-90);
      break;
    case '6mo':
      filteredHistory = companyData.history.slice(-180);
      break;
    case '1y':
      filteredHistory = companyData.history;
      break;
  }
  
  // Recreate chart with filtered data
  createTradingViewChart(filteredHistory);
}

// Helper functions
function formatNumber(num) {
  if (!num) return 'N/A';
  
  if (num >= 1e12) return (num / 1e12).toFixed(2) + 'T';
  if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
  if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
  if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
  
  return num.toLocaleString();
}

function formatMarketCap(num) {
  if (!num) return 'N/A';
  
  if (num >= 1e12) return '$' + (num / 1e12).toFixed(2) + 'T';
  if (num >= 1e9) return '$' + (num / 1e9).toFixed(2) + 'B';
  if (num >= 1e6) return '$' + (num / 1e6).toFixed(2) + 'M';
  
  return '$' + num.toLocaleString();
}
