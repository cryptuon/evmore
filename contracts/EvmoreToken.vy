# @version ^0.4.0
# SPDX-License-Identifier: MIT

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
    _from: indexed(address)
    _to: indexed(address)
    _value: uint256

event Approval:
    _owner: indexed(address)
    _spender: indexed(address)
    _value: uint256

event Mining:
    miner: indexed(address)
    reward: uint256
    solution: Bytes[128]  # KeccakCollision solution size

# New Events
event Paused:
    account: address

event Unpaused:
    account: address

event OwnershipTransferStarted:
    previous_owner: indexed(address)
    new_owner: indexed(address)

event OwnershipTransferred:
    previous_owner: indexed(address)
    new_owner: indexed(address)

event DifficultyAdjusted:
    old_difficulty: uint256
    new_difficulty: uint256
    block_number: uint256

event EpochTransition:
    old_epoch: indexed(uint256)
    new_epoch: indexed(uint256)
    total_reward: uint256
    miner_count: uint256

event ChallengeGenerated:
    new_challenge: indexed(bytes32)
    block_number: uint256

event ProofSubmitted:
    miner: indexed(address)
    epoch: indexed(uint256)
    solution_hash: indexed(bytes32)

event RewardClaimed:
    miner: indexed(address)
    epoch: indexed(uint256)
    amount: uint256

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
# Global solution hash tracking to prevent replay attacks
used_solution_hashes: HashMap[bytes32, bool]
# Current epoch number
current_epoch: public(uint256)

# Security state variables
owner: public(address)
pending_owner: public(address)
paused: public(bool)
reentrancy_lock: bool

# Bridge preparation (inactive until Stage 2)
bridge_contract: address
bridge_mint_enabled: bool
bridge_burn_enabled: bool

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
    """
    Generate a cryptographically secure challenge with multiple entropy sources
    """
    # Combine multiple entropy sources for better unpredictability
    challenge_input: Bytes[128] = concat(
        convert(block.timestamp, bytes32),      # Time entropy
        block.prevhash,                         # Previous block hash
        convert(block.number, bytes32),         # Block number
        convert(self.blocksMined, bytes32)      # Internal state entropy
    )
    new_challenge: bytes32 = keccak256(challenge_input)
    log ChallengeGenerated(new_challenge, block.number)
    return new_challenge

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

    # Log difficulty adjustment
    if new_difficulty != self.currentDifficulty:
        log DifficultyAdjusted(self.currentDifficulty, new_difficulty, block.number)

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

    # Check for global solution uniqueness (prevent replay attacks)
    solution_hash: bytes32 = keccak256(solution)
    assert not self.used_solution_hashes[solution_hash], "Solution already used"

    # Mark solution as used globally
    self.used_solution_hashes[solution_hash] = True

    # Store proof
    self.pendingProofs[msg.sender] = MiningProof({
        solution: solution,
        timestamp: block.timestamp,
        claimed: False
    })

    # Log proof submission
    log ProofSubmitted(msg.sender, self.current_epoch, solution_hash)

    # Add miner to current epoch if not present
    current_miners: DynArray[address, 100] = self.epoch_miners[self.current_epoch]
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

