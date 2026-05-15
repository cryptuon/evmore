# Smart Contract Reference

All EVMORE contracts are written in Vyper 0.4.0 and deployed on Ethereum. This page documents the public interfaces, key functions, and events.

---

## Contract Summary

| Contract | Lines | Purpose | Stage |
|----------|-------|---------|-------|
| `EvmoreToken.vy` | 627 | ERC-20 token with integrated mining | 1 |
| `KeccakCollisionVerifier.vy` | 62 | Mining proof verification | 1 |
| `EVMOREBridgeStage2.vy` | 338 | Manual Ethereum-Polygon bridge | 2 |
| `wEVMOREPolygon.vy` | 236 | Wrapped EVMORE on Polygon | 2 |
| `EVMOREBridge.vy` | 482 | Multi-chain automated bridge | 3 |

---

## EvmoreToken.vy

The core token contract. Implements ERC-20 and integrates the mining reward system.

### Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `INITIAL_REWARD` | 50 * 10^18 | 50 EVMORE per block |
| `HALVING_BLOCKS` | 210,000 | Blocks between halvings (~4 years) |
| `MAX_SUPPLY` | 21,000,000 * 10^18 | Hard supply cap |
| `TARGET_BLOCK_TIME` | 600 | 10-minute target (seconds) |
| `DIFFICULTY_ADJUSTMENT_INTERVAL` | 2,016 | Blocks between adjustments |
| `MAX_ADJUSTMENT_FACTOR` | 4 | Max 4x change per difficulty adjustment |
| `SUBMISSION_WINDOW` | 100 | Rolling window (blocks) for congestion measurement |
| `TARGET_SUBMISSIONS_PER_BLOCK` | 10 | Congestion target |

### ERC-20 Functions

| Function | Description |
|----------|-------------|
| `transfer(to, amount)` | Transfer tokens |
| `approve(spender, amount)` | Approve spending |
| `transferFrom(from, to, amount)` | Transfer on behalf |
| `balanceOf(owner) -> uint256` | Get balance |
| `allowance(owner, spender) -> uint256` | Get allowance |
| `totalSupply() -> uint256` | Current total supply |

### Mining Functions

| Function | Description |
|----------|-------------|
| `submitProof(solution: Bytes[128])` | Submit a single mining proof |
| `submitProofBatch(solutions: DynArray[Bytes[128], 10])` | Submit up to 10 proofs in one transaction |
| `claimReward(epoch: uint256)` | Claim mining reward for a completed epoch |
| `currentChallenge() -> bytes32` | Get the current mining challenge |
| `currentDifficulty() -> uint256` | Get the current difficulty level |
| `currentEpoch() -> uint256` | Get the current epoch number |

### Bridge Functions (Dormant Until Stage 2+)

| Function | Description |
|----------|-------------|
| `setBridgeContract(bridge: address)` | Set the bridge contract address (owner only) |
| `enableBridgeMint()` | Activate bridge minting (owner only) |
| `enableBridgeBurn()` | Activate bridge burning (owner only) |
| `bridgeMint(to: address, amount: uint256)` | Mint tokens via bridge (bridge only) |
| `bridgeBurn(from_: address, amount: uint256)` | Burn tokens via bridge (bridge only) |

### Admin Functions

| Function | Description |
|----------|-------------|
| `pause()` | Pause all transfers and mining (owner only) |
| `unpause()` | Unpause the contract (owner only) |
| `transferOwnership(new_owner: address)` | Initiate ownership transfer (owner only) |
| `acceptOwnership()` | Accept ownership transfer (pending owner only) |
| `renounceOwnership()` | Renounce ownership permanently (owner only) |
| `withdraw()` | Withdraw accidentally-sent ETH from the contract (owner only) |

### Events

