---
title: "ERC-20 Tokens Explained: How Tokens Work on Ethereum"
description: "ERC-20 is Ethereum's standard interface for fungible tokens, defining transfer, balance, and approval functions. Learn how ERC-20 tokens work, how they differ from ETH, and how they power DeFi."
date: 2026-03-26
author: "EVMORE Team"
tags: [ERC-20, Ethereum, tokens, smart-contracts, DeFi]
seoKeywords: ["ERC-20 tokens explained", "what is ERC-20", "Ethereum token standard"]
comparison: false
draft: false
---

## What Is ERC-20?

ERC-20 is a technical standard for creating fungible tokens on the Ethereum blockchain. The abbreviation stands for Ethereum Request for Comment 20, referring to the proposal number assigned when Fabian Vogelsteller and Vitalik Buterin introduced the standard in November 2015.

Before ERC-20, every token on Ethereum implemented its own interface. Wallets, exchanges, and other applications had to write custom code to interact with each token. ERC-20 solved this by defining a common set of functions and events that all compliant tokens must implement. Once a wallet supports ERC-20, it automatically works with every ERC-20 token -- whether it was created in 2015 or yesterday.

As of 2026, there are over 500,000 ERC-20 tokens deployed on Ethereum mainnet. They represent everything from stablecoins (USDC, USDT, DAI) and governance tokens (UNI, AAVE, MKR) to meme coins and mining-based digital assets like EVMORE. The standard has been so successful that virtually every smart contract platform (Polygon, Arbitrum, Base, BNB Chain) has adopted compatible token standards.

## How ERC-20 Tokens Differ from ETH

