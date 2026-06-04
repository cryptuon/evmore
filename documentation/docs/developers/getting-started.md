# Developer Getting Started

Set up your development environment, compile contracts, run tests, and deploy EVMORE locally.

---

## Prerequisites

- **Python 3.12+**
- **Node.js 18+** (for Hardhat)
- **uv** -- Python package manager ([install](https://docs.astral.sh/uv/getting-started/installation/))
- **Git**

---

## Setup

```bash
# Clone the repository
git clone https://github.com/evmore/evmore-contracts
cd evmore-contracts

# Install Python dependencies
uv sync

# Install Node dependencies (for Hardhat)
npm install
```

---

## Compile Contracts

```bash
uv run ape compile
```

This compiles all Vyper contracts in `contracts/` using the Ape framework with the Vyper plugin.

---

## Run Tests

```bash
# Run the full test suite
uv run ape test

# Run a specific test file
uv run ape test tests/test_evmore.py

# Run security-focused tests
uv run ape test tests/test_security_fixes.py
```

### Test Files

| File | Focus |
|------|-------|
| `tests/test_evmore.py` | Core mining and token functionality |
| `tests/test_basic_security.py` | Pause, ownership, authorization |
| `tests/test_security_fixes.py` | Reentrancy, replay attacks, epoch integrity |

---

## Deploy Locally

Deploy to a local Hardhat node for development:

```bash
uv run python scripts/deploy_testnet.py
```

This deploys:

1. `KeccakCollisionVerifier` -- Mining verification
2. `EvmoreToken` -- Token contract (linked to the verifier)

---

## Deploy to Mainnet

!!! warning
    Mainnet deployment requires ETH for gas (~0.02-0.05 ETH for Stage 1).

### Configure Network

Edit `ape-config.yaml` to add mainnet configuration:

```yaml
ethereum:
  mainnet:
    default_provider: alchemy
    transaction_acceptance_timeout: 600
```

Set environment variables:

```bash
export WEB3_ALCHEMY_API_KEY="your-api-key"
export DEPLOYER_PRIVATE_KEY="your-private-key"
```

### Check Readiness

```bash
uv run python scripts/deployment_readiness.py
```

### Deploy

```bash
uv run python scripts/deploy_stage1.py --network ethereum:mainnet
```

---

## Project Structure

```
evmore-contracts/
  contracts/                 # Vyper smart contracts
    EvmoreToken.vy           # Core token + mining (627 lines)
    KeccakCollisionVerifier.vy # PoW verification (62 lines)
    EVMOREBridge.vy          # Multi-chain bridge (482 lines)
    bridges/                 # Stage 2 bridge contracts
  scripts/                   # Deployment and utility scripts
    deploy_stage1.py         # Mainnet deployment
    deploy_testnet.py        # Local deployment
    deploy.py                # Generic deployment
    generate_mining_solution.py  # Mining solution generator
    migration_manager.py     # Stage migration
    mining/                  # Mining tools
      optimized_miner.py     # Multi-threaded miner
      mining_pool.py         # Pool protocol
  tests/                     # Test suite
    test_evmore.py           # Core tests
    test_basic_security.py   # Security tests
    test_security_fixes.py   # Vulnerability fix tests
  documentation/             # User-facing docs (this site)
  docs/                      # Technical/developer docs
  frontend/                  # Vue 3 + TypeScript dApp
```

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Smart contracts | Vyper 0.4.0 |
| Development framework | Ape + Hardhat |
| Package manager | uv (Python), npm (Node) |
| Testing | pytest via Ape |
| Frontend | Vue 3 + TypeScript + Tailwind CSS |
| Web3 | ethers.js v6 |
| State management | Pinia |

---

## Useful Commands

| Task | Command |
|------|---------|
| Install dependencies | `uv sync && npm install` |
| Compile contracts | `uv run ape compile` |
| Run all tests | `uv run ape test` |
| Deploy locally | `uv run python scripts/deploy_testnet.py` |
| Deploy mainnet | `uv run python scripts/deploy_stage1.py --network ethereum:mainnet` |
| Generate mining solution | `uv run python scripts/generate_mining_solution.py` |
| Demo mining | `uv run python scripts/demo_mining.py` |
| Check deployment readiness | `uv run python scripts/deployment_readiness.py` |

---

## Further Reading

- [Smart Contract Reference](../contracts/reference.md) -- Full contract API
- [Architecture Overview](../architecture/overview.md) -- System design
- [KeccakCollision Algorithm](../mining/mining-algorithm.md) -- Mining details
- [Contributing](contributing.md) -- How to contribute
