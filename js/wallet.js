import { ethers } from "https://cdn.jsdelivr.net/npm/ethers/dist/ethers.min.js";

export function initWallet() {
  const connectBtn = document.getElementById('connectBtn');
  const walletInfo = document.getElementById('walletInfo');

  connectBtn.addEventListener('click', async () => {
    if (!window.ethereum) {
      walletInfo.textContent = 'MetaMask not found. Install it to continue.';
      return;
    }
    try {
      await window.ethereum.request({ method: 'eth_requestAccounts' });
      const provider = new ethers.providers.Web3Provider(window.ethereum);
      const signer = provider.getSigner();
      const address = await signer.getAddress();
      const balance = await provider.getBalance(address);
      walletInfo.innerHTML = `Connected: ${address}<br>Balance: ${parseFloat(ethers.utils.formatEther(balance)).toFixed(4)} ETH`;
    } catch (e) {
      console.error(e);
      walletInfo.textContent = 'Connection failed.';
    }
  });
}
