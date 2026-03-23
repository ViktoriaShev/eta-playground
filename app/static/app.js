async function fetchJson(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return response.json();
}

function formatNumber(value) {
  if (value === undefined || value === null || Number.isNaN(Number(value))) return '—';
  return Number(value).toFixed(1);
}

function renderTrains(state) {
  const container = document.getElementById('train-list');
  const trainIds = Object.keys(state || {});

  if (!trainIds.length) {
    container.innerHTML = '<div class="card muted">Пока нет данных. Нажмите «Отправить демо-данные».</div>';
    return;
  }

  container.innerHTML = trainIds.map((trainId) => {
    const item = state[trainId] || {};
    const position = item.position || {};
    const event = item.event || {};
    const prediction = item.prediction || {};
    const etaMin = prediction.eta_sec ? prediction.eta_sec / 60 : null;

    return `
      <article class="train-card">
        <div class="row">
          <div>
            <h3>${trainId}</h3>
            <div class="muted">Линия: ${position.line_id || '—'} · Станция: ${position.station_id || '—'}</div>
          </div>
          <div class="badge ok">ETA: ${etaMin ? formatNumber(etaMin) + ' мин' : '—'}</div>
        </div>
        <div class="metrics">
          <div class="metric">
            <div class="metric-label">Расстояние</div>
            <div class="metric-value">${formatNumber(position.distance_to_station_km)} км</div>
          </div>
          <div class="metric">
            <div class="metric-label">Скорость</div>
            <div class="metric-value">${formatNumber(position.speed_kmh)} км/ч</div>
          </div>
          <div class="metric">
            <div class="metric-label">Задержка</div>
            <div class="metric-value">${formatNumber(prediction.delay_sec)} сек</div>
          </div>
          <div class="metric">
            <div class="metric-label">Историческое ETA</div>
            <div class="metric-value">${formatNumber(prediction.historical_avg_sec)} сек</div>
          </div>
        </div>
        <p><b>Последнее событие:</b> ${event.type || 'нет'} ${event.delay_sec ? `(${event.delay_sec} сек)` : ''}</p>
        <p><b>Время расчета:</b> ${prediction.generated_at || '—'}</p>
      </article>
    `;
  }).join('');
}

function renderEvents(items) {
  const container = document.getElementById('events-list');
  if (!items.length) {
    container.innerHTML = '<div class="muted">Сообщений пока нет.</div>';
    return;
  }

  container.innerHTML = items.map((item) => `
    <div class="list-item">
      <div class="row"><b>${item.topic}</b><span class="muted">${item.payload.ts || 'без ts'}</span></div>
      <code>${JSON.stringify(item.payload, null, 2)}</code>
    </div>
  `).join('');
}

async function refresh() {
  try {
    const [health, config, state, events] = await Promise.all([
      fetchJson('/health'),
      fetchJson('/config'),
      fetchJson('/state'),
      fetchJson('/events')
    ]);

    const statusNode = document.getElementById('service-status');
    statusNode.textContent = health.status === 'ok' ? 'Сервис работает' : 'Ошибка';
    statusNode.classList.toggle('ok', health.status === 'ok');

    document.getElementById('config-view').textContent = JSON.stringify(config, null, 2);
    renderTrains(state);
    renderEvents(events.items || []);
  } catch (error) {
    document.getElementById('service-status').textContent = 'Не удалось получить данные';
  }
}

document.getElementById('send-demo').addEventListener('click', async () => {
  const button = document.getElementById('send-demo');
  button.disabled = true;
  button.textContent = 'Отправка...';
  try {
    await fetchJson('/demo/send', { method: 'POST' });
    setTimeout(refresh, 1000);
  } finally {
    setTimeout(() => {
      button.disabled = false;
      button.textContent = 'Отправить демо-данные';
    }, 1200);
  }
});

refresh();
setInterval(refresh, 3000);
