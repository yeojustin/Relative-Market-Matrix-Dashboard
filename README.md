# Decentralized Feedback Wall + Live Crypto Feed (IPFS + ENS + MetaMask)

Features:
- Upload feedback (text + optional file) to IPFS via web3.storage
- Provenance: user signs message with MetaMask (personal_sign) before upload; signature stored in `meta.json`
- Live crypto feed from CoinGecko (free public API)
- Snapshot current feed to IPFS (web3.storage) and get CID + gateway link
- ENS resolve (address + contenthash) via ethers.js

## Setup (exact steps)
1. Clone this repo / copy files locally.

2. Create `js/config.js` from `js/config.example.js`:
   - `WEB3_STORAGE_TOKEN`: get it at https://web3.storage/ → Account → Create API Token. :contentReference[oaicite:4]{index=4}
   - `ETHEREUM_RPC_KEY` (optional): create free key at Alchemy or Infura if you want more reliable ENS lookups. If blank, ethers.getDefaultProvider is used. :contentReference[oaicite:5]{index=5}

   **Example `js/config.js`**:
   ```js
   export default {
     WEB3_STORAGE_TOKEN: 'YOUR_TOKEN_HERE',
     ETHEREUM_RPC_KEY: ''
   }
