import { initWallet } from './wallet.js';
import { fetchMarketData, renderMarketTable, coins } from './market.js';
import { computeRatios, renderRatios } from './ratios.js';
import { initTopCharts, renderTopCharts, initModal } from './charts.js';

initWallet();
initTopCharts(coins);
initModal();

async function refreshData() {
  const data = await fetchMarketData();
  renderMarketTable(data);
  renderRatios(computeRatios(data));
}

refreshData();
setInterval(refreshData, 60000);
