# Cross-Chain Bridge

EVMORE uses a **hub-and-spoke** bridge architecture with Ethereum as the hub. All EVMORE tokens are minted on Ethereum; on other chains, wrapped versions (wEVMORE) are minted when tokens are locked on the hub.

---

## Architecture

```mermaid
flowchart TD
    subgraph Ethereum["Ethereum (Hub)"]
        TOKEN["EvmoreToken.vy<br/>21M supply cap"]
        BRIDGE["EVMOREBridge.vy<br/>Lock / Unlock"]
        TOKEN <--> BRIDGE
    end

    subgraph Polygon
        wPOLY["wEVMORE Polygon<br/>0.1% fee"]
    end

    subgraph Arbitrum
        wARB["wEVMORE Arbitrum<br/>0.15% fee"]
    end

    subgraph Base
        wBASE["wEVMORE Base<br/>0.2% fee"]
    end

    subgraph Optimism
        wOP["wEVMORE Optimism<br/>0.25% fee"]
    end

    subgraph Avalanche
        wAVAX["wEVMORE Avalanche<br/>0.3% fee"]
    end

    BRIDGE -->|"Lock EVMORE → Mint wEVMORE"| wPOLY
    BRIDGE -->|"Lock EVMORE → Mint wEVMORE"| wARB
    BRIDGE -->|"Lock EVMORE → Mint wEVMORE"| wBASE
    BRIDGE -->|"Lock EVMORE → Mint wEVMORE"| wOP
    BRIDGE -->|"Lock EVMORE → Mint wEVMORE"| wAVAX

    wPOLY -->|"Burn wEVMORE → Unlock EVMORE"| BRIDGE
    wARB -->|"Burn wEVMORE → Unlock EVMORE"| BRIDGE
    wBASE -->|"Burn wEVMORE → Unlock EVMORE"| BRIDGE
    wOP -->|"Burn wEVMORE → Unlock EVMORE"| BRIDGE
    wAVAX -->|"Burn wEVMORE → Unlock EVMORE"| BRIDGE
```

---

## How Bridging Works

### Bridging Out (Ethereum to Target Chain)

```mermaid
sequenceDiagram
    participant User
    participant Bridge as EVMOREBridge (Ethereum)
    participant Token as EvmoreToken
    participant Target as wEVMORE (Target Chain)
    participant Validators

    User->>Bridge: initiateBridge(amount, targetChain)
    Bridge->>Token: transferFrom(user, bridge, amount)
    Bridge->>Bridge: Create BridgeRequest
    Bridge-->>User: Request ID

    Validators->>Bridge: confirmBridgeRequest(requestId)
    Note over Validators: Min 3 validators must confirm
    Bridge->>Bridge: Check confirmations >= threshold

    Note over Bridge,Target: After withdrawal delay (1 hour)
    Bridge-->>Target: Mint wEVMORE to user on target chain
```

### Bridging Back (Target Chain to Ethereum)

1. User burns wEVMORE on the target chain
2. Validators confirm the burn
3. After the withdrawal delay, EVMORE is unlocked on Ethereum
4. User receives EVMORE on Ethereum

---

## Chain Configuration

| Chain | Chain ID | Fee | Daily Limit | Max Single Transfer |
|-------|----------|-----|-------------|---------------------|
| Polygon | 137 | 0.1% | 1,000,000 EVMORE | 1,000,000 EVMORE |
| Arbitrum | 42161 | 0.15% | 1,000,000 EVMORE | 1,000,000 EVMORE |
| Base | 8453 | 0.2% | 500,000 EVMORE | 1,000,000 EVMORE |
| Optimism | 10 | 0.25% | 500,000 EVMORE | 1,000,000 EVMORE |
| Avalanche | 43114 | 0.3% | 250,000 EVMORE | 1,000,000 EVMORE |

!!! note
    Ethereum is the hub chain. Bridging _to_ Ethereum is always an unlock operation, not a mint.

---

## Security Model

### Multi-Signature Validation

- Minimum 3 validators required to confirm a bridge request
- Up to 20 active validators supported
- Validators are managed by the contract owner (add/remove)

### Rate Limiting

- **Per-user limit**: 10% of the chain's daily limit
- **Global daily limit**: Per-chain caps as listed above
- **Volume tracking**: Resets every 24 hours

### Withdrawal Delay

All bridge requests have a configurable delay (default: 1 hour) between confirmation and execution. This provides time to detect and respond to suspicious activity.

### Emergency Controls

- `emergencyPause()` -- Immediately halt all bridge operations
- Owner-controlled with instant effect

---

## Fee Revenue

Bridge fees accumulate in the bridge contract and contribute to the project treasury. These fees fund subsequent stage deployments:

| Volume (Monthly) | Fee Revenue (Polygon, 0.1%) |
|-------------------|-----------------------------|
| 100,000 EVMORE | 100 EVMORE |
| 1,000,000 EVMORE | 1,000 EVMORE |
| 10,000,000 EVMORE | 10,000 EVMORE |

---

## Stage 2 vs Stage 3 Bridge

| Feature | Stage 2 | Stage 3 |
|---------|---------|---------|
| Chains | Ethereum + Polygon | 6 chains |
| Processing | Manual operator | Automated multi-sig |
| Limits | 1-10K EVMORE | Up to 1M EVMORE/day |
| Validators | Single operator | 3-20 validators |
| Delay | 1 hour | Configurable |

---

## Further Reading

- [Staged Deployment](staged-deployment.md) -- When each bridge stage activates
- [Federated Mining](federated-mining.md) -- How Stage 4 goes beyond bridging
- [Architecture Overview](overview.md) -- How the bridge fits into the broader system
- [Smart Contract Reference](../contracts/reference.md) -- Bridge contract API
