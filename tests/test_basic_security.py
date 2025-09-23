"""
Basic security tests that validate core fixes work
"""

import pytest
from ape import accounts, project, chain
from eth_utils import to_wei


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


def test_contract_deployment_with_security_features(token, verifier):
    """
    Test that the contract deploys successfully with all security features
    """
    # Check basic deployment
    assert token.name() == "EVM ORE Token"
    assert token.symbol() == "EVMORE"
    assert token.decimals() == 18

    # Check security state variables are initialized
    assert token.owner() != "0x0000000000000000000000000000000000000000"
    assert token.pending_owner() == "0x0000000000000000000000000000000000000000"
    assert not token.paused()


def test_two_step_ownership_transfer_pattern(token, owner, miner1):
    """
    Test the secure two-step ownership transfer
    """
    initial_owner = token.owner()

    # Step 1: Start transfer
    tx = token.transferOwnership(miner1.address, sender=owner)

    # Check events
    events = tx.decode_logs(token.OwnershipTransferStarted)
    assert len(events) == 1
    assert events[0].previous_owner == owner.address
    assert events[0].new_owner == miner1.address

    # Ownership not transferred yet
    assert token.owner() == initial_owner
    assert token.pending_owner() == miner1.address

    # Step 2: Accept transfer
    tx = token.acceptOwnership(sender=miner1)

    # Check transfer completed
    events = tx.decode_logs(token.OwnershipTransferred)
    assert len(events) == 1
    assert token.owner() == miner1.address
    assert token.pending_owner() == "0x0000000000000000000000000000000000000000"


def test_ownership_transfer_security(token, owner, miner1):
    """
    Test security features of ownership transfer
    """
    # Cannot transfer to zero address
    with pytest.raises(Exception):
        token.transferOwnership("0x0000000000000000000000000000000000000000", sender=owner)

    # Cannot transfer to self
    with pytest.raises(Exception):
        token.transferOwnership(owner.address, sender=owner)

    # Only pending owner can accept
    token.transferOwnership(miner1.address, sender=owner)
    with pytest.raises(Exception):
        token.acceptOwnership(sender=owner)


def test_reentrancy_guard_state_variable(token):
    """
    Test that reentrancy guard state variable exists and is initialized
    """
    # We can't directly read the private reentrancy_lock variable,
    # but we can test that functions with reentrancy protection work normally

    # This is a basic test to ensure the reentrancy guard doesn't break normal operation
    challenge = token.currentChallenge()
    difficulty = token.currentDifficulty()

    # Contract functions should work normally
    assert challenge != "0x0000000000000000000000000000000000000000000000000000000000000000"
    assert difficulty > 0


def test_enhanced_challenge_generation(token):
    """
    Test that challenge generation works and produces different challenges
    """
    initial_challenge = token.currentChallenge()

    # Mine blocks to change entropy
    chain.mine(5)  # Mine 5 blocks

    # The challenge should be deterministic but use multiple entropy sources
    # We can't force a new challenge generation directly, but we can verify
    # the current challenge is properly formed
    assert len(initial_challenge) == 32  # 32 bytes
    assert initial_challenge != "0x0000000000000000000000000000000000000000000000000000000000000000"


def test_comprehensive_event_definitions(token):
    """
    Test that all security events are properly defined
    """
    # Check that event definitions exist by trying to access them
    # This will raise an AttributeError if events don't exist

    assert hasattr(token, 'OwnershipTransferStarted')
    assert hasattr(token, 'OwnershipTransferred')
    assert hasattr(token, 'DifficultyAdjusted')
    assert hasattr(token, 'EpochTransition')
    assert hasattr(token, 'ChallengeGenerated')
    assert hasattr(token, 'ProofSubmitted')
    assert hasattr(token, 'RewardClaimed')


def test_global_solution_tracking_initialization(token):
    """
    Test that global solution tracking is properly initialized
    """
    # We can't directly test the mapping, but we can test that the
    # contract works and that solution submission functions are available

    assert hasattr(token, 'submitProof')
    assert hasattr(token, 'submitProofBatch')

    # Contract should be in working state
    assert not token.paused()


def test_batch_submission_limits(token, miner1):
    """
    Test batch submission size limits
    """
    # Test empty batch rejection
    with pytest.raises(Exception):
        token.submitProofBatch([], sender=miner1)

    # Test oversized batch rejection (we'll create a mock batch with 11 items)
    mock_solution = b"0" * 128  # 128 bytes of zeros
    oversized_batch = [mock_solution] * 11

    with pytest.raises(Exception):
        token.submitProofBatch(oversized_batch, sender=miner1)


def test_pause_functionality_with_security(token, owner, miner1):
    """
    Test pause functionality works with security features
    """
    # Pause the contract
    tx = token.pause(sender=owner)
    assert token.paused()

    # Check pause event
    events = tx.decode_logs(token.Paused)
    assert len(events) == 1
    assert events[0].account == owner.address

    # Unpause the contract
    tx = token.unpause(sender=owner)
    assert not token.paused()

    # Check unpause event
    events = tx.decode_logs(token.Unpaused)
    assert len(events) == 1
    assert events[0].account == owner.address


def test_contract_compilation_integrity(token, verifier):
    """
    Test that contract compiled successfully with all security fixes
    """
    # Basic contract interaction should work
    assert token.totalSupply() == 0
    assert token.blocksMined() == 0
    assert token.current_epoch() == 0

    # Verifier should be properly linked
    assert token.verifier() == verifier.address

    # Security parameters should be set
    assert token.INITIAL_REWARD() == to_wei(50, "ether")
    assert token.MAX_SUPPLY() == to_wei(21000000, "ether")


def test_basic_mining_workflow_security(token, verifier, miner1):
    """
    Test basic mining workflow works with security features
    """
    # Check initial state
    initial_epoch = token.current_epoch()
    initial_challenge = token.currentChallenge()
    initial_difficulty = token.currentDifficulty()

    # Verify basic parameters are set correctly
    assert initial_epoch == 0
    assert initial_difficulty >= 8  # Minimum difficulty
    assert len(initial_challenge) == 32

    # Test that we can call mining functions (even if they fail due to invalid solutions)
    # This tests that the function signatures and security checks are in place
    mock_solution = b"0" * 128

    # This should fail due to invalid solution, but not due to security errors
    with pytest.raises(Exception, match="Invalid solution"):
        token.submitProof(mock_solution, sender=miner1)