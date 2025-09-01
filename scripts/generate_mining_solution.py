import random
from eth_hash.auto import keccak
from typing import List

def generate_mining_solution(challenge: bytes, difficulty: int, k_values: int = 4) -> bytes:
    """
    Generate a KeccakCollision mining solution
    
    Args:
        challenge: The current mining challenge bytes
        difficulty: Number of bits that must match
        k_values: Number of values needed for solution (default 4)
        
    Returns:
        bytes: Concatenated solution values in ascending order
    
    The solution must satisfy:
    1. All k_values produce the same difficulty least significant bits when hashed with challenge
    2. The values must be in strictly ascending order
    """
    if not isinstance(challenge, bytes) or len(challenge) != 32:
        raise ValueError("Challenge must be 32 bytes")
    
    mask = (1 << difficulty) - 1
    
    solutions: List[bytes] = []
    target_bits = None
    attempts = 0
    max_attempts = 10000000  # Increased attempts for better success rate
    
    while len(solutions) < k_values and attempts < max_attempts:
        attempts += 1
        candidate = random.randbytes(32)
        
        hash_input = challenge + candidate
        hash_result = keccak(hash_input)
        bits = int.from_bytes(hash_result, 'big') & mask
        
        if target_bits is None:
            target_bits = bits
            solutions.append(candidate)
        elif bits == target_bits:
            # Check if candidate would maintain ascending order
            candidate_int = int.from_bytes(candidate, 'big')
            # Find the correct position to insert to maintain ascending order
            insert_pos = len(solutions)
            for i, existing in enumerate(solutions):
                if candidate_int < int.from_bytes(existing, 'big'):
                    insert_pos = i
                    break
                elif candidate_int == int.from_bytes(existing, 'big'):
                    # Duplicate value, skip it
                    insert_pos = -1
                    break
            
            if insert_pos >= 0:
                # Insert at the correct position to maintain ascending order
                if insert_pos == len(solutions):
                    solutions.append(candidate)
                else:
                    solutions.insert(insert_pos, candidate)
    
    if len(solutions) < k_values:
        raise RuntimeError(f"Failed to find solution after {max_attempts} attempts")
        
    return b''.join(solutions)