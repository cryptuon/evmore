# Frequently Asked Questions

Comprehensive answers to common questions about EVMORE digital gold.

---

## General Questions

### What is EVMORE?

EVMORE is a digital gold cryptocurrency built on Ethereum. It uses a unique KeccakCollision proof-of-work algorithm to create verifiable digital scarcity, similar to how physical gold requires real effort to mine.

### Why is EVMORE called "digital gold"?

EVMORE shares the key economic properties of physical gold:
- **Fixed supply**: Maximum 21 million tokens (like gold's finite reserves)
- **Requires work to obtain**: Mining requires computational effort
- **Increasing difficulty**: Gets harder to mine over time
- **Store of value**: Designed to preserve purchasing power

### How is EVMORE different from Bitcoin?

| Aspect | Bitcoin | EVMORE |
|--------|---------|--------|
| Supply | 21 million | 21 million |
| Mining | SHA-256 (ASIC required) | KeccakCollision (GPU/CPU) |
| Smart Contracts | Limited | Full ERC-20 + DeFi |
| Mining Accessibility | Industrial only | Consumer hardware |
| Ecosystem | Separate chain | Ethereum ecosystem |

### How is EVMORE different from Ethereum?

| Aspect | Ethereum | EVMORE |
|--------|----------|--------|
| Consensus | Proof-of-Stake | Proof-of-Work |
| Supply | Unlimited | 21 million cap |
| Token Type | Native chain | ERC-20 token |
| Distribution | Validator rewards | Mining rewards |

### Is EVMORE an ERC-20 token?

Yes. EVMORE is a standard ERC-20 token deployed on Ethereum, making it compatible with all Ethereum wallets, exchanges, and DeFi protocols.

### Was there a premine or ICO?

No. EVMORE has a completely fair launch:
- Zero premine
- No initial coin offering
- No team allocation
- No investor tokens
- 100% distributed through mining

### Who created EVMORE?

EVMORE was created by a community of developers passionate about fair, decentralized digital money. The code is open-source and available on GitHub.

### Is EVMORE a security?

EVMORE is designed as a utility token and commodity-like digital asset. It has no premine, no ICO, and is earned entirely through computational work (mining). However, regulatory treatment varies by jurisdiction. Consult a legal professional for specific advice.

---

## Supply and Economics

### What is the total supply of EVMORE?

The maximum supply is **21 million EVMORE**. This is a hard cap enforced by the smart contract.

### How are new EVMORE created?

New EVMORE tokens are created only through mining. When miners submit valid proof-of-work solutions, new tokens are minted as rewards.

### What is the block reward?

The initial reward is **50 EVMORE per block**. This amount halves every 210,000 blocks (approximately every 4 years).

### What is the halving schedule?

| Period | Reward | Total Supply |
|--------|--------|--------------|
| Years 0-4 | 50 EVMORE | 10.5M (50%) |
| Years 4-8 | 25 EVMORE | 15.75M (75%) |
| Years 8-12 | 12.5 EVMORE | 18.375M (87.5%) |
| Years 12-16 | 6.25 EVMORE | 19.69M (93.75%) |
| Years 16-20 | 3.125 EVMORE | 20.34M (96.88%) |

### What happens when all EVMORE is mined?

Once all 21 million EVMORE are mined (estimated in 100+ years), no new tokens will be created. Miners will then be incentivized by transaction fees rather than block rewards.

### How does difficulty adjustment work?

The mining difficulty adjusts automatically based on network hashrate:
- More miners join → difficulty increases → block time stays consistent
- Miners leave → difficulty decreases → block time stays consistent

This maintains predictable token issuance regardless of network size.

### Is EVMORE inflationary or deflationary?

EVMORE is **disinflationary** (decreasing inflation over time):
- Early years: Higher inflation from mining rewards
- Each halving: Inflation rate cuts in half
- Eventually: Near-zero new supply
- If tokens are lost: Effectively deflationary

---

## Mining

### Can I mine EVMORE with my computer?

Yes! The KeccakCollision algorithm is designed to be memory-hard, making it accessible to regular GPUs and CPUs. Unlike Bitcoin, you don't need specialized ASIC hardware.

### What hardware do I need to mine?

**Minimum requirements:**
- Modern CPU (Intel i5/AMD Ryzen 5 or better) OR GPU
- 8GB+ RAM (algorithm is memory-intensive)
- Stable internet connection
- Small amount of ETH for gas fees

**Recommended:**
- Gaming GPU (RTX 3060 or better)
- 16GB+ RAM
- SSD storage

### How much can I earn from mining?

Earnings depend on:
- Your hardware hashrate
- Total network hashrate (competition)
- Current block reward
- EVMORE market price
- Electricity costs

Use the profitability calculator in the [Mining Guide](../mining/mining-guide.md).

### Should I solo mine or join a pool?

| Approach | Pros | Cons |
|----------|------|------|
| **Solo** | Keep 100% of rewards | Irregular income |
| **Pool** | Steady payouts | Pool fees (1-3%) |

**Recommendation:** Pool mining for most users, solo mining only for large operations.

### How long does it take to mine a block?

Target block time is 10 minutes. However, mining is probabilistic:
- You might find a block quickly (luck)
- You might go hours without one (bad luck)
- On average, the network finds a block every 10 minutes

### What is an "epoch" in EVMORE mining?

An epoch is a mining period. Multiple miners can submit proofs during an epoch, and rewards are distributed based on contribution at the end.

### Do I need ETH to mine?

Yes, a small amount. You need ETH to:
- Submit mining proofs to the blockchain
- Claim mining rewards
- Transfer your earned EVMORE

A few dollars worth of ETH is usually sufficient.

---

## Wallets and Storage

### What wallets support EVMORE?

Any Ethereum-compatible wallet works:
- **Browser**: MetaMask, Rabby
- **Mobile**: MetaMask, Rainbow, Trust Wallet
- **Hardware**: Ledger, Trezor
- **Desktop**: Frame

### How do I add EVMORE to my wallet?

1. Open your wallet
2. Find "Add Token" or "Import Token"
3. Enter the EVMORE contract address
4. Token details should auto-fill
5. Confirm to add

### Is EVMORE safe to store in a hot wallet?

For everyday use, yes. For large holdings:
- Consider a hardware wallet
- Use a separate wallet for daily transactions
- Never store recovery phrases digitally

### What if I lose my wallet password?

Use your recovery phrase (12/24 words) to restore access. This is why securing your recovery phrase is critical.

### What if I lose my recovery phrase?

If you lose your recovery phrase AND lose access to your wallet, your funds are permanently lost. There is no recovery mechanism - this is true for all cryptocurrencies.

**Prevention:**
- Write it down on paper
- Store in multiple secure locations
- Consider metal backup plates for fire/water resistance

---

## Transactions

### How long do transactions take?

EVMORE transactions confirm when the Ethereum block containing them is mined:
- Typical: 15-60 seconds
- Busy network: 1-5 minutes
- After confirmation: Usually wait for 2-3 more blocks for security

### What are transaction fees?

You pay Ethereum gas fees (in ETH) for all transactions. EVMORE has no additional protocol fees.

| Transaction Type | Typical Cost |
|-----------------|--------------|
| Simple transfer | $1-10 |
| DEX swap | $5-30 |
| Mining proof | $5-20 |

*Costs vary based on network congestion*

### Can I reverse a transaction?

No. Blockchain transactions are permanent and irreversible. Always:
- Double-check recipient addresses
- Send small test amounts first
- Verify transaction details before confirming

### Can I send EVMORE to a Bitcoin address?

No. EVMORE is an Ethereum token. You can only send to Ethereum addresses (starting with 0x).

### What if I send to the wrong address?

Unfortunately, the funds are lost unless:
- The recipient voluntarily returns them
- You sent to a contract that has a recovery function

Always triple-check addresses before sending.

---

## DeFi and Trading

### Where can I trade EVMORE?

**Decentralized Exchanges (DEXs):**
- Uniswap
- Sushiswap
- Other Ethereum DEXs

**Centralized Exchanges:**
- Listings will be announced as they happen

### Can I use EVMORE in DeFi?

Yes. As an ERC-20 token, EVMORE is compatible with:
- **Lending**: Aave, Compound (once supported)
- **DEXs**: Uniswap, Sushiswap
- **Yield Farming**: Various protocols
- **Derivatives**: Options, futures platforms

### What is impermanent loss?

When providing liquidity to DEXs, if the price ratio between tokens changes, you may have less value than if you just held. This is "impermanent loss." It becomes permanent when you withdraw.

### Can I stake EVMORE?

EVMORE itself uses proof-of-work mining, not staking. However, you may be able to:
- Stake in DeFi protocols for yield
- Provide liquidity for trading fees
- Participate in governance (future feature)

### What price should I expect for EVMORE?

Price is determined by market supply and demand. The project makes no price predictions. EVMORE's value proposition is:
- Digital scarcity (21M cap)
- Fair distribution
- Proof-of-work security
- DeFi compatibility

---

## Security

### Is EVMORE secure?

EVMORE smart contracts have undergone:
- Comprehensive security review
- All critical vulnerabilities fixed
- Reentrancy protection
- Two-step ownership transfer
- External audit preparation

### What are the security features?

1. **Solution replay prevention**: Mining solutions can't be reused
2. **Global uniqueness**: Each solution is globally unique
3. **Reentrancy guards**: Protection against financial attacks
4. **Two-step ownership**: Prevents accidental ownership transfer
5. **Fair reward calculation**: No precision loss in distributions

### Has EVMORE been audited?

The contracts have undergone comprehensive internal security review. External audit status will be updated in documentation.

### What if there's a bug in the contract?

- Minor bugs: May be fixable through governance
- Critical bugs: Community would coordinate response
- Design philosophy: Minimize upgrade ability to maximize decentralization

### Can the team steal my funds?

No. The smart contracts are designed so that:
- Only you control your tokens
- No admin can transfer your funds
- No backdoors or special privileges

---

## Technical Questions

### What blockchain is EVMORE on?

EVMORE is deployed on **Ethereum mainnet**. Future bridges may enable use on other chains.

### What is the contract address?

The official contract address will be published after mainnet deployment. Always verify addresses from official sources.

### What programming language are the contracts written in?

Vyper - a security-focused smart contract language that prioritizes simplicity and auditability over complexity.

### Is the code open source?

Yes. All smart contract code is available on GitHub for review, auditing, and contribution.

### What is KeccakCollision?

KeccakCollision is EVMORE's mining algorithm:
- Based on Keccak (the algorithm behind SHA-3)
- Requires finding multiple values with matching hash patterns
- Memory-hard to prevent ASIC dominance
- Verified on-chain by smart contracts

### How does on-chain verification work?

When a miner submits a solution:
1. The smart contract receives the values
2. It computes the hashes
3. It verifies the collision pattern meets difficulty
4. If valid, the miner is credited

This happens entirely on-chain, creating a transparent record.

---

## Troubleshooting

### My transaction is stuck

1. Check gas price - you may need higher gas
2. Wait - network congestion can cause delays
3. Speed up - in MetaMask, you can speed up pending transactions
4. Cancel - you can cancel and retry with higher gas

### I can't see EVMORE in my wallet

1. Ensure you're on Ethereum mainnet
2. Add EVMORE as a custom token
3. Use the correct contract address
4. Refresh your wallet

### Mining isn't finding solutions

1. Check your hardware is working correctly
2. Verify mining software configuration
3. Ensure internet connection is stable
4. Check that the challenge is current

### Gas fees are too high

1. Wait for lower network congestion
2. Use gas tracking tools to find optimal times
3. Set appropriate (not excessive) gas limits
4. Consider batching transactions

See the [Troubleshooting Guide](troubleshooting.md) for more solutions.

---

## Getting Help

### Where can I get support?

1. **Documentation**: Check these docs first
2. **FAQ**: You're here!
3. **Discord**: Community chat support
4. **GitHub Issues**: Technical problems

### How do I report a bug?

1. Check if it's already reported on GitHub
2. Create a new issue with:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if helpful

### How can I contribute?

- **Code**: Submit pull requests
- **Documentation**: Improve guides
- **Community**: Help others, answer questions
- **Mining**: Strengthen the network
- **Testing**: Find and report bugs

See [Community Resources](../community/resources.md) for more ways to participate.

---

## Glossary Quick Reference

| Term | Meaning |
|------|---------|
| Block | A group of transactions confirmed together |
| Challenge | The current mining puzzle to solve |
| Difficulty | How hard the mining puzzle is |
| Epoch | A mining period for reward distribution |
| Gas | Fee paid for Ethereum transactions |
| Halving | Reduction of block reward by 50% |
| Hashrate | Mining computation speed |
| Pool | Group of miners sharing rewards |
| Proof-of-Work | Consensus requiring computational effort |
| Wallet | Software/hardware storing crypto keys |

For more terms, see the [Glossary](glossary.md).
