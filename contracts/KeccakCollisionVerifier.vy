# @version ^0.3.10
# SPDX-License-Identifier: MIT

############################################
# KeccakCollision Parameters
############################################
N: constant(uint256) = 16  # Number of bits that must match
K: constant(uint256) = 4   # Number of values needed
SOLUTION_SIZE: constant(uint256) = 128  # K * 32 bytes

############################################
# Main Verification Function
############################################
@external
@view
def verify_solution(
    challenge: bytes32,
    solution: Bytes[128],  # K * 32 bytes
    difficulty: uint256
) -> bool:
    """
    @notice Verifies a KeccakCollision solution
    @param challenge Current mining challenge
    @param solution Raw solution bytes (K * 32-byte values)
    @param difficulty Current mining difficulty
    @return True if solution is valid
    """
    values: DynArray[bytes32, 4] = []
    
    # Parse each 32-byte value
    for i in range(K):
        start_pos: uint256 = i * 32
        # Extract the full 32-byte value
        value: bytes32 = convert(slice(solution, start_pos, 32), bytes32)
        values.append(value)
        
        # Check ascending order
        if i > 0:
            if convert(values[i], uint256) <= convert(values[i-1], uint256):
                return False
    
    # Create bit mask for matching (optimized for common difficulties)
    mask: uint256 = 0
    if difficulty <= 32:
        mask = shift(1, difficulty) - 1
    else:
        # For higher difficulties, compute dynamically
        mask = MAX_UINT256 >> (256 - difficulty)
    
    # Calculate hashes and verify bit matches
    first_hash: uint256 = 0
    
    for i in range(K):
        hash: bytes32 = keccak256(concat(challenge, values[i]))
        bits: uint256 = convert(hash, uint256) & mask
        
        if i == 0:
            first_hash = bits
        elif bits != first_hash:
            return False
            
    return True
