# EVMORE Dashboard

Stateless Vue 3 + Rust (axum) dashboard served as a single container, deployed to `evmore.cryptuon.com` on CapRover.

## Components

- `frontend/` — Vue 3 + Tailwind SPA (existing). Talks to MetaMask for writes and to the Rust backend for read-only network data.
- `backend/` — Rust axum service. Exposes `/api/*` and serves the built SPA from `/app/public` (SPA fallback for Vue Router history mode).
- `Dockerfile` — multi-stage build (node → rust → debian-slim).
- `captain-definition` — CapRover entry point (schema v2, points at `Dockerfile`).

## API

| Endpoint | Purpose |
|---|---|
| `GET /api/health` | Liveness probe |
| `GET /api/config` | Chain registry (no secret RPC URLs) |
| `GET /api/overview?chain=<key>` | Aggregated on-chain state for `mainnet` / `sepolia` / `devnet` |
| `GET /api/price` | CoinGecko ETH price proxy |

All responses are cached in-memory for 10s; there is no database and no disk state.

## Local development

```bash
# Terminal 1 — backend
cd backend
RPC_DEVNET=http://localhost:8545 \
TOKEN_DEVNET=0x5FbDB2315678afecb367f032d93F642f64180aa3 \
VERIFIER_DEVNET=0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512 \
cargo run

# Terminal 2 — frontend
cd frontend
cp .env.example .env.local
# set VITE_API_BASE=http://localhost:8080 in .env.local
npm install
npm run dev
```

## Environment variables

Per chain, suffix with `_MAINNET`, `_SEPOLIA`, or `_DEVNET`:

- `RPC_*` — RPC URL used by the backend (may include API key; never returned to clients)
- `TOKEN_*` — EvmoreToken address
- `VERIFIER_*` — KeccakCollisionVerifier address
- `BRIDGE_*` — Bridge contract address (optional)
- `PUBLIC_RPC_*` — Optional public RPC URL returned via `/api/config` for direct wallet use
- `EXPLORER_*` — Block explorer base URL
- `CHAIN_ID_*` — Override default chain ID

Global:

- `PORT` (default `8080`)
- `STATIC_DIR` (default `/app/public`)
- `COINGECKO_BASE` (default `https://api.coingecko.com/api/v3`)

A chain is only registered if its `RPC_*` variable is set.

## Build and run with Docker

```bash
docker build -t evmore-dashboard .
docker run --rm -p 8080:8080 \
  -e RPC_MAINNET=https://eth-mainnet.g.alchemy.com/v2/KEY \
  -e TOKEN_MAINNET=0x... \
  -e VERIFIER_MAINNET=0x... \
  evmore-dashboard
```

Open `http://localhost:8080`.

## Deploy to CapRover

1. Create a new app in CapRover UI (e.g. `evmore-dashboard`). HTTP port: `8080`.
2. Set the environment variables above under **App Configs → Environmental Variables**.
3. Map the custom domain `evmore.cryptuon.com` and enable HTTPS.
4. From the repo root, deploy:
   ```bash
   caprover deploy
   ```
   CapRover builds the `Dockerfile`, starts the container, and proxies `evmore.cryptuon.com → :8080`.

The container is stateless — you can scale or restart it freely.
