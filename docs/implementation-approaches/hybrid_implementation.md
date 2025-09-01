# Hybrid PoW Implementation: Off-Chain Mining with On-Chain Verification

This document describes a hybrid approach for implementing EVMORE PoW that combines off-chain mining with on-chain verification and reward distribution.

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Mining Pool   │◄──►│  Mining Clients  │◄──►│  Off-Chain PoW  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐
│  Ethereum Smart │
│    Contracts    │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│Reward Distribution│
└─────────────────┘
```

## Off-Chain Components

### 1. Mining Client

The mining client runs the KeccakCollision algorithm:

```python
# mining_client.py
import hashlib
import random
from eth_hash.auto import keccak

class KeccakCollisionMiner:
    def __init__(self, challenge: bytes, difficulty: int, k_values: int = 4):
        self.challenge = challenge
        self.difficulty = difficulty
        self.k_values = k_values
        self.mask = (1 << difficulty) - 1
        
    def mine(self, max_attempts: int = 1000000) -> bytes:
        """
        Mine for a valid solution
        """
        solutions = []
        target_bits = None
        attempts = 0
        
        while len(solutions) < self.k_values and attempts < max_attempts:
            attempts += 1
            candidate = random.randbytes(32)
            
            # Check if candidate would maintain ascending order
            candidate_int = int.from_bytes(candidate, 'big')
            if solutions and candidate_int <= int.from_bytes(solutions[-1], 'big'):
                continue
                
            hash_input = self.challenge + candidate
            hash_result = keccak(hash_input)
            bits = int.from_bytes(hash_result, 'big') & self.mask
            
            if target_bits is None:
                target_bits = bits
                solutions.append(candidate)
            elif bits == target_bits:
                solutions.append(candidate)
                
        if len(solutions) < self.k_values:
            raise RuntimeError(f"Failed to find solution after {max_attempts} attempts")
            
        return b''.join(solutions)
```

### 2. Pool Coordinator

Coordinates multiple miners and batches submissions:

```python
# pool_coordinator.py
import time
from web3 import Web3
from typing import List, Dict

class PoolCoordinator:
    def __init__(self, web3: Web3, contract_address: str):
        self.web3 = web3
        self.contract_address = contract_address
        self.pending_solutions: List[Dict] = []
        self.batch_size = 10
        self.submission_interval = 300  # 5 minutes
        
    def add_solution(self, miner_address: str, solution: bytes):
        """
        Add a solution to the pending batch
        """
        self.pending_solutions.append({
            'miner': miner_address,
            'solution': solution,
            'timestamp': time.time()
        })
        
        # Submit batch if size limit reached
        if len(self.pending_solutions) >= self.batch_size:
            self.submit_batch()
            
    def submit_batch(self):
        """
        Submit a batch of solutions to the contract
        """
        if not self.pending_solutions:
            return
            
        # Extract solutions (in a real implementation, you'd need to handle
        # the mapping between miners and their solutions)
        solutions = [s['solution'] for s in self.pending_solutions[:self.batch_size]]
        
        # Call contract function (simplified)
        # contract.functions.submitProofBatch(solutions).transact()
        
        # Clear processed solutions
        self.pending_solutions = self.pending_solutions[self.batch_size:]
        
    def run_submission_scheduler(self):
        """
        Periodically submit batches
        """
        while True:
            time.sleep(self.submission_interval)
            self.submit_batch()
```

## On-Chain Components

### 1. Batch Submission Function

Add batch submission to the token contract:

```vy
# Add to EvmoreToken.vy
@external
def submitProofBatch(
    solutions: DynArray[Bytes[128], 50],
    miners: DynArray[address, 50]
) -> bool:
    """
    Submit multiple mining proofs in a single transaction
    """
    assert len(solutions) == len(miners), "Solutions and miners arrays must match"
    assert len(solutions) <= 50, "Batch size exceeds limit"
    
    # Verify all solutions first
    for i: uint256 in range(len(solutions)):
        assert staticcall self.verifier.verify_solution(
            self.currentChallenge, 
            solutions[i],
            self.currentDifficulty
        ), "Invalid solution"
    
    # Process valid solutions
    for i: uint256 in range(len(solutions)):
        solution: Bytes[128] = solutions[i]
        miner: address = miners[i]
        
        # Check for duplicate solutions in current epoch
        current_miners: DynArray[address, 100] = self.epoch_miners[self.current_epoch]
        duplicate_found: bool = False
        for j: uint256 in range(len(current_miners)):
            existing_proof: MiningProof = self.pendingProofs[current_miners[j]]
            if existing_proof.solution == solution:
                duplicate_found = True
                break
                
        assert not duplicate_found, "Duplicate solution"
        
        # Store proof
        self.pendingProofs[miner] = MiningProof({
            solution: solution,
            timestamp: block.timestamp,
            claimed: False
        })
        
        # Add miner to current epoch if not present
        miner_in_epoch: bool = False
        for j: uint256 in range(len(current_miners)):
            if current_miners[j] == miner:
                miner_in_epoch = True
                break
                
        if not miner_in_epoch:
            current_miners.append(miner)
            self.epoch_miners[self.current_epoch] = current_miners
            
            # Update epoch data
            epoch: EpochData = self.epochs[self.current_epoch]
            epoch.miner_count += 1
            self.epochs[self.current_epoch] = epoch
    
    # Check if we should transition to new epoch
    time_since_last: uint256 = block.timestamp - self.lastMiningTimestamp
    if time_since_last >= TARGET_BLOCK_TIME:
        self._transition_epoch()
    
    return True
