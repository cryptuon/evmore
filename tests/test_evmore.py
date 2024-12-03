import pytest
from ape import accounts, project, chain, Contract
from eth_utils import to_wei
from scripts.generate_mining_solution import generate_mining_solution

@pytest.fixture(scope="session", autouse=True)
def setup():
    # Connect to the network first
    chain.provider.connect()
    
    accounts.init_test_account(
        index=0,
        private_key="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
        address="0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    )
    accounts.init_test_account(
        index=1,
        private_key="0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d",
        address="0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
    )
    yield

@pytest.fixture(scope="session")
def owner():
    return accounts.test_accounts[0]

@pytest.fixture(scope="session")
def miner():
    return accounts.test_accounts[1]

@pytest.fixture
def verifier(owner):
    return owner.deploy(project.KeccakCollisionVerifier)

@pytest.fixture
def token(owner, verifier):
    return owner.deploy(project.EvmoreToken, verifier.address)

def test_token_deployment(token):
    assert token.name() == "EVM ORE Token"
    assert token.symbol() == "EVMORE"
    assert token.decimals() == 18
    assert token.totalSupply() == 0
    assert token.currentDifficulty() == 8  # Initial difficulty
    assert token.blocksMined() == 0
    assert token.current_epoch() == 0

def test_initial_mining_parameters(token):
    assert token.INITIAL_REWARD() == to_wei(50, "ether")
    assert token.HALVING_BLOCKS() == 210000
    assert token.MAX_SUPPLY() == to_wei(21000000, "ether")
    assert token.TARGET_BLOCK_TIME() == 600
    assert token.DIFFICULTY_ADJUSTMENT_INTERVAL() == 2016

def test_mining_process(token, verifier, miner):
    # Get current challenge and difficulty
    challenge = token.currentChallenge()
    difficulty = token.currentDifficulty()
    
    # Generate valid solution
    solution = generate_mining_solution(challenge, difficulty)
    
    # Verify solution directly with verifier
    assert verifier.verify_solution(challenge, solution, difficulty)
    
    # Submit proof
    initial_balance = token.balanceOf(miner)
    initial_supply = token.totalSupply()
    current_epoch = token.current_epoch()
    
    assert token.submitProof(solution, sender=miner)
    
    # Wait for target block time to trigger epoch transition
    chain.mine(timestamp=chain.pending_timestamp + token.TARGET_BLOCK_TIME())
    
    # Verify miner was added to epoch - check index 0 since it's the first miner
    assert token.epoch_miners(current_epoch, 0) == miner
    
    # Claim reward for the epoch
    token.claimReward(current_epoch, sender=miner)
    
    # Verify mining results
    expected_reward = token.INITIAL_REWARD()  # Full reward since only one miner
    assert token.balanceOf(miner) == initial_balance + expected_reward
    assert token.totalSupply() == initial_supply + expected_reward
    assert token.blocksMined() == 1
    
    # Verify epoch data
    epoch_data = token.epochs(current_epoch)
    assert epoch_data[0] > 0  # block_number
    assert epoch_data[1] == expected_reward  # total_reward
    assert epoch_data[2] == 1  # miner_count
    assert epoch_data[3] == 1  # claimed_count
    assert epoch_data[4] > 0  # timestamp

def test_cannot_claim_without_mining(token, miner):
    current_epoch = token.current_epoch()
    with pytest.raises(Exception):
        token.claimReward(current_epoch, sender=miner)

def test_cannot_claim_twice(token, miner):
    # Submit proof and wait for epoch transition
    solution = generate_mining_solution(token.currentChallenge(), token.currentDifficulty())
    token.submitProof(solution, sender=miner)
    chain.mine(timestamp=chain.pending_timestamp + token.TARGET_BLOCK_TIME())
    
    epoch = token.current_epoch() - 1
    token.claimReward(epoch, sender=miner)
    
    with pytest.raises(Exception):
        token.claimReward(epoch, sender=miner)

def test_reward_sharing(token, owner, miner):
    # First miner submits solution
    solution1 = generate_mining_solution(token.currentChallenge(), token.currentDifficulty())
    token.submitProof(solution1, sender=owner)
    
    # Wait for epoch transition to get new challenge
    chain.mine(timestamp=chain.pending_timestamp + token.TARGET_BLOCK_TIME())
    
    # Second miner submits solution for new challenge
    solution2 = generate_mining_solution(token.currentChallenge(), token.currentDifficulty())
    token.submitProof(solution2, sender=miner)
    
    # Wait for next epoch transition
    chain.mine(timestamp=chain.pending_timestamp + token.TARGET_BLOCK_TIME())
    
    # Both claim rewards from their respective epochs
    token.claimReward(token.current_epoch() - 2, sender=owner)
    token.claimReward(token.current_epoch() - 1, sender=miner)
    
    # Verify rewards
    expected_reward = token.INITIAL_REWARD()  # Full reward since one miner per epoch
    assert token.balanceOf(owner) == expected_reward
    assert token.balanceOf(miner) == expected_reward

def test_cannot_claim_future_epoch(token, miner):
    current_epoch = token.current_epoch()
    with pytest.raises(Exception):
        token.claimReward(current_epoch, sender=miner)

def test_difficulty_adjustment(token, miner):
    initial_difficulty = token.currentDifficulty()
    blocks_until_adjustment = token.DIFFICULTY_ADJUSTMENT_INTERVAL() - (token.blocksMined() % token.DIFFICULTY_ADJUSTMENT_INTERVAL())
    
    # Mine blocks quickly to trigger difficulty increase
    for _ in range(blocks_until_adjustment):
        solution = generate_mining_solution(token.currentChallenge(), token.currentDifficulty())
        token.submitProof(solution, sender=miner)
        chain.mine(timestamp=chain.pending_timestamp + 1)  # Mine blocks with 1 second intervals
    
    # Verify difficulty increased
    assert token.currentDifficulty() > initial_difficulty

def test_max_supply_limit(token, miner):
    current_supply = token.totalSupply()
    max_supply = token.MAX_SUPPLY()
    
    while current_supply < max_supply:
        solution = generate_mining_solution(token.currentChallenge(), token.currentDifficulty())
        token.submitProof(solution, sender=miner)
        chain.mine(timestamp=chain.pending_timestamp + token.TARGET_BLOCK_TIME())
        epoch = token.current_epoch() - 1
        token.claimReward(epoch, sender=miner)
        current_supply = token.totalSupply()
    
    # Try to mine one more block
    solution = generate_mining_solution(token.currentChallenge(), token.currentDifficulty())
    token.submitProof(solution, sender=miner)
    chain.mine(timestamp=chain.pending_timestamp + token.TARGET_BLOCK_TIME())
    epoch = token.current_epoch() - 1
    
    # Should revert due to max supply
    with pytest.raises(Exception):
        token.claimReward(epoch, sender=miner)

def test_token_transfer(token, owner, miner):
    # First mine some tokens
    challenge = token.currentChallenge()
    solution = generate_mining_solution(challenge, token.currentDifficulty())
    token.submitProof(solution, sender=owner)
    
    # Wait for epoch transition
    chain.mine(timestamp=chain.pending_timestamp + token.TARGET_BLOCK_TIME())
    
    # Claim reward from previous epoch
    token.claimReward(token.current_epoch() - 1, sender=owner)
    
    # Test transfer
    amount = to_wei(10, "ether")
    initial_owner_balance = token.balanceOf(owner)
    initial_miner_balance = token.balanceOf(miner)
    
    token.transfer(miner, amount, sender=owner)
    
    assert token.balanceOf(owner) == initial_owner_balance - amount
    assert token.balanceOf(miner) == initial_miner_balance + amount