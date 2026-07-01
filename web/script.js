/* ===================== Fallback data (used only if the API call fails) ===================== */
const sampleInsights = {
  metadata: { generated_at: new Date().toISOString(), total_records: 1500, total_days: 180 },
  insights: {
    total_days_analyzed: 180,
    date_range: { start: "2024-01-01", end: "2024-06-29" },
    risk_metrics: {
      total_pnl: 15400.50, total_trades: 450, win_rate: 58.5,
      total_volume: 850000, avg_trade_size: 1888.89, sharpe_ratio: 1.45
    },
    performance_by_sentiment: {
      "Extreme Fear": { avg_pnl_pct: 2.15, total_pnl: 3200, win_rate: 62.5, trade_count: 40,  volume: 75000 },
      "Fear":         { avg_pnl_pct: 1.85, total_pnl: 5600, win_rate: 60.2, trade_count: 120, volume: 250000 },
      "Neutral":      { avg_pnl_pct: 1.20, total_pnl: 3200, win_rate: 55.0, trade_count: 150, volume: 300000 },
      "Greed":        { avg_pnl_pct: 0.85, total_pnl: 2200, win_rate: 52.5, trade_count: 100, volume: 150000 },
      "Extreme Greed":{ avg_pnl_pct: -0.50,total_pnl: 1200, win_rate: 48.5, trade_count: 40,  volume: 75000 }
    },
    correlations: { sentiment_value_vs_pnl: 0.342, momentum_vs_returns: 0.285, volatility_vs_returns: -0.165 },
    sentiment_distribution: { "Fear": 140, "Neutral": 95, "Greed": 60, "Extreme Fear": 35, "Extreme Greed": 15 },
    recommendations: [
      { title: "Best Sentiment Environment",  description: "Trading performance is highest during Extreme Fear sentiment.", action: "Increase position sizing and take more trades during Extreme Fear phases." },
      { title: "Worst Sentiment Environment", description: "Trading performance is lowest during Extreme Greed sentiment.", action: "Reduce risk or avoid trading during Extreme Greed phases." },
      { title: "Solid Win Rate",              description: "Current win rate is 58.5%, above the 50% breakeven threshold.", action: "Maintain discipline; consider a modest increase in position size." },
      { title: "High Volatility Strategy",    description: "Trading performance improves during high-volatility periods.", action: "Increase activity and size during volatile market conditions." }
    ]
  }
};

const SENTIMENT_COLOR = {
  "Extreme Fear": "#C0392B", "Fear": "#E0724B", "Neutral": "#D4A24C",
  "Greed": "#7FB88A", "Extreme Greed": "#3FA36B"
};
const SENTIMENT_ORDER = ["Extreme Fear","Fear","Neutral","Greed","Extreme Greed"];

let activeFilter = null;
let perfChart = null, activeChartTab = 'performance';
let sortState = { key: null, dir: 1 };
let INSIGHTS = null;

/* ===================== Clock ===================== */
function tickClock(){
  const now = new Date();
  const s = now.toLocaleTimeString('en-US', { hour12:false });
  const el = document.getElementById('clock');
  if(el) el.textContent = s;
}
setInterval(tickClock, 1000); tickClock();

/* ===================== Load ===================== */
function loadInsights(){
  fetch('/api/insights')
    .then(r => {
      if(!r.ok) throw new Error('bad response');
      return r.json();
    })
    .then(data => render(data.insights || data))
    .catch(() => render(sampleInsights.insights));
}

