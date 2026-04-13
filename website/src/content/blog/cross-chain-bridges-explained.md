---
title: "Cross-Chain Bridges: How Crypto Moves Between Blockchains"
description: "Cross-chain bridges transfer crypto between blockchains using lock-and-mint or burn-and-mint models, but carry security risks as shown by Ronin and Wormhole hacks."
date: 2026-04-05
author: "EVMORE Team"
tags: [bridges, cross-chain, security, multi-chain, interoperability]
seoKeywords: ["cross-chain bridge explained", "crypto bridge", "how bridges work"]
comparison: false
draft: false
---

The cryptocurrency ecosystem is not a single network. It is a collection of independent blockchains -- Ethereum, Bitcoin, Solana, Polygon, Arbitrum, Base, and dozens more -- each with its own consensus mechanism, programming language, and user base. For the first decade of blockchain development, these networks existed largely in isolation. Moving value between them required centralized exchanges: deposit Bitcoin, withdraw Ethereum, and trust the exchange to handle the swap.

Cross-chain bridges emerged to solve this fragmentation problem. They allow tokens and data to move between blockchains without relying on a centralized intermediary. In theory, bridges unlock the full potential of a multi-chain ecosystem, letting users access DeFi protocols, liquidity, and applications across any chain. In practice, bridges have also become one of the largest sources of security risk in the entire cryptocurrency industry, with over $2.5 billion stolen in bridge exploits between 2021 and 2024.

This article explains how cross-chain bridges work, what security risks they carry, the major bridge designs currently in use, and how newer projects like EVMORE are approaching the bridge challenge with caution.

## What Is a Cross-Chain Bridge?

A cross-chain bridge is a protocol that enables the transfer of tokens or data from one blockchain to another. Because blockchains cannot natively read each other's state (Ethereum does not know what happened on Polygon, and vice versa), bridges serve as the communication layer between isolated networks.

At a fundamental level, a bridge must solve a single problem: how do you represent an asset that exists on Chain A within the environment of Chain B? The token cannot simply "move" -- it exists as a record in Chain A's state. Instead, bridges create a representation of the token on Chain B that is backed by the original token locked or burned on Chain A.

## How Bridges Work: Core Mechanisms

Most cross-chain bridges use one of two fundamental mechanisms to transfer value between chains.

### Lock-and-Mint

The lock-and-mint model is the most common bridge design. It works in three steps:

1. **Lock:** The user sends their tokens to a smart contract on the source chain. These tokens are locked (held in the contract) and cannot be spent.
2. **Verify:** A set of validators, relayers, or an oracle observes that the tokens have been locked and communicates this information to the destination chain.
3. **Mint:** A smart contract on the destination chain mints an equivalent number of "wrapped" tokens, which represent a claim on the locked tokens.

To move tokens back, the process reverses: wrapped tokens are burned on the destination chain, and the original tokens are unlocked on the source chain.

**Example:** Wrapped Bitcoin (WBTC) is the most well-known lock-and-mint bridge token. Bitcoin is locked with a custodian (originally BitGo), and WBTC is minted on Ethereum. Each WBTC is backed 1:1 by Bitcoin held in custody.

**Advantages:**
- Conceptually simple
- Original tokens remain on the source chain
- Well-established pattern with many implementations

**Risks:**
- The locked tokens represent a concentrated honey pot for attackers
- The verification layer (validators/relayers) is a critical trust assumption
- If the bridge is compromised, all locked tokens are at risk

### Burn-and-Mint

The burn-and-mint model destroys tokens on the source chain and creates new tokens on the destination chain. This approach works best when the same entity controls token contracts on both chains.

1. **Burn:** The user sends tokens to a burn function on the source chain, permanently removing them from circulation.
2. **Verify:** Validators or relayers confirm the burn event.
3. **Mint:** New tokens are minted on the destination chain.

**Advantages:**
- No locked token pool (reduces honey pot risk)
- Cleaner accounting (total supply across all chains stays constant)
- More flexible for multi-chain deployments

**Risks:**
- Requires trusted minting authority on the destination chain
- Verification layer remains a critical trust point
- If minting is compromised, tokens can be created without corresponding burns

### Liquidity Network Model

