let topChartCoins = [];
let coinChartInstance;

export function initTopCharts(coinList) {
  const selector = document.getElementById('coinSelector');
  const addBtn = document.getElementById('addChartBtn');
  const timeframeSel = document.getElementById('globalTimeframe');

  coinList.forEach(c => {
    const opt = document.createElement('option');
    opt.value = c;
    opt.textContent = c.toUpperCase();
    selector.appendChild(opt);
  });

  addBtn.addEventListener('click', () => {
    const coin = selector.value;
    if (coin && !topChartCoins.includes(coin) && topChartCoins.length < 3) {
      topChartCoins.push(coin);
      renderTopCharts(timeframeSel.value);
    }
  });

  timeframeSel.addEventListener('change', () => renderTopCharts(timeframeSel.value));
}

async function loadMiniChart(coin, canvasId, days) {
  const url = `https://api.coingecko.com/api/v3/coins/${coin}/market_chart?vs_currency=usd&days=${days}`;
  const data = await fetch(url).then(r => r.json());
  const labels = data.prices.map(p => new Date(p[0]).toLocaleDateString());
  const prices = data.prices.map(p => p[1]);

  new Chart(document.getElementById(canvasId), {
    type:'line',
    data:{labels,datasets:[{
      label:`${coin.toUpperCase()} USD`,
      data:prices,
      borderColor:'#0ff',
      pointRadius:0,
      tension:0.2
    }]},
    options:{
      responsive:true,
      plugins:{
        legend:{labels:{color:'#fff'}},
        tooltip:{
          enabled:true,
          backgroundColor:'#111',
          titleColor:'#0ff',
          bodyColor:'#fff'
        }
      },
      scales:{x:{display:false},y:{display:false}}
    }
  });
}

export function renderTopCharts(days) {
  const container = document.getElementById('topCharts');
  container.innerHTML = '';
  topChartCoins.forEach(coin => {
    const div = document.createElement('div');
    div.className = 'border border-white p-2 flex flex-col';
    div.innerHTML = `
      <div class="flex justify-between items-center border-b border-white mb-1">
        <span>${coin.toUpperCase()}</span>
        <button data-remove="${coin}" class="text-red-400">X</button>
      </div>
      <canvas id="mini-${coin}" class="h-40"></canvas>
    `;
    container.appendChild(div);
    div.querySelector('[data-remove]').addEventListener('click',()=>{
      topChartCoins = topChartCoins.filter(x => x !== coin);
      renderTopCharts(days);
    });
    loadMiniChart(coin, `mini-${coin}`, days);
  });
}

// Modal chart
export function initModal() {
  const modal = document.getElementById('chartModal');
  const closeBtn = document.getElementById('closeModal');
  const title = document.getElementById('chartTitle');
  const timeframeSel = document.getElementById('modalTimeframe');
  const ctx = document.getElementById('coinChart').getContext('2d');

  closeBtn.addEventListener('click', () => {
    modal.classList.add('hidden');
    if (coinChartInstance) { coinChartInstance.destroy(); coinChartInstance = null; }
  });

  document.getElementById('priceTable').addEventListener('click', async e => {
    const row = e.target.closest('tr[data-coin]');
    if (!row) return;
    const coin = row.getAttribute('data-coin');
    title.textContent = `${coin.toUpperCase()} Price Chart`;
    modal.classList.remove('hidden');
    await showCoinChart(coin, ctx, timeframeSel.value);

    timeframeSel.onchange = () => showCoinChart(coin, ctx, timeframeSel.value);
  });
}

async function showCoinChart(coin, ctx, days) {
  const url = `https://api.coingecko.com/api/v3/coins/${coin}/market_chart?vs_currency=usd&days=${days}`;
  const data = await fetch(url).then(r => r.json());
  const labels = data.prices.map(p => new Date(p[0]).toLocaleDateString());
  const prices = data.prices.map(p => p[1]);

  if (coinChartInstance) coinChartInstance.destroy();

  coinChartInstance = new Chart(ctx, {
    type:'line',
    data:{labels,datasets:[{
      label:`${coin.toUpperCase()} USD`,
      data:prices,
      borderColor:'#0ff',
      backgroundColor:'rgba(0,255,255,0.1)',
      tension:0.1,
      pointRadius:0
    }]},
    options:{
      responsive:true,
      maintainAspectRatio:false,
      plugins:{
        legend:{labels:{color:'#fff'}},
        tooltip:{enabled:true,backgroundColor:'#111',titleColor:'#0ff',bodyColor:'#fff'}
      },
      scales:{
        x:{ticks:{color:'#fff'},grid:{color:'#444'}},
        y:{ticks:{color:'#fff'},grid:{color:'#444'}}
      }
    }
  });
}