function render(insights){
  INSIGHTS = insights;
  document.getElementById('footTime').textContent = new Date().toLocaleString();

  const content = document.getElementById('content');
  content.className = '';
  content.innerHTML = `
    ${renderHero(insights)}
    <section class="section" id="overview">
      <div class="section-head"><h2>Key Metrics</h2><span class="section-num mono">01 / Overview</span></div>
      <div class="section-desc">Aggregate performance across ${insights.total_days_analyzed} trading days, ${insights.date_range.start} – ${insights.date_range.end}.</div>
      <div class="stats-grid" id="statsGrid"></div>
    </section>

    <section class="section" id="sentiment">
      <div class="section-head"><h2>Market Sentiment Distribution</h2><span class="section-num mono">02 / Sentiment</span></div>
      <div class="section-desc">Click a regime to filter the chart and trade ledger below.</div>
      <div class="chip-row" id="chipRow"></div>
    </section>

    <section class="section" id="analysis">
      <div class="section-head"><h2>Performance Analysis</h2><span class="section-num mono">03 / Analysis</span></div>
      <div class="section-desc">How returns, win rate and correlated factors move with sentiment.</div>
      <div class="chart-tabs" id="chartTabs">
        <button data-tab="performance" class="active">Performance by Sentiment</button>
        <button data-tab="correlation">Factor Correlation</button>
      </div>
      <div class="chart-card"><canvas id="mainChart"></canvas></div>
    </section>

    <section class="section" id="strategy">
      <div class="section-head"><h2>Strategy Recommendations</h2><span class="section-num mono">04 / Strategy</span></div>
      <div class="section-desc">Read directly off the data above — no discretionary overlay.</div>
      <div class="rec-grid" id="recGrid"></div>
    </section>

    <section class="section" id="ledger">
      <div class="section-head"><h2>Performance by Sentiment</h2><span class="section-num mono">05 / Ledger</span></div>
      <div class="section-desc">Click column headers to sort. Filter is synced with the sentiment chips above.</div>
      <div class="table-wrap">
        <table>
          <thead><tr id="tableHead"></tr></thead>
          <tbody id="tableBody"></tbody>
        </table>
      </div>
    </section>
  `;

  renderStats(insights.risk_metrics, insights);
  renderChips(insights.sentiment_distribution);
  renderTable(insights.performance_by_sentiment);
  renderRecs(insights.recommendations);
  setupNav();
  setupChartTabs();
  buildChart();
  setupScrollReveal();
  animateCounters();
}

/* ===================== Hero + gauge ===================== */
function overallSentimentValue(insights){
  const weights = { "Extreme Fear": 10, "Fear": 30, "Neutral": 50, "Greed": 70, "Extreme Greed": 90 };
  const dist = insights.sentiment_distribution;
  let total = 0, weighted = 0;
  Object.entries(dist).forEach(([k,v]) => { total += v; weighted += v * weights[k]; });
  return total ? Math.round(weighted / total) : 50;
}

function labelForValue(v){
  if(v <= 20) return { text: "Extreme Fear", color: SENTIMENT_COLOR["Extreme Fear"] };
  if(v <= 40) return { text: "Fear", color: SENTIMENT_COLOR["Fear"] };
  if(v <= 60) return { text: "Neutral", color: SENTIMENT_COLOR["Neutral"] };
  if(v <= 80) return { text: "Greed", color: SENTIMENT_COLOR["Greed"] };
  return { text: "Extreme Greed", color: SENTIMENT_COLOR["Extreme Greed"] };
}

function renderHero(insights){
  const val = overallSentimentValue(insights);
  const lab = labelForValue(val);
  const m = insights.risk_metrics;
  return `
    <div class="hero">
      <div>
        <div class="eyebrow">Trader Sentiment Analysis</div>
        <h1>Trading edge shifts with <em>market emotion.</em></h1>
        <p class="lede">A cross-read of the Bitcoin Fear &amp; Greed Index against ${m.total_trades} executed trades — mapping which psychological regimes actually pay.</p>
        <div class="hero-metrics">
          <div>
            <div class="hero-metric-label">Net PnL</div>
            <div class="hero-metric-value up mono">$${m.total_pnl.toLocaleString()}</div>
          </div>
          <div>
            <div class="hero-metric-label">Win Rate</div>
            <div class="hero-metric-value mono">${m.win_rate}%</div>
          </div>
          <div>
            <div class="hero-metric-label">Sharpe</div>
            <div class="hero-metric-value mono">${m.sharpe_ratio}</div>
          </div>
        </div>
      </div>
      <div class="gauge-card">
        <div class="gauge-title">Composite Fear &amp; Greed</div>
        <div class="gauge-sub">Weighted across analyzed period</div>
        <div class="gauge-wrap">
          <svg viewBox="0 0 240 150" width="100%">
            <defs>
              <linearGradient id="gaugeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stop-color="${SENTIMENT_COLOR['Extreme Fear']}"/>
                <stop offset="25%" stop-color="${SENTIMENT_COLOR['Fear']}"/>
                <stop offset="50%" stop-color="${SENTIMENT_COLOR['Neutral']}"/>
                <stop offset="75%" stop-color="${SENTIMENT_COLOR['Greed']}"/>
                <stop offset="100%" stop-color="${SENTIMENT_COLOR['Extreme Greed']}"/>
              </linearGradient>
            </defs>
            <path d="M 20 130 A 100 100 0 0 1 220 130" fill="none" stroke="url(#gaugeGrad)" stroke-width="16" stroke-linecap="round"/>
            <line id="gaugeNeedle" x1="120" y1="130" x2="120" y2="40" stroke="#EAEFF7" stroke-width="3" stroke-linecap="round" transform="rotate(-90 120 130)"/>
            <circle cx="120" cy="130" r="6" fill="#EAEFF7"/>
          </svg>
          <div class="gauge-readout">
            <div class="gauge-value mono" id="gaugeValue" style="color:${lab.color}">0</div>
            <div class="gauge-label" id="gaugeLabel" style="color:${lab.color}">—</div>
          </div>
        </div>
      </div>
    </div>
  `;
}

