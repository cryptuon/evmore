# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EVMORE is a revolutionary digital gold cryptocurrency that uses KeccakCollision proof-of-work mining. It implements a 4-stage deployment architecture progressing from Ethereum-only to federated cross-chain mining. The project is designed for zero-budget bootstrap launch with self-funding through mining economics.

## Key Technologies

- **Smart Contracts**: Vyper 0.4.0 (security-focused, migrated from 0.3.10)
- **Development Framework**: Ape framework with Hardhat
- **Blockchain**: Ethereum mainnet with multi-chain expansion
- **Mining Algorithm**: KeccakCollision (ASIC-resistant, memory-hard)
- **Dependencies**: uv for Python package management

## Essential Commands

### Environment Setup
```bash
# Install all dependencies
uv sync

# Compile smart contracts
uv run ape compile

# Run comprehensive test suite
uv run ape test

# Deploy to local testnet (development)
uv run python scripts/deploy_testnet.py

# Check deployment readiness
uv run python scripts/deployment_readiness.py
```

### Development Workflow
```bash
# Run specific test file
uv run ape test tests/test_evmore.py

# Deploy Stage 1 (production - requires ETH)
uv run python scripts/deploy_stage1.py

# Generate mining solution (for testing)
uv run python scripts/generate_mining_solution.py

# Run migration between stages
uv run python scripts/migration_manager.py
```

### Mining and Testing
```bash
# Demo mining process
uv run python scripts/demo_mining.py

# Test batch mining submissions
uv run python scripts/batch_submission_demo.py
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
- Always run full test suite before deployment: `uv run ape test`

### Bootstrap Economics
- Self-funding through mining rewards and bridge fees
- No external funding required beyond initial $500 deployment
- Community-driven treasury accumulation enables upgrades
- Fair launch model with no premine

## Deployment Guide

### Prerequisites
1. **Ethereum wallet** with deployer private key
2. **ETH for gas** (~0.02-0.05 ETH for Stage 1 deployment)
3. **RPC endpoint** (Infura, Alchemy, or own node)

### Deployment Process

#### Step 1: Configure Network
Edit `ape-config.yaml` to add mainnet configuration:
```yaml
ethereum:
  mainnet:
    default_provider: alchemy  # or infura
    transaction_acceptance_timeout: 600
```

Set environment variables:
```bash
export WEB3_ALCHEMY_API_KEY="your-api-key"
export DEPLOYER_PRIVATE_KEY="your-private-key"
```

#### Step 2: Pre-deployment Verification
```bash
# Verify all contracts compile
uv run ape compile

# Run test suite
uv run ape test

# Check deployment readiness
uv run python scripts/deployment_readiness.py
```

#### Step 3: Deploy Stage 1 (Mainnet)
```bash
# Deploy KeccakCollisionVerifier + EvmoreToken
uv run python scripts/deploy_stage1.py --network ethereum:mainnet
```

This deploys:
1. `KeccakCollisionVerifier` - Mining verification contract
2. `EvmoreToken` - Main token contract (linked to verifier)

#### Step 4: Verify Deployment
```bash
# Verify contracts on Etherscan
uv run ape verify <verifier_address> --network ethereum:mainnet
uv run ape verify <token_address> --network ethereum:mainnet
```

#### Step 5: Post-deployment
1. **Start mining** - Use `scripts/demo_mining.py` or build custom miner
2. **Monitor treasury** - Track EVMORE accumulation for Stage 2 trigger
3. **Community launch** - Announce contract addresses, begin fair distribution

### Deployment Costs (Estimated)
| Stage | Gas Cost | USD (@ $2000 ETH, 30 gwei) |
|-------|----------|---------------------------|
| Stage 1 | ~2M gas | ~$120 |
| Stage 2 | ~1.5M gas | ~$90 |
| Stage 3 | ~3M gas | ~$180 |
| Stage 4 | ~5M gas | ~$300 |

### Security Checklist Before Mainnet
- [ ] External security audit completed
- [ ] All tests passing
- [ ] Deployer key secured (hardware wallet recommended)
- [ ] Multi-sig setup for owner functions (recommended)
- [ ] Emergency contacts established
- [ ] Monitoring infrastructure ready

## File Structure Context

- `contracts/`: Core Vyper smart contracts
- `contracts/bridges/`: Multi-chain bridge infrastructure
- `scripts/`: Deployment and management scripts
- `docs/`: Comprehensive architecture and strategy documentation
- `tests/`: Security and integration test suites

The codebase is production-ready with comprehensive documentation, automated deployment scripts, and a clear path from $500 launch to revolutionary federated mining architecture.

## Quick Reference

| Task | Command |
|------|---------|
| Install deps | `uv sync` |
| Compile | `uv run ape compile` |
| Test | `uv run ape test` |
| Deploy testnet | `uv run python scripts/deploy_testnet.py` |
| Deploy mainnet | `uv run python scripts/deploy_stage1.py --network ethereum:mainnet` |
