# EVMORE

<p align="center">
  <img src="documentation/assets/images/hero-banner.png" alt="EVMORE - Digital Gold on Ethereum" width="100%">
</p>

<p align="center">
  <strong>Scarce. Mineable. Programmable.</strong><br>
  A 21-million-supply proof-of-work token on Ethereum, powered by KeccakCollision mining.
</p>

<p align="center">
  <a href="https://github.com/evmore/evmore-contracts"><img src="https://img.shields.io/badge/build-passing-brightgreen.svg" alt="Build Status"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
  <a href="https://vyper.readthedocs.io/"><img src="https://img.shields.io/badge/vyper-0.4.0-purple.svg" alt="Vyper"></a>
  <a href="contracts/EvmoreToken.vy"><img src="https://img.shields.io/badge/token-ERC--20-brightgreen.svg" alt="ERC-20"></a>
  <a href="#at-a-glance"><img src="https://img.shields.io/badge/max%20supply-21M-gold.svg" alt="Max Supply"></a>
  <a href="docs/operational/security-assessment.md"><img src="https://img.shields.io/badge/security-audited-blue.svg" alt="Security"></a>
</p>

<p align="center">
  <strong><a href="https://evmore.cryptuon.com/">🌐 Site</a> · <a href="https://docs.cryptuon.com/evmore/">📚 Docs</a> · <a href="https://github.com/cryptuon">🔬 Cryptuon Research</a></strong>
</p>

---

## Overview

EVMORE is a digital gold token that combines Bitcoin's proven scarcity model (21M fixed supply, halving schedule) with Ethereum's programmability (ERC-20, DeFi composability). Instead of SHA-256 or proof-of-stake, EVMORE introduces **KeccakCollision** -- a memory-hard proof-of-work algorithm where miners must find four values whose Keccak-256 hashes collide on the lowest N bits.

The result is a token that is ASIC-resistant, GPU/CPU accessible, and verified entirely on-chain. No premine. No ICO. No team allocation. Every EVMORE in circulation was mined through computational work.

## At a Glance

| Parameter | Value |
|-----------|-------|
| **Max Supply** | 21,000,000 EVMORE |
| **Token Standard** | ERC-20 |
| **Mining Algorithm** | KeccakCollision (memory-hard) |
| **Block Reward** | 50 EVMORE (halves every ~4 years) |
| **Block Time** | ~10 minutes |
| **Difficulty Adjustment** | Every 2,016 blocks |
| **Decimals** | 18 |
| **Premine** | None -- 100% fair launch |
| **Smart Contract Language** | Vyper 0.4.0 |

---

## For Investors and Token Holders

### Digital Scarcity

| Property | Physical Gold | Bitcoin | EVMORE |
|----------|---------------|---------|--------|
| Max supply | ~200K tonnes | 21M BTC | 21M EVMORE |
| New supply | ~1.5%/year | Halving schedule | Halving schedule |
| Mining hardware | Industrial | ASIC-dominated | GPU/CPU accessible |
| Verification | Assaying | Off-chain nodes | On-chain smart contract |
| Programmability | None | Limited | Full ERC-20 + DeFi |
| Storage cost | 0.5-1%/year | ~0.1% custody | Self-custody, free |
| Divisibility | ~1 gram | 8 decimals | 18 decimals |

### Halving Schedule

| Era | Years | Block Reward | Cumulative Supply | % Mined |
|-----|-------|--------------|-------------------|---------|
| 1 | 0-4 | 50 EVMORE | 10.5M | 50% |
| 2 | 4-8 | 25 EVMORE | 15.75M | 75% |
| 3 | 8-12 | 12.5 EVMORE | 18.375M | 87.5% |
| 4 | 12-16 | 6.25 EVMORE | 19.69M | 93.75% |
| 5+ | 16+ | Continues halving | Approaches 21M | ~100% |

### Self-Funding Roadmap

EVMORE uses a 4-stage deployment model funded entirely by mining treasury accumulation:

| Stage | Trigger | What Unlocks |
|-------|---------|--------------|
| 1. Ethereum Launch | ~$500 deployment | Mining + ERC-20 token |
| 2. Polygon Bridge | 1,000 EVMORE treasury | Ethereum-Polygon bridging |
| 3. Multi-Chain | 10,000 EVMORE treasury | Arbitrum, Base, Optimism, Avalanche |
| 4. Federated Mining | 100,000 EVMORE treasury | Native mining on all chains |

---

## For Developers

### Tech Stack

| Component | Technology |
|-----------|------------|
| Smart contracts | Vyper 0.4.0 |
| Framework | Ape + Hardhat |
| Package manager | uv (Python), npm (Node) |
| Frontend | Vue 3 + TypeScript + Tailwind CSS |
| Web3 | ethers.js v6 |
| Testing | pytest via Ape |

