# 🔗 EVMORE Federated Mining Protocol

**Detailed technical specification for distributed mining across multiple EVM networks**

## 🎯 Protocol Overview

The Federated Mining Model allows EVMORE to be mined simultaneously across multiple EVM networks while maintaining a unified 21M supply and coordinated difficulty adjustment.

## 🏗️ Architecture Components

### 1. Cross-Chain Oracle Network

```vyper
# @title EVMORE Mining Coordinator Oracle
# @notice Coordinates mining challenges and difficulty across multiple chains

interface IChainReporter:
    def reportMiningStats(
        chain_id: uint256,
        hash_rate: uint256,
        solutions_found: uint256,
        miners_active: uint256
    ): nonpayable

struct ChainMiningStats:
    chain_id: uint256
    hash_rate: uint256
    solutions_found: uint256
    miners_active: uint256
    last_update: uint256
    supply_allocation: uint256  # Out of 21M total

struct GlobalChallenge:
    challenge: bytes32
    difficulty: uint256
    epoch: uint256
    start_time: uint256
    target_duration: uint256
    participating_chains: DynArray[uint256, 10]

# State variables
chain_stats: HashMap[uint256, ChainMiningStats]
current_challenge: GlobalChallenge
global_used_solutions: HashMap[bytes32, bool]
chain_contracts: HashMap[uint256, address]

# Oracle configuration
oracle_operators: HashMap[address, bool]
min_oracle_confirmations: uint256

@external
def generateGlobalChallenge() -> GlobalChallenge:
    """Generate synchronized mining challenge for all chains"""
    assert self.oracle_operators[msg.sender], "Only oracle operators"

    # Calculate global difficulty based on all chain stats
    total_hash_rate: uint256 = 0
    total_miners: uint256 = 0

    for chain_id in [1, 137, 42161, 8453, 43114]:  # ETH, Polygon, Arbitrum, Base, Avalanche
        stats: ChainMiningStats = self.chain_stats[chain_id]
        total_hash_rate += stats.hash_rate
        total_miners += stats.miners_active

    # Adjust difficulty to maintain 10-minute average block time
    new_difficulty: uint256 = self._calculate_adjusted_difficulty(total_hash_rate)

    new_challenge: GlobalChallenge = GlobalChallenge({
        challenge: keccak256(concat(
            convert(block.prevhash, bytes32),
            convert(block.timestamp, bytes32),
            convert(total_hash_rate, bytes32)
        )),
        difficulty: new_difficulty,
        epoch: self.current_challenge.epoch + 1,
        start_time: block.timestamp,
        target_duration: 600,  # 10 minutes
        participating_chains: [1, 137, 42161, 8453, 43114]
    })

    self.current_challenge = new_challenge

    # Broadcast to all chain contracts
    for chain_id in new_challenge.participating_chains:
        self._broadcast_challenge(chain_id, new_challenge)

    log GlobalChallengeGenerated(new_challenge.challenge, new_difficulty, new_challenge.epoch)
    return new_challenge

@external
def validateCrossChainSolution(
    solution: Bytes[128],
    source_chain: uint256,
    miner: address
) -> bool:
    """Validate that solution is unique across ALL chains"""
    solution_id: bytes32 = keccak256(solution)

    # Check global uniqueness
    assert not self.global_used_solutions[solution_id], "Solution already used globally"

    # Verify solution meets current difficulty
    assert self._verify_solution(solution, self.current_challenge), "Invalid solution"

    # Mark as used globally
    self.global_used_solutions[solution_id] = True

    # Trigger reward distribution across all chains
    self._distribute_cross_chain_rewards(solution_id, source_chain, miner)

    log CrossChainSolutionValidated(solution_id, source_chain, miner)
    return True

@internal
def _distribute_cross_chain_rewards(solution_id: bytes32, source_chain: uint256, finder: address):
    """Distribute block rewards proportionally across all participating chains"""

    total_reward: uint256 = 50 * 10**18  # 50 EVMORE base reward

    # Calculate rewards based on supply allocation
    for chain_id in self.current_challenge.participating_chains:
        chain_stats: ChainMiningStats = self.chain_stats[chain_id]
        chain_reward: uint256 = total_reward * chain_stats.supply_allocation / (21 * 10**6 * 10**18)

        # Send reward to chain-specific mining contract
        self._send_reward_to_chain(chain_id, chain_reward, finder if chain_id == source_chain else empty(address))

@internal
def _calculate_adjusted_difficulty(total_hash_rate: uint256) -> uint256:
    """Calculate globally adjusted difficulty based on total network hash rate"""

    # Target: 10 minutes per block across ALL chains combined
    target_time: uint256 = 600  # seconds
    actual_time: uint256 = block.timestamp - self.current_challenge.start_time

    if actual_time == 0:
        return self.current_challenge.difficulty

    # Difficulty adjustment algorithm (simplified)
    current_difficulty: uint256 = self.current_challenge.difficulty

    if actual_time < target_time:
        # Blocks too fast, increase difficulty
        new_difficulty: uint256 = current_difficulty + (current_difficulty * (target_time - actual_time)) / (target_time * 4)
        return min(new_difficulty, 32)  # Cap at 32 bits
    else:
        # Blocks too slow, decrease difficulty
        new_difficulty: uint256 = current_difficulty - (current_difficulty * (actual_time - target_time)) / (target_time * 4)
        return max(new_difficulty, 8)  # Minimum 8 bits
```

