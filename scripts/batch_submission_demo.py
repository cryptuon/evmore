#!/usr/bin/env python3

"""
Test script for batch submission functionality
"""

import random
from ape import accounts, project, networks, chain
from scripts.generate_mining_solution import generate_mining_solution


def test_batch_submission():
    # Connect to the network
    provider = networks.active_provider
    if not provider.is_connected:
        provider.connect()
    
    # Get accounts
    owner = accounts.test_accounts[0]
    miner1 = accounts.test_accounts[1]
    miner2 = accounts.test_accounts[2]
    
    # Deploy contracts
    print("Deploying contracts...")
    verifier = owner.deploy(project.KeccakCollisionVerifier)
    token = owner.deploy(project.EvmoreToken, verifier.address)
    
    print(f"Token deployed at: {token.address}")
    print(f"Initial difficulty: {token.currentDifficulty()}")
    
    # Generate some test solutions
    print("Generating test solutions...")
    challenge = token.currentChallenge()
    difficulty = token.currentDifficulty()
    
    # Generate solutions for miner1
    solutions1 = []
    for i in range(3):
        try:
            solution = generate_mining_solution(challenge, difficulty)
            solutions1.append(solution)
            print(f"Generated solution {i+1} for miner1")
        except Exception as e:
            print(f"Failed to generate solution {i+1}: {e}")
            continue
    
    # Generate solutions for miner2
    solutions2 = []
    for i in range(2):
        try:
            solution = generate_mining_solution(challenge, difficulty)
            solutions2.append(solution)
            print(f"Generated solution {i+1} for miner2")
        except Exception as e:
            print(f"Failed to generate solution {i+1}: {e}")
            continue
    
    # Test batch submission
    print("\nTesting batch submission...")
    
    # Submit batch from miner1
    if solutions1:
        try:
            tx = token.submitProofBatch(solutions1, sender=miner1)
            print(f"Batch submission from miner1 successful: {tx.txn_hash}")
        except Exception as e:
            print(f"Batch submission from miner1 failed: {e}")
    
    # Submit batch from miner2
    if solutions2:
        try:
            tx = token.submitProofBatch(solutions2, sender=miner2)
            print(f"Batch submission from miner2 successful: {tx.txn_hash}")
        except Exception as e:
            print(f"Batch submission from miner2 failed: {e}")
    
    # Wait for epoch transition
    print("\nWaiting for epoch transition...")
    chain.mine(timestamp=chain.pending_timestamp + token.TARGET_BLOCK_TIME())
    
    # Claim rewards
    print("\nClaiming rewards...")
    current_epoch = token.current_epoch() - 1
    
    try:
        tx = token.claimReward(current_epoch, sender=miner1)
        print(f"Miner1 claimed reward: {tx.txn_hash}")
        reward1 = token.balanceOf(miner1)
        print(f"Miner1 balance: {reward1 / 10**18} EVMORE")
    except Exception as e:
        print(f"Miner1 failed to claim reward: {e}")
    
    try:
        tx = token.claimReward(current_epoch, sender=miner2)
        print(f"Miner2 claimed reward: {tx.txn_hash}")
        reward2 = token.balanceOf(miner2)
        print(f"Miner2 balance: {reward2 / 10**18} EVMORE")
    except Exception as e:
        print(f"Miner2 failed to claim reward: {e}")
    
    # Test security functions
    print("\nTesting security functions...")
    
    # Test pause functionality
    try:
        tx = token.pause(sender=owner)
        print(f"Contract paused: {tx.txn_hash}")
    except Exception as e:
        print(f"Failed to pause contract: {e}")
    
    # Try to transfer tokens when paused
    try:
        tx = token.transfer(miner2, 100, sender=miner1)
        print(f"Transfer succeeded (unexpected): {tx.txn_hash}")
    except Exception as e:
        print(f"Transfer correctly blocked when paused: {type(e).__name__}")
    
    # Unpause contract
    try:
        tx = token.unpause(sender=owner)
        print(f"Contract unpaused: {tx.txn_hash}")
    except Exception as e:
        print(f"Failed to unpause contract: {e}")
    
    print("\n=== TEST COMPLETE ===")


if __name__ == "__main__":
    test_batch_submission()
