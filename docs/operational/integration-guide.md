# EVMORE Integration Guide - Security Enhanced Version

## Overview

This guide documents the integration changes and new features introduced with the security fixes for EVMORE contracts. All critical vulnerabilities have been resolved, and new security features have been added.

## Contract Changes Summary

### Major Security Enhancements

1. **Global Solution Uniqueness Tracking** - Prevents replay attacks across epochs
2. **Fair Reward Distribution** - Eliminates precision loss in reward calculations
3. **Two-Step Ownership Transfer** - Secure ownership management
4. **Enhanced Challenge Generation** - Multi-source entropy for better security
5. **Comprehensive Event Logging** - Full transparency and monitoring capabilities
6. **Reentrancy Protection** - Guards against reentrancy attacks
7. **Gas Optimization** - Improved batch processing efficiency

## API Changes and New Features

### New State Variables

```vyper
# Global solution tracking (prevents replay attacks)
used_solution_hashes: HashMap[bytes32, bool]

# Two-step ownership transfer
pending_owner: public(address)

# Reentrancy protection
reentrancy_lock: bool
```

### New Events

```vyper
# Ownership management
event OwnershipTransferStarted:
    previous_owner: indexed(address)
    new_owner: indexed(address)

event OwnershipTransferred:
    previous_owner: indexed(address)
    new_owner: indexed(address)

# Mining operations
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
```

### Enhanced Functions

#### Two-Step Ownership Transfer

```python
# OLD: Single-step transfer (UNSAFE)
token.transferOwnership(new_owner, sender=current_owner)

# NEW: Two-step transfer (SECURE)
# Step 1: Initiate transfer
token.transferOwnership(new_owner, sender=current_owner)

# Step 2: New owner accepts (must be called by new_owner)
token.acceptOwnership(sender=new_owner)

# Alternative: Renounce ownership permanently
token.renounceOwnership(sender=current_owner)
```

#### Enhanced Proof Submission

```python
# Single proof submission (now with global uniqueness check)
tx = token.submitProof(solution, sender=miner)

# Extract events
proof_events = tx.decode_logs(token.ProofSubmitted)
print(f"Solution hash: {proof_events[0].solution_hash}")

# Batch submission (optimized for gas efficiency)
solutions = [solution1, solution2, solution3]  # Max 10 solutions
tx = token.submitProofBatch(solutions, sender=miner)
```

#### Reward Claiming with Fair Distribution

```python
# Enhanced reward claiming with remainder distribution
epoch = 5
tx = token.claimReward(epoch, sender=miner)

# Extract reward information
reward_events = tx.decode_logs(token.RewardClaimed)
amount_received = reward_events[0].amount
print(f"Reward received: {amount_received / 10**18} EVMORE")
```

## Integration Code Examples

### Basic Mining Workflow

```python
from ape import accounts, project

def complete_mining_workflow():
    # Deploy contracts
    owner = accounts[0]
    miner = accounts[1]

    verifier = owner.deploy(project.KeccakCollisionVerifier)
    token = owner.deploy(project.EvmoreToken, verifier.address)

    # Get current mining parameters
    challenge = token.currentChallenge()
    difficulty = token.currentDifficulty()
    current_epoch = token.current_epoch()

    print(f"Challenge: {challenge.hex()}")
    print(f"Difficulty: {difficulty}")
    print(f"Current Epoch: {current_epoch}")

    # Generate and submit solution (implementation dependent)
    solution = generate_valid_solution(challenge, difficulty)

    # Submit proof
    tx = token.submitProof(solution, sender=miner)

    # Monitor events
    proof_events = tx.decode_logs(token.ProofSubmitted)
    print(f"Proof submitted for epoch {proof_events[0].epoch}")

    # Wait for epoch transition (600 seconds or manual trigger)
    # ... time passes or manual epoch transition ...

    # Claim reward
    reward_tx = token.claimReward(current_epoch, sender=miner)
    reward_events = reward_tx.decode_logs(token.RewardClaimed)

    print(f"Reward claimed: {reward_events[0].amount / 10**18} EVMORE")
```

### Event Monitoring Setup

