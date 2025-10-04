export const coins = [
  'bitcoin','ethereum','solana','binancecoin','cardano',
  'dogecoin','ripple','toncoin','avalanche-2','chainlink'
];

export async function fetchMarketData() {
  const url = `https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=${coins.join(',')}`;
  return await fetch(url).then(r => r.json());
}

export function renderMarketTable(data) {
  const tbody = document.getElementById('priceTable');
  tbody.innerHTML = '';
  data.forEach(c => {
    const tr = document.createElement('tr');
    tr.className = 'border-b border-white hover:bg-gray-800 cursor-pointer';
    tr.setAttribute('data-coin', c.id);
    tr.innerHTML = `
      <td class="p-2 text-cyan-400 underline">${c.name}</td>
      <td class="p-2 text-right">$${c.current_price.toLocaleString()}</td>
      <td class="p-2 text-right ${c.price_change_percentage_24h>=0?'text-green-400':'text-red-400'}">
        ${c.price_change_percentage_24h.toFixed(2)}%
      </td>
      <td class="p-2 text-right">$${(c.market_cap/1e9).toFixed(1)}B</td>
    `;
    tbody.appendChild(tr);
  });
}
