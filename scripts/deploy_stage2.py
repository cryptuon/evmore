#!/usr/bin/env python3
"""
EVMORE Stage 2 Deployment Script
Deploy Polygon bridge when treasury reaches 1K EVMORE
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

def check_treasury_requirement(evmore_contract, deployer_address, threshold=1000):
    """Check if deployer has enough EVMORE for Stage 2"""
    balance = evmore_contract.balanceOf(deployer_address)
    balance_evmore = balance / 10**18

    log_info(f"💰 Current EVMORE balance: {balance_evmore:.2f}")
    log_info(f"🎯 Required for Stage 2: {threshold} EVMORE")

    if balance_evmore >= threshold:
        log_info(f"✅ Treasury requirement met!")
        return True
    else:
        log_info(f"❌ Need {threshold - balance_evmore:.2f} more EVMORE")
        return False

def deploy_stage2_ethereum(evmore_address, deployer):
    """Deploy Stage 2 bridge on Ethereum"""

    log_info("📦 Deploying Stage 2 Bridge on Ethereum...")

    # Deploy bridge contract
    bridge = deployer.deploy(project.EVMOREBridgeStage2, evmore_address)
    bridge_gas = bridge.creation_metadata.receipt.gas_used

    log_info(f"✅ Bridge deployed at: {bridge.address}")
    log_info(f"⛽ Gas used: {bridge_gas:,}")

    # Connect bridge to EVMORE token
    log_info("🔗 Connecting bridge to EVMORE token...")
    evmore = project.EvmoreToken.at(evmore_address)

    # Set bridge contract in EVMORE token
    tx = evmore.setBridgeContract(bridge.address, sender=deployer)
    log_info(f"✅ Bridge connected to EVMORE token")

    # Activate bridge
    tx = bridge.activateBridge(sender=deployer)
    log_info(f"✅ Bridge activated")

    return bridge, bridge_gas

def deploy_stage2_polygon(deployer):
    """Deploy wrapped EVMORE on Polygon"""

    log_info("📦 Deploying wEVMORE on Polygon...")

    # Deploy wrapped EVMORE
    wevmore = deployer.deploy(project.wEVMOREPolygon)
    wevmore_gas = wevmore.creation_metadata.receipt.gas_used

    log_info(f"✅ wEVMORE deployed at: {wevmore.address}")
    log_info(f"⛽ Gas used: {wevmore_gas:,}")

    # Activate bridge
    tx = wevmore.activateBridge(sender=deployer)
    log_info(f"✅ wEVMORE bridge activated")

    return wevmore, wevmore_gas

def deploy_stage2():
    """Deploy EVMORE Stage 2 bridge infrastructure"""

    log_info("🚀 Starting EVMORE Stage 2 Deployment")
    log_info("🌉 Deploying Polygon Bridge Infrastructure")

    deployment_start = time.time()

    # Load Stage 1 deployment info
    try:
        # Try to load most recent Stage 1 deployment
        import glob
        stage1_files = glob.glob("deployment_stage1_*.json")
        if not stage1_files:
            log_info("❌ No Stage 1 deployment found")
            sys.exit(1)

        latest_stage1 = max(stage1_files)
        with open(latest_stage1, 'r') as f:
            stage1_info = json.load(f)

        evmore_address = stage1_info["contracts"]["EvmoreToken"]["address"]
        log_info(f"📍 Found EVMORE token at: {evmore_address}")

    except Exception as e:
        log_info(f"❌ Failed to load Stage 1 deployment: {e}")
        sys.exit(1)

    # Deploy to Ethereum first
    try:
        log_info("🌐 Connecting to Ethereum mainnet...")

        with networks.parse_network_choice("ethereum:mainnet:infura"):
            deployer = accounts[0]
            log_info(f"👤 Deployer: {deployer.address}")

            # Check treasury requirement
            evmore = project.EvmoreToken.at(evmore_address)
            if not check_treasury_requirement(evmore, deployer.address):
                log_info("❌ Insufficient EVMORE treasury for Stage 2")
                sys.exit(1)

            # Deploy bridge on Ethereum
            bridge, bridge_gas = deploy_stage2_ethereum(evmore_address, deployer)

    except Exception as e:
        log_info(f"❌ Ethereum deployment failed: {e}")
        sys.exit(1)

    # Deploy to Polygon
    try:
        log_info("🌐 Connecting to Polygon...")

        with networks.parse_network_choice("polygon:mainnet:infura"):
            deployer = accounts[0]  # Same account on Polygon
            log_info(f"👤 Deployer: {deployer.address}")

            # Deploy wEVMORE on Polygon
            wevmore, wevmore_gas = deploy_stage2_polygon(deployer)

    except Exception as e:
        log_info(f"❌ Polygon deployment failed: {e}")
        sys.exit(1)

    deployment_time = time.time() - deployment_start
    total_gas = bridge_gas + wevmore_gas

    # Save deployment info
    deployment_info = {
        "stage": "Stage 2 - Polygon Bridge",
        "timestamp": datetime.now().isoformat(),
        "deployment_time": deployment_time,
        "total_gas_used": total_gas,
        "networks": {
            "ethereum": {
                "evmore_token": evmore_address,
                "bridge_contract": bridge.address,
                "gas_used": bridge_gas
            },
            "polygon": {
                "wevmore_token": wevmore.address,
                "gas_used": wevmore_gas
            }
        },
        "deployer": deployer.address,
        "bridge_config": {
            "min_bridge_amount": "1 EVMORE",
            "max_bridge_amount": "10,000 EVMORE",
            "daily_limit": "50,000 EVMORE",
            "withdrawal_delay": "1 hour",
            "bridge_fee": "0.2%"
        },
        "operational_model": "Manual processing with operator",
        "security_features": [
            "Conservative limits",
            "Manual verification",
            "Emergency pause",
            "Daily rate limiting",
            "Owner controls"
        ],
        "next_steps": [
            "Test bridge with small amounts",
            "Monitor for 1 week",
            "Gradually increase limits",
            "Plan Stage 3 multi-chain"
        ]
    }

    # Save deployment info
    filename = f"deployment_stage2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(deployment_info, f, indent=2)

    # Print deployment summary
    print("\n" + "="*80)
    print("🏆 EVMORE STAGE 2 DEPLOYMENT COMPLETE")
    print("="*80)
    print(f"🌉 Bridge Type: Ethereum ↔ Polygon")
    print(f"⏱️  Deployment Time: {deployment_time:.2f} seconds")
    print(f"⛽ Total Gas Used: {total_gas:,}")
    print()
    print("📋 CONTRACT ADDRESSES:")
    print("   🌐 Ethereum:")
    print(f"      💎 EVMORE Token:  {evmore_address}")
    print(f"      🌉 Bridge:        {bridge.address}")
    print("   🟣 Polygon:")
    print(f"      💎 wEVMORE Token: {wevmore.address}")
    print()
    print("🔧 BRIDGE CONFIGURATION:")
    print("   🎯 Min Amount:     1 EVMORE")
    print("   🎯 Max Amount:     10,000 EVMORE")
    print("   📊 Daily Limit:    50,000 EVMORE")
    print("   ⏰ Delay:          1 hour")
    print("   💸 Fee:            0.2%")
    print()
    print("🛠️  OPERATIONAL MODEL:")
    print("   📋 Manual Processing: Bridge operator reviews each transaction")
    print("   🔒 Security First:   Conservative limits for initial rollout")
    print("   ⚡ Speed:            1-6 hours processing time")
    print("   🏦 Revenue:          Bridge fees accumulate for treasury")
    print()
    print("🚀 BRIDGE OPERATIONS:")
    print("   1. Ethereum → Polygon:")
    print("      • User calls bridgeToPolygon(amount)")
    print("      • EVMORE burned on Ethereum")
    print("      • Operator mints wEVMORE on Polygon")
    print()
    print("   2. Polygon → Ethereum:")
    print("      • User burns wEVMORE on Polygon")
    print("      • Operator verifies and mints EVMORE on Ethereum")
    print()
    print("📈 NEXT MILESTONES:")
    print("   🎯 Stage 3 Threshold: 10K EVMORE treasury")
    print("   🌐 Additional Networks: Arbitrum, Base")
    print("   🤖 Automated Processing: Multi-sig validators")
    print("   🏛️ Governance: Community voting")
    print()
    print(f"📄 Deployment saved to: {filename}")
    print("="*80)

    return deployment_info

if __name__ == "__main__":
    log_info("EVMORE Stage 2 Deployment - Polygon Bridge")

    # Confirm deployment
    response = input("Deploy EVMORE Stage 2 Polygon bridge? (y/N): ").lower().strip()
    if response != 'y':
        print("Deployment cancelled")
        sys.exit(0)

    try:
        deployment_info = deploy_stage2()

        print("\n🎉 Stage 2 deployment completed successfully!")
        print("🌉 EVMORE bridge is now live on Polygon!")
        print("💎 Users can bridge EVMORE for cheaper transactions!")

    except KeyboardInterrupt:
        print("\n❌ Deployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        sys.exit(1)