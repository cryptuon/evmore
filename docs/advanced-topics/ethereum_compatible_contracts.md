# Ethereum-Compatible EVMORE Contracts

This document shows the specific modifications needed to make the existing EVMORE contracts compatible with Ethereum deployment.

## KeccakCollisionVerifier.vy Modifications

```vy
# @version ^0.3.10

############################################
# KeccakCollision Parameters
############################################
N: constant(uint256) = 16  # Number of bits that must match
K: constant(uint256) = 4   # Number of values needed
SOLUTION_SIZE: constant(uint256) = 128  # K * 32 bytes

############################################
# Main Verification Function
############################################
@external
@view
def verify_solution(
    challenge: bytes32,
    solution: Bytes[128],  # K * 32 bytes
    difficulty: uint256
) -> bool:
    """
    @notice Verifies a KeccakCollision solution
    @param challenge Current mining challenge
    @param solution Raw solution bytes (K * 32-byte values)
    @param difficulty Current mining difficulty
    @return True if solution is valid
    """
    values: DynArray[bytes32, 4] = []
    
    # Parse each 32-byte value
    for i: uint256 in range(K):
        start_pos: uint256 = i * 32
        # Extract the full 32-byte value
        value: bytes32 = convert(slice(solution, start_pos, 32), bytes32)
        values.append(value)
        
        # Check ascending order
        if i > 0:
            if convert(values[i], uint256) <= convert(values[i-1], uint256):
                return False
    
    # Create bit mask for matching (optimized for common difficulties)
    mask: uint256 = 0
    if difficulty <= 32:
        mask = shift(1, difficulty) - 1
    else:
        # For higher difficulties, compute dynamically
        mask = MAX_UINT256 >> (256 - difficulty)
    
    # Calculate hashes and verify bit matches
    first_hash: uint256 = 0
    
    for i: uint256 in range(K):
        hash: bytes32 = keccak256(concat(challenge, values[i]))
        bits: uint256 = convert(hash, uint256) & mask
        
        if i == 0:
            first_hash = bits
        elif bits != first_hash:
            return False
            
    return True
```

## EvmoreToken.vy Modifications