function animateGaugeNeedle(targetVal){
  const needle = document.getElementById('gaugeNeedle');
  const valueEl = document.getElementById('gaugeValue');
  const labelEl = document.getElementById('gaugeLabel');
  const lab = labelForValue(targetVal);
  labelEl.textContent = lab.text.toUpperCase();
  labelEl.style.color = lab.color;
  valueEl.style.color = lab.color;

  const targetAngle = -90 + (targetVal / 100) * 180;
  let start = null;
  const duration = 1100;
  function step(ts){
    if(!start) start = ts;
    const progress = Math.min((ts - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const angle = -90 + eased * (targetAngle + 90);
    needle.setAttribute('transform', `rotate(${angle} 120 130)`);
    valueEl.textContent = Math.round(eased * targetVal);
    if(progress < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

/* ===================== Stats ===================== */
function renderStats(m, insights){
  const cards = [
    { label:'Total PnL', value:`$${m.total_pnl.toLocaleString()}`, sub:`${m.total_trades} trades`, cls:'up' },
    { label:'Win Rate', value:`${m.win_rate}%`, sub:'Profitable trades', cls:'up' },
    { label:'Total Volume', value:`$${(m.total_volume/1000).toFixed(1)}K`, sub:'USD traded', cls:'' },
    { label:'Avg Trade Size', value:`$${m.avg_trade_size.toLocaleString(undefined,{maximumFractionDigits:0})}`, sub:'Per trade', cls:'' },
    { label:'Sharpe Ratio', value:`${m.sharpe_ratio}`, sub:'Risk-adjusted return', cls:'up' },
    { label:'Period Analyzed', value:`${insights.total_days_analyzed} days`, sub:`${insights.date_range.start} → ${insights.date_range.end}`, cls:'' },
  ];
  document.getElementById('statsGrid').innerHTML = cards.map((c,i) => `
    <div class="stat-card" data-animate style="transition-delay:${i*40}ms">
      <div class="stat-label">${c.label}</div>
      <div class="stat-value ${c.cls}" data-count="${c.value}">${c.value}</div>
      <div class="stat-sub">${c.sub}</div>
    </div>
  `).join('');
}

function animateCounters(){
  document.querySelectorAll('[data-count]').forEach(el => {
    const target = el.getAttribute('data-count');
    const num = parseFloat(target.replace(/[^0-9.\-]/g,''));
    if(isNaN(num)){ return; }
    const prefix = target.match(/^[^0-9\-]*/)[0];
    const suffix = target.match(/[^0-9]*$/)[0];
    const isDecimal = target.includes('.');
    let startTs = null; const duration = 900;
    function step(ts){
      if(!startTs) startTs = ts;
      const p = Math.min((ts-startTs)/duration, 1);
      const eased = 1 - Math.pow(1-p, 3);
      const val = num * eased;
      el.textContent = prefix + (isDecimal ? val.toFixed(2) : Math.round(val).toLocaleString()) + suffix;
      if(p < 1) requestAnimationFrame(step);
      else el.textContent = target;
    }
    requestAnimationFrame(step);
  });
}

/* ===================== Chips ===================== */
function renderChips(dist){
  const max = Math.max(...Object.values(dist));
  document.getElementById('chipRow').innerHTML = SENTIMENT_ORDER
    .filter(k => dist[k] !== undefined)
    .map(k => `
      <div class="chip" data-key="${k}">
        <div class="chip-name">${k}</div>
        <div class="chip-count mono">${dist[k]} days</div>
        <div class="chip-bar"><div class="chip-bar-fill" style="width:0%; background:${SENTIMENT_COLOR[k]}" data-width="${(dist[k]/max*100).toFixed(0)}%"></div></div>
      </div>
    `).join('');

  document.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const key = chip.getAttribute('data-key');
      activeFilter = (activeFilter === key) ? null : key;
      document.querySelectorAll('.chip').forEach(c => c.classList.toggle('active', c.getAttribute('data-key') === activeFilter));
      applyFilter();
      buildChart();
    });
  });

  requestAnimationFrame(() => {
    document.querySelectorAll('.chip-bar-fill').forEach(f => f.style.width = f.getAttribute('data-width'));
  });
}

function applyFilter(){
  document.querySelectorAll('#tableBody tr').forEach(row => {
    const key = row.getAttribute('data-key');
    row.classList.toggle('dimmed', !!activeFilter && key !== activeFilter);
  });
}

/* ===================== Chart tabs ===================== */
function setupChartTabs(){
  document.querySelectorAll('#chartTabs button').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('#chartTabs button').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeChartTab = btn.getAttribute('data-tab');
      buildChart();
    });
  });
}

