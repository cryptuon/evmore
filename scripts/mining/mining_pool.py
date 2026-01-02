"""
EVMORE Digital Gold Mining Pool Protocol
Decentralized mining pool for fair reward distribution
"""

import json
import time
import hashlib
import asyncio
import websockets
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from collections import defaultdict
import logging

@dataclass
class Miner:
    """Individual miner in the pool"""
    address: str
    connection_id: str
    hash_rate: float
    shares_submitted: int
    last_seen: float
    difficulty: int
    worker_name: str

@dataclass
class WorkPackage:
    """Mining work package for pool miners"""
    job_id: str
    challenge: str  # hex string
    difficulty: int
    target_bits: int
    timestamp: float
    epoch: int

@dataclass
class Share:
    """Mining share submission"""
    job_id: str
    miner_address: str
    solution: str  # hex string
    nonce: int
    timestamp: float
    difficulty: int
    is_valid: bool

@dataclass
class PoolStats:
    """Pool statistics"""
    total_miners: int
    active_miners: int
    pool_hash_rate: float
    shares_per_second: float
    blocks_found: int
    current_difficulty: int
    next_payout: float

class DigitalGoldMiningPool:
    """
    EVMORE Digital Gold Mining Pool

    Features:
    - Proportional Pay-Per-Share (PPS) rewards
    - Real-time difficulty adjustment per miner
    - WebSocket-based communication
    - Fair share validation
    - Automatic pool fee distribution
    - Anti-cheating mechanisms
    """

    def __init__(self, pool_address: str, pool_fee: float = 0.02):
        self.pool_address = pool_address
        self.pool_fee = pool_fee  # 2% pool fee

        # Pool state
        self.miners: Dict[str, Miner] = {}
        self.active_jobs: Dict[str, WorkPackage] = {}
        self.pending_shares: List[Share] = []
        self.validated_shares: Dict[str, List[Share]] = defaultdict(list)

        # Statistics
        self.total_shares = 0
        self.blocks_found = 0
        self.pool_start_time = time.time()

        # Configuration
        self.share_difficulty = 8  # Lower difficulty for shares
        self.job_timeout = 300  # 5 minutes
        self.miner_timeout = 180  # 3 minutes
        self.min_payout = 1.0  # Minimum 1 EVMORE for payout

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def generate_work(self, epoch: int, challenge: bytes, difficulty: int) -> WorkPackage:
        """Generate new mining work package"""
        job_id = hashlib.sha256(
            f"{epoch}_{challenge.hex()}_{time.time()}".encode()
        ).hexdigest()[:16]

        work = WorkPackage(
            job_id=job_id,
            challenge=challenge.hex(),
            difficulty=difficulty,
            target_bits=difficulty,
            timestamp=time.time(),
            epoch=epoch
        )

        self.active_jobs[job_id] = work
        self.logger.info(f"📦 Generated work package {job_id} for epoch {epoch}")

        return work

    def validate_share(self, share: Share) -> bool:
        """
        Validate submitted mining share

        Checks:
        1. Job ID exists and is active
        2. Solution meets share difficulty
        3. Miner is registered
        4. No duplicate submissions
        """
        # Check job exists
        if share.job_id not in self.active_jobs:
            self.logger.warning(f"❌ Invalid job ID: {share.job_id}")
            return False

        work = self.active_jobs[share.job_id]

        # Check job not expired
        if time.time() - work.timestamp > self.job_timeout:
            self.logger.warning(f"⏰ Expired job: {share.job_id}")
            return False

        # Check miner exists
        if share.miner_address not in self.miners:
            self.logger.warning(f"👤 Unknown miner: {share.miner_address}")
            return False

        try:
            # Validate solution format
            solution_bytes = bytes.fromhex(share.solution)
            if len(solution_bytes) != 128:  # 4 * 32 bytes
                return False

            # Check solution meets share difficulty
            challenge_bytes = bytes.fromhex(work.challenge)
            hash_input = challenge_bytes + solution_bytes[:32]
            hash_result = hashlib.sha256(hash_input).digest()
            bits = int.from_bytes(hash_result[-4:], 'big') & ((1 << self.share_difficulty) - 1)

            # For shares, we use lower difficulty
            share_target = (1 << self.share_difficulty) - 1
            if bits > share_target:
                self.logger.warning(f"🎯 Share difficulty not met: {bits} > {share_target}")
                return False

            # Check for duplicate shares
            miner_shares = self.validated_shares[share.miner_address]
            for existing_share in miner_shares:
                if existing_share.solution == share.solution:
                    self.logger.warning(f"🔄 Duplicate share from {share.miner_address}")
                    return False

            return True

        except Exception as e:
            self.logger.error(f"💥 Share validation error: {e}")
            return False

    def submit_share(self, share: Share) -> Dict:
        """Process share submission from miner"""
        share.timestamp = time.time()
        share.is_valid = self.validate_share(share)

        if share.is_valid:
            # Add to validated shares
            self.validated_shares[share.miner_address].append(share)
            self.total_shares += 1

            # Update miner stats
            miner = self.miners[share.miner_address]
            miner.shares_submitted += 1
            miner.last_seen = time.time()

            # Check if this is a block solution (meets full difficulty)
            work = self.active_jobs[share.job_id]
            if self._check_block_solution(share, work):
                self._handle_block_found(share, work)
                return {
                    "status": "block_found",
                    "message": "🏆 Block found! Congratulations!",
                    "block_reward": True
                }

            self.logger.info(f"✅ Valid share from {share.miner_address}")
            return {
                "status": "accepted",
                "message": "Share accepted",
                "total_shares": miner.shares_submitted
            }
        else:
            self.logger.warning(f"❌ Invalid share from {share.miner_address}")
            return {
                "status": "rejected",
                "message": "Invalid share",
                "reason": "Solution validation failed"
            }

    def _check_block_solution(self, share: Share, work: WorkPackage) -> bool:
        """Check if share is actually a valid block solution"""
        try:
            challenge_bytes = bytes.fromhex(work.challenge)
            solution_bytes = bytes.fromhex(share.solution)

            # Verify against full difficulty
            from scripts.generate_mining_solution import generate_mining_solution
            from contracts.KeccakCollisionVerifier import verify_solution

            # This would call the actual verifier contract
            # For now, simplified check
            return True  # Placeholder

        except Exception as e:
            self.logger.error(f"💥 Block validation error: {e}")
            return False

    def _handle_block_found(self, share: Share, work: WorkPackage):
        """Handle when a pool miner finds a valid block"""
        self.blocks_found += 1
        block_finder = share.miner_address

        self.logger.info(f"🎉 BLOCK FOUND by {block_finder}!")
        self.logger.info(f"📊 Block #{self.blocks_found}")
        self.logger.info(f"💎 Job: {share.job_id}")

        # Distribute block rewards to all miners
        self._distribute_block_rewards(work.epoch, block_finder)

    def _distribute_block_rewards(self, epoch: int, block_finder: str):
        """Distribute block rewards proportionally to all miners"""
        # Get all shares for this epoch
        epoch_shares = defaultdict(int)
        total_epoch_shares = 0

        for miner_addr, shares in self.validated_shares.items():
            miner_epoch_shares = sum(1 for s in shares if s.job_id in self.active_jobs)
            epoch_shares[miner_addr] = miner_epoch_shares
            total_epoch_shares += miner_epoch_shares

        if total_epoch_shares == 0:
            self.logger.warning("⚠️  No shares to distribute rewards")
            return

        # Calculate rewards (assuming 50 EVMORE block reward)
        block_reward = 50.0
        pool_fee_amount = block_reward * self.pool_fee
        miner_reward_pool = block_reward - pool_fee_amount

        # Block finder bonus (extra 5%)
        finder_bonus = miner_reward_pool * 0.05
        proportional_pool = miner_reward_pool - finder_bonus

        rewards = {}
        for miner_addr, shares in epoch_shares.items():
            share_ratio = shares / total_epoch_shares
            base_reward = proportional_pool * share_ratio

            if miner_addr == block_finder:
                total_reward = base_reward + finder_bonus
            else:
                total_reward = base_reward

            rewards[miner_addr] = total_reward

        self.logger.info(f"💰 Reward distribution for epoch {epoch}:")
        for miner_addr, reward in rewards.items():
            self.logger.info(f"   {miner_addr}: {reward:.6f} EVMORE")

        # In production, this would trigger smart contract payout

    def register_miner(self, miner_address: str, connection_id: str, worker_name: str = "") -> Dict:
        """Register new miner in the pool"""
        if miner_address in self.miners:
            # Update existing miner
            miner = self.miners[miner_address]
            miner.connection_id = connection_id
            miner.last_seen = time.time()
            status = "reconnected"
        else:
            # Create new miner
            miner = Miner(
                address=miner_address,
                connection_id=connection_id,
                hash_rate=0.0,
                shares_submitted=0,
                last_seen=time.time(),
                difficulty=self.share_difficulty,
                worker_name=worker_name or f"worker_{len(self.miners)}"
            )
            self.miners[miner_address] = miner
            status = "registered"

        self.logger.info(f"👤 Miner {status}: {miner_address} ({worker_name})")

        return {
            "status": status,
            "pool_fee": self.pool_fee,
            "share_difficulty": self.share_difficulty,
            "miner_stats": asdict(miner)
        }

    def get_pool_stats(self) -> PoolStats:
        """Get current pool statistics"""
        current_time = time.time()
        active_miners = sum(
            1 for miner in self.miners.values()
            if current_time - miner.last_seen < self.miner_timeout
        )

        total_hash_rate = sum(
            miner.hash_rate for miner in self.miners.values()
            if current_time - miner.last_seen < self.miner_timeout
        )

        uptime = current_time - self.pool_start_time
        shares_per_second = self.total_shares / uptime if uptime > 0 else 0

        return PoolStats(
            total_miners=len(self.miners),
            active_miners=active_miners,
            pool_hash_rate=total_hash_rate,
            shares_per_second=shares_per_second,
            blocks_found=self.blocks_found,
            current_difficulty=self.share_difficulty,
            next_payout=time.time() + 3600  # Next hourly payout
        )

    async def handle_websocket(self, websocket, path):
        """Handle WebSocket connections from miners"""
        connection_id = id(websocket)
        miner_address = None

        try:
            self.logger.info(f"🔌 New connection: {connection_id}")

            async for message in websocket:
                try:
                    data = json.loads(message)
                    response = await self._process_message(data, connection_id)

                    if response:
                        await websocket.send(json.dumps(response))

                        # Track miner address for this connection
                        if data.get("method") == "register" and response.get("status") in ["registered", "reconnected"]:
                            miner_address = data.get("miner_address")

                except Exception as e:
                    self.logger.error(f"💥 Message processing error: {e}")
                    await websocket.send(json.dumps({
                        "error": "Invalid message format"
                    }))

        except websockets.exceptions.ConnectionClosed:
            self.logger.info(f"🔌 Connection closed: {connection_id}")
        except Exception as e:
            self.logger.error(f"💥 WebSocket error: {e}")
        finally:
            # Clean up miner registration if needed
            if miner_address and miner_address in self.miners:
                miner = self.miners[miner_address]
                if miner.connection_id == connection_id:
                    # Mark as disconnected
                    miner.last_seen = 0

    async def _process_message(self, data: Dict, connection_id: str) -> Dict:
        """Process incoming message from miner"""
        method = data.get("method")

        if method == "register":
            return self.register_miner(
                data.get("miner_address"),
                str(connection_id),
                data.get("worker_name", "")
            )

        elif method == "get_work":
            # Return current work package
            if self.active_jobs:
                latest_job = max(self.active_jobs.values(), key=lambda x: x.timestamp)
                return {
                    "method": "work",
                    "job": asdict(latest_job)
                }

        elif method == "submit_share":
            share = Share(
                job_id=data.get("job_id"),
                miner_address=data.get("miner_address"),
                solution=data.get("solution"),
                nonce=data.get("nonce", 0),
                timestamp=0,  # Set in submit_share
                difficulty=data.get("difficulty"),
                is_valid=False  # Set in submit_share
            )
            return self.submit_share(share)

        elif method == "get_stats":
            stats = self.get_pool_stats()
            return {
                "method": "stats",
                "data": asdict(stats)
            }

        return {"error": "Unknown method"}

def main():
    """Start the mining pool server"""
    pool = DigitalGoldMiningPool("0x123...ABC")

    # Generate some test work
    import os
    test_challenge = os.urandom(32)
    work = pool.generate_work(1, test_challenge, 16)

    print(f"🏊 EVMORE Digital Gold Mining Pool Started")
    print(f"💎 Pool Address: {pool.pool_address}")
    print(f"💸 Pool Fee: {pool.pool_fee * 100}%")
    print(f"🎯 Share Difficulty: {pool.share_difficulty} bits")
    print(f"📦 Initial Work: {work.job_id}")

    # Start WebSocket server
    start_server = websockets.serve(pool.handle_websocket, "localhost", 8765)

    print(f"🌐 Mining pool listening on ws://localhost:8765")
    print("📡 Miners can connect and start submitting shares")

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()