# EVMORE: KeccakCollision PoW Algorithm

EVMORE is a novel cryptocurrency implementing a KeccakCollision-based Proof-of-Work (PoW) algorithm. Unlike traditional PoW algorithms like SHA256 (Bitcoin) or Ethash (Ethereum), EVMORE uses partial hash collisions as its mining mechanism, specifically requiring miners to find multiple inputs that produce matching least-significant bits when hashed with Keccak256.

## Core Concept

- Similar to Equihash but using Keccak256 for both mining and verification
- Requires finding multiple inputs that produce partial collisions in their hashes
- Uses bit manipulation to verify collisions, making verification efficient on-chain

## Algorithm Parameters

- **N**: Number of bits that must collide (difficulty parameter)
- **K**: Number of values that must have matching bits (e.g., K=4 means find 4 values)
- Each solution consists of K different 32-byte values that when hashed:
  1. Have N matching bits in their least significant bits
  2. Are in strictly ascending order (to prevent permutation duplicates)

## Mining Process

1. Take block challenge as input
2. Generate K different values
3. For each value:
   - Concatenate with challenge and hash with keccak256
   - Extract N least significant bits
4. Verify all K hashes have matching N bits
5. Values must be in ascending order

## Verification Process

1. Verify K values are in ascending order
2. Hash each value with challenge
3. Extract and compare N least significant bits
4. All must match

## Security Properties

- **Memory-hard**: Requires keeping track of many hash values
- **Verification is O(K) hashing operations**
- **Non-parallelizable** due to sequential nature
- **Difficulty adjustable** via N parameter

## Economic Model

- **Initial block reward**: 50 EVMORE
- **Halving interval**: Every 210,000 blocks (approximately 4 years with 10-minute blocks)
- **Total supply cap**: 21 million EVMORE
- **Block target time**: 10 minutes
- **Difficulty adjustment**: Every 2016 blocks (approximately 2 weeks)

## Smart Contracts

This repository contains Vyper smart contracts implementing the EVMORE token with KeccakCollision-based Proof-of-Work:

1. **[EvmoreToken.vy](contracts/EvmoreToken.vy)**: Main ERC-20 token contract with integrated mining mechanics
2. **[KeccakCollisionVerifier.vy](contracts/KeccakCollisionVerifier.vy)**: Efficient on-chain verification of mining solutions

## Documentation

All documentation is organized in the [docs](docs/) directory:

### Getting Started
- [Executive Summary](docs/executive_summary.md) - High-level overview of the project and integration strategy
- [Technical Specification](docs/technical_specification.md) - Detailed technical implementation specifications

### Implementation Approaches
- [Direct Integration](docs/simplified_implementation.md) - Minimal changes needed for deployment
- [Hybrid Approach](docs/hybrid_implementation.md) - Off-chain mining with on-chain verification approach
- [Approach Comparison](docs/approach_comparison.md) - Comparison of different implementation approaches

### Advanced Topics
- [Ethereum Integration Plan](docs/ethereum_integration_plan.md) - Comprehensive plan for Ethereum deployment
- [Ethereum Compatible Contracts](docs/ethereum_compatible_contracts.md) - Modified contracts for Ethereum deployment
- [Final Summary](docs/final_summary.md) - Conclusions and recommendations

## Prerequisites

- Python 3.12+
- Poetry (for Python dependency management)
- Node.js (for Hardhat)

## Installation

```bash
# Install Python dependencies
poetry install

# Install Node.js dependencies
npm install
```

## Testing

```bash
# Run tests using Ape framework
ape test
```

## Deployment

```bash
# Deploy contracts (for Ethereum deployment, see docs for required modifications)
ape run deploy
```

## License

[MIT License](LICENSE)