#!/usr/bin/env python3

"""
Demo script for EVMORE mining workflow
This script demonstrates the complete mining workflow:
1. Deploy contracts
2. Generate a mining solution
3. Submit the solution
4. Claim the reward
"""

import random
import sys
import os

# Add the parent directory to the path so we can import the scripts
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ape import accounts, project, networks, chain
from scripts.generate_mining_solution import generate_mining_solution

def demo_mining_workflow():
    print("=== EVMORE Mining Workflow Demo ===\n")
    
    # Connect to local network (Hardhat)
    print("Connecting to local network...")
    networks.parse_network_choice("ethereum:local:hardhat").__enter__()
    
    # Get accounts
    owner = accounts.test_accounts[0]
    miner = accounts.test_accounts[1]
    
    print(f"Owner account: {owner.address}")
    print(f"Miner account: {miner.address}\n")
    
    # Deploy contracts
    print("Deploying contracts...")
    verifier = owner.deploy(project.KeccakCollisionVerifier)
    token = owner.deploy(project.EvmoreToken, verifier.address)
    
    print(f"Verifier deployed at: {verifier.address}")
    print(f"Token deployed at: {token.address}")
    print(f"Initial difficulty: {token.currentDifficulty()}")
    print(f"Current challenge: {token.currentChallenge().hex()}\n")
    
    # Generate mining solution
    print("Generating mining solution...")
    challenge = token.currentChallenge()
    difficulty = token.currentDifficulty()
    
    try:
        solution = generate_mining_solution(challenge, difficulty)
        print(f"Generated solution of {len(solution)} bytes")
        
        # Verify solution with verifier contract
        print("Verifying solution with contract...")
        is_valid = verifier.verify_solution(challenge, solution, difficulty)
        print(f"Solution is valid: {is_valid}")
        
        if not is_valid:
            print("ERROR: Generated solution is not valid!")
            return False
            
    except Exception as e:
        print(f"ERROR: Failed to generate solution: {e}")
        return False
    
    # Submit proof
    print("\nSubmitting proof...")
    try:
        tx = token.submitProof(solution, sender=miner)
        print(f"Proof submitted in transaction: {tx.txn_hash}")
        
        # Check if miner was added to epoch
        current_epoch = token.current_epoch()
        miner_in_epoch = False
        
        # Check up to 100 miners (max array size)
        for i in range(100):
            try:
                epoch_miner = token.epoch_miners(current_epoch, i)
                if epoch_miner == miner.address:
                    miner_in_epoch = True
                    break
            except:
                # Index out of bounds, no more miners
                break
                
        print(f"Miner added to epoch: {miner_in_epoch}")
        
    except Exception as e:
        print(f"ERROR: Failed to submit proof: {e}")
        return False
    
    # Wait for epoch transition
    print("\nWaiting for epoch transition...")
    chain.mine(timestamp=chain.pending_timestamp + token.TARGET_BLOCK_TIME())
    
    # Claim reward
    print("Claiming reward...")
    try:
        # The epoch that just finished is current_epoch - 1
        finished_epoch = token.current_epoch() - 1
        tx = token.claimReward(finished_epoch, sender=miner)
        print(f"Reward claimed in transaction: {tx.txn_hash}")
        
        # Check miner balance
        balance = token.balanceOf(miner)
        print(f"Miner balance: {balance / 10**18} EVMORE")
        
    except Exception as e:
        print(f"ERROR: Failed to claim reward: {e}")
        return False
    
    print("\n=== Demo Completed Successfully! ===")
    return True

if __name__ == "__main__":
    try:
        success = demo_mining_workflow()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Demo failed with error: {e}")
        sys.exit(1)