function buildChart(){
  const ctx = document.getElementById('mainChart');
  if(!ctx || !INSIGHTS) return;
  if(perfChart){ perfChart.destroy(); perfChart = null; }

  Chart.defaults.color = '#8FA0BC';
  Chart.defaults.font.family = "'Inter', sans-serif";
  Chart.defaults.borderColor = '#1B2740';

  if(activeChartTab === 'performance'){
    const perf = INSIGHTS.performance_by_sentiment;
    const labels = SENTIMENT_ORDER.filter(k => perf[k]);
    const avgPnl = labels.map(k => perf[k].avg_pnl_pct);
    const winRates = labels.map(k => perf[k].win_rate);
    const bgAvg = labels.map(k => (!activeFilter || activeFilter === k) ? '#D4A24C' : 'rgba(212,162,76,0.18)');
    const bgWin = labels.map(k => (!activeFilter || activeFilter === k) ? '#7FA6E0' : 'rgba(127,166,224,0.15)');

    perfChart = new Chart(ctx, {
      type: 'bar',
      data: { labels, datasets: [
        { label:'Avg PnL %', data: avgPnl, backgroundColor: bgAvg, borderRadius: 5, maxBarThickness: 34 },
        { label:'Win Rate %', data: winRates, backgroundColor: bgWin, borderRadius: 5, maxBarThickness: 34 }
      ]},
      options: {
        responsive:true, maintainAspectRatio:false,
        onClick: (evt, els) => {
          if(els.length){
            const key = labels[els[0].index];
            activeFilter = (activeFilter === key) ? null : key;
            document.querySelectorAll('.chip').forEach(c => c.classList.toggle('active', c.getAttribute('data-key') === activeFilter));
            applyFilter(); buildChart();
          }
        },
        plugins: {
          legend:{ labels:{ usePointStyle:true, boxWidth:7 } },
          tooltip: { backgroundColor:'#16213A', borderColor:'#24314B', borderWidth:1, padding:10, titleColor:'#EAEFF7', bodyColor:'#8FA0BC' }
        },
        scales: {
          y: { beginAtZero:true, grid:{ color:'#1B2740' } },
          x: { grid:{ display:false } }
        }
      }
    });
  } else {
    const corr = INSIGHTS.correlations;
    const labels = ['Sentiment vs PnL','Momentum vs Returns','Volatility vs Returns'];
    const values = Object.values(corr).map(c => +(c*100).toFixed(1));
    perfChart = new Chart(ctx, {
      type: 'radar',
      data: { labels, datasets: [{
        label:'Correlation (×100)', data: values,
        borderColor:'#D4A24C', backgroundColor:'rgba(212,162,76,0.14)',
        pointBackgroundColor:'#D4A24C', borderWidth:2
      }]},
      options: {
        responsive:true, maintainAspectRatio:false,
        plugins: {
          legend:{ display:false },
          tooltip: { backgroundColor:'#16213A', borderColor:'#24314B', borderWidth:1, padding:10, titleColor:'#EAEFF7', bodyColor:'#8FA0BC' }
        },
        scales: { r: { min:-50, max:100, grid:{ color:'#1B2740' }, angleLines:{ color:'#1B2740' }, pointLabels:{ color:'#8FA0BC', font:{size:11} }, ticks:{ backdropColor:'transparent', color:'#55698C' } } }
      }
    });
  }
}

