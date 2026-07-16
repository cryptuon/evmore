# EVMORE

<p align="center">
  <img src="documentation/docs/assets/images/hero-banner.png" alt="EVMORE - A fair-launch proof-of-work token on Ethereum" width="100%">
</p>

<p align="center">
  <strong>Fair-launch. Mineable. Verifiable.</strong><br>
  A 21-million-supply proof-of-work ERC-20 on Ethereum, distributed entirely through KeccakCollision mining.
</p>

<p align="center">
  <a href="https://github.com/cryptuon/evmore"><img src="https://img.shields.io/badge/build-passing-brightgreen.svg" alt="Build Status"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
  <a href="https://vyper.readthedocs.io/"><img src="https://img.shields.io/badge/vyper-0.4.0-purple.svg" alt="Vyper"></a>
  <a href="contracts/EvmoreToken.vy"><img src="https://img.shields.io/badge/token-ERC--20-brightgreen.svg" alt="ERC-20"></a>
  <a href="#at-a-glance"><img src="https://img.shields.io/badge/max%20supply-21M-gold.svg" alt="Max Supply"></a>
  <a href="#at-a-glance"><img src="https://img.shields.io/badge/premine-none-brightgreen.svg" alt="No Premine"></a>
</p>

<p align="center">
  <strong><a href="https://evmore.cryptuon.com/">🌐 Site</a> · <a href="https://docs.cryptuon.com/evmore/">📚 Docs</a> · <a href="ROADMAP.md">🗺️ Roadmap</a> · <a href="https://github.com/cryptuon">🔬 Cryptuon Research</a></strong>
</p>

---

## Overview

**EVMORE is an experiment in credibly-neutral token distribution.** It is a 21-million-supply, fixed-cap ERC-20 on Ethereum in which every unit is issued only through proof-of-work mining — there is no premine, no ICO, no team allocation, and no founder reserve. The rules of issuance are enforced entirely on-chain: a 62-line Vyper verifier (`KeccakCollisionVerifier.vy`) decides whether a submitted proof is valid, and the token contract mints the reward. Nobody, including the deployer, can create EVMORE any other way.

The mining function is **KeccakCollision**, a memory-hard proof-of-work in which a miner must find *K = 4* distinct 32-byte values (in strictly ascending order) whose Keccak-256 hashes, when combined with the current challenge, all collide on the lowest *N = 16* bits (widened by difficulty). Because the search is over Keccak-256 preimages rather than raw hashrate, the workload leans on memory access patterns and is comparatively ASIC-unfriendly, keeping it accessible to commodity GPUs and CPUs.

