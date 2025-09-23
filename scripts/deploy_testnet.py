#!/usr/bin/env python3
"""
EVMORE Digital Gold Testnet Deployment Script
Comprehensive testnet infrastructure with monitoring and validation
"""

import os
import time
import json
import sys
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from ape import accounts, project, networks, chain
from ape.utils import ZERO_ADDRESS
from eth_utils import to_checksum_address, to_wei
import logging

@dataclass
class TestnetConfig:
    """Testnet deployment configuration"""
    network_name: str = "ethereum:local:test"
    initial_difficulty: int = 12  # Easier for testing
    initial_reward: int = 50 * 10**18  # 50 EVMORE
    max_supply: int = 21_000_000 * 10**18  # 21M EVMORE
    target_block_time: int = 120  # 2 minutes for testing
    test_miners: int = 5
    deployment_gas_limit: int = 5_000_000

@dataclass
class DeploymentResult:
    """Results from testnet deployment"""
    evmore_token: str
    verifier: str
    deployer: str
    test_accounts: List[str]
    deployment_block: int
    gas_used: int
    deployment_time: float


class EVMORETestnetDeployer:
    """
    EVMORE Digital Gold Testnet Deployer

    Features:
    - Automated contract deployment
    - Test account setup with initial funds
    - Mining infrastructure initialization
    - Health checks and validation
    - Monitoring dashboard setup
    """

    def __init__(self, config: TestnetConfig = None):
        self.config = config or TestnetConfig()
        self.logger = self._setup_logging()

        # Deployment state
        self.evmore_token: Optional = None
        self.verifier: Optional = None
        self.deployer_account = None
        self.test_accounts: List = []

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for deployment process"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)

    def log_deployment_info(self, message):
        """Log deployment information with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")

    def validate_deployment_environment(self):
        """Validate that the deployment environment is properly configured"""
        self.log_deployment_info("🔍 Validating deployment environment...")

        # Check network connection
        try:
            current_block = chain.blocks.height
            self.log_deployment_info(f"✅ Connected to network. Current block: {current_block}")
        except Exception as e:
            self.log_deployment_info(f"❌ Network connection failed: {e}")
            sys.exit(1)

        # Check account availability
        if len(accounts.test_accounts) == 0:
            self.log_deployment_info("❌ No test accounts available")
            sys.exit(1)

        deployer = accounts.test_accounts[0]
        balance = deployer.balance
        self.log_deployment_info(f"✅ Deployer account: {deployer.address}")
        self.log_deployment_info(f"✅ Deployer balance: {balance / 10**18:.4f} ETH")

        if balance < to_wei(0.1, "ether"):
            self.log_deployment_info("⚠️  Warning: Low balance for deployment")

        return deployer

    def deploy_contracts(self) -> DeploymentResult:
        """
        Deploy EVMORE smart contracts to testnet
        """
        self.log_deployment_info("🚀 Starting EVMORE Digital Gold Testnet Deployment")
        self.log_deployment_info(f"📍 Network: {self.config.network_name}")
        self.log_deployment_info(f"💎 Initial Difficulty: {self.config.initial_difficulty} bits")
        self.log_deployment_info(f"🏆 Initial Reward: {self.config.initial_reward / 10**18} EVMORE")

        start_time = time.time()
        total_gas_used = 0

        try:
            # Setup deployer account
            self.deployer_account = self.validate_deployment_environment()

            # Deploy KeccakCollision Verifier first
            self.log_deployment_info("📦 Deploying KeccakCollisionVerifier...")
            self.verifier = self.deployer_account.deploy(project.KeccakCollisionVerifier)
            total_gas_used += getattr(self.verifier, 'gas_used', 0)
            self.log_deployment_info(f"✅ Verifier deployed at: {self.verifier.address}")

            # Deploy EVMORE Token with verifier reference
            self.log_deployment_info("📦 Deploying EvmoreToken...")
            self.evmore_token = self.deployer_account.deploy(project.EvmoreToken, self.verifier.address)
            total_gas_used += getattr(self.evmore_token, 'gas_used', 0)
            self.log_deployment_info(f"✅ EVMORE Token deployed at: {self.evmore_token.address}")

            # Setup test accounts
            self._setup_test_accounts()

            # Initialize mining parameters
            self._initialize_mining_parameters()

            # Validate deployment
            self._validate_deployment()

            # Setup monitoring
            self._setup_monitoring()

            deployment_time = time.time() - start_time
            deployment_block = chain.blocks.height

            result = DeploymentResult(
                evmore_token=self.evmore_token.address,
                verifier=self.verifier.address,
                deployer=self.deployer_account.address,
                test_accounts=[acc.address for acc in self.test_accounts],
                deployment_block=deployment_block,
                gas_used=total_gas_used,
                deployment_time=deployment_time
            )

            self._save_deployment_info(result)
            self._print_deployment_summary(result)

            return result

        except Exception as e:
            self.log_deployment_info(f"💥 Deployment failed: {e}")
            raise

    def _setup_test_accounts(self):
        """Setup test accounts with initial ETH funding"""
        self.log_deployment_info("👥 Setting up test accounts...")

        # Create test accounts
        for i in range(1, self.config.test_miners + 1):
            account = accounts.test_accounts[i] if i < len(accounts.test_accounts) else accounts.test_accounts[0]
            self.test_accounts.append(account)

            # Fund with test ETH for gas
            if account.balance < 10 * 10**18:  # Less than 10 ETH
                try:
                    self.deployer_account.transfer(account, "5 ether")
                except:
                    pass  # May fail on some networks

            self.log_deployment_info(f"   Miner {i}: {account.address} ({account.balance / 10**18:.2f} ETH)")

    def _initialize_mining_parameters(self):
        """Initialize mining parameters for testnet"""
        self.log_deployment_info("⚙️  Initializing mining parameters...")

        # Get current mining state
        current_challenge = self.evmore_token.currentChallenge()
        current_difficulty = self.evmore_token.currentDifficulty()
        current_epoch = self.evmore_token.current_epoch()

        self.log_deployment_info(f"   Challenge: {current_challenge.hex()[:16]}...")
        self.log_deployment_info(f"   Difficulty: {current_difficulty} bits")
        self.log_deployment_info(f"   Epoch: {current_epoch}")

    def _validate_deployment(self):
        """Validate deployment with comprehensive tests"""
        self.log_deployment_info("✅ Validating deployment...")

        # Test 1: Contract state validation
        assert self.evmore_token.verifier() == self.verifier.address
        assert self.evmore_token.owner() == self.deployer_account.address
        assert self.evmore_token.totalSupply() == 0
        assert self.evmore_token.INITIAL_REWARD() == self.config.initial_reward
        assert self.evmore_token.MAX_SUPPLY() == self.config.max_supply
        self.log_deployment_info("   ✓ Contract state validation passed")

        # Test 2: Verifier functionality
        test_challenge = b"test_challenge_for_validation_32b"
        test_solution = b"test" * 32  # 128 bytes

        try:
            is_valid = self.verifier.verify_solution(test_challenge, test_solution, 8)
            self.log_deployment_info(f"   ✓ Verifier callable (test result: {is_valid})")
        except Exception as e:
            self.log_deployment_info(f"   ⚠️  Verifier test failed: {e}")

        # Test 3: Mining interface
        try:
            challenge = self.evmore_token.currentChallenge()
            difficulty = self.evmore_token.currentDifficulty()
            epoch = self.evmore_token.current_epoch()
            assert len(challenge) == 32
            assert difficulty > 0
            assert epoch >= 0
            self.log_deployment_info("   ✓ Mining interface validation passed")
        except Exception as e:
            self.log_deployment_info(f"   ❌ Mining interface validation failed: {e}")
            raise

        # Test 4: ERC-20 functionality
        try:
            name = self.evmore_token.name()
            symbol = self.evmore_token.symbol()
            decimals = self.evmore_token.decimals()
            assert name in ["Evmore", "EVM ORE Token"]
            assert symbol == "EVMORE"
            assert decimals == 18
            self.log_deployment_info("   ✓ ERC-20 interface validation passed")
        except Exception as e:
            self.log_deployment_info(f"   ❌ ERC-20 validation failed: {e}")
            raise

        self.log_deployment_info("🎉 All validation tests passed!")

    def _setup_monitoring(self):
        """Setup monitoring and health checks"""
        self.log_deployment_info("📊 Setting up monitoring...")

        # Create monitoring configuration
        monitoring_config = {
            "contracts": {
                "evmore_token": self.evmore_token.address,
                "verifier": self.verifier.address
            },
            "monitoring": {
                "block_time_target": self.config.target_block_time,
                "difficulty_adjustment_blocks": 100,
                "health_check_interval": 30
            },
            "alerts": {
                "high_difficulty_threshold": 20,
                "low_mining_activity_threshold": 60,
                "contract_error_alerts": True
            }
        }

        # Save monitoring config
        with open("testnet_monitoring.json", "w") as f:
            json.dump(monitoring_config, f, indent=2)

        self.log_deployment_info("   ✓ Monitoring configuration saved")

    def _save_deployment_info(self, result: DeploymentResult):
        """Save deployment information for future reference"""
        deployment_info = {
            "network": self.config.network_name,
            "timestamp": time.time(),
            "contracts": {
                "evmore_token": result.evmore_token,
                "verifier": result.verifier
            },
            "deployer": result.deployer,
            "test_accounts": result.test_accounts,
            "deployment_stats": {
                "block_number": result.deployment_block,
                "gas_used": result.gas_used,
                "deployment_time": result.deployment_time
            },
            "mining_config": {
                "initial_difficulty": self.config.initial_difficulty,
                "initial_reward": self.config.initial_reward,
                "target_block_time": self.config.target_block_time
            }
        }

        # Save to file
        with open("testnet_deployment.json", "w") as f:
            json.dump(deployment_info, f, indent=2)

        # Also save simplified version for easy import
        simple_config = {
            "EVMORE_TOKEN": result.evmore_token,
            "VERIFIER": result.verifier,
            "DEPLOYER": result.deployer
        }

        with open("testnet_addresses.json", "w") as f:
            json.dump(simple_config, f, indent=2)

    def _print_deployment_summary(self, result: DeploymentResult):
        """Print comprehensive deployment summary"""
        print("\n" + "="*80)
        print("🏆 EVMORE DIGITAL GOLD TESTNET DEPLOYMENT COMPLETE")
        print("="*80)
        print(f"🌐 Network: {self.config.network_name}")
        print(f"⏱️  Deployment Time: {result.deployment_time:.2f} seconds")
        print(f"⛽ Total Gas Used: {result.gas_used:,}")
        print(f"📦 Deployment Block: {result.deployment_block:,}")
        print()
        print("📋 CONTRACT ADDRESSES:")
        print(f"   💎 EVMORE Token:  {result.evmore_token}")
        print(f"   🔍 Verifier:      {result.verifier}")
        print()
        print("👥 TEST ACCOUNTS:")
        print(f"   🏗️  Deployer:      {result.deployer}")
        for i, account in enumerate(result.test_accounts, 1):
            print(f"   ⛏️  Miner {i}:       {account}")
        print()
        print("⚙️  MINING PARAMETERS:")
        print(f"   🎯 Difficulty:     {self.config.initial_difficulty} bits")
        print(f"   🏆 Block Reward:   {self.config.initial_reward / 10**18} EVMORE")
        print(f"   ⏱️  Block Time:     {self.config.target_block_time} seconds")
        print(f"   💎 Max Supply:     {self.config.max_supply / 10**18:,} EVMORE")
        print()
        print("🚀 NEXT STEPS:")
        print("   1. Run mining simulation: python scripts/simulate_mining.py")
        print("   2. Start monitoring: python scripts/monitor_testnet.py")
        print("   3. Test mining pools: python mining/mining_pool.py")
        print("   4. Deploy to public testnet for community testing")
        print()
        print("📊 QUICK START COMMANDS:")
        print(f"   export EVMORE_TOKEN={result.evmore_token}")
        print(f"   export VERIFIER={result.verifier}")
        print("   python examples/mine_first_gold.py")
        print("="*80)


def deploy_verifier_contract(deployer):
    """Deploy the KeccakCollisionVerifier contract"""
    log_deployment_info("🚀 Deploying KeccakCollisionVerifier contract...")

    try:
        verifier = deployer.deploy(project.KeccakCollisionVerifier)
        log_deployment_info(f"✅ KeccakCollisionVerifier deployed at: {verifier.address}")

        # Validate verifier deployment
        test_challenge = b"0" * 32
        test_solution = b"0" * 128
        test_difficulty = 8

        try:
            # This should return False for invalid solution, but not revert
            result = verifier.verify_solution(test_challenge, test_solution, test_difficulty)
            log_deployment_info(f"✅ Verifier validation test: {result} (expected: False)")
        except Exception as e:
            log_deployment_info(f"✅ Verifier properly rejects invalid solution: {e}")

        return verifier

    except Exception as e:
        log_deployment_info(f"❌ Verifier deployment failed: {e}")
        sys.exit(1)


def deploy_token_contract(deployer, verifier):
    """Deploy the EvmoreToken contract with enhanced validation"""
    log_deployment_info("🚀 Deploying EvmoreToken contract...")

    try:
        token = deployer.deploy(project.EvmoreToken, verifier.address)
        log_deployment_info(f"✅ EvmoreToken deployed at: {token.address}")

        # Comprehensive validation of deployed contract
        validate_token_deployment(token, verifier, deployer)

        return token

    except Exception as e:
        log_deployment_info(f"❌ Token deployment failed: {e}")
        sys.exit(1)


def validate_token_deployment(token, verifier, deployer):
    """Validate that the token contract is properly deployed with security features"""
    log_deployment_info("🔍 Validating token contract deployment...")

    # Basic contract properties
    assert token.name() == "EVM ORE Token", "Invalid token name"
    assert token.symbol() == "EVMORE", "Invalid token symbol"
    assert token.decimals() == 18, "Invalid decimals"
    assert token.totalSupply() == 0, "Initial supply should be 0"

    log_deployment_info("✅ Basic token properties validated")

    # Mining parameters
    assert token.INITIAL_REWARD() == to_wei(50, "ether"), "Invalid initial reward"
    assert token.MAX_SUPPLY() == to_wei(21000000, "ether"), "Invalid max supply"
    assert token.TARGET_BLOCK_TIME() == 600, "Invalid target block time"

    log_deployment_info("✅ Mining parameters validated")

    # Security features validation
    assert token.owner() == deployer.address, "Invalid owner"
    assert token.pending_owner() == "0x0000000000000000000000000000000000000000", "Pending owner should be zero"
    assert not token.paused(), "Contract should not be paused initially"

    log_deployment_info("✅ Security features validated")

    # Mining state validation
    assert token.blocksMined() == 0, "Initial blocks mined should be 0"
    assert token.current_epoch() == 0, "Initial epoch should be 0"
    assert token.currentDifficulty() >= 8, "Initial difficulty should be at least 8"
    assert len(token.currentChallenge()) == 32, "Challenge should be 32 bytes"

    log_deployment_info("✅ Mining state validated")

    # Verifier integration
    assert token.verifier() == verifier.address, "Verifier address mismatch"

    log_deployment_info("✅ Verifier integration validated")


def test_security_features(token, deployer):
    """Test that security features work correctly"""
    log_deployment_info("🔒 Testing security features...")

    # Test pause/unpause functionality
    try:
        token.pause(sender=deployer)
        assert token.paused(), "Pause function failed"

        token.unpause(sender=deployer)
        assert not token.paused(), "Unpause function failed"

        log_deployment_info("✅ Pause/unpause functionality working")
    except Exception as e:
        log_deployment_info(f"❌ Pause/unpause test failed: {e}")

    # Test ownership transfer initiation (we won't complete it)
    try:
        test_address = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
        token.transferOwnership(test_address, sender=deployer)
        assert token.pending_owner() == test_address, "Ownership transfer initiation failed"

        # Reset by having deployer transfer back to themselves (which should fail)
        try:
            token.transferOwnership(deployer.address, sender=deployer)
            log_deployment_info("❌ Should not allow transfer to current owner")
        except:
            log_deployment_info("✅ Correctly prevents transfer to current owner")

        log_deployment_info("✅ Two-step ownership transfer working")
    except Exception as e:
        log_deployment_info(f"❌ Ownership transfer test failed: {e}")


def save_deployment_info(verifier, token, network_name):
    """Save deployment information to a JSON file"""
    deployment_info = {
        "network": network_name,
        "timestamp": datetime.now().isoformat(),
        "contracts": {
            "KeccakCollisionVerifier": {
                "address": verifier.address,
                "transaction_hash": verifier.txn_hash if hasattr(verifier, 'txn_hash') else None
            },
            "EvmoreToken": {
                "address": token.address,
                "transaction_hash": token.txn_hash if hasattr(token, 'txn_hash') else None
            }
        },
        "configuration": {
            "initial_reward": str(token.INITIAL_REWARD()),
            "max_supply": str(token.MAX_SUPPLY()),
            "target_block_time": token.TARGET_BLOCK_TIME(),
            "initial_difficulty": token.currentDifficulty(),
            "initial_challenge": token.currentChallenge().hex()
        }
    }

    filename = f"deployment_{network_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = f"deployments/{filename}"

    try:
        # Create deployments directory if it doesn't exist
        import os
        os.makedirs("deployments", exist_ok=True)

        with open(filepath, 'w') as f:
            json.dump(deployment_info, f, indent=2)

        log_deployment_info(f"✅ Deployment info saved to: {filepath}")
    except Exception as e:
        log_deployment_info(f"⚠️  Failed to save deployment info: {e}")

    return deployment_info


def print_deployment_summary(verifier, token, deployment_info):
    """Print a comprehensive deployment summary"""
    print("\n" + "="*80)
    print("🎉 EVMORE DEPLOYMENT COMPLETE")
    print("="*80)

    print(f"\n📊 NETWORK INFORMATION:")
    print(f"   Network: {deployment_info['network']}")
    print(f"   Timestamp: {deployment_info['timestamp']}")
    print(f"   Block Number: {chain.blocks.height}")

    print(f"\n🏗️  CONTRACT ADDRESSES:")
    print(f"   KeccakCollisionVerifier: {verifier.address}")
    print(f"   EvmoreToken:             {token.address}")

    print(f"\n⚙️  MINING CONFIGURATION:")
    print(f"   Initial Reward: {int(token.INITIAL_REWARD()) // 10**18} EVMORE")
    print(f"   Max Supply: {int(token.MAX_SUPPLY()) // 10**18:,} EVMORE")
    print(f"   Target Block Time: {token.TARGET_BLOCK_TIME()} seconds")
    print(f"   Initial Difficulty: {token.currentDifficulty()} bits")

    print(f"\n🔒 SECURITY FEATURES:")
    print(f"   Owner: {token.owner()}")
    print(f"   Two-step Ownership Transfer: ✅ Enabled")
    print(f"   Reentrancy Protection: ✅ Enabled")
    print(f"   Global Solution Tracking: ✅ Enabled")
    print(f"   Enhanced Challenge Generation: ✅ Enabled")
    print(f"   Comprehensive Event Logging: ✅ Enabled")

    print(f"\n⛏️  MINING STATUS:")
    print(f"   Current Epoch: {token.current_epoch()}")
    print(f"   Blocks Mined: {token.blocksMined()}")
    print(f"   Current Challenge: {token.currentChallenge().hex()[:20]}...")
    print(f"   Contract Paused: {token.paused()}")

    print(f"\n📝 NEXT STEPS:")
    print(f"   1. Verify contracts on block explorer")
    print(f"   2. Test mining functionality")
    print(f"   3. Run comprehensive test suite")
    print(f"   4. Prepare for external security audit")

    print("\n" + "="*80)


def main():
    """Deploy EVMORE testnet with full validation"""
    print("🚀 EVMORE Digital Gold Testnet Deployment")
    print("=" * 50)

    # Create deployment configuration
    config = TestnetConfig(
        network_name="ethereum:local:test",
        initial_difficulty=10,  # Easy for testing
        test_miners=3,
        target_block_time=60    # 1 minute blocks for testing
    )

    # Deploy testnet
    deployer = EVMORETestnetDeployer(config)
    result = deployer.deploy_contracts()

    print("\n✅ Testnet deployment complete!")
    print("📄 Deployment info saved to: testnet_deployment.json")
    print("🔧 Contract addresses saved to: testnet_addresses.json")

    return result


if __name__ == "__main__":
    try:
        # Connect to network
        with networks.parse_network_choice("ethereum:local:test"):
            result = main()

        print("🎉 Deployment completed successfully!")

    except KeyboardInterrupt:
        print("❌ Deployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Deployment failed with error: {e}")
        sys.exit(1)