#!/usr/bin/env python3

"""
Deployment script for EVMORE contracts
"""

import sys
from ape import accounts, project, networks


def deploy_contracts():
    # Connect to the network
    networks.parse_network_choice("ethereum:local:hardhat").__enter__()
    
    # Get the account to deploy from
    # Using the first test account for now
    account = accounts.test_accounts[0]
    
    print(f"Deploying from account: {account.address}")
    
    # Deploy the verifier contract first
    print("Deploying KeccakCollisionVerifier...")
    verifier = account.deploy(project.KeccakCollisionVerifier)
    print(f"KeccakCollisionVerifier deployed at: {verifier.address}")
    
    # Deploy the token contract
    print("Deploying EvmoreToken...")
    token = account.deploy(project.EvmoreToken, verifier.address)
    print(f"EvmoreToken deployed at: {token.address}")
    
    # Print contract info
    print("\n=== CONTRACT INFO ===")
    print(f"Verifier Address: {verifier.address}")
    print(f"Token Address: {token.address}")
    print(f"Initial Difficulty: {token.currentDifficulty()}")
    print(f"Current Challenge: {token.currentChallenge().hex()}")
    
    return verifier, token


if __name__ == "__main__":
    try:
        deploy_contracts()
    except Exception as e:
        print(f"Deployment failed: {e}")
        sys.exit(1)