@internal
def _transition_epoch():
    """
    Handle transition to new mining epoch
    """
    # Calculate base reward for current epoch
    epoch: uint256 = self.blocksMined // HALVING_BLOCKS
    base_reward: uint256 = INITIAL_REWARD >> epoch
    
    # Store current epoch data
    miner_count: uint256 = len(self.epoch_miners[self.current_epoch])
    self.epochs[self.current_epoch] = EpochData({
        block_number: block.number,
        total_reward: base_reward,
        miner_count: miner_count,
        claimed_count: 0,
        timestamp: block.timestamp
    })

    # Log epoch transition
    old_epoch: uint256 = self.current_epoch
    log EpochTransition(old_epoch, old_epoch + 1, base_reward, miner_count)

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
    Protected against reentrancy
    """
    # Check if contract is paused
    assert not self.paused, "Contract is paused"
    assert not self.reentrancy_lock, "Reentrancy detected"

    # Set reentrancy lock
    self.reentrancy_lock = True
    
    assert epoch < self.current_epoch, "Epoch not finished"
    assert not self.miner_claimed_epochs[msg.sender][epoch], "Already claimed"
    
    epoch_data: EpochData = self.epochs[epoch]
    assert msg.sender in self.epoch_miners[epoch], "Not a miner in epoch"
    
    # Calculate individual reward with fair remainder distribution
    base_reward: uint256 = epoch_data.total_reward // epoch_data.miner_count
    remainder: uint256 = epoch_data.total_reward % epoch_data.miner_count

    # Get miner index for remainder distribution
    miner_index: uint256 = 0
    epoch_miners: DynArray[address, 100] = self.epoch_miners[epoch]
    for i: uint256 in range(100):
        if i >= len(epoch_miners):
            break
        if epoch_miners[i] == msg.sender:
            miner_index = i
            break

    # Distribute remainder to first N miners where N = remainder
    reward: uint256 = base_reward
    if miner_index < remainder:
        reward += 1

    assert self.totalSupply + reward <= MAX_SUPPLY, "Max supply reached"
    
    # Mark as claimed
    self.miner_claimed_epochs[msg.sender][epoch] = True
    
    # Update epoch claimed count
    epoch_data.claimed_count += 1
    self.epochs[epoch] = epoch_data
    
    # Mint rewards
    self._mint(msg.sender, reward)

    # Log reward claim
    log RewardClaimed(msg.sender, epoch, reward)

    # Emit mining event
    proof: MiningProof = self.pendingProofs[msg.sender]
    log Mining(msg.sender, reward, proof.solution)

    # Clear reentrancy lock
    self.reentrancy_lock = False

    return True

# Add batch submission function
@external
def submitProofBatch(solutions: DynArray[Bytes[128], 10]) -> bool:
    """
    Submit multiple mining proofs in a single transaction
    Optimized to prevent gas DoS attacks
    """
    # Check if contract is paused
    assert not self.paused, "Contract is paused"

    assert len(solutions) <= 10, "Batch size exceeds limit"
    assert len(solutions) > 0, "Empty batch not allowed"

    # Verify all solutions and check uniqueness efficiently
    solution_hashes: DynArray[bytes32, 10] = []
    solutions_len: uint256 = len(solutions)
    for i: uint256 in range(10):
        if i >= solutions_len:
            break
        solution: Bytes[128] = solutions[i]

        # Verify solution
        assert staticcall self.verifier.verify_solution(
            self.currentChallenge,
            solution,
            self.currentDifficulty
        ), "Invalid solution"

        # Check global uniqueness
        solution_hash: bytes32 = keccak256(solution)
        assert not self.used_solution_hashes[solution_hash], "Solution already used"

        # Check for duplicates within this batch
        for j: uint256 in range(10):
            if j >= len(solution_hashes):
                break
            assert solution_hashes[j] != solution_hash, "Duplicate in batch"

        solution_hashes.append(solution_hash)

    # Mark all solutions as used (all or nothing approach)
    for i: uint256 in range(10):
        if i >= len(solution_hashes):
            break
        self.used_solution_hashes[solution_hashes[i]] = True

    # Store the best solution (last one) for this miner
    best_solution: Bytes[128] = solutions[solutions_len - 1]
    self.pendingProofs[msg.sender] = MiningProof({
        solution: best_solution,
        timestamp: block.timestamp,
        claimed: False
    })

    # Add miner to current epoch if not already present
    current_miners: DynArray[address, 100] = self.epoch_miners[self.current_epoch]
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

@internal
def _mint(to: address, amount: uint256):
    self.totalSupply += amount
    self.balanceOf[to] += amount
    log Transfer(empty(address), to, amount)

@external
def transfer(_to: address, _value: uint256) -> bool:
    assert not self.paused, "Contract is paused"
    assert _to != empty(address), "Invalid recipient"
    self.balanceOf[msg.sender] -= _value
    self.balanceOf[_to] += _value
    log Transfer(msg.sender, _to, _value)
    return True

@external
def approve(_spender: address, _value: uint256) -> bool:
    assert not self.paused, "Contract is paused"
    self.allowance[msg.sender][_spender] = _value
    log Approval(msg.sender, _spender, _value)
    return True

@external
def transferFrom(_from: address, _to: address, _value: uint256) -> bool:
    assert not self.paused, "Contract is paused"
    assert _to != empty(address), "Invalid recipient"
    self.allowance[_from][msg.sender] -= _value
    self.balanceOf[_from] -= _value
    self.balanceOf[_to] += _value
    log Transfer(_from, _to, _value)
    return True

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
    Start ownership transfer process (owner only)
    New owner must accept to complete transfer
    """
    assert msg.sender == self.owner, "Only owner can transfer ownership"
    assert new_owner != empty(address), "New owner cannot be zero address"
    assert new_owner != self.owner, "New owner cannot be current owner"

    self.pending_owner = new_owner
    log OwnershipTransferStarted(self.owner, new_owner)
    return True