### 2. Chain-Specific Mining Contracts

```vyper
# @title EVMORE Federated Mining Contract (Chain-Specific)
# @notice Mining contract deployed on each participating EVM network

interface IFederatedOracle:
    def validateCrossChainSolution(solution: Bytes[128], source_chain: uint256, miner: address) -> bool: nonpayable
    def getCurrentChallenge() -> (bytes32, uint256, uint256): view  # challenge, difficulty, epoch

struct FederatedMiningState:
    chain_id: uint256
    supply_allocation: uint256  # This chain's portion of 21M
    oracle_address: address
    local_difficulty_multiplier: uint256  # Chain-specific adjustment

# Chain configuration
CHAIN_ID: immutable(uint256)
SUPPLY_ALLOCATION: immutable(uint256)  # e.g., 7M for Ethereum
ORACLE: immutable(address)

# Mining state
federated_state: FederatedMiningState
local_miners: HashMap[address, uint256]  # miner -> solutions submitted
epoch_rewards: HashMap[uint256, HashMap[address, uint256]]

@external
def __init__(chain_id: uint256, supply_allocation: uint256, oracle_address: address):
    self.CHAIN_ID = chain_id
    self.SUPPLY_ALLOCATION = supply_allocation
    self.ORACLE = oracle_address

    self.federated_state = FederatedMiningState({
        chain_id: chain_id,
        supply_allocation: supply_allocation,
        oracle_address: oracle_address,
        local_difficulty_multiplier: 100  # 1.0x (no adjustment)
    })

@external
def submitFederatedProof(solution: Bytes[128]):
    """Submit mining solution to federated network"""

    # Get current global challenge from oracle
    challenge: bytes32 = empty(bytes32)
    difficulty: uint256 = 0
    epoch: uint256 = 0
    challenge, difficulty, epoch = IFederatedOracle(self.ORACLE).getCurrentChallenge()

    # Apply local difficulty multiplier (for chain-specific tuning)
    local_difficulty: uint256 = difficulty * self.federated_state.local_difficulty_multiplier / 100

    # Verify solution locally first
    assert self._verify_solution_local(solution, challenge, local_difficulty), "Invalid solution"

    # Submit to oracle for global validation
    success: bool = IFederatedOracle(self.ORACLE).validateCrossChainSolution(
        solution,
        self.CHAIN_ID,
        msg.sender
    )

    assert success, "Global solution validation failed"

    # Track local mining activity
    self.local_miners[msg.sender] += 1

    log FederatedProofSubmitted(msg.sender, solution, epoch, self.CHAIN_ID)

@external
def claimFederatedReward(epoch: uint256):
    """Claim rewards from federated mining"""
    reward_amount: uint256 = self.epoch_rewards[epoch][msg.sender]
    assert reward_amount > 0, "No rewards to claim"

    # Clear reward to prevent double claiming
    self.epoch_rewards[epoch][msg.sender] = 0

    # Mint EVMORE tokens on this chain
    self._mint(msg.sender, reward_amount)

    log FederatedRewardClaimed(msg.sender, epoch, reward_amount, self.CHAIN_ID)

@external
def receiveCrossChainReward(miner: address, amount: uint256, epoch: uint256):
    """Receive reward allocation from oracle (called by oracle only)"""
    assert msg.sender == self.ORACLE, "Only oracle can distribute rewards"

    self.epoch_rewards[epoch][miner] += amount

    log CrossChainRewardReceived(miner, amount, epoch, self.CHAIN_ID)

@internal
def _verify_solution_local(solution: Bytes[128], challenge: bytes32, difficulty: uint256) -> bool:
    """Verify solution meets local difficulty requirements"""

    # Extract the 4 values from solution (32 bytes each)
    values: DynArray[bytes32, 4] = []
    for i in range(4):
        start_pos: uint256 = i * 32
        value: bytes32 = slice(solution, start_pos, 32)
        values.append(value)

    # Verify ascending order
    for i in range(3):
        assert convert(values[i], uint256) < convert(values[i + 1], uint256), "Values not in ascending order"

    # Verify collision property
    target_pattern: uint256 = 0
    mask: uint256 = (2 ** difficulty) - 1

    for i in range(4):
        hash_input: bytes32 = keccak256(concat(challenge, values[i]))
        pattern: uint256 = convert(hash_input, uint256) & mask

        if i == 0:
            target_pattern = pattern
        else:
            assert pattern == target_pattern, "Pattern mismatch"

    return True
```

