# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EVMORE is a revolutionary digital gold cryptocurrency that uses KeccakCollision proof-of-work mining. It implements a 4-stage deployment architecture progressing from Ethereum-only to federated cross-chain mining. The project is designed for zero-budget bootstrap launch with self-funding through mining economics.

## Key Technologies

- **Smart Contracts**: Vyper 0.4.0 (security-focused)
- **Development Framework**: Ape framework with Hardhat
- **Blockchain**: Ethereum mainnet with multi-chain expansion
- **Mining Algorithm**: KeccakCollision (ASIC-resistant, memory-hard)
- **Dependencies**: Poetry for Python, npm for JavaScript tooling

## Essential Commands

### Environment Setup
```bash
# Install all dependencies
poetry install && npm install

# Compile smart contracts
poetry run ape compile

# Run comprehensive test suite
poetry run ape test

# Deploy to local testnet (development)
poetry run python scripts/deploy_testnet.py

# Check deployment readiness
python3 scripts/deployment_readiness.py
```

### Development Workflow
```bash
# Run specific test file
poetry run ape test tests/test_evmore.py

# Deploy Stage 1 (production - requires ETH)
poetry run python scripts/deploy_stage1.py

# Generate mining solution (for testing)
poetry run python scripts/generate_mining_solution.py

# Run migration between stages
poetry run python scripts/migration_manager.py
```

### Mining and Testing
```bash
# Demo mining process
poetry run python scripts/demo_mining.py

# Test batch mining submissions
poetry run python scripts/batch_submission_demo.py
```

## Architecture Overview

### Core Smart Contracts

**EvmoreToken.vy** (630 lines) - The central digital gold token
- Implements ERC-20 with integrated KeccakCollision mining
- Contains bridge hooks for multi-chain migration (setBridgeContract, bridgeMint, bridgeBurn)
- Economics: 21M max supply, halving schedule, difficulty adjustment
- Security: Reentrancy protection, two-step ownership, solution replay prevention

**KeccakCollisionVerifier.vy** (62 lines) - Mining algorithm verification
- Verifies KeccakCollision solutions (N=16 bits, K=4 values required)
- Memory-hard algorithm preventing ASIC dominance
- On-chain verification enables smart contract integration

**Bridge Contracts** (Stage 2+ migration-ready)
- EVMOREBridgeStage2.vy: Manual processing bridge for Polygon
- wEVMOREPolygon.vy: Wrapped EVMORE token on Polygon
- Built-in migration capabilities with treasury-based activation

### Staged Deployment Architecture

The project uses a unique 4-stage deployment model:

1. **Stage 1** ($500 budget): Ethereum-only deployment with mining
2. **Stage 2** (1K EVMORE treasury): Polygon bridge activation
3. **Stage 3** (10K EVMORE treasury): Multi-chain expansion (Arbitrum, Base)
4. **Stage 4** (100K EVMORE treasury): Federated mining across all chains

Migration between stages is handled by `scripts/migration_manager.py` which automatically checks treasury thresholds and executes seamless upgrades.

### KeccakCollision Mining

Unlike traditional hash-based mining, EVMORE requires finding multiple values that create matching collision patterns:

```python
# Find 4 values where keccak256(challenge + value) has matching N-bit patterns
# Must be memory-hard and ASIC-resistant
# Solutions verified on-chain for smart contract integration
```

## Important Development Notes

### Contract Security
- All contracts have undergone comprehensive security review
- Fixed 12 vulnerabilities (2 critical, 3 high priority)
- Uses production-grade patterns: checks-effects-interactions, reentrancy guards
- Two-step ownership transfer prevents accidental loss

### Migration Strategy
- Contracts are built with migration hooks from deployment
- Bridge functionality is dormant until activated
- Treasury accumulation automatically triggers stage upgrades
- Zero-downtime migration between deployment stages

### Testing Strategy
- Comprehensive test suite in `tests/` directory
- Security-focused tests in `test_security_fixes.py`
- Integration tests in `test_evmore.py`
- Always run full test suite before deployment: `poetry run ape test`

### Bootstrap Economics
- Self-funding through mining rewards and bridge fees
- No external funding required beyond initial $500 deployment
- Community-driven treasury accumulation enables upgrades
- Fair launch model with no premine

## Deployment Workflow

1. **Pre-deployment**: Run `python3 scripts/deployment_readiness.py`
2. **Stage 1**: Deploy with `poetry run python scripts/deploy_stage1.py`
3. **Mining**: Start with `scripts/demo_mining.py` or custom miners
4. **Migration**: Automatic via `scripts/migration_manager.py` when thresholds met

## File Structure Context

- `contracts/`: Core Vyper smart contracts
- `contracts/bridges/`: Multi-chain bridge infrastructure
- `scripts/`: Deployment and management scripts
- `docs/`: Comprehensive architecture and strategy documentation
- `tests/`: Security and integration test suites
- `DEPLOYMENT_READY.md`: Complete launch readiness summary

The codebase is production-ready with comprehensive documentation, automated deployment scripts, and a clear path from $500 launch to revolutionary federated mining architecture.