/* ===================== Recommendations ===================== */
function renderRecs(recs){
  document.getElementById('recGrid').innerHTML = recs.map((r,i) => `
    <div class="rec-card" data-animate style="transition-delay:${i*50}ms">
      <h4>${r.title}</h4>
      <p>${r.description}</p>
      <div class="rec-action">→ ${r.action}</div>
    </div>
  `).join('');
}

/* ===================== Table ===================== */
const COLS = [
  { key:'sentiment', label:'Sentiment' },
  { key:'avg_pnl_pct', label:'Avg PnL %' },
  { key:'total_pnl', label:'Total PnL' },
  { key:'win_rate', label:'Win Rate' },
  { key:'trade_count', label:'Trades' },
  { key:'volume', label:'Volume' }
];

function renderTable(perf){
  document.getElementById('tableHead').innerHTML = COLS.map(c => `
    <th data-key="${c.key}">${c.label} <span class="arrow">▲</span></th>
  `).join('');

  document.querySelectorAll('#tableHead th').forEach(th => {
    th.addEventListener('click', () => {
      const key = th.getAttribute('data-key');
      if(sortState.key === key) sortState.dir *= -1;
      else { sortState.key = key; sortState.dir = 1; }
      document.querySelectorAll('#tableHead th').forEach(t => t.classList.remove('sorted'));
      th.classList.add('sorted');
      th.querySelector('.arrow').textContent = sortState.dir === 1 ? '▲' : '▼';
      drawRows(perf);
    });
  });

  drawRows(perf);
}

function drawRows(perf){
  let rows = SENTIMENT_ORDER.filter(k => perf[k]).map(k => ({ sentiment:k, ...perf[k] }));
  if(sortState.key){
    rows.sort((a,b) => {
      const av = a[sortState.key], bv = b[sortState.key];
      if(typeof av === 'string') return av.localeCompare(bv) * sortState.dir;
      return (av - bv) * sortState.dir;
    });
  }
  document.getElementById('tableBody').innerHTML = rows.map(row => {
    const pnlCls = row.avg_pnl_pct >= 0 ? 'up' : 'down';
    return `
      <tr data-key="${row.sentiment}">
        <td><span class="tag"><span class="dot" style="background:${SENTIMENT_COLOR[row.sentiment]}"></span>${row.sentiment}</span></td>
        <td class="mono ${pnlCls}">${row.avg_pnl_pct.toFixed(2)}%</td>
        <td class="mono ${pnlCls}">$${row.total_pnl.toLocaleString()}</td>
        <td class="mono">${row.win_rate.toFixed(1)}%</td>
        <td class="mono">${row.trade_count}</td>
        <td class="mono">$${(row.volume/1000).toFixed(1)}K</td>
      </tr>
    `;
  }).join('');
  applyFilter();
}

/* ===================== Nav + scroll reveal ===================== */
function setupNav(){
  const buttons = document.querySelectorAll('#navTabs button');
  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      const target = document.getElementById(btn.getAttribute('data-target'));
      if(target) target.scrollIntoView({ behavior:'smooth', block:'start' });
    });
  });

  const sections = document.querySelectorAll('.section');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if(entry.isIntersecting){
        const id = entry.target.id;
        buttons.forEach(b => b.classList.toggle('active', b.getAttribute('data-target') === id));
      }
    });
  }, { rootMargin: '-40% 0px -50% 0px' });
  sections.forEach(s => observer.observe(s));
}

function setupScrollReveal(){
  const els = document.querySelectorAll('[data-animate]');
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => { if(e.isIntersecting) e.target.classList.add('in'); });
  }, { threshold: 0.15 });
  els.forEach(el => io.observe(el));
}

window.addEventListener('load', () => {
  loadInsights();
  setTimeout(() => {
    if(INSIGHTS) animateGaugeNeedle(overallSentimentValue(INSIGHTS));
  }, 300);
});