A third approach uses liquidity pools on both chains. Instead of locking and minting, the bridge facilitates swaps between existing token pools on each chain.

1. **Deposit:** The user deposits tokens into a liquidity pool on the source chain.
2. **Withdraw:** The user receives tokens from a pre-funded liquidity pool on the destination chain.
3. **Rebalancing:** The protocol periodically rebalances liquidity between chains.

**Examples:** Hop Protocol, Across Protocol, and Stargate use variations of this model.

**Advantages:**
- No minting required (uses native tokens)
- Can be faster than lock-and-mint
- Reduced smart contract complexity on each chain

**Risks:**
- Requires significant capital locked in liquidity pools
- Liquidity imbalances can cause delays or slippage
- Pool management introduces additional complexity

## The Verification Problem

Regardless of the mechanism used, every bridge must solve the verification problem: how does the destination chain know that something really happened on the source chain?

This is the hardest part of bridge design and the source of most bridge vulnerabilities. Several verification approaches exist.

### Trusted Validators (Multisig)

The simplest approach: a set of known validators sign off on bridge transactions. If a majority (or threshold) of validators confirm that tokens were locked on Chain A, the bridge mints tokens on Chain B.

This is effectively a multisignature wallet controlling the bridge. It is fast and cheap but introduces significant trust assumptions. If the validators collude or their keys are compromised, the bridge can be drained.

### Optimistic Verification

Optimistic bridges assume transactions are valid unless challenged. A relayer submits a bridge transaction, and there is a challenge period (typically hours to days) during which anyone can submit a fraud proof if the transaction is invalid.

This approach reduces the trust assumption (only one honest verifier is needed to catch fraud) but introduces latency. Users must wait for the challenge period to expire before their tokens are available on the destination chain.

### Zero-Knowledge Proofs

The most advanced approach uses zero-knowledge proofs to cryptographically prove that a transaction occurred on the source chain. The destination chain can verify the proof without trusting any validator set.

This approach offers the strongest security guarantees but is computationally expensive and complex to implement. Several teams are building ZK-based bridges, and this technology is expected to mature significantly over the next few years.

### Light Client Verification

Some bridges run a light client of the source chain on the destination chain. The light client can verify block headers and transaction inclusion proofs, providing a trustless (or minimally-trusted) verification mechanism.

This approach is limited by the computational cost of running a light client on-chain and the availability of suitable consensus mechanisms for light client verification.

## Bridge Security: Lessons from Major Hacks

The history of cross-chain bridges includes some of the largest security breaches in cryptocurrency history. Understanding these incidents is essential for anyone using or building bridges.

### Ronin Bridge -- $625 Million (March 2022)

The Ronin Bridge connected the Ronin sidechain (used by the game Axie Infinity) to Ethereum. It used a multisig validator scheme with 9 validators, requiring 5 signatures to approve a bridge transaction.

The attacker, later attributed to North Korea's Lazarus Group, compromised 5 of the 9 validator keys. With a majority of keys, they approved fraudulent withdrawals, draining 173,600 ETH and 25.5 million USDC from the bridge.

**Key lesson:** Multisig bridges are only as secure as their key management. A small validator set creates a concentrated attack surface.

### Wormhole -- $320 Million (February 2022)

Wormhole is a generalized messaging bridge connecting multiple chains. The attacker exploited a vulnerability in the Solana-side verification logic, which allowed them to mint 120,000 wrapped ETH (wETH) on Solana without actually depositing ETH on Ethereum.

The vulnerability was in a signature verification function that failed to properly validate the signer's authority. The attacker was able to forge a valid-looking message that the bridge accepted.

**Key lesson:** Smart contract bugs in bridge verification logic can have catastrophic consequences. The complexity of cross-chain verification increases the attack surface.

### Nomad Bridge -- $190 Million (August 2022)

The Nomad Bridge used an optimistic verification model. A routine upgrade introduced a bug that effectively set the trusted root to zero, meaning any message could pass verification. Once one attacker discovered this, others joined in, draining the bridge in a chaotic free-for-all.

**Key lesson:** Even well-designed bridge architectures can be compromised by implementation bugs. Upgrade mechanisms themselves introduce risk.

### Harmony Horizon Bridge -- $100 Million (June 2022)