A common point of confusion is the relationship between ETH (Ethereum's native currency) and ERC-20 tokens. They are fundamentally different:

| Aspect | ETH | ERC-20 Tokens |
|--------|-----|---------------|
| Type | Native currency | Smart contract |
| Storage | Account balance in protocol | Token contract state mapping |
| Transfer mechanism | Native transaction | Contract function call |
| Gas payment | Used to pay gas | Cannot pay gas (need ETH) |
| Creation | Protocol-level mining/staking rewards | Smart contract deployment |
| Supply rules | Protocol-defined issuance | Contract-defined (varies per token) |
| Account requirement | Just an Ethereum address | Address + token contract interaction |

ETH exists at the protocol level. When you send ETH, the Ethereum Virtual Machine (EVM) directly modifies the sender's and receiver's account balances. No smart contract is involved.

ERC-20 tokens exist as entries in a smart contract's storage. When you "own" 100 USDC, what actually exists on-chain is a mapping inside the USDC contract that associates your address with the number 100. Transferring tokens means calling a function on that contract to update the mapping.

This distinction has practical implications. You always need ETH to interact with ERC-20 tokens because every function call on Ethereum requires gas, and gas is paid in ETH. If your wallet holds millions in USDC but zero ETH, you cannot move those tokens until you acquire some ETH for gas.

## The ERC-20 Interface

The ERC-20 standard defines six mandatory functions and two events. Every compliant token must implement all of them.

### Core Functions

**`totalSupply()`** -- Returns the total number of tokens in existence. This is a read-only function that costs no gas to call.

```
function totalSupply() view returns (uint256)
```

For fixed-supply tokens, this returns a constant. For tokens with minting or burning mechanisms, this value changes over time. EVMORE's `totalSupply` increases as miners discover new blocks, up to the 21 million hard cap.

**`balanceOf(address)`** -- Returns the token balance of a specific address. Also read-only and gas-free.

```
function balanceOf(address account) view returns (uint256)
```

Internally, this reads from the contract's balance mapping, which stores every holder's balance.

**`transfer(address, uint256)`** -- Transfers tokens from the caller's address to a recipient. This is the most basic way to send tokens.

```
function transfer(address to, uint256 amount) returns (bool)
```

The function must check that the caller has sufficient balance, subtract from the sender, add to the recipient, and emit a Transfer event. It returns true on success.

**`approve(address, uint256)`** -- Grants another address permission to spend up to a specified amount of the caller's tokens.

```
function approve(address spender, uint256 amount) returns (bool)
```

This is essential for DeFi interactions. When you use a decentralized exchange like Uniswap, you first approve the exchange contract to spend your tokens, then the exchange contract transfers them on your behalf during the swap.

**`allowance(address, address)`** -- Returns how many tokens the spender is still allowed to withdraw from the owner.

```
function allowance(address owner, address spender) view returns (uint256)
```

**`transferFrom(address, address, uint256)`** -- Transfers tokens from one address to another, using the allowance mechanism.

```
function transferFrom(address from, address to, uint256 amount) returns (bool)
```

This function is called by the approved spender (typically a smart contract). It checks the allowance, deducts the transfer amount from the allowance, performs the transfer, and emits a Transfer event.

### Events

**`Transfer(address indexed from, address indexed to, uint256 value)`** -- Emitted whenever tokens move between addresses, including minting (from the zero address) and burning (to the zero address).

**`Approval(address indexed owner, address indexed spender, uint256 value)`** -- Emitted when an allowance is set or changed via the `approve` function.

Events are critical for off-chain infrastructure. Wallets, block explorers, and indexing services monitor these events to track balances, display transaction history, and maintain searchable databases of token activity.

## The Token Lifecycle

### Creation and Deployment

An ERC-20 token begins its life when someone deploys a smart contract implementing the ERC-20 interface to Ethereum. The deployment transaction includes the contract's bytecode and any constructor parameters (token name, symbol, initial supply, etc.).

The deployer pays gas for this transaction, and once the contract is confirmed on-chain, it exists at a specific Ethereum address. This address becomes the token's permanent identifier -- for example, USDC lives at `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48` on Ethereum mainnet.

### Minting

Tokens come into existence through minting, which creates new tokens and assigns them to an address. The ERC-20 standard does not specify how minting works -- that is up to each token's implementation.

Common minting approaches:

- **Fixed supply at deployment:** All tokens are minted in the constructor and assigned to the deployer. Many simple tokens use this approach.
- **Owner-controlled minting:** A privileged address (the contract owner or a minting role) can create new tokens. Stablecoins like USDC use this model.
- **Programmatic minting:** Tokens are minted according to rules encoded in the contract. This includes staking rewards, liquidity mining, and proof-of-work mining.

EVMORE uses programmatic minting through proof-of-work mining. New tokens are minted only when a miner submits a valid KeccakCollision solution to the smart contract. The contract verifies the solution on-chain and, if valid, mints the block reward to the miner's address. No entity can mint tokens outside this process.

### Transfers and Trading

Once minted, tokens flow through the ecosystem via transfers. Direct transfers (using `transfer()`) handle simple person-to-person payments. The approve-and-transferFrom pattern enables more complex interactions with smart contracts.

Token trading typically happens through:

- **Decentralized exchanges (DEXs):** Automated market makers like Uniswap allow anyone to create a trading pair and provide liquidity. Trading happens entirely on-chain through smart contract interactions.
- **Centralized exchanges (CEXs):** Traditional order-book exchanges that custody user funds. They process ERC-20 deposits by monitoring Transfer events to their deposit addresses.
- **OTC (over-the-counter):** Direct trades between parties, sometimes using escrow contracts.

### Burning

Burning destroys tokens by sending them to an address from which they can never be recovered (typically the zero address `0x0000...0000`). This permanently reduces the total supply.

Some tokens burn programmatically. Ethereum burns a portion of transaction fees (EIP-1559). Other tokens burn based on usage, buy-backs, or governance decisions.

## Token Economics and Design Patterns

The ERC-20 standard defines the interface, but the economic model is entirely up to the creator. This flexibility has produced a wide range of token designs.

### Fixed Supply Tokens

The simplest model: a fixed number of tokens are created at deployment and never change. Examples include many governance tokens where the total supply is allocated at launch according to a predetermined schedule.

### Inflationary Tokens

New tokens are continuously minted, usually as rewards for network participants. Staking reward tokens follow this pattern. The inflation rate may be fixed, decreasing, or governance-controlled.

### Deflationary Tokens

Token supply decreases over time through burning mechanisms. Some tokens burn a percentage of each transfer, creating constant deflationary pressure.

### Halving Supply Tokens

Inspired by Bitcoin, these tokens decrease their minting rate on a predetermined schedule. EVMORE follows this model, with block rewards halving at set intervals until the 21 million supply cap is reached. This creates predictable scarcity and a supply curve that early adopters can model.

### Supply Comparison

| Token Type | Supply Over Time | Scarcity Model | Example |
|-----------|-----------------|----------------|---------|
| Fixed supply | Constant | Scarcity from day one | UNI |
| Inflationary | Increasing | Offset by utility/staking | Staking reward tokens |
| Deflationary | Decreasing | Increasing scarcity | Burn-on-transfer tokens |
| Halving | Increasing then capped | Bitcoin-style scarcity | EVMORE |
| Elastic | Variable (rebasing) | Target price stability | AMPL |

## DeFi Integration

ERC-20 tokens are the building blocks of decentralized finance. The standardized interface means any ERC-20 token can plug into any DeFi protocol without custom integration.

### Decentralized Exchanges

DEXs like Uniswap, SushiSwap, and Curve allow permissionless trading of any ERC-20 token. Anyone can create a liquidity pool for a new token by depositing it alongside ETH or another base token. This gives new tokens immediate trading capability without exchange listings.

The process relies heavily on the approve/transferFrom pattern. When you swap tokens on Uniswap, you first approve the router contract to spend your tokens, then the router executes the swap -- pulling your tokens in and sending the output tokens back -- all in a single transaction.

### Lending and Borrowing

Protocols like Aave and Compound allow users to supply ERC-20 tokens as collateral and borrow other tokens against them. The ERC-20 standard makes this possible because the lending contracts can hold, transfer, and account for any compliant token using the same code.

### Yield Farming and Liquidity Mining

Users can deposit ERC-20 tokens into various protocols to earn rewards, often paid in other ERC-20 tokens. This composability -- where one token protocol interacts with another -- is sometimes called "money legos" and is only possible because of the standardized interface.

### Wrapping and Bridging

Non-ERC-20 assets can be "wrapped" to create ERC-20 representations. Wrapped Bitcoin (WBTC) is an ERC-20 token backed 1:1 by BTC held in custody. This pattern enables assets from other blockchains to participate in Ethereum's DeFi ecosystem.

Bridge contracts extend this to cross-chain transfers. An ERC-20 token on Ethereum can be bridged to Polygon, Arbitrum, or other chains, typically by locking tokens on the source chain and minting wrapped equivalents on the destination chain.

## Mining-Based ERC-20 Tokens: A Special Case

Most ERC-20 tokens are created through simple minting by a privileged address or through token sales. A smaller category of tokens uses proof-of-work mining for distribution, combining the ERC-20 standard with Bitcoin-style mining economics.

This approach offers several unique advantages:

**Fair distribution.** Tokens are earned through verifiable work, not purchased from insiders. There is no ICO, no pre-sale, and no allocation that gives anyone a head start.

**On-chain verification.** Mining solutions are submitted to and verified by the token's smart contract. Every minting event is transparent and auditable.

**Built-in scarcity.** Mining-based tokens typically implement supply caps and halving schedules, creating programmatic scarcity without relying on governance decisions.

**Commodity characteristics.** Tokens that are mined through proof-of-work have a stronger argument for commodity classification under securities law, since they are not investment contracts sold by an issuer.

EVMORE implements this model as an ERC-20 token with integrated KeccakCollision mining. The smart contract serves as both the token contract and the mining coordinator. When a miner calls the mining function with a valid KeccakCollision solution, the contract verifies the solution, adjusts difficulty, and mints the reward -- all on-chain, all in a single transaction.

This architecture means EVMORE tokens have the full interoperability of any ERC-20 token. They can be traded on Uniswap, used as collateral on Aave, bridged to Layer 2 networks, and integrated into any application that supports the ERC-20 standard. The mining mechanism is the distribution method, but the resulting token is fully standard and composable.

## Common ERC-20 Pitfalls

Understanding ERC-20 also means understanding its limitations and common issues.

### Approval Front-Running

The approve function has a known race condition. If a user changes an allowance from 100 to 50, a malicious spender can front-run the transaction to spend the original 100 and then spend the new 50, extracting 150 total. The mitigation is to set allowance to 0 before setting a new value, or use `increaseAllowance`/`decreaseAllowance` functions (introduced by OpenZeppelin but not part of the core standard).

### Lost Tokens

If you accidentally send ERC-20 tokens to a contract that does not handle them (or directly to the token contract's own address), those tokens may be permanently locked. Unlike ETH, there is no built-in mechanism for contracts to reject incoming token transfers.

### Decimal Confusion

ERC-20 tokens store balances as integers with an implied decimal point. Most tokens use 18 decimals (matching ETH's wei), but some use 6 (USDC) or 8 (WBTC). Confusing decimals can lead to transferring wildly incorrect amounts.

### Fake Tokens

Anyone can create an ERC-20 token with any name and symbol. There is nothing preventing someone from deploying a token called "USDC" or "EVMORE" with a different contract address. Always verify a token's contract address through official sources before interacting with it.

## Beyond ERC-20: Related Standards

The ERC-20 standard has inspired several extensions and alternatives:

| Standard | Purpose | Key Difference from ERC-20 |
|----------|---------|---------------------------|
| ERC-721 | Non-fungible tokens (NFTs) | Each token is unique |
| ERC-1155 | Multi-token standard | Supports both fungible and non-fungible in one contract |
| ERC-777 | Advanced fungible token | Hooks for send/receive, operator permissions |
| ERC-4626 | Tokenized vaults | Standard interface for yield-bearing tokens |
| ERC-2612 | Permit (gasless approvals) | Allows approvals via signatures instead of transactions |

ERC-2612 is particularly noteworthy because it solves the two-transaction problem (approve then transferFrom) by allowing users to sign an off-chain message granting approval, which the spender submits on-chain alongside the transfer.

## Conclusion

ERC-20 is one of the most consequential standards in blockchain history. By defining a common interface for fungible tokens, it unlocked an ecosystem of interoperable financial applications that now handles hundreds of billions of dollars in value.

Understanding how ERC-20 works -- the balance mappings, the transfer functions, the approval mechanism -- is fundamental knowledge for anyone participating in the Ethereum ecosystem. Whether you are trading tokens on a DEX, providing liquidity, or participating in governance, you are interacting with ERC-20 contracts.

Projects like EVMORE demonstrate that the ERC-20 standard is flexible enough to support novel distribution mechanisms like proof-of-work mining while maintaining full compatibility with the broader Ethereum ecosystem. By implementing mining logic directly in the ERC-20 contract, EVMORE combines the fair distribution properties of Bitcoin-style mining with the composability and interoperability that make Ethereum's token ecosystem so powerful.