This repository is the reference implementation: the Vyper contracts, a Rust mining backend, deployment tooling, tests, and documentation. It is offered as open infrastructure for people who want to study, run, or fork a verifiable fair-launch token — **not as a financial product.** See [Limitations & honest disclaimers](#limitations--honest-disclaimers).

## Why fair launches matter

A token's distribution is the one property that can never be patched later. If a team mints a premine, allocates a treasury, or sells an ICO, the resulting ownership concentration is baked into the ledger forever — and holders must simply *trust* the disclosed allocation tables. Fair-launch distribution replaces that trust with a rule anyone can verify:

- **Credible neutrality.** The issuance rules treat every participant identically. There is no privileged address, no allowlist, and no discretionary minting. The only way in is to do the work.
- **On-chain verifiability.** You do not have to take a whitepaper's word for the supply schedule. The cap (21M), the reward (50, halving every 210,000 mined blocks), and the validity of every mined unit are checked by the deployed bytecode. Read the contract, not the marketing.
- **No insider head start.** With no premine and no team allocation, the deployer begins with the same zero balance as everyone else. Ownership emerges from participation over time rather than being pre-assigned.

Fair-launch, mineable distribution is a **niche and honest** design, not a growth hack. It trades away the funding and coordination advantages of a premine in exchange for a distribution story that is credibly neutral and independently checkable. EVMORE exists to explore whether that tradeoff can be made practical on modern EVM chains — the [roadmap](ROADMAP.md) is candid about where it is not yet practical.

## At a Glance

| Parameter | Value |
|-----------|-------|
| **Max Supply** | 21,000,000 EVMORE (hard cap, enforced on-chain) |
| **Token Standard** | ERC-20 (18 decimals) |
| **Mining Algorithm** | KeccakCollision (memory-hard, ASIC-unfriendly) |
| **Initial Block Reward** | 50 EVMORE |
| **Halving Interval** | Every 210,000 mined blocks |
| **Target Block Time** | ~10 minutes |
| **Difficulty Adjustment** | Every 2,016 blocks (±4× clamp) |
| **Premine** | None — 100% mined |
| **ICO / Presale** | None |
| **Team / Founder Allocation** | None |
| **Verifier Contract** | `KeccakCollisionVerifier.vy` — 62 lines of Vyper |
| **License** | MIT |

---

## Distribution fairness vs. common launch models

The table below compares EVMORE's distribution mechanics to typical premined and ICO tokens. It is a factual comparison of *how supply enters circulation and who can verify it* — not a claim about value, adoption, or outcomes.

| Property | Premined / team-allocation token | ICO / presale token | Fair-launch mineable (EVMORE) |
|----------|----------------------------------|---------------------|-------------------------------|
| Initial insider balance | Team/treasury holds a large share at genesis | Presale buyers hold allocated share | Zero — deployer starts at 0 |
| How units are created | Minted at deploy per allocation table | Sold before/at launch, often vested | Only via valid PoW proof, minted by contract |
| Who can create new supply | Privileged mint role (unless renounced) | Issuer, per token terms | Anyone who mines a valid solution |
| Supply cap enforcement | Contract or off-chain policy | Varies | Hard-coded `MAX_SUPPLY`, checked on every mint |
| Verifiability of distribution | Trust disclosed tables | Trust disclosed terms | Read the on-chain verifier + mint logic |
| Barrier to participate at launch | Be an insider / early allocatee | Have capital during sale | Have compute; permissionless |
| Ongoing centralization risk | Concentrated genesis holdings | Concentrated presale holdings | Hashrate concentration (see limitations) |

Fair-launch mining does not eliminate centralization risk — it moves it from *genesis allocation* to *hashrate distribution*, which is at least observable on-chain and open to anyone with hardware. See [Limitations](#limitations--honest-disclaimers).

---

## How mining works

EVMORE mining is a two-step, epoch-based process implemented in `EvmoreToken.vy`:

1. **Submit a proof.** A miner searches off-chain for a valid KeccakCollision solution against the current on-chain `currentChallenge` and `currentDifficulty`, then calls `submitProof(solution)` (or `submitProofBatch(...)` for up to 10 at once). The contract calls the verifier via `staticcall`, rejects the proof if invalid, and rejects any solution hash that has been used before (global replay protection). Valid submitters are recorded in the current epoch.
2. **Epoch transition & claim.** Once at least the target block time has elapsed since the last mined block, the next submission triggers `_transition_epoch()`: the block reward for the era (`INITIAL_REWARD >> epoch`, i.e. halving every 210,000 blocks) is recorded, difficulty is retargeted, and a fresh challenge is generated. Miners who contributed to a finished epoch call `claimReward(epoch)` to mint their pro-rata share, with the remainder distributed deterministically to the first miners by index. Every mint is checked against `MAX_SUPPLY`.

Difficulty retargets on two axes: a Bitcoin-style adjustment every 2,016 blocks (clamped to ±4×) toward the ~10-minute target, plus a lightweight congestion adjustment based on recent submission rate.

### The KeccakCollision verifier (62 lines)

The entire validity rule fits in `contracts/KeccakCollisionVerifier.vy`. Its job: parse the solution into *K = 4* ascending 32-byte values, build a difficulty mask, and confirm that `keccak256(challenge ‖ value)` matches on the masked low bits for all four values. If any check fails, the proof is rejected. This is the whole trust anchor of the system — small enough to audit line-by-line.

```python
# @version ^0.4.0
N: constant(uint256) = 16  # bits that must match at base difficulty
K: constant(uint256) = 4   # values needed for a collision

@external
@view
def verify_solution(challenge: bytes32, solution: Bytes[128], difficulty: uint256) -> bool:
    values: DynArray[bytes32, 4] = []
    for i: uint256 in range(K):
        value: bytes32 = convert(slice(solution, i * 32, 32), bytes32)
        values.append(value)
        if i > 0 and convert(values[i], uint256) <= convert(values[i-1], uint256):
            return False  # values must be strictly ascending (dedupes trivially)
    mask: uint256 = shift(1, difficulty) - 1 if difficulty <= 32 else max_value(uint256) >> (256 - difficulty)
    first_hash: uint256 = 0
    for i: uint256 in range(K):
        bits: uint256 = convert(keccak256(concat(challenge, values[i])), uint256) & mask
        if i == 0:
            first_hash = bits
        elif bits != first_hash:
            return False
    return True
```

---

## For Developers

### Tech Stack

| Component | Technology |
|-----------|------------|
| Smart contracts | Vyper 0.4.0 |
| Framework | Ape + Hardhat |
| Mining backend | Rust (`backend/`) |
| Package manager | uv (Python), npm (Node) |
| Frontend | Vue 3 + TypeScript + Tailwind CSS |
| Web3 | ethers.js v6 |
| Testing | pytest via Ape |

### Quick Start

```bash
# Clone and install
git clone https://github.com/cryptuon/evmore
cd evmore
uv sync && npm install

# Compile contracts
uv run ape compile

# Run tests
uv run ape test

# Deploy to a local testnet
uv run python scripts/deploy_testnet.py
```

### Smart Contracts

| Contract | Lines | Purpose |
|----------|-------|---------|
| `EvmoreToken.vy` | 627 | ERC-20 token with integrated mining, halving, difficulty adjustment |
| `KeccakCollisionVerifier.vy` | 62 | On-chain mining proof verification (the validity rule) |
| `EVMOREBridge.vy` | 482 | Multi-chain hub-and-spoke bridge (roadmap) |
| `EVMOREBridgeStage2.vy` | 338 | Manual Ethereum-Polygon bridge (roadmap) |
| `wEVMOREPolygon.vy` | 236 | Wrapped EVMORE on Polygon (roadmap) |

### Architecture

```
                     DeFi Protocols / dApp / Wallets
                                 |
                          ERC-20 Interface
                                 |
              +------------------+------------------+
              |                  |                  |
      EvmoreToken.vy    KeccakCollision     EVMOREBridge.vy
      (Token + Mining)   Verifier.vy       (Cross-Chain Hub)
              |                  |                  |
              +--------+---------+         +--------+--------+
                       |                   |        |        |
                 Proof Submission     Polygon  Arbitrum   Base
                       |
            +----------+----------+
            |          |          |
        Solo       Mining     Reference
        Miners     Pools      Backend (Rust)
```

---

## Roadmap & production viability

The honest challenge with a mineable ERC-20 on Ethereum L1 is that **mining and claiming rewards cost gas** — at L1 prices, the per-block transaction cost can dwarf the economic meaning of the reward, which makes mainnet PoW mining largely impractical. The [**ROADMAP.md**](ROADMAP.md) treats this head-on, including a **Cheapest path to production** analysis of deploying and mining on the cheapest viable EVM L2 (e.g. Base or Arbitrum), plus what production would actually require: a Vyper audit of the token contract, reference miner tooling, difficulty/retarget tuning, block-explorer source verification, and liquidity/listing considerations. No return or price claims — just the engineering and economic realities.

---

## Documentation

Full documentation is available in the `documentation/` directory, built with MkDocs Material.

| Section | Description |
|---------|-------------|
| [What is EVMORE?](documentation/docs/getting-started/what-is-evmore.md) | Introduction for newcomers |
| [Quick Start](documentation/docs/getting-started/quick-start.md) | Wallet setup and first steps |
| [Token Economics](documentation/docs/getting-started/economics.md) | Supply model, halving, distribution |
| [Mining Guide](documentation/docs/mining/mining-guide.md) | Hardware, setup, solo vs pool |
| [KeccakCollision Algorithm](documentation/docs/mining/mining-algorithm.md) | Deep dive into the mining algorithm |
| [Architecture Overview](documentation/docs/architecture/overview.md) | Smart contract design and interaction flows |
| [Contract Reference](documentation/docs/contracts/reference.md) | Full smart contract API |
| [Developer Guide](documentation/docs/developers/getting-started.md) | Environment setup, compile, test, deploy |
| [Contributing](documentation/docs/developers/contributing.md) | How to contribute |
| [FAQ](documentation/docs/getting-started/faq.md) | Frequently asked questions |

To serve the documentation locally:

```bash
cd documentation
uv run mkdocs serve
```

---

## Security

EVMORE's on-chain surface has been hardened, though it has **not** undergone a formal third-party audit — treat it as experimental software:

- Reentrancy protection on state-changing functions (`claimReward`, `withdraw`)
- Global solution-hash uniqueness prevents replay across epochs
- Two-step ownership transfer, plus `renounceOwnership` for credibly-neutral operation
- Test suites under `tests/` covering core token, mining, and security paths
- Independent audit remains an open roadmap item — see [ROADMAP.md](ROADMAP.md)

Report vulnerabilities per [SECURITY.md](SECURITY.md).

---

## Limitations & honest disclaimers

- **Not financial advice, not an investment.** EVMORE is a research and infrastructure experiment in fair distribution and verifiable scarcity. This repository makes no claim about price, return, yield, or future value, and nothing here should be read as investment advice.
- **L1 gas makes mainnet mining impractical today.** Submitting proofs and claiming rewards are on-chain transactions; at Ethereum L1 gas prices this is often uneconomic. The realistic path is a low-cost L2 — see [ROADMAP.md](ROADMAP.md).
- **No formal audit yet.** The contracts are small and hardened but unaudited by a third party.
- **Hashrate can centralize.** Fair genesis distribution does not prevent a well-resourced miner or pool from accumulating a large share of newly mined supply. This risk is observable on-chain but real.
- **Roadmap features are not shipped.** Cross-chain bridging, federated mining, and multi-chain deployment are design targets, not live functionality.

---

## Contributing

We welcome contributions across smart contracts, the Rust mining backend, the Vue 3 frontend, documentation, and security review. See the [Contributing Guide](documentation/developers/contributing.md) and [CONTRIBUTING.md](CONTRIBUTING.md) to get started.

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Part of Cryptuon Research

`evmore` is one of [20 open-source blockchain-infrastructure projects](https://www.cryptuon.com/projects) from **[Cryptuon Research](https://www.cryptuon.com)** — blockchain theory, shipped as protocols.

**Related projects:** [Zig-EVM](https://zig-evm.cryptuon.com/) · [Tesseract](https://tesseract.cryptuon.com/) · [blockchain-compression](https://blockchain-compression.cryptuon.com/)

Docs: [docs.cryptuon.com/evmore](https://docs.cryptuon.com/evmore/) · Contact: [contact@cryptuon.com](mailto:contact@cryptuon.com)

---

<p align="center"><em>A credibly-neutral experiment in verifiable, mined-from-zero scarcity.</em></p>