```python
def setup_event_monitoring(token):
    """Set up comprehensive event monitoring"""

    # Mining events
    def on_proof_submitted(event):
        print(f"New proof submitted by {event.miner} for epoch {event.epoch}")
        print(f"Solution hash: {event.solution_hash.hex()}")

    def on_epoch_transition(event):
        print(f"Epoch transition: {event.old_epoch} → {event.new_epoch}")
        print(f"Total reward: {event.total_reward / 10**18} EVMORE")
        print(f"Miner count: {event.miner_count}")

    def on_difficulty_adjusted(event):
        print(f"Difficulty adjusted: {event.old_difficulty} → {event.new_difficulty}")
        print(f"Block: {event.block_number}")

    # Security events
    def on_ownership_transfer_started(event):
        print(f"Ownership transfer initiated: {event.previous_owner} → {event.new_owner}")

    def on_ownership_transferred(event):
        print(f"Ownership transferred: {event.previous_owner} → {event.new_owner}")

    # Register event handlers
    token.ProofSubmitted.subscribe(on_proof_submitted)
    token.EpochTransition.subscribe(on_epoch_transition)
    token.DifficultyAdjusted.subscribe(on_difficulty_adjusted)
    token.OwnershipTransferStarted.subscribe(on_ownership_transfer_started)
    token.OwnershipTransferred.subscribe(on_ownership_transferred)
```

### Gas-Optimized Batch Mining

```python
def efficient_batch_mining(token, miner, challenges_and_solutions):
    """Efficiently submit multiple solutions in batches"""

    MAX_BATCH_SIZE = 10
    total_solutions = len(challenges_and_solutions)

    for i in range(0, total_solutions, MAX_BATCH_SIZE):
        batch = challenges_and_solutions[i:i + MAX_BATCH_SIZE]
        solutions = [item['solution'] for item in batch]

        try:
            # Submit batch
            tx = token.submitProofBatch(solutions, sender=miner)
            gas_used = tx.gas_used

            print(f"Batch {i//MAX_BATCH_SIZE + 1} submitted successfully")
            print(f"Solutions in batch: {len(solutions)}")
            print(f"Gas used: {gas_used:,}")

            # Extract events
            proof_events = tx.decode_logs(token.ProofSubmitted)
            for event in proof_events:
                print(f"  Solution hash: {event.solution_hash.hex()[:16]}...")

        except Exception as e:
            print(f"Batch {i//MAX_BATCH_SIZE + 1} failed: {e}")

            # Fallback to individual submissions
            for solution in solutions:
                try:
                    token.submitProof(solution, sender=miner)
                except Exception as individual_error:
                    print(f"Individual solution failed: {individual_error}")
```

## Breaking Changes

### 1. Solution Uniqueness Enforcement

**Impact**: Solutions cannot be reused across epochs
**Migration**: Ensure mining software generates unique solutions

```python
# OLD: Could reuse solutions across epochs
solution = generate_solution_once()
for epoch in range(10):
    token.submitProof(solution, sender=miner)  # This would work

# NEW: Must generate unique solutions
for epoch in range(10):
    challenge = token.currentChallenge()
    solution = generate_unique_solution(challenge, epoch)
    token.submitProof(solution, sender=miner)  # Each must be unique
```

### 2. Ownership Transfer Process

**Impact**: Ownership transfers require two steps
**Migration**: Update admin interfaces to handle pending ownership

```python
# OLD: Direct transfer
token.transferOwnership(new_owner, sender=current_owner)
# Ownership immediately transferred

# NEW: Two-step process
token.transferOwnership(new_owner, sender=current_owner)
# Ownership NOT transferred yet, new_owner must accept
token.acceptOwnership(sender=new_owner)
# Ownership now transferred
```

### 3. Batch Submission Behavior

**Impact**: Batch submission stores only the last solution per miner
**Migration**: Adjust expectations for batch processing

```python
# OLD: All solutions in batch were stored
batch = [solution1, solution2, solution3]
token.submitProofBatch(batch, sender=miner)
# All 3 solutions stored for miner

# NEW: Only the last solution is stored per miner
batch = [solution1, solution2, solution3]
token.submitProofBatch(batch, sender=miner)
# Only solution3 is stored for miner, but all are marked as used globally
```

## Security Considerations for Integrators

### 1. Solution Generation

- **Never reuse solutions**: Each solution must be globally unique
- **Secure randomness**: Use cryptographically secure random number generation
- **Solution validation**: Always validate solutions locally before submission

