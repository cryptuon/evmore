# EVMORE Roadmap

> **Scope & honesty note.** EVMORE is a research experiment in credibly-neutral, fair-launch token distribution. This roadmap describes engineering and economic realities. It contains **no price, return, yield, or investment claims**, and the presence of an item here is not a promise of value or a schedule guarantee.

## Vision

EVMORE exists to answer a narrow, honest question: *can a fully mined, no-premine, on-chain-verifiable ERC-20 be made practical on a modern EVM chain?* The distribution rules are the product — 21M hard cap, 50-EVMORE reward halving every 210,000 mined blocks, and a 62-line Vyper verifier that anyone can read. The mission is to keep those rules credibly neutral (no privileged mint, no insider genesis balance) while removing the practical barriers that today make mineable ERC-20s uneconomic to run.

Success is measured in **verifiability and neutrality**, not market metrics: contracts small enough to audit, issuance anyone can reproduce, and a participation cost low enough that mining is open to commodity hardware rather than only the well-capitalized.

---

## Milestones

### M0 — Reference implementation (current)
- Vyper token (`EvmoreToken.vy`) with integrated mining, halving, and dual difficulty retargeting.
- 62-line `KeccakCollisionVerifier.vy` as the sole validity rule.
- Rust mining backend (`backend/`), Ape/Hardhat tooling, deploy scripts, and test suites.
- Local-testnet deployment verified.

### M1 — Verifiable testnet launch
- Deploy token + verifier to a public testnet (e.g. Sepolia and an L2 testnet).
- Publish verified source on the block explorer so anyone can read the deployed bytecode.
- Reference miner produces valid proofs end-to-end against the live challenge.
- Difficulty/retarget parameters observed and tuned under real block timing.

### M2 — Cheapest-path production candidate (see below)
- Select the cheapest viable EVM L2 and deploy there as the primary network.
- Reference miner tooling packaged for non-experts (build once, run anywhere).
- Third-party Vyper audit of the token contract; findings published.
- Difficulty retarget calibrated to L2 block times and realistic hashrate.

### M3 — Ecosystem & durability
- Optional cross-chain presence (bridge contracts already stubbed in `contracts/`).
- Mining pool reference / coordination tooling for smaller miners.
- Liquidity and listing considerations documented (not solicited — see caveats below).
- Long-term maintenance: ownership renounced or transferred to a neutral steward.

---

## Cheapest path to production

**The core problem.** Mining EVMORE is not free CPU work that stays off-chain — every valid solution must be **submitted on-chain** (`submitProof` / `submitProofBatch`) and every reward **claimed on-chain** (`claimReward`). Both are state-changing transactions that cost gas. On Ethereum **L1**, a single proof submission plus a claim can cost several dollars to tens of dollars depending on gas price and calldata (each solution is 128 bytes; batches carry up to 10). When the per-transaction gas cost is on the order of, or larger than, the economic meaning of a block reward, **L1 mining is effectively impractical** — the network cost of *recording* the work dominates the work itself. This is the single biggest barrier to EVMORE being usable, and it is not solvable by tuning difficulty.

**The direction: deploy and mine on the cheapest viable EVM L2.** An L2 preserves everything that makes EVMORE meaningful — the same Vyper bytecode, the same verifier, the same on-chain verifiability and fair-launch rules — while reducing per-transaction cost by one to several orders of magnitude. Nothing in the contract is L1-specific; it is standard EVM.

### L2 comparison (gas/cost characteristics, factual)

| Chain | Rollup type | Cost driver | Why it fits EVMORE | Tradeoff |
|-------|-------------|-------------|--------------------|----------|
| **Base** | OP-stack optimistic | Very low fees post-EIP-4844 blob calldata; large user base | Cheapest common denominator for frequent small txns; broad wallet/explorer support | Sequencer is currently centralized; L1 finality delay |
| **Arbitrum One** | Optimistic (Nitro) | Low fees; efficient calldata compression | Mature tooling, deep DeFi/liquidity, good Vyper/EVM parity | Similar centralized-sequencer caveat |
| **Optimism** | OP-stack optimistic | Comparable to Base | Same OP-stack model; superchain interop | Overlaps Base with less distinct upside |
| **Ethereum L1** | Base layer | Full L1 gas | Maximum neutrality/decentralization | Per-txn cost makes frequent mining uneconomic |

**Recommendation:** target an **OP-stack L2 (Base as the reference candidate, Arbitrum One as the alternative)** as the primary production network, with L1 reserved as an optional high-assurance settlement anchor rather than the mining venue. Base is the reference candidate because its post-blob (EIP-4844) fee floor is low enough that the *repeated small transactions* mining requires — many proof submissions and reward claims — stop being the dominant cost. Arbitrum One is the fallback for its deeper existing liquidity and tooling maturity. Both keep the contract, the verifier, and the fair-launch guarantees byte-for-byte identical to L1.

> This is an engineering and cost analysis only. It makes no claim about token price, returns, or profitability of mining.

### Production-viability checklist

Moving from reference implementation to a credible production launch requires, at minimum:

1. **Vyper contract audit.** Independent third-party audit of `EvmoreToken.vy` (627 lines) and `KeccakCollisionVerifier.vy` (62 lines) — with public findings and remediations. The verifier is the trust anchor and must be audited line-by-line.
2. **Reference miner tooling.** Package the Rust backend into a reproducible, easy-to-run miner (prebuilt binaries + docs) so participation does not require deep expertise. Fair launch is only fair if ordinary participants can actually mine.
3. **Difficulty / retarget tuning.** Recalibrate `TARGET_BLOCK_TIME`, the 2,016-block adjustment window, the ±4× clamp, and the congestion adjustment to the chosen L2's block times and realistic starting hashrate, so early blocks neither stall nor over-issue.
4. **Block-explorer source verification.** Publish and verify the deployed source on the L2's explorer (Basescan / Arbiscan) so the exact rules of issuance — cap, reward, halving — are independently readable, not just claimed.
5. **Liquidity & listing considerations.** Document, factually and without solicitation, how a permissionless fair-launch asset typically reaches secondary markets (e.g. permissionless AMM pools). Because there is no treasury or presale, any liquidity is community-provided; the project neither guarantees nor promises listings, market-making, or price support.
6. **Neutral operation of admin surface.** Decide and document the fate of the owner role (pause / bridge setters): renounce it or transfer it to a neutral steward before or shortly after launch, so "credibly neutral" is true in practice, not just in intent.

### Non-goals

- No premine, presale, or team allocation will be introduced to fund development.
- No price, APY, or return targets. EVMORE is not marketed as a money-maker.
- No privileged minting path beyond the mining reward and the (optional, roadmap) bridge.

---

## Contributing to the roadmap

Roadmap items are open to discussion and contribution. See [CONTRIBUTING.md](CONTRIBUTING.md). Security-sensitive items should follow [SECURITY.md](SECURITY.md).

Docs: [docs.cryptuon.com/evmore](https://docs.cryptuon.com/evmore/) · Site: [evmore.cryptuon.com](https://evmore.cryptuon.com/) · Contact: [contact@cryptuon.com](mailto:contact@cryptuon.com)