```

### 2. Pool Registration

Allow pools to register and get preferential treatment:

```vy
# Add to EvmoreToken.vy
# State variables
registered_pools: public(HashMap[address, bool])
pool_submission_limits: public(HashMap[address, uint256])

# Events
event PoolRegistered:
    pool: indexed(address)
    limit: uint256

# Functions
@external
def registerPool(limit: uint256) -> bool:
    """
    Register a mining pool (owner only)
    """
    assert msg.sender == self.owner, "Only owner can register pools"
    assert limit <= 100, "Pool limit too high"
    
    self.registered_pools[msg.sender] = True
    self.pool_submission_limits[msg.sender] = limit
    log PoolRegistered(msg.sender, limit)
    return True

# Modified submitProofBatch with pool support
@external
def submitProofBatch(
    solutions: DynArray[Bytes[128], 50],
    miners: DynArray[address, 50]
) -> bool:
    """
    Submit multiple mining proofs in a single transaction
    Pool version with higher limits
    """
    # Check if sender is a registered pool
    if self.registered_pools[msg.sender]:
        assert len(solutions) <= self.pool_submission_limits[msg.sender], "Pool batch size exceeded"
    else:
        assert len(solutions) <= 10, "Regular user batch size exceeded"
    
    # ... rest of existing logic
```

## Economic Model

### 1. Pool Fees

Implement a fee structure for pools:

```vy
# Add to EvmoreToken.vy
pool_fee_percentage: public(uint256)  # e.g., 5 for 5%

@deploy
def __init__(verifier_address: address, pool_fee: uint256):
    # ... existing initialization
    self.pool_fee_percentage = pool_fee

# Modified reward distribution with fees
@external
def claimReward(epoch: uint256) -> bool:
    # ... existing validation
    
    epoch_data: EpochData = self.epochs[epoch]
    total_reward: uint256 = epoch_data.total_reward
    
    # Calculate pool fee if claimed by a pool
    pool_fee: uint256 = 0
    if self.registered_pools[msg.sender]:
        pool_fee = (total_reward * self.pool_fee_percentage) / 100
        total_reward -= pool_fee
    
    # ... rest of reward calculation and distribution
    
    # Send pool fee to owner
    if pool_fee > 0:
        self._mint(self.owner, pool_fee)
```

## Implementation Steps

### Phase 1: Core Contracts
1. Deploy updated verifier contract
2. Deploy updated token contract with batch submission
3. Register initial pools

### Phase 2: Off-Chain Infrastructure
1. Develop mining clients
2. Create pool coordinators
3. Implement batch submission services

### Phase 3: Testing and Deployment
1. Test on testnets
2. Optimize gas costs
3. Deploy to mainnet

## Benefits of Hybrid Approach

1. **Reduced Gas Costs**: Batch submissions reduce per-solution gas costs
2. **Better Scalability**: Off-chain mining handles computational load
3. **Improved User Experience**: Pools handle complexity for individual miners
4. **Enhanced Security**: On-chain verification ensures solution validity
5. **Economic Incentives**: Pool fees create sustainable ecosystem

## Challenges and Mitigations

1. **Pool Centralization**: Implement multiple pools and rotation mechanisms
2. **Front-running**: Use commit-reveal or timestamp-based solutions
3. **Spam Prevention**: Rate limiting and deposit requirements for pools
4. **Network Congestion**: Off-peak submission scheduling

This hybrid approach provides a practical implementation of the EVMORE PoW algorithm on Ethereum while addressing the network's constraints and characteristics.