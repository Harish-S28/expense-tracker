// ── Navigation ─────────────────────────────────────────
const navBtns = document.querySelectorAll('.nav-btn');
const pages   = document.querySelectorAll('.page');

navBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    navBtns.forEach(b => b.classList.remove('active'));
    pages.forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('page-' + btn.dataset.page).classList.add('active');
    if (btn.dataset.page === 'dashboard') loadDashboard();
    if (btn.dataset.page === 'history')   loadHistory();
    if (btn.dataset.page === 'add')       loadCategories();
  });
});

// ── Default categories ─────────────────────────────────
const DEFAULT_CATS = ['Food', 'Transport', 'Shopping', 'Bills', 'Health', 'Entertainment', 'Education', 'Other'];

// ── Helpers ────────────────────────────────────────────
const fmt = n => '₹' + Number(n).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

async function api(path, opts = {}) {
  const res = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...opts
  });
  return res.json();
}

// ── ADD EXPENSE ────────────────────────────────────────
function loadCategories() {
  const pills = document.getElementById('cat-pills');
  pills.innerHTML = DEFAULT_CATS.map(c =>
    `<button class="cat-pill" data-cat="${c}">${c}</button>`
  ).join('');
  pills.querySelectorAll('.cat-pill').forEach(pill => {
    pill.addEventListener('click', () => {
      pills.querySelectorAll('.cat-pill').forEach(p => p.classList.remove('selected'));
      pill.classList.add('selected');
      document.getElementById('f-category').value = pill.dataset.cat;
    });
  });

  // Default date = today
  const today = new Date().toISOString().split('T')[0];
  document.getElementById('f-date').value = today;
}

document.getElementById('btn-add').addEventListener('click', async () => {
  const date     = document.getElementById('f-date').value;
  const amount   = document.getElementById('f-amount').value;
  const category = document.getElementById('f-category').value.trim();
  const note     = document.getElementById('f-note').value.trim();
  const msg      = document.getElementById('add-msg');

  msg.className = 'msg';
  if (!date || !amount || !category) {
    msg.textContent = 'Please fill in date, amount and category.';
    msg.className = 'msg error';
    return;
  }

  try {
    await api('/api/expenses', {
      method: 'POST',
      body: JSON.stringify({ date, amount: parseFloat(amount), category, note })
    });
    msg.textContent = '✓ Expense saved!';
    msg.className = 'msg success';
    document.getElementById('f-amount').value = '';
    document.getElementById('f-note').value = '';
    document.getElementById('f-category').value = '';
    document.querySelectorAll('.cat-pill').forEach(p => p.classList.remove('selected'));
    setTimeout(() => { msg.className = 'msg'; }, 2500);
  } catch {
    msg.textContent = 'Failed to save. Is the server running?';
    msg.className = 'msg error';
  }
});