## 🔄 Cross-Chain Communication Flow

### Challenge Synchronization
```
1. Oracle detects new epoch needed (based on time/solutions)
2. Oracle calculates global difficulty from all chain stats
3. Oracle generates new challenge with entropy
4. Oracle broadcasts challenge to ALL chain contracts
5. Each chain updates its local mining parameters
6. Miners on ALL chains start working on SAME challenge
```

### Solution Processing
```
1. Miner finds solution on Chain A
2. Chain A verifies solution locally
3. Chain A sends solution to Oracle for global validation
4. Oracle checks solution uniqueness across ALL chains
5. Oracle marks solution as used globally
6. Oracle calculates proportional rewards for each chain
7. Oracle sends reward instructions to ALL chain contracts
8. Each chain mints appropriate EVMORE amount for their miners
```

## 📊 Economic Distribution Example

### Block 1,000,000 Scenario
```
Challenge: 0xabcd1234...
Difficulty: 16 bits
Total Hash Rate: 1,000,000 H/s across all chains

Hash Rate Distribution:
├── Ethereum: 400,000 H/s (40% of network)
├── Polygon: 350,000 H/s (35% of network)
├── Arbitrum: 150,000 H/s (15% of network)
├── Base: 75,000 H/s (7.5% of network)
└── Avalanche: 25,000 H/s (2.5% of network)

Solution found by: Polygon miner "0x123..."
Block reward: 50 EVMORE

Reward Distribution:
├── Ethereum pool: 16.5 EVMORE (33% of 50)
├── Polygon pool: 16.5 EVMORE (33% of 50)
│   └── Extra finder bonus: +2.5 EVMORE to 0x123...
├── Arbitrum pool: 9.5 EVMORE (19% of 50)
├── Base pool: 5.0 EVMORE (10% of 50)
└── Avalanche pool: 2.5 EVMORE (5% of 50)
```

## ⚡ Benefits of Federated Mining

### For Miners
- **Geographic Optimization**: Mine on locally optimal chains
- **Cost Flexibility**: Choose chains based on gas costs
- **Reduced Competition**: Distribute mining across multiple pools
- **Network Diversification**: Not dependent on single chain

### For Users
- **Multi-Chain Native**: EVMORE exists natively on multiple chains
- **No Bridge Risk**: No cross-chain bridge vulnerabilities
- **Optimized Experience**: Use fastest/cheapest chain for each use case
- **Unified Liquidity**: Combined liquidity across all chains

### For Ecosystem
- **True Multi-Chain**: Not just wrapped tokens, but native EVMORE
- **Scalable Mining**: Distribute load across multiple networks
- **Future-Proof**: Adapt to changing blockchain landscape
- **Innovation**: Enables chain-specific optimizations

## 🔒 Security Considerations

### Global Solution Uniqueness
- Oracle maintains global HashMap of used solutions
- Solution IDs generated using keccak256 for uniqueness
- Cross-chain verification before any rewards distributed
- Replay attack prevention across ALL networks

### Oracle Security
- Multi-signature requirement for oracle operations
- Time-based challenge expiry (10 minutes)
- Rate limiting on solution submissions
- Emergency pause functionality

### Economic Security
- Supply allocation prevents chain dominance
- Difficulty adjustment based on global hash rate
- Proportional reward distribution maintains fairness
- Anti-gaming mechanisms across chains

## 🚀 Implementation Challenges

### Technical Complexity
- **Oracle Infrastructure**: Requires robust cross-chain communication
- **State Synchronization**: Must keep all chains in sync
- **Gas Optimization**: Oracle operations can be expensive
- **Network Latency**: Cross-chain verification delays

### Economic Risks
- **Oracle Dependency**: Single point of failure
- **Chain Imbalance**: Uneven adoption across chains
- **Gas Cost Variation**: Different costs on each chain
- **Liquidity Fragmentation**: Multiple EVMORE versions

## 🎯 Recommendation

While the Federated Mining Model is technically fascinating and truly innovative, it's **significantly more complex** than the Hub-and-Spoke model.

**Pros:**
- ✅ True multi-chain native EVMORE
- ✅ No bridge security risks
- ✅ Distributed mining load
- ✅ Future-proof architecture

**Cons:**
- ❌ High technical complexity
- ❌ Oracle dependency
- ❌ Higher development costs
- ❌ Regulatory complexity across chains

**For Phase 3 deployment, I'd recommend starting with Hub-and-Spoke (Option 2) and potentially evolving to Federated Mining (Option 3) in Phase 4 once the ecosystem matures.**