@external
def acceptOwnership() -> bool:
    """
    Accept ownership transfer (pending owner only)
    """
    assert msg.sender == self.pending_owner, "Only pending owner can accept"

    previous_owner: address = self.owner
    self.owner = self.pending_owner
    self.pending_owner = empty(address)

    log OwnershipTransferred(previous_owner, self.owner)
    return True

@external
def renounceOwnership() -> bool:
    """
    Renounce ownership permanently (owner only)
    """
    assert msg.sender == self.owner, "Only owner can renounce ownership"

    previous_owner: address = self.owner
    self.owner = empty(address)
    self.pending_owner = empty(address)

    log OwnershipTransferred(previous_owner, empty(address))
    return True

# Bridge integration functions (Stage 2+)

@external
def setBridgeContract(bridge_address: address) -> bool:
    """
    Set bridge contract address (owner only)
    """
    assert msg.sender == self.owner, "Only owner can set bridge contract"
    assert bridge_address != empty(address), "Invalid bridge address"

    self.bridge_contract = bridge_address
    return True

@external
def enableBridgeMint() -> bool:
    """
    Enable bridge minting (owner only)
    """
    assert msg.sender == self.owner, "Only owner can enable bridge mint"
    assert self.bridge_contract != empty(address), "Bridge contract not set"

    self.bridge_mint_enabled = True
    return True

@external
def enableBridgeBurn() -> bool:
    """
    Enable bridge burning (owner only)
    """
    assert msg.sender == self.owner, "Only owner can enable bridge burn"
    assert self.bridge_contract != empty(address), "Bridge contract not set"

    self.bridge_burn_enabled = True
    return True

@external
def bridgeMint(to: address, amount: uint256) -> bool:
    """
    Mint tokens for bridge (bridge contract only)
    """
    assert msg.sender == self.bridge_contract, "Only bridge contract can mint"
    assert self.bridge_mint_enabled, "Bridge minting not enabled"
    assert to != empty(address), "Invalid recipient"
    assert amount > 0, "Invalid amount"

    # Check max supply
    assert self.totalSupply + amount <= MAX_SUPPLY, "Exceeds max supply"

    # Mint tokens
    self.totalSupply += amount
    self.balanceOf[to] += amount

    log Transfer(empty(address), to, amount)
    return True

@external
def bridgeBurn(from_: address, amount: uint256) -> bool:
    """
    Burn tokens for bridge (bridge contract only)
    """
    assert msg.sender == self.bridge_contract, "Only bridge contract can burn"
    assert self.bridge_burn_enabled, "Bridge burning not enabled"
    assert from_ != empty(address), "Invalid address"
    assert amount > 0, "Invalid amount"
    assert self.balanceOf[from_] >= amount, "Insufficient balance"

    # Burn tokens
    self.balanceOf[from_] -= amount
    self.totalSupply -= amount

    log Transfer(from_, empty(address), amount)
    return True

@external
def withdraw() -> bool:
    """
    Withdraw contract balance (owner only)
    Protected against reentrancy
    """
    assert msg.sender == self.owner, "Only owner can withdraw"
    assert not self.reentrancy_lock, "Reentrancy detected"

    # Set reentrancy lock
    self.reentrancy_lock = True

    # Perform withdrawal using checks-effects-interactions pattern
    balance_to_withdraw: uint256 = self.balance

    # External call
    send(self.owner, balance_to_withdraw)

    # Clear reentrancy lock after external call completes
    self.reentrancy_lock = False

    return True