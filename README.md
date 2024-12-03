KeccakCollision PoW Algorithm

Core Concept:
- Similar to Equihash but using Keccak256 for both mining and verification
- Requires finding multiple inputs that produce partial collisions in their hashes
- Uses bit manipulation to verify collisions, making verification efficient on-chain

Parameters:
- N: Number of bits that must collide (difficulty parameter)
- K: Number of values that must have matching bits (e.g., K=4 means find 4 values)
- Each solution consists of K different 32-byte values that when hashed:
  1. Have N matching bits in their least significant bits
  2. Are in strictly ascending order (to prevent permutation duplicates)

Mining Process:
1. Take block challenge as input
2. Generate K different values
3. For each value:
   - Concatenate with challenge and hash with keccak256
   - Extract N least significant bits
4. Verify all K hashes have matching N bits
5. Values must be in ascending order

Verification Process:
1. Verify K values are in ascending order
2. Hash each value with challenge
3. Extract and compare N least significant bits
4. All must match

Security Properties:
- Memory-hard: Requires keeping track of many hash values
- Verification is O(K) hashing operations
- Non-parallelizable due to sequential nature
- Difficulty adjustable via N parameter

Mining Economics:
- Initial block reward: 50 EVMORE
- Halving interval: Every 210,000 blocks (approximately 4 years with 10-minute blocks)
- Total supply cap: 21 million EVMORE
- Block target time: 10 minutes
- Difficulty adjustment: Every 2016 blocks (approximately 2 weeks)

Difficulty Adjustment:
- Measured every 2016 blocks
- Target block time: 10 minutes
- New difficulty = Current difficulty * (Actual time for last 2016 blocks / Expected time)
- Maximum adjustment: 4x up or down per period