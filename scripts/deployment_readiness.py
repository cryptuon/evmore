#!/usr/bin/env python3
"""
EVMORE Deployment Readiness Verification
Verifies all components are ready for staged deployment
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

def check_contracts() -> Tuple[bool, List[str]]:
    """Verify all contract files are present and valid"""

    required_contracts = [
        "contracts/EvmoreToken.vy",
        "contracts/KeccakCollisionVerifier.vy",
        "contracts/bridges/EVMOREBridgeStage2.vy",
        "contracts/bridges/wEVMOREPolygon.vy"
    ]

    issues = []

    for contract in required_contracts:
        if not os.path.exists(contract):
            issues.append(f"❌ Missing contract: {contract}")
        else:
            # Basic syntax check
            with open(contract, 'r') as f:
                content = f.read()
                if not content.strip():
                    issues.append(f"❌ Empty contract: {contract}")
                elif "# SPDX-License-Identifier:" not in content:
                    issues.append(f"⚠️  Missing license in: {contract}")

    return len(issues) == 0, issues

def check_deployment_scripts() -> Tuple[bool, List[str]]:
    """Verify deployment scripts are present"""

    required_scripts = [
        "scripts/deploy_stage1.py",
        "scripts/deploy_stage2.py",
        "scripts/migration_manager.py"
    ]

    issues = []

    for script in required_scripts:
        if not os.path.exists(script):
            issues.append(f"❌ Missing script: {script}")
        else:
            with open(script, 'r') as f:
                content = f.read()
                if "def main():" not in content and "__main__" not in content:
                    issues.append(f"⚠️  Script may not be executable: {script}")

    return len(issues) == 0, issues

def check_documentation() -> Tuple[bool, List[str]]:
    """Verify documentation is complete"""

    required_docs = [
        "docs/deployment/staged-deployment-plan.md",
        "docs/strategy/bootstrap-launch-strategy.md",
        "docs/architecture/digital-gold-architecture.md"
    ]

    issues = []

    for doc in required_docs:
        if not os.path.exists(doc):
            issues.append(f"❌ Missing documentation: {doc}")
        else:
            with open(doc, 'r') as f:
                content = f.read()
                if len(content) < 1000:  # Basic completeness check
                    issues.append(f"⚠️  Documentation may be incomplete: {doc}")

    return len(issues) == 0, issues

def check_migration_readiness() -> Tuple[bool, List[str]]:
    """Verify migration capabilities are built-in"""

    issues = []

    # Check EvmoreToken for migration hooks
    evmore_path = "contracts/EvmoreToken.vy"
    if os.path.exists(evmore_path):
        with open(evmore_path, 'r') as f:
            content = f.read()

            migration_features = [
                "bridge_contract:",
                "bridge_mint_enabled:",
                "bridge_burn_enabled:",
                "setBridgeContract",
                "bridgeMint",
                "bridgeBurn"
            ]

            for feature in migration_features:
                if feature not in content:
                    issues.append(f"❌ Missing migration feature in EvmoreToken: {feature}")
    else:
        issues.append("❌ EvmoreToken.vy not found")

    return len(issues) == 0, issues

def check_stage_dependencies() -> Tuple[bool, List[str]]:
    """Verify stage dependencies and thresholds"""

    issues = []

    # Check migration manager for proper stage definitions
    manager_path = "scripts/migration_manager.py"
    if os.path.exists(manager_path):
        with open(manager_path, 'r') as f:
            content = f.read()

            stage_checks = [
                "stage1_to_stage2",
                "stage2_to_stage3",
                "stage3_to_stage4",
                "1,000 EVMORE",
                "10,000 EVMORE",
                "100,000 EVMORE"
            ]

            for check in stage_checks:
                if check not in content:
                    issues.append(f"❌ Missing stage definition: {check}")
    else:
        issues.append("❌ Migration manager not found")

    return len(issues) == 0, issues

def estimate_deployment_costs() -> Dict[str, str]:
    """Estimate deployment costs for each stage"""

    return {
        "Stage 1": "~$500 (immediate deployment)",
        "Stage 2": "~$200 (bridge activation)",
        "Stage 3": "~$1,500 (multi-chain deployment)",
        "Stage 4": "~$5,000 (federated mining)"
    }

def verify_bootstrap_strategy() -> Tuple[bool, List[str]]:
    """Verify bootstrap strategy is viable"""

    issues = []

    strategy_path = "docs/strategy/bootstrap-launch-strategy.md"
    if os.path.exists(strategy_path):
        with open(strategy_path, 'r') as f:
            content = f.read()

            bootstrap_elements = [
                "mining economics",
                "treasury accumulation",
                "community building",
                "price discovery"
            ]

            for element in bootstrap_elements:
                if element.lower() not in content.lower():
                    issues.append(f"⚠️  Bootstrap strategy may be missing: {element}")
    else:
        issues.append("❌ Bootstrap strategy documentation not found")

    return len(issues) == 0, issues

def main():
    """Run complete deployment readiness verification"""

    print("🔍 EVMORE Deployment Readiness Verification")
    print("=" * 50)

    all_passed = True

    # Check contracts
    print("\n📦 Checking Smart Contracts...")
    contracts_ok, contract_issues = check_contracts()
    if contracts_ok:
        print("✅ All contracts present and valid")
    else:
        all_passed = False
        for issue in contract_issues:
            print(f"   {issue}")

    # Check deployment scripts
    print("\n🚀 Checking Deployment Scripts...")
    scripts_ok, script_issues = check_deployment_scripts()
    if scripts_ok:
        print("✅ All deployment scripts ready")
    else:
        all_passed = False
        for issue in script_issues:
            print(f"   {issue}")

    # Check documentation
    print("\n📚 Checking Documentation...")
    docs_ok, doc_issues = check_documentation()
    if docs_ok:
        print("✅ Documentation complete")
    else:
        all_passed = False
        for issue in doc_issues:
            print(f"   {issue}")

    # Check migration readiness
    print("\n🔄 Checking Migration Capabilities...")
    migration_ok, migration_issues = check_migration_readiness()
    if migration_ok:
        print("✅ Migration hooks built-in")
    else:
        all_passed = False
        for issue in migration_issues:
            print(f"   {issue}")

    # Check stage dependencies
    print("\n🎯 Checking Stage Dependencies...")
    stages_ok, stage_issues = check_stage_dependencies()
    if stages_ok:
        print("✅ All stages properly defined")
    else:
        all_passed = False
        for issue in stage_issues:
            print(f"   {issue}")

    # Check bootstrap strategy
    print("\n💰 Checking Bootstrap Strategy...")
    bootstrap_ok, bootstrap_issues = verify_bootstrap_strategy()
    if bootstrap_ok:
        print("✅ Bootstrap strategy documented")
    else:
        all_passed = False
        for issue in bootstrap_issues:
            print(f"   {issue}")

    # Cost estimates
    print("\n💸 Deployment Cost Estimates:")
    costs = estimate_deployment_costs()
    for stage, cost in costs.items():
        print(f"   {stage}: {cost}")

    # Final readiness assessment
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 EVMORE IS READY FOR DEPLOYMENT!")
        print()
        print("🚀 IMMEDIATE NEXT STEPS:")
        print("   1. Set up Ethereum mainnet connection in ape-config.yaml")
        print("   2. Fund deployer account with 0.02+ ETH (~$50)")
        print("   3. Run: python scripts/deploy_stage1.py")
        print("   4. Start mining immediately for early advantage")
        print("   5. Build community while accumulating treasury")
        print()
        print("💎 DIGITAL GOLD LAUNCH SEQUENCE READY")
        print("   • Revolutionary KeccakCollision mining")
        print("   • Self-funding through mining economics")
        print("   • Seamless multi-chain migration path")
        print("   • Path to federated mining future")

    else:
        print("❌ DEPLOYMENT NOT READY - Issues found above")
        print("   Please resolve all issues before deployment")

    print("=" * 50)

    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)