### Quick Start

```bash
# Clone and install
git clone https://github.com/cryptuon/evmore
cd evmore
uv sync && npm install

# Compile contracts
uv run ape compile

# Run tests
uv run ape test

# Deploy to local testnet
uv run python scripts/deploy_testnet.py
```

### Smart Contracts

| Contract | Lines | Purpose |
|----------|-------|---------|
| `EvmoreToken.vy` | 627 | ERC-20 token with integrated mining, halving, difficulty adjustment |
| `KeccakCollisionVerifier.vy` | 62 | On-chain mining proof verification |
| `EVMOREBridge.vy` | 482 | Multi-chain hub-and-spoke bridge (Stage 3) |
| `EVMOREBridgeStage2.vy` | 338 | Manual Ethereum-Polygon bridge (Stage 2) |
| `wEVMOREPolygon.vy` | 236 | Wrapped EVMORE on Polygon |

### Architecture

```
                     DeFi Protocols / dApp / Wallets
                                 |
                          ERC-20 Interface
                                 |
              +------------------+------------------+
              |                  |                  |
      EvmoreToken.vy    KeccakCollision     EVMOREBridge.vy
      (Token + Mining)   Verifier.vy       (Cross-Chain Hub)
              |                  |                  |
              +--------+---------+         +--------+--------+
                       |                   |        |        |
                 Proof Submission     Polygon  Arbitrum   Base
                       |
            +----------+----------+
            |          |          |
        Solo       Mining     Enterprise
        Miners     Pools      Mining
```

---

## Documentation

Full documentation is available in the `documentation/` directory, built with MkDocs Material.

| Section | Description |
|---------|-------------|
| [What is EVMORE?](documentation/getting-started/what-is-evmore.md) | Introduction for newcomers |
| [Quick Start](documentation/getting-started/quick-start.md) | Wallet setup and first steps |
| [Token Economics](documentation/getting-started/economics.md) | Supply model, halving, value proposition |
| [Mining Guide](documentation/mining/mining-guide.md) | Hardware, setup, solo vs pool, profitability |
| [KeccakCollision Algorithm](documentation/mining/mining-algorithm.md) | Deep dive into the mining algorithm |
| [Architecture Overview](documentation/architecture/overview.md) | Smart contract design and interaction flows |
| [Staged Deployment](documentation/architecture/staged-deployment.md) | 4-stage self-funding model |
| [Cross-Chain Bridge](documentation/architecture/cross-chain-bridge.md) | Hub-and-spoke bridge design |
| [Federated Mining](documentation/architecture/federated-mining.md) | Stage 4 multi-chain native mining |
| [Contract Reference](documentation/contracts/reference.md) | Full smart contract API |
| [Developer Guide](documentation/developers/getting-started.md) | Environment setup, compile, test, deploy |
| [Contributing](documentation/developers/contributing.md) | How to contribute |
| [FAQ](documentation/getting-started/faq.md) | Frequently asked questions |

To serve the documentation locally:

```bash
cd documentation
uv run mkdocs serve
```

---

## Security

EVMORE contracts have undergone comprehensive security hardening:

- All critical and high-priority vulnerabilities resolved (5/5 fixed)
- Reentrancy protection on all state-changing functions
- Global solution uniqueness prevents replay attacks across epochs
- Two-step ownership transfer prevents accidental loss
- 90% test coverage across 3 test suites (718 lines)
- External audit ready

See [Security Assessment](docs/operational/security-assessment.md) for details.

---

## Community

- **GitHub**: [evmore/evmore-contracts](https://github.com/evmore/evmore-contracts)
- **Discord**: [EVMORE Community](https://discord.gg/evmore)
- **Twitter**: [@EVMOREGold](https://twitter.com/EVMOREGold)

### Contributing

We welcome contributions across smart contracts, mining software, the Vue 3 frontend, documentation, and security review. See the [Contributing Guide](documentation/developers/contributing.md) to get started.

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Part of Cryptuon Research

`evmore` is one of [20 open-source blockchain-infrastructure projects](https://www.cryptuon.com/projects) from **[Cryptuon Research](https://www.cryptuon.com)** — blockchain theory, shipped as protocols.

**Related projects:** [Zig-EVM](https://zig-evm.cryptuon.com/) · [Tesseract](https://tesseract.cryptuon.com/) · [blockchain-compression](https://blockchain-compression.cryptuon.com/)

Docs: [docs.cryptuon.com/evmore](https://docs.cryptuon.com/evmore/) · Contact: [contact@cryptuon.com](mailto:contact@cryptuon.com)

---

<p align="center"><em>Where 5,000 years of gold meets 21st century cryptography.</em></p>
