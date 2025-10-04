let pinnedRatios = [];

export function computeRatios(data) {
  const btc = data.find(c => c.id === 'bitcoin');
  const eth = data.find(c => c.id === 'ethereum');
  const sol = data.find(c => c.id === 'solana');
  const totalMcap = data.reduce((s, c) => s + c.market_cap, 0);

  return [
    { name: 'BTC Dominance', value: `${(btc.market_cap / totalMcap * 100).toFixed(1)}%` },
    { name: 'ETH/BTC', value: (eth.current_price / btc.current_price).toFixed(4) },
    { name: 'SOL/ETH', value: (sol.current_price / eth.current_price).toFixed(4) },
    { name: 'Total Mcap', value: `$${(totalMcap/1e12).toFixed(2)}T` },
    { name: 'BTC 24h Vol', value: `$${(btc.total_volume/1e9).toFixed(2)}B` },
    { name: 'ETH 24h Vol', value: `$${(eth.total_volume/1e9).toFixed(2)}B` },
    { name: 'BTC/ETH Vol Ratio', value: (btc.total_volume/eth.total_volume).toFixed(2) },
    { name: 'Top3 Mcap Share', value: ((btc.market_cap+eth.market_cap+sol.market_cap)/totalMcap*100).toFixed(1)+'%' },
    { name: 'BTC/ETH Price Ratio', value: (btc.current_price/eth.current_price).toFixed(2) },
    { name: 'ETH Gas Proxy', value: `${Math.floor(Math.random()*200)} gwei` } // sample
  ];
}

function ratioCard(r, pinned=false) {
  const div = document.createElement('div');
  div.className = `ratio-card ${pinned ? 'pinned':''}`;
  div.innerHTML = `
    <div class="flex justify-between items-center">
      <span>${r.name}</span>
      <button class="text-cyan-400 text-xs pin-btn">${pinned?'UNPIN':'PIN'}</button>
    </div>
    <div class="mt-1">${r.value}</div>
  `;
  return div;
}

export function renderRatios(ratios) {
  const pinnedContainer = document.getElementById('pinnedRatios');
  const allContainer = document.getElementById('allRatios');
  pinnedContainer.innerHTML = '';
  allContainer.innerHTML = '';

  ratios.forEach(r => {
    const isPinned = pinnedRatios.includes(r.name);
    const card = ratioCard(r, isPinned);
    (isPinned ? pinnedContainer : allContainer).appendChild(card);
    card.querySelector('.pin-btn').addEventListener('click', () => {
      if (isPinned) pinnedRatios = pinnedRatios.filter(x => x !== r.name);
      else if (pinnedRatios.length < 3) pinnedRatios.push(r.name);
      renderRatios(ratios);
    });
  });
}