| Event | Description |
|-------|-------------|
| `Transfer(from, to, value)` | Token transfer |
| `Approval(owner, spender, value)` | Spending approval |
| `Mining(miner, reward, solution)` | Mining reward emitted |
| `ProofSubmitted(miner, epoch, solution_hash)` | Mining proof accepted |
| `RewardClaimed(miner, epoch, amount)` | Reward claimed |
| `EpochTransition(old_epoch, new_epoch, total_reward, miner_count)` | New epoch started |
| `DifficultyAdjusted(old_difficulty, new_difficulty, block_number)` | Difficulty changed |
| `ChallengeGenerated(new_challenge, block_number)` | New mining challenge issued |
| `Paused(account)` / `Unpaused(account)` | Contract pause state changed |
| `OwnershipTransferStarted(previous_owner, new_owner)` | Two-step ownership initiated |
| `OwnershipTransferred(previous_owner, new_owner)` | Ownership transfer accepted |

---

## KeccakCollisionVerifier.vy

A stateless verification contract with a single view function.

### Functions

| Function | Description |
|----------|-------------|
| `verify_solution(challenge: bytes32, solution: Bytes[128], difficulty: uint256) -> bool` | Verify a mining solution |

**Verification steps:**

1. Parse 4 x 32-byte values from the 128-byte solution
2. Verify values are in strictly ascending order
3. Compute `keccak256(challenge + value)` for each value
4. Apply difficulty mask: `(1 << difficulty) - 1`
5. Verify all masked hash results are identical
6. Return `true` if all checks pass

**Gas optimization:** Inline mask computation -- `(1 << difficulty) - 1` for difficulty <= 32, otherwise `max_value(uint256) >> (256 - difficulty)`.

---

## EVMOREBridge.vy

The production bridge contract for Stage 3+ multi-chain operations.

### Key Functions

| Function | Description |
|----------|-------------|
| `initiateBridge(amount: uint256, target_chain: uint256)` | Start a bridge transfer |
| `confirmBridgeRequest(request_id: bytes32)` | Validator confirms a request |
| `addValidator(validator: address)` | Add a bridge validator (owner only) |
| `removeValidator(validator: address)` | Remove a validator (owner only) |
| `updateChainConfig(...)` | Update per-chain parameters (owner only) |
| `emergencyPause()` | Emergency halt (owner only) |
| `getBridgeStats() -> (uint256, uint256, uint256)` | Get locked, bridged-out, and request counts |

### Security Parameters

| Parameter | Value |
|-----------|-------|
| Minimum validators | 3 |
| Maximum validators | 20 |
| Default withdrawal delay | 1 hour |
| Per-user rate limit | 10% of daily chain limit |
| Max single withdrawal | 1,000,000 EVMORE |

---

## EVMOREBridgeStage2.vy

Simplified bridge for Stage 2 (Ethereum-Polygon only).

| Feature | Value |
|---------|-------|
| Min bridge amount | 1 EVMORE |
| Max bridge amount | 10,000 EVMORE |
| Processing | Manual operator |
| Withdrawal delay | 1 hour |
| Fee | 0.1% |

---

## wEVMOREPolygon.vy

Wrapped EVMORE on Polygon. Mints when tokens are locked on Ethereum, burns when bridging back.

| Function | Description |
|----------|-------------|
| `mint(to: address, amount: uint256)` | Mint wEVMORE (bridge only) |
| `burn(from_: address, amount: uint256)` | Burn wEVMORE (bridge only) |
| Standard ERC-20 functions | transfer, approve, balanceOf, etc. |

---

## Source Code

All contracts are in the `contracts/` directory:

```
contracts/
  EvmoreToken.vy              # Core token + mining
  KeccakCollisionVerifier.vy   # PoW verification
  EVMOREBridge.vy              # Multi-chain bridge (Stage 3)
  bridges/
    EVMOREBridgeStage2.vy      # Polygon bridge (Stage 2)
    wEVMOREPolygon.vy          # Wrapped token on Polygon
```

---

## Further Reading

- [Architecture Overview](../architecture/overview.md) -- How contracts interact
- [KeccakCollision Algorithm](../mining/mining-algorithm.md) -- Mining verification details
- [Developer Getting Started](../developers/getting-started.md) -- Compile and test contracts