```vy
# @version ^0.3.10

from ethereum.ercs import IERC20

implements: IERC20

# Define MiningProof struct
struct MiningProof:
    solution: Bytes[128]
    timestamp: uint256
    claimed: bool

interface IKeccakCollisionVerifier:
    def verify_solution(challenge: bytes32, solution: Bytes[128], difficulty: uint256) -> bool: view

# ERC20 Events
event Transfer:
    sender: indexed(address)
    receiver: indexed(address)
    amount: uint256

event Approval:
    owner: indexed(address)
    spender: indexed(address)
    amount: uint256

event Mining:
    miner: indexed(address)
    reward: uint256
    solution: Bytes[128]  # KeccakCollision solution size

# New Events
event Paused:
    account: address

event Unpaused:
    account: address

# Mining parameters
INITIAL_REWARD: public(constant(uint256)) = 50 * 10**18
HALVING_BLOCKS: public(constant(uint256)) = 210000
MAX_SUPPLY: public(constant(uint256)) = 21000000 * 10**18
TARGET_BLOCK_TIME: public(constant(uint256)) = 600  # 10 minutes in seconds
DIFFICULTY_ADJUSTMENT_INTERVAL: public(constant(uint256)) = 2016
MAX_ADJUSTMENT_FACTOR: public(constant(uint256)) = 4

# State Variables
name: public(String[32])
symbol: public(String[8])
decimals: public(uint8)
totalSupply: public(uint256)

balanceOf: public(HashMap[address, uint256])
allowance: public(HashMap[address, HashMap[address, uint256]])

blocksMined: public(uint256)
lastDifficultyAdjustment: public(uint256)
currentDifficulty: public(uint256)
difficultyStartBlock: public(uint256)
difficultyStartTimestamp: public(uint256)

verifier: public(IKeccakCollisionVerifier)
currentChallenge: public(bytes32)
lastMiningTimestamp: public(uint256)

pendingProofs: public(HashMap[address, MiningProof])

SUBMISSION_WINDOW: public(constant(uint256)) = 100  # Number of blocks to measure congestion
TARGET_SUBMISSIONS_PER_BLOCK: public(constant(uint256)) = 10

# Track submissions in window
submissionTimestamps: DynArray[uint256, 1000]  # Rolling window of submission times
currentEpochMiners: DynArray[address, 100]  # Miners who submitted valid proofs in current epoch

# New state variables to add after line 66
struct EpochData:
    block_number: uint256
    total_reward: uint256
    miner_count: uint256
    claimed_count: uint256
    timestamp: uint256

# Mapping of epoch number to epoch data
epochs: public(HashMap[uint256, EpochData])
# Mapping of epoch number to list of miners
epoch_miners: public(HashMap[uint256, DynArray[address, 100]])
# Track which epochs each miner has claimed
miner_claimed_epochs: public(HashMap[address, HashMap[uint256, bool]])
# Current epoch number
current_epoch: public(uint256)

# New state variables for security
owner: public(address)
paused: public(bool)

@deploy
def __init__(verifier_address: address):
    self.name = "EVM ORE Token"
    self.symbol = "EVMORE"
    self.decimals = 18
    self.totalSupply = 0
    self.verifier = IKeccakCollisionVerifier(verifier_address)
    self.currentDifficulty = 8  # Initial difficulty
    self.difficultyStartTimestamp = block.timestamp
    self.currentChallenge = self._generate_challenge()
    self.owner = msg.sender
    self.paused = False

@internal
def _generate_challenge() -> bytes32:
    # Simply combine timestamp and previous block hash
    challenge_input: Bytes[64] = concat(
        convert(block.timestamp, bytes32),
        block.prevhash
    )
    return keccak256(challenge_input)

@internal
def _adjust_difficulty() -> uint256:
    if self.blocksMined % DIFFICULTY_ADJUSTMENT_INTERVAL != 0:
        return self.currentDifficulty
        
    expected_time: uint256 = DIFFICULTY_ADJUSTMENT_INTERVAL * TARGET_BLOCK_TIME
    actual_time: uint256 = block.timestamp - self.difficultyStartTimestamp
    
    adjustment: uint256 = (actual_time * 100) // expected_time
    
    # Limit adjustment to 4x up or down
    if adjustment > MAX_ADJUSTMENT_FACTOR * 100:
        adjustment = MAX_ADJUSTMENT_FACTOR * 100
    elif adjustment < 100 // MAX_ADJUSTMENT_FACTOR:
        adjustment = 100 // MAX_ADJUSTMENT_FACTOR
        
    new_difficulty: uint256 = (self.currentDifficulty * 100) // adjustment
    
    # Ensure minimum difficulty
    if new_difficulty < 16:
        new_difficulty = 8
        
    return new_difficulty

@internal
def _adjust_difficulty_for_congestion() -> uint256:
    if len(self.submissionTimestamps) < 2:
        return self.currentDifficulty
        
    # Calculate submission rate per block
    time_span: uint256 = self.submissionTimestamps[len(self.submissionTimestamps)-1] - self.submissionTimestamps[0]
    blocks_span: uint256 = time_span // TARGET_BLOCK_TIME
    if blocks_span == 0:
        blocks_span = 1
    submission_count: uint256 = len(self.submissionTimestamps)
    submission_rate: uint256 = submission_count // blocks_span
    
    # Adjust difficulty based on submission rate
    if submission_rate > TARGET_SUBMISSIONS_PER_BLOCK:
        return self.currentDifficulty + 1
    elif submission_rate < TARGET_SUBMISSIONS_PER_BLOCK // 2:
        return max(self.currentDifficulty - 1, 16)
    
    return self.currentDifficulty

@external
def submitProof(solution: Bytes[128]) -> bool:
    """
    First step of mining - submit proof
    Must be unique solution and may trigger epoch transition
    """
    # Check if contract is paused
    assert not self.paused, "Contract is paused"
    
    assert staticcall self.verifier.verify_solution(
        self.currentChallenge, 
        solution,
        self.currentDifficulty
    ), "Invalid solution"
    
    # Check for duplicate solutions in current epoch
    current_miners: DynArray[address, 100] = self.epoch_miners[self.current_epoch]
    for i: uint256 in range(100):
        if i >= len(current_miners):
            break
        existing_proof: MiningProof = self.pendingProofs[current_miners[i]]
        assert existing_proof.solution != solution, "Duplicate solution"
    
    # Store proof
    self.pendingProofs[msg.sender] = MiningProof({
        solution: solution,
        timestamp: block.timestamp,
        claimed: False
    })
    
    # Add miner to current epoch if not present
    if msg.sender not in current_miners:
        current_miners.append(msg.sender)
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

# Add batch submission function
@external
def submitProofBatch(solutions: DynArray[Bytes[128], 10]) -> bool:
    """
    Submit multiple mining proofs in a single transaction
    """
    # Check if contract is paused
    assert not self.paused, "Contract is paused"
    
    assert len(solutions) <= 10, "Batch size exceeds limit"
    
    # Verify all solutions first to prevent partial processing
    for i: uint256 in range(len(solutions)):
        assert staticcall self.verifier.verify_solution(
            self.currentChallenge, 
            solutions[i],
            self.currentDifficulty
        ), "Invalid solution"
    
    # Process valid solutions
    for i: uint256 in range(len(solutions)):
        solution: Bytes[128] = solutions[i]
        
        # Check for duplicate solutions in current epoch
        current_miners: DynArray[address, 100] = self.epoch_miners[self.current_epoch]
        duplicate_found: bool = False
        for j: uint256 in range(len(current_miners)):
            if j >= len(current_miners):
                break
            existing_proof: MiningProof = self.pendingProofs[current_miners[j]]
            if existing_proof.solution == solution:
                duplicate_found = True
                break
                
        assert not duplicate_found, "Duplicate solution"
        
        # Store proof (using msg.sender for all submissions in batch)
        self.pendingProofs[msg.sender] = MiningProof({
            solution: solution,
            timestamp: block.timestamp,
            claimed: False
        })
        
        # Add miner to current epoch if not present
        miner_in_epoch: bool = False
        for j: uint256 in range(len(current_miners)):
            if j >= len(current_miners):
                break
            if current_miners[j] == msg.sender:
                miner_in_epoch = True
                break
                
        if not miner_in_epoch:
            current_miners.append(msg.sender)
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

@internal
def _transition_epoch():
    """
    Handle transition to new mining epoch
    """
    # Calculate base reward for current epoch
    epoch: uint256 = self.blocksMined // HALVING_BLOCKS
    base_reward: uint256 = shift(INITIAL_REWARD, -convert(epoch, int128))
    
    # Store current epoch data
    self.epochs[self.current_epoch] = EpochData({
        block_number: block.number,
        total_reward: base_reward,
        miner_count: len(self.epoch_miners[self.current_epoch]),
        claimed_count: 0,
        timestamp: block.timestamp
    })
    
    # Update mining state
    self.blocksMined += 1
    self.current_epoch += 1
    self.lastMiningTimestamp = block.timestamp
    
    # Adjust difficulty if needed
    if self.blocksMined % DIFFICULTY_ADJUSTMENT_INTERVAL == 0:
        self.currentDifficulty = self._adjust_difficulty()
        self.difficultyStartTimestamp = block.timestamp
    else:
        self.currentDifficulty = self._adjust_difficulty_for_congestion()
        
    # Generate new challenge
    self.currentChallenge = self._generate_challenge()

@external
def claimReward(epoch: uint256) -> bool:
    """
    Claim mining reward for a specific epoch
    """
    # Check if contract is paused
    assert not self.paused, "Contract is paused"
    
    assert epoch < self.current_epoch, "Epoch not finished"
    assert not self.miner_claimed_epochs[msg.sender][epoch], "Already claimed"
    
    epoch_data: EpochData = self.epochs[epoch]
    miner_in_epoch: bool = False
    
    # Check if miner was in this epoch
    current_miners: DynArray[address, 100] = self.epoch_miners[epoch]
    for i: uint256 in range(len(current_miners)):
        if i >= len(current_miners):
            break
        if current_miners[i] == msg.sender:
            miner_in_epoch = True
            break
            
    assert miner_in_epoch, "Not a miner in epoch"
    
    # Calculate individual reward
    reward: uint256 = epoch_data.total_reward // epoch_data.miner_count
    assert self.totalSupply + reward <= MAX_SUPPLY, "Max supply reached"
    
    # Mark as claimed
    self.miner_claimed_epochs[msg.sender][epoch] = True
    
    # Update epoch claimed count
    epoch_data.claimed_count += 1
    self.epochs[epoch] = epoch_data
    
    # Mint rewards
    self._mint(msg.sender, reward)
    
    # Emit mining event
    proof: MiningProof = self.pendingProofs[msg.sender]
    log Mining(msg.sender, reward, proof.solution)
    
    return True

@internal
def _mint(to: address, amount: uint256):
    self.totalSupply += amount
    self.balanceOf[to] += amount
    log Transfer(empty(address), to, amount)

# Security functions
@external
def pause() -> bool:
    """
    Pause the contract (owner only)
    """
    assert msg.sender == self.owner, "Only owner can pause"
    self.paused = True
    log Paused(msg.sender)
    return True

@external
def unpause() -> bool:
    """
    Unpause the contract (owner only)
    """
    assert msg.sender == self.owner, "Only owner can unpause"
    self.paused = False
    log Unpaused(msg.sender)
    return True

@external
def transferOwnership(new_owner: address) -> bool:
    """
    Transfer ownership (owner only)
    """
    assert msg.sender == self.owner, "Only owner can transfer ownership"
    self.owner = new_owner
    return True

@external
def withdraw() -> bool:
    """
    Withdraw contract balance (owner only)
    """
    assert msg.sender == self.owner, "Only owner can withdraw"
    send(self.owner, self.balance)
    return True

@external
def transfer(to: address, amount: uint256) -> bool:
    assert not self.paused, "Contract is paused"
    assert to != empty(address), "Invalid recipient"
    self.balanceOf[msg.sender] -= amount
    self.balanceOf[to] += amount
    log Transfer(msg.sender, to, amount)
    return True

@external
def approve(spender: address, amount: uint256) -> bool:
    assert not self.paused, "Contract is paused"
    self.allowance[msg.sender][spender] = amount
    log Approval(msg.sender, spender, amount)
    return True

@external
def transferFrom(sender: address, recipient: address, amount: uint256) -> bool:
    assert not self.paused, "Contract is paused"
    assert recipient != empty(address), "Invalid recipient"
    self.allowance[sender][msg.sender] -= amount
    self.balanceOf[sender] -= amount
    self.balanceOf[recipient] += amount
    log Transfer(sender, recipient, amount)
    return True
```

## Deployment Instructions

1. Compile the contracts with Vyper 0.3.10:
   ```bash
   vyper KeccakCollisionVerifier.vy -o KeccakCollisionVerifier.bin
   vyper EvmoreToken.vy -o EvmoreToken.bin
   ```

2. Deploy KeccakCollisionVerifier first to get its address

3. Deploy EvmoreToken with the verifier address as a parameter

4. Verify contracts on Etherscan for transparency

These modifications make the contracts Ethereum-compatible while preserving the core PoW mechanics of the EVMORE token.