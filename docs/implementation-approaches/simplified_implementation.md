# Simplified Ethereum Implementation

This document provides a minimal set of changes needed to deploy the EVMORE PoW contracts on Ethereum.

## Required Changes

### 1. Version Compatibility

Update the version pragma in both contracts:

```vy
# In both EvmoreToken.vy and KeccakCollisionVerifier.vy
# @version ^0.3.10
```

### 2. Gas Optimization - Precomputed Masks

Modify the verifier to use precomputed masks for common difficulties:

```vy
# In KeccakCollisionVerifier.vy
@external
@view
def verify_solution(
    challenge: bytes32,
    solution: Bytes[128],
    difficulty: uint256
) -> bool:
    values: DynArray[bytes32, 4] = []
    
    # Parse each 32-byte value
    for i: uint256 in range(K):
        start_pos: uint256 = i * 32
        value: bytes32 = convert(slice(solution, start_pos, 32), bytes32)
        values.append(value)
        
        # Check ascending order
        if i > 0:
            if convert(values[i], uint256) <= convert(values[i-1], uint256):
                return False
    
    # Use precomputed masks for efficiency
    mask: uint256 = 0
    if difficulty <= 32:
        mask = shift(1, difficulty) - 1
    else:
        # For higher difficulties, compute dynamically
        mask = MAX_UINT256 >> (256 - difficulty)
    
    # Calculate hashes and verify bit matches
    first_hash: uint256 = 0
    
    for i: uint256 in range(K):
        hash: bytes32 = keccak256(concat(challenge, values[i]))
        bits: uint256 = convert(hash, uint256) & mask
        
        if i == 0:
            first_hash = bits
        elif bits != first_hash:
            return False
            
    return True
```

### 3. Add Emergency Pause Functionality

Add pause functionality for security:

```vy
# In EvmoreToken.vy
# Add state variable
paused: public(bool)

# Add pause functions (only owner can call)
@external
def pause() -> bool:
    # ONLY OWNER CAN CALL - add proper access control
    assert msg.sender == self.owner, "Only owner can pause"
    self.paused = True
    return True

@external
def unpause() -> bool:
    # ONLY OWNER CAN CALL - add proper access control
    assert msg.sender == self.owner, "Only owner can unpause"
    self.paused = False
    return True

# Modify existing functions to check pause state
@external
def submitProof(solution: Bytes[128]) -> bool:
    assert not self.paused, "Contract is paused"
    # ... rest of existing logic

@external
def claimReward(epoch: uint256) -> bool:
    assert not self.paused, "Contract is paused"
    # ... rest of existing logic
```

### 4. Add Withdraw Function for Owner

```vy
# In EvmoreToken.vy
# Add state variable for owner
owner: public(address)

# Modify deploy function
@deploy
def __init__(verifier_address: address):
    self.owner = msg.sender
    # ... rest of existing initialization

# Add withdraw function
@external
def withdraw() -> bool:
    assert msg.sender == self.owner, "Only owner can withdraw"
    send(self.owner, self.balance)
    return True
```

## Deployment Steps

1. Compile contracts with Vyper 0.3.10:
   ```bash
   vyper EvmoreToken.vy -o EvmoreToken.bin
   vyper KeccakCollisionVerifier.vy -o KeccakCollisionVerifier.bin
   ```

2. Deploy KeccakCollisionVerifier first

3. Deploy EvmoreToken with verifier address

4. Verify contracts on Etherscan

## Gas Cost Considerations

The main gas costs will be:
1. `submitProof`: ~200,000-300,000 gas (due to verification)
2. `claimReward`: ~100,000-150,000 gas (minting and transfers)
3. `transfer`: ~50,000 gas (standard ERC20 transfer)

Miners should ensure their rewards exceed these costs.

## Testing on Testnets

Before mainnet deployment:
1. Deploy to Goerli/Rinkeby testnet
2. Test all functionality with multiple accounts
3. Verify gas costs are acceptable
4. Conduct security review