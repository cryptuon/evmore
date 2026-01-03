# EVMORE Token - Deployment Guide

## Prerequisites

1. Python 3.12+
2. Poetry (for dependency management)
3. Node.js and npm (for Hardhat)
4. Ethereum wallet with testnet ETH (Goerli or Sepolia)
5. Infura/Alchemy account for RPC access

## Setup

1. Install dependencies:
   ```bash
   uv sync
   npm install
   ```

2. Compile contracts:
   ```bash
   ape compile
   ```

## Deployment

### Local Testing

1. Start a local Hardhat node:
   ```bash
   npx hardhat node
   ```

2. In another terminal, deploy to the local network:
   ```bash
   ape run deploy
   ```

### Sepolia Testnet Deployment

1. Add your private key and provider URL to the environment:
   ```bash
   export PRIVATE_KEY="your_private_key_here"
   export WEB3_PROVIDER_URI="https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID"
   ```

2. Deploy to Sepolia:
   ```bash
   ape deploy --network ethereum:sepolia
   ```

### Goerli Testnet Deployment (Deprecated)

Note: Goerli is being deprecated. Use Sepolia for new deployments.

1. Add your private key and provider URL to the environment:
   ```bash
   export PRIVATE_KEY="your_private_key_here"
   export WEB3_PROVIDER_URI="https://goerli.infura.io/v3/YOUR_INFURA_PROJECT_ID"
   ```

2. Deploy to Goerli:
   ```bash
   ape deploy --network ethereum:goerli
   ```

## Testing

Run the full test suite:
```bash
ape test
```

Run specific tests:
```bash
ape test -k test_mining_process
```

## Contract Addresses

After deployment, the script will output the addresses of the deployed contracts:
- `KeccakCollisionVerifier`: Verification contract
- `EvmoreToken`: Main token contract with mining functionality

## Key Features

1. **PoW Mining**: Mine EVMORE tokens by finding KeccakCollision solutions
2. **Batch Submission**: Submit multiple solutions in a single transaction to save gas
3. **Security Functions**: Pause/unpause functionality for emergency situations
4. **Epoch-based Rewards**: Rewards distributed based on mining epochs
5. **Difficulty Adjustment**: Automatic difficulty adjustment based on network conditions

## Interacting with Contracts

After deployment, you can interact with the contracts using the Ape framework or any web3 library:

1. **Submit a single proof**:
   ```python
   token.submitProof(solution, sender=miner_account)
   ```

2. **Submit a batch of proofs**:
   ```python
   token.submitProofBatch(solutions, sender=miner_account)
   ```

3. **Claim mining rewards**:
   ```python
   token.claimReward(epoch_number, sender=miner_account)
   ```

4. **Pause the contract** (owner only):
   ```python
   token.pause(sender=owner_account)
   ```

5. **Unpause the contract** (owner only):
   ```python
   token.unpause(sender=owner_account)
   ```

## Gas Optimization

The contracts include several gas optimization features:
- Precomputed masks for common difficulty levels
- Batch submission to reduce per-solution gas costs
- Efficient storage patterns

## Security Considerations

- Only the contract owner can pause/unpause the contract
- Duplicate solutions are rejected
- Solutions are verified on-chain before acceptance
- Emergency withdrawal functionality for the owner

## Documentation

For more detailed information about the EVMORE protocol and implementation approaches, see our [documentation](docs/README.md):

- [Getting Started](docs/getting-started/)
- [Implementation Approaches](docs/implementation-approaches/)
- [Advanced Topics](docs/advanced-topics/)