### 2. Event Monitoring

- **Monitor all events**: Security events provide critical operational information
- **Set up alerts**: Configure alerts for ownership changes and security events
- **Log everything**: Maintain comprehensive logs for audit trails

### 3. Error Handling

```python
def safe_proof_submission(token, solution, miner):
    """Safely submit proof with proper error handling"""
    try:
        # Check if contract is paused
        if token.paused():
            raise Exception("Contract is paused")

        # Validate solution locally first
        challenge = token.currentChallenge()
        difficulty = token.currentDifficulty()
        verifier = token.verifier()

        if not verifier.verify_solution(challenge, solution, difficulty):
            raise Exception("Solution validation failed")

        # Submit proof
        tx = token.submitProof(solution, sender=miner)
        return tx

    except Exception as e:
        if "Solution already used" in str(e):
            print("Solution has been used before - generate new solution")
        elif "Invalid solution" in str(e):
            print("Solution is mathematically invalid")
        elif "Contract is paused" in str(e):
            print("Contract operations are paused")
        else:
            print(f"Unexpected error: {e}")
        raise
```

## Testing Integration

### Unit Tests for Integration

```python
def test_solution_uniqueness_integration():
    """Test that integration respects solution uniqueness"""
    solution = generate_valid_solution()

    # First submission should succeed
    token.submitProof(solution, sender=miner1)

    # Second submission should fail
    with pytest.raises(Exception, match="Solution already used"):
        token.submitProof(solution, sender=miner2)

def test_ownership_transfer_integration():
    """Test two-step ownership transfer integration"""
    # Initiate transfer
    token.transferOwnership(new_owner, sender=current_owner)
    assert token.pending_owner() == new_owner
    assert token.owner() == current_owner

    # Complete transfer
    token.acceptOwnership(sender=new_owner)
    assert token.owner() == new_owner
    assert token.pending_owner() == ZERO_ADDRESS

def test_event_monitoring_integration():
    """Test that events are properly emitted and can be monitored"""
    events_received = []

    def event_handler(event):
        events_received.append(event)

    token.ProofSubmitted.subscribe(event_handler)
    token.submitProof(solution, sender=miner)

    assert len(events_received) == 1
    assert events_received[0].miner == miner
```

## Performance Optimizations

### Gas Usage Guidelines

| Operation | Estimated Gas | Notes |
|-----------|---------------|-------|
| submitProof() | ~150,000 | Single solution submission |
| submitProofBatch(10) | ~800,000 | 10 solutions in batch |
| claimReward() | ~80,000 | With reentrancy protection |
| transferOwnership() | ~50,000 | Start ownership transfer |
| acceptOwnership() | ~45,000 | Complete ownership transfer |

### Best Practices

1. **Batch Operations**: Use batch submission for multiple solutions
2. **Event Filtering**: Filter events by indexed parameters for efficiency
3. **Local Validation**: Validate solutions locally before submission
4. **Error Recovery**: Implement robust error handling and retry logic

## Migration Checklist

### For Existing Integrations

- [ ] Update solution generation to ensure uniqueness
- [ ] Modify ownership transfer workflows for two-step process
- [ ] Add event monitoring for security events
- [ ] Update error handling for new error messages
- [ ] Test batch submission behavior changes
- [ ] Verify gas limit adjustments for new features
- [ ] Update documentation and user interfaces

### For New Integrations

- [ ] Implement comprehensive event monitoring
- [ ] Use secure solution generation practices
- [ ] Implement proper error handling
- [ ] Follow gas optimization guidelines
- [ ] Set up security monitoring and alerting
- [ ] Test all edge cases and error conditions

## Support and Resources

### Getting Help

- **Documentation**: Complete API documentation in `/docs`
- **Examples**: Reference implementations in `/scripts`
- **Tests**: Comprehensive test suite in `/tests`
- **Issues**: Report issues via GitHub

### Security Best Practices

1. **Never commit private keys** to version control
2. **Use multi-signature wallets** for contract ownership
3. **Monitor events continuously** for security incidents
4. **Test on testnets first** before mainnet deployment
5. **Keep dependencies updated** and audit third-party code

This integration guide ensures safe and efficient integration with the security-enhanced EVMORE contracts.