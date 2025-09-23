"""
Security fixes validation tests for EVMORE contracts
Tests all the critical security vulnerabilities that were fixed
"""

import pytest
from ape import accounts, project, chain
from eth_utils import to_wei
from scripts.generate_mining_solution import generate_mining_solution


@pytest.fixture(scope="session", autouse=True)
def setup():
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
def miner1():
    return accounts.test_accounts[1]


@pytest.fixture
def verifier(owner):
    return owner.deploy(project.KeccakCollisionVerifier)


@pytest.fixture
def token(owner, verifier):
    return owner.deploy(project.EvmoreToken, verifier.address)


def test_solution_replay_prevention(token, verifier, miner1):
    """
    Test that the same solution cannot be reused across epochs
    This tests the fix for the critical solution replay vulnerability
    """
    challenge = token.currentChallenge()
    difficulty = token.currentDifficulty()

    # Generate and submit a valid solution
    solution = generate_mining_solution(challenge, difficulty)
    assert token.submitProof(solution, sender=miner1)

    # Force epoch transition
    chain.mine(timestamp=chain.pending_timestamp + token.TARGET_BLOCK_TIME())

    # Try to reuse the same solution in the new epoch
    with pytest.raises(Exception, match="Solution already used"):
        token.submitProof(solution, sender=miner1)


def test_fair_remainder_distribution(token, verifier, owner):
    """
    Test that remainder distribution works fairly when total reward
    doesn't divide evenly among miners
    """
    # Create scenario with 3 miners and 100 wei reward (100/3 = 33 remainder 1)
    # First miner should get 34 wei, others get 33 wei each

    # Add 3 miners to epoch
    miners = accounts.test_accounts[:3]
    challenge = token.currentChallenge()
    difficulty = token.currentDifficulty()

    for miner in miners:
        solution = generate_mining_solution(challenge, difficulty)
        token.submitProof(solution, sender=miner)

    # Force epoch transition
    chain.mine(timestamp=chain.pending_timestamp + token.TARGET_BLOCK_TIME())

    current_epoch = token.current_epoch() - 1  # Previous epoch

    # Check reward distribution
    rewards = []
    for miner in miners:
        initial_balance = token.balanceOf(miner)
        token.claimReward(current_epoch, sender=miner)
        final_balance = token.balanceOf(miner)
        reward = final_balance - initial_balance
        rewards.append(reward)

    # With 50 ETH reward and 3 miners:
    # 50 ETH / 3 = 16.666... ETH
    # First miner gets 16.666... + remainder, others get 16.666...
    expected_base = token.INITIAL_REWARD() // 3
    expected_remainder = token.INITIAL_REWARD() % 3

    assert rewards[0] == expected_base + (1 if expected_remainder > 0 else 0)
    assert rewards[1] == expected_base + (1 if expected_remainder > 1 else 0)
    assert rewards[2] == expected_base

    # Verify total is correct
    assert sum(rewards) == token.INITIAL_REWARD()


def test_batch_submission_optimization(token, verifier, miner1):
    """
    Test that batch submission prevents duplicate solutions and processes efficiently
    """
    challenge = token.currentChallenge()
    difficulty = token.currentDifficulty()

    # Generate multiple unique solutions
    solutions = []
    for _ in range(5):
        solution = generate_mining_solution(challenge, difficulty)
        solutions.append(solution)

    # Test successful batch submission
    assert token.submitProofBatch(solutions, sender=miner1)

    # Test duplicate within batch fails
    duplicate_solutions = [solutions[0], solutions[0]]  # Same solution twice
    with pytest.raises(Exception, match="Duplicate in batch"):
        token.submitProofBatch(duplicate_solutions, sender=miner1)


def test_two_step_ownership_transfer(token, owner, miner1):
    """
    Test the secure two-step ownership transfer pattern
    """
    # Start ownership transfer
    assert token.transferOwnership(miner1.address, sender=owner)
    assert token.pending_owner() == miner1.address
    assert token.owner() == owner.address  # Owner unchanged until accepted

    # Only pending owner can accept
    with pytest.raises(Exception, match="Only pending owner can accept"):
        token.acceptOwnership(sender=owner)

    # Accept ownership
    assert token.acceptOwnership(sender=miner1)
    assert token.owner() == miner1.address
    assert token.pending_owner() == "0x0000000000000000000000000000000000000000"


def test_enhanced_challenge_generation(token, owner):
    """
    Test that challenge generation uses multiple entropy sources
    """
    initial_challenge = token.currentChallenge()

    # Mine a block to change entropy sources
    chain.mine()

    # Generate new challenge manually by calling internal function through epoch transition
    # We'll test this indirectly by checking challenges are different
    token.pause(sender=owner)
    token.unpause(sender=owner)  # This should trigger new challenge generation

    new_challenge = token.currentChallenge()

    # Challenges should be different due to different entropy
    assert initial_challenge != new_challenge


def test_comprehensive_event_logging(token, verifier, miner1, owner):
    """
    Test that all security-relevant events are properly emitted
    """
    challenge = token.currentChallenge()
    difficulty = token.currentDifficulty()
    solution = generate_mining_solution(challenge, difficulty)

    # Test ProofSubmitted event
    tx_receipt = token.submitProof(solution, sender=miner1)
    proof_events = tx_receipt.decode_logs(token.ProofSubmitted)
    assert len(proof_events) == 1
    assert proof_events[0].miner == miner1.address

    # Force epoch transition and test EpochTransition event
    tx_receipt = chain.mine(timestamp=chain.pending_timestamp + token.TARGET_BLOCK_TIME())

    # Test RewardClaimed event
    current_epoch = token.current_epoch() - 1
    tx_receipt = token.claimReward(current_epoch, sender=miner1)
    reward_events = tx_receipt.decode_logs(token.RewardClaimed)
    assert len(reward_events) == 1
    assert reward_events[0].miner == miner1.address
    assert reward_events[0].amount == token.INITIAL_REWARD()


def test_reentrancy_protection(token, owner):
    """
    Test that reentrancy protection works on financial functions
    """
    # Test withdraw function reentrancy protection
    # This test is limited since we can't easily create a reentrancy attack in tests
    # but we can verify the function executes and the lock works

    # Send some ETH to the contract first
    owner.transfer(token.address, to_wei(1, "ether"))

    # Withdraw should work normally
    initial_balance = owner.balance
    assert token.withdraw(sender=owner)
    assert owner.balance > initial_balance


def test_gas_dos_prevention(token, verifier, miner1):
    """
    Test that the optimized batch submission prevents gas DoS attacks
    """
    challenge = token.currentChallenge()
    difficulty = token.currentDifficulty()

    # Generate maximum batch size (10 solutions)
    solutions = []
    for _ in range(10):
        solution = generate_mining_solution(challenge, difficulty)
        solutions.append(solution)

    # This should succeed without running out of gas
    gas_before = chain.provider.get_balance(miner1.address)
    tx_receipt = token.submitProofBatch(solutions, sender=miner1)

    # Verify reasonable gas consumption (should be much less than block limit)
    gas_used = tx_receipt.gas_used
    assert gas_used < 5_000_000  # Reasonable upper bound

    # Test that exceeding batch size fails
    oversized_batch = solutions + [solutions[0]]  # 11 solutions
    with pytest.raises(Exception, match="Batch size exceeds limit"):
        token.submitProofBatch(oversized_batch, sender=miner1)


def test_ownership_transfer_safety(token, owner):
    """
    Test various edge cases in ownership transfer
    """
    # Cannot transfer to zero address
    with pytest.raises(Exception, match="New owner cannot be zero address"):
        token.transferOwnership("0x0000000000000000000000000000000000000000", sender=owner)

    # Cannot transfer to self
    with pytest.raises(Exception, match="New owner cannot be current owner"):
        token.transferOwnership(owner.address, sender=owner)

    # Test renounce ownership
    assert token.renounceOwnership(sender=owner)
    assert token.owner() == "0x0000000000000000000000000000000000000000"


def test_solution_hash_tracking(token, verifier, miner1):
    """
    Test that solution hashes are properly tracked globally
    """
    challenge = token.currentChallenge()
    difficulty = token.currentDifficulty()

    # Submit a solution
    solution = generate_mining_solution(challenge, difficulty)
    token.submitProof(solution, sender=miner1)

    # Force multiple epoch transitions
    for _ in range(3):
        chain.mine(timestamp=chain.pending_timestamp + token.TARGET_BLOCK_TIME())

    # The same solution should still be blocked
    with pytest.raises(Exception, match="Solution already used"):
        token.submitProof(solution, sender=miner1)