The Horizon Bridge used a 2-of-5 multisig to secure cross-chain transfers. The attacker compromised 2 private keys, which was sufficient to authorize fraudulent withdrawals.

**Key lesson:** A 2-of-5 threshold is dangerously low for securing hundreds of millions in value. Bridge security must be proportional to the value at risk.

### Common Patterns in Bridge Exploits

Across these and other incidents, several patterns emerge:

1. **Small or compromised validator sets** -- multisig bridges with few signers are vulnerable to key compromise.
2. **Smart contract vulnerabilities** -- complex verification logic is prone to bugs that can bypass security checks.
3. **Upgrade-related bugs** -- upgrades can introduce vulnerabilities, especially when they change core verification logic.
4. **Insufficient monitoring** -- several exploits went undetected for hours or days.
5. **Excessive locked value** -- large pools of locked tokens create irresistible targets.

## Modern Bridge Designs

The bridge exploits of 2022-2023 catalyzed significant innovation in bridge design. Modern bridges incorporate lessons from these incidents.

### Canonical Rollup Bridges

Layer 2 rollups (Arbitrum, Optimism, Base, zkSync) include native bridges as part of their architecture. These bridges benefit from the rollup's own security model:

- **Optimistic rollup bridges** use fraud proofs and a challenge period (typically 7 days) for withdrawals. Security relies on at least one honest verifier monitoring the bridge.
- **ZK rollup bridges** use validity proofs that cryptographically guarantee correctness. Withdrawals are finalized once the proof is verified on Layer 1.

These canonical bridges are generally considered the most secure because they inherit the security of Ethereum itself.

### Intent-Based Bridges

A newer model where users express an "intent" (e.g., "I want to move 100 USDC from Ethereum to Arbitrum"), and solvers compete to fulfill the intent. The solver fronts the tokens on the destination chain and is later reimbursed from the source chain.

**Examples:** Across Protocol, UniswapX cross-chain

This model reduces latency (users receive tokens immediately) and distributes risk across multiple solvers rather than concentrating it in a single bridge contract.

### Proof-of-Reserve Bridges

Some bridges implement regular proof-of-reserve audits, where the locked collateral backing wrapped tokens is cryptographically verified. This provides ongoing assurance that the bridge is fully collateralized.

### Staged and Progressive Bridges

Rather than deploying a fully automated bridge from day one, some projects take a staged approach, starting with more conservative mechanisms and gradually increasing automation as the system proves itself.

## EVMORE's Approach to Cross-Chain Bridging

EVMORE takes a deliberately cautious, staged approach to cross-chain expansion. Rather than launching with a bridge immediately, the project implements bridges as part of a multi-stage deployment architecture, with each stage activated only when the project reaches specific treasury milestones.

### Stage 1: Ethereum Only

In the initial stage, EVMORE operates exclusively on Ethereum. There is no bridge, no cross-chain complexity, and no additional attack surface. All mining, verification, and token transfers happen on a single chain.

This single-chain phase allows the project to establish a security track record and build community confidence before introducing cross-chain complexity.

### Stage 2: Manual Processing Bridge (Polygon)

The second stage introduces a bridge to Polygon, but with a critical design choice: manual processing. Rather than fully automated validator-based transfers, the bridge uses a controlled process that limits the speed and scale of cross-chain transfers.

The EVMOREBridgeStage2 smart contract implements the source-chain side of the bridge, while the wEVMOREPolygon contract handles the wrapped token on Polygon. This dual-contract architecture ensures that bridge logic is transparent and auditable on both chains.

Manual processing adds latency but dramatically reduces the attack surface. A compromised validator cannot drain the bridge instantly because transfers require human review and approval. This design explicitly trades convenience for security.

### Stage 3: Multi-Chain Expansion

The third stage extends bridge support to additional chains (Arbitrum, Base), adding more pathways for cross-chain transfer. By this point, the bridge contracts have been live and tested on the Ethereum-Polygon pathway, providing confidence in their design.

### Stage 4: Federated Mining

The final stage introduces cross-chain mining, where miners on different chains can participate in EVMORE mining and have their rewards reflected across the multi-chain deployment. This is the most complex stage and is only activated once the project has substantial treasury backing and a proven bridge track record.

### Design Principles

EVMORE's bridge approach reflects several principles drawn from the lessons of bridge exploits:

**Minimized locked value:** Each stage introduces limited bridge capacity, avoiding the accumulation of massive locked token pools that attract attackers.

**Treasury-gated activation:** Bridge stages are activated only when the EVMORE treasury reaches specific thresholds (1K EVMORE for Stage 2, 10K for Stage 3, 100K for Stage 4). This ensures that bridge complexity is only introduced when the project has sufficient resources to monitor and maintain it.

**Upgrade through migration:** Rather than upgrading bridge contracts in place (which has been a source of vulnerabilities), EVMORE uses migration between distinct contracts for each stage. This avoids the risks associated with in-place upgrades.

**Built-in bridge hooks:** The EvmoreToken contract includes bridge functions (setBridgeContract, bridgeMint, bridgeBurn) that are dormant until activated. This means the token contract is bridge-ready from deployment, but no bridge functionality is exposed until explicitly enabled.

## Best Practices for Bridge Users

If you use cross-chain bridges, here are practical guidelines for reducing your risk.

### Evaluate the Bridge's Security Model

Before using a bridge, understand how it verifies cross-chain transactions. Is it a multisig? How many signers are required? Is it optimistic? What is the challenge period? Is it ZK-based?

### Check the Locked Value

Bridges holding very large amounts of locked tokens (hundreds of millions or billions) are high-value targets. Consider whether the bridge's security model is proportional to the value it secures.

### Prefer Canonical Bridges for Rollups

When bridging to Layer 2 rollups, the canonical bridge (provided by the rollup itself) is generally the most secure option. Third-party bridges may be faster but carry additional risk.

### Wait for Finality

Do not consider a bridge transaction complete until it has achieved finality on both chains. For optimistic bridges, this means waiting for the challenge period to expire.

### Diversify Bridge Usage

If you need to move large amounts cross-chain, consider splitting across multiple bridges rather than routing everything through a single bridge. This limits exposure to any single point of failure.

### Monitor Bridge Health

Several analytics platforms track bridge health metrics, including total value locked, recent transactions, and validator status. Monitoring these metrics can provide early warning of potential issues.

## The Future of Cross-Chain Interoperability

The bridge landscape is evolving rapidly, driven by the clear demand for cross-chain functionality and the equally clear need for better security.

### ZK Bridges

Zero-knowledge proof technology is advancing quickly, and ZK-based bridges are expected to become the gold standard for cross-chain verification. By providing cryptographic proof of source-chain events, ZK bridges eliminate the need to trust validator sets or wait for challenge periods.

### Chain Abstraction

A growing trend toward "chain abstraction" aims to make the underlying blockchain invisible to users. In this vision, users interact with applications without knowing or caring which chain their tokens are on. Bridges operate in the background, and users experience a seamless multi-chain environment.

### Shared Sequencers and Shared Security

Some projects are exploring shared sequencers and shared security models that blur the line between independent chains and a single network. If multiple chains share a sequencer, atomic cross-chain transactions become possible without traditional bridges.

### Standardization

The lack of bridge standards has been a significant contributor to security issues. Efforts to standardize bridge messaging formats, verification interfaces, and security requirements may reduce the incidence of implementation-specific vulnerabilities.

## Conclusion

Cross-chain bridges solve a fundamental problem in the multi-chain cryptocurrency ecosystem: how to move value and data between independent blockchains. The core mechanisms -- lock-and-mint, burn-and-mint, and liquidity networks -- are well-understood, but the verification layer remains a significant security challenge.

The history of bridge exploits, from Ronin to Wormhole to Nomad, demonstrates that bridge security is not a theoretical concern. Billions of dollars have been lost to bridge vulnerabilities, and the complexity of cross-chain verification continues to be a rich attack surface.

Projects like EVMORE are taking a measured approach, introducing cross-chain capabilities through staged deployment rather than launching with full bridge functionality from day one. This philosophy -- start simple, prove security, then expand -- reflects hard-learned lessons from the bridge exploits of recent years.

For users, the practical advice is straightforward: understand the security model of any bridge you use, prefer battle-tested designs, and never assume that a bridge is as secure as the underlying blockchains it connects. Cross-chain interoperability is essential for the future of cryptocurrency, but achieving it safely remains one of the industry's most important open challenges.
