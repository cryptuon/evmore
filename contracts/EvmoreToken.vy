# @version ^0.4.0

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
    assert epoch < self.current_epoch, "Epoch not finished"
    assert not self.miner_claimed_epochs[msg.sender][epoch], "Already claimed"
    
    epoch_data: EpochData = self.epochs[epoch]
    assert msg.sender in self.epoch_miners[epoch], "Not a miner in epoch"
    
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

@external
def transfer(to: address, amount: uint256) -> bool:
    assert to != empty(address), "Invalid recipient"
    self.balanceOf[msg.sender] -= amount
    self.balanceOf[to] += amount
    log Transfer(msg.sender, to, amount)
    return True

@external
def approve(spender: address, amount: uint256) -> bool:
    self.allowance[msg.sender][spender] = amount
    log Approval(msg.sender, spender, amount)
    return True

@external
def transferFrom(sender: address, recipient: address, amount: uint256) -> bool:
    assert recipient != empty(address), "Invalid recipient"
    self.allowance[sender][msg.sender] -= amount
    self.balanceOf[sender] -= amount
    self.balanceOf[recipient] += amount
    log Transfer(sender, recipient, amount)
    return True