#!/usr/bin/env python3
"""
EVMORE Stage 1 Deployment Script
Deploy immediately to Ethereum mainnet for ~$500 gas cost
"""

import sys
import json
import time
from datetime import datetime
from ape import accounts, project, networks, chain
from eth_utils import to_wei

def log_info(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def deploy_stage1():
    """Deploy EVMORE Stage 1 to Ethereum mainnet"""

    log_info("🚀 Starting EVMORE Stage 1 Deployment")
    log_info("💎 Deploying Digital Gold to Ethereum Mainnet")

    # Check network
    try:
        current_block = chain.blocks.height
        log_info(f"✅ Connected to network. Current block: {current_block}")
    except Exception as e:
        log_info(f"❌ Network connection failed: {e}")
        sys.exit(1)

    # Get deployer account
    if len(accounts) == 0:
        log_info("❌ No accounts available for deployment")
        sys.exit(1)

    deployer = accounts[0]  # Use first available account
    balance = deployer.balance
    log_info(f"👤 Deployer: {deployer.address}")
    log_info(f"💰 Balance: {balance / 10**18:.4f} ETH")

    if balance < to_wei(0.02, "ether"):  # Need ~0.02 ETH for deployment
        log_info("❌ Insufficient ETH for deployment (~0.02 ETH needed)")
        sys.exit(1)

    deployment_start = time.time()

    try:
        # Deploy KeccakCollisionVerifier first
        log_info("📦 Deploying KeccakCollisionVerifier...")
        verifier = deployer.deploy(project.KeccakCollisionVerifier)
        verifier_gas = verifier.creation_metadata.receipt.gas_used
        log_info(f"✅ Verifier deployed at: {verifier.address}")
        log_info(f"⛽ Gas used: {verifier_gas:,}")

        # Deploy EVMORE Token with migration capabilities
        log_info("📦 Deploying EVMORE Token (Stage 1 with migration hooks)...")
        evmore = deployer.deploy(project.EvmoreToken, verifier.address)
        evmore_gas = evmore.creation_metadata.receipt.gas_used
        log_info(f"✅ EVMORE deployed at: {evmore.address}")
        log_info(f"⛽ Gas used: {evmore_gas:,}")

        deployment_time = time.time() - deployment_start
        total_gas = verifier_gas + evmore_gas

        # Validate deployment
        log_info("🔍 Validating deployment...")

        # Basic validation
        assert evmore.name() == "Evmore", "Invalid token name"
        assert evmore.symbol() == "EVMORE", "Invalid token symbol"
        assert evmore.decimals() == 18, "Invalid decimals"
        assert evmore.totalSupply() == 0, "Initial supply should be 0"
        assert evmore.owner() == deployer.address, "Invalid owner"
        assert evmore.verifier() == verifier.address, "Invalid verifier"

        log_info("✅ Deployment validation passed")

        # Test mining interface
        challenge = evmore.currentChallenge()
        difficulty = evmore.currentDifficulty()
        epoch = evmore.current_epoch()

        log_info(f"⛏️  Mining Status:")
        log_info(f"   Challenge: {challenge.hex()[:16]}...")
        log_info(f"   Difficulty: {difficulty} bits")
        log_info(f"   Epoch: {epoch}")

        # Save deployment info
        deployment_info = {
            "network": "ethereum",
            "timestamp": datetime.now().isoformat(),
            "deployment_time": deployment_time,
            "total_gas_used": total_gas,
            "contracts": {
                "KeccakCollisionVerifier": {
                    "address": verifier.address,
                    "gas_used": verifier_gas
                },
                "EvmoreToken": {
                    "address": evmore.address,
                    "gas_used": evmore_gas
                }
            },
            "deployer": deployer.address,
            "mining_config": {
                "initial_difficulty": difficulty,
                "initial_challenge": challenge.hex(),
                "initial_epoch": epoch,
                "initial_reward": str(evmore.INITIAL_REWARD()),
                "max_supply": str(evmore.MAX_SUPPLY())
            },
            "stage": "Stage 1 - Ethereum Only",
            "bridge_status": "Ready for Stage 2 activation",
            "next_steps": [
                "Start mining to accumulate treasury",
                "Build community and establish price",
                "Activate bridge when treasury reaches 1K EVMORE"
            ]
        }

        # Save deployment info
        filename = f"deployment_stage1_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(deployment_info, f, indent=2)

        # Print deployment summary
        print("\n" + "="*80)
        print("🏆 EVMORE STAGE 1 DEPLOYMENT COMPLETE")
        print("="*80)
        print(f"🌐 Network: Ethereum Mainnet")
        print(f"⏱️  Deployment Time: {deployment_time:.2f} seconds")
        print(f"⛽ Total Gas Used: {total_gas:,}")
        print(f"💰 Estimated Cost: ~${total_gas * 20 * 2000 / 10**9:.0f} (at 20 gwei)")
        print()
        print("📋 CONTRACT ADDRESSES:")
        print(f"   💎 EVMORE Token:  {evmore.address}")
        print(f"   🔍 Verifier:      {verifier.address}")
        print()
        print("⛏️  MINING PARAMETERS:")
        print(f"   🎯 Difficulty:     {difficulty} bits")
        print(f"   🏆 Block Reward:   {evmore.INITIAL_REWARD() / 10**18} EVMORE")
        print(f"   💎 Max Supply:     {evmore.MAX_SUPPLY() / 10**18:,} EVMORE")
        print(f"   🔢 Current Epoch:  {epoch}")
        print()
        print("🚀 NEXT STEPS:")
        print("   1. Start mining immediately (low competition advantage)")
        print("   2. Create Uniswap liquidity pool")
        print("   3. Build community and establish price discovery")
        print("   4. Accumulate 1K EVMORE treasury for Stage 2")
        print()
        print("📊 QUICK START MINING:")
        print(f"   export EVMORE_TOKEN={evmore.address}")
        print(f"   export VERIFIER={verifier.address}")
        print("   python mining/optimized_miner.py")
        print()
        print("🌐 STAGE 2 READINESS:")
        print("   - Bridge contracts: ✅ Pre-built")
        print("   - Migration hooks: ✅ Integrated")
        print("   - Polygon support: ✅ Ready")
        print("   - Activation threshold: 1K EVMORE treasury")
        print()
        print(f"📄 Deployment saved to: {filename}")
        print("="*80)

        return deployment_info

    except Exception as e:
        log_info(f"❌ Deployment failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    log_info("EVMORE Stage 1 Deployment - Digital Gold Launch")

    # Confirm deployment
    response = input("Deploy EVMORE Stage 1 to Ethereum mainnet? (y/N): ").lower().strip()
    if response != 'y':
        print("Deployment cancelled")
        sys.exit(0)

    try:
        # Connect to Ethereum mainnet
        with networks.parse_network_choice("ethereum:mainnet:infura"):
            deployment_info = deploy_stage1()

        print("\n🎉 Stage 1 deployment completed successfully!")
        print("🏁 EVMORE Digital Gold is now live on Ethereum!")
        print("⛏️  Start mining to begin the digital gold rush!")

    except KeyboardInterrupt:
        print("\n❌ Deployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        sys.exit(1)