// ── HISTORY ────────────────────────────────────────────
async function loadHistory() {
  const search   = document.getElementById('h-search').value;
  const category = document.getElementById('h-category').value;
  const month    = document.getElementById('h-month').value;

  const params = new URLSearchParams();
  if (search)   params.set('search', search);
  if (category) params.set('category', category);
  if (month)    params.set('month', month);

  const expenses = await api('/api/expenses?' + params);
  const body     = document.getElementById('history-body');
  const empty    = document.getElementById('history-empty');

  body.innerHTML = '';
  if (expenses.length === 0) { empty.style.display = 'block'; return; }
  empty.style.display = 'none';

  expenses.forEach(e => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${e.date}</td>
      <td><span class="cat-badge">${e.category}</span></td>
      <td style="color:var(--text-muted);font-size:13px">${e.note || '—'}</td>
      <td class="amount-cell">${fmt(e.amount)}</td>
      <td><button class="btn-del" data-id="${e.id}" title="Delete">✕</button></td>
    `;
    body.appendChild(tr);
  });

  body.querySelectorAll('.btn-del').forEach(btn => {
    btn.addEventListener('click', async () => {
      if (!confirm('Delete this expense?')) return;
      await api('/api/expenses/' + btn.dataset.id, { method: 'DELETE' });
      loadHistory();
    });
  });

  // Populate category filter
  const cats = await api('/api/categories');
  const sel  = document.getElementById('h-category');
  const cur  = sel.value;
  sel.innerHTML = '<option value="">All categories</option>';
  cats.forEach(c => { sel.innerHTML += `<option value="${c}" ${c===cur?'selected':''}>${c}</option>`; });
}

['h-search','h-category','h-month'].forEach(id => {
  document.getElementById(id).addEventListener('change', loadHistory);
  if (id === 'h-search')
    document.getElementById(id).addEventListener('input', loadHistory);
});
document.getElementById('h-clear').addEventListener('click', () => {
  document.getElementById('h-search').value = '';
  document.getElementById('h-category').value = '';
  document.getElementById('h-month').value = '';
  loadHistory();
});

// ── DASHBOARD ──────────────────────────────────────────
let catChart, trendChart;
const COLORS = ['#6c63ff','#22d3a0','#f59e0b','#f87171','#38bdf8','#a78bfa','#fb7185','#34d399'];

async function loadDashboard() {
  const month  = document.getElementById('dash-month').value;
  const params = month ? '?month=' + month : '';
  const data   = await api('/api/analytics' + params);

  // Stats
  document.getElementById('stat-total').textContent = fmt(data.total);
  document.getElementById('stat-count').textContent = data.count;
  document.getElementById('stat-avg').textContent   = fmt(data.count ? data.total / data.count : 0);

  // Category chart
  const catCtx = document.getElementById('chart-cat').getContext('2d');
  if (catChart) catChart.destroy();
  catChart = new Chart(catCtx, {
    type: 'doughnut',
    data: {
      labels:   data.by_category.map(c => c.category),
      datasets: [{ data: data.by_category.map(c => c.total), backgroundColor: COLORS, borderWidth: 0 }]
    },
    options: {
      plugins: { legend: { display: false } },
      cutout: '65%'
    }
  });

  // Legend
  const legend = document.getElementById('cat-legend');
  legend.innerHTML = data.by_category.map((c, i) =>
    `<div class="legend-item">
      <div class="legend-dot" style="background:${COLORS[i % COLORS.length]}"></div>
      ${c.category} · ${fmt(c.total)}
    </div>`
  ).join('');

  // Trend chart
  const trendCtx = document.getElementById('chart-trend').getContext('2d');
  if (trendChart) trendChart.destroy();
  trendChart = new Chart(trendCtx, {
    type: 'bar',
    data: {
      labels:   data.trend.map(t => t.month),
      datasets: [{
        label: 'Spent',
        data:  data.trend.map(t => t.total),
        backgroundColor: 'rgba(108,99,255,0.5)',
        borderColor: '#6c63ff',
        borderWidth: 2,
        borderRadius: 6
      }]
    },
    options: {
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: '#8892b0' }, grid: { color: '#2e3248' } },
        y: { ticks: { color: '#8892b0', callback: v => '₹' + v }, grid: { color: '#2e3248' } }
      }
    }
  });

  // Top days
  const tbody = document.querySelector('#top-days-table tbody');
  const max   = data.by_date[0]?.total || 1;
  tbody.innerHTML = data.by_date.map(d => `
    <tr>
      <td>${d.date}</td>
      <td class="amount-cell">${fmt(d.total)}</td>
      <td>
        <div class="bar-wrap">
          <div class="bar-fill" style="width:${(d.total/max*100).toFixed(1)}%"></div>
        </div>
      </td>
    </tr>`).join('');
}

document.getElementById('dash-month').addEventListener('change', loadDashboard);
document.getElementById('dash-clear').addEventListener('click', () => {
  document.getElementById('dash-month').value = '';
  loadDashboard();
});

// ── Init ───────────────────────────────────────────────
loadDashboard();
loadCategories();
