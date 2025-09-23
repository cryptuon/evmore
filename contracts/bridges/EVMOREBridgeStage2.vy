# @title EVMORE Stage 2 Bridge Contract
# @notice Simple manual bridge for Polygon deployment when treasury reaches 1K EVMORE
# @dev Simplified security model for Stage 2, upgradeable to Stage 3

# SPDX-License-Identifier: MIT

interface IEVMOREToken:
    def balanceOf(user: address) -> uint256: view
    def transferFrom(from_: address, to: address, amount: uint256) -> bool: nonpayable
    def bridgeMint(to: address, amount: uint256): nonpayable
    def bridgeBurn(from_: address, amount: uint256): nonpayable

struct BridgeRequest:
    user: address
    amount: uint256
    timestamp: uint256
    nonce: uint256
    processed: bool
    bridge_direction: uint8  # 0 = to Polygon, 1 = from Polygon

# Contract state
evmore_token: IEVMOREToken
owner: address
bridge_operator: address
bridge_active: bool

# Bridge state
bridge_requests: HashMap[bytes32, BridgeRequest]
total_bridged_to_polygon: uint256
total_bridged_from_polygon: uint256
requests_count: uint256

# Stage 2 security settings (conservative)
min_bridge_amount: uint256
max_bridge_amount: uint256
daily_limit: uint256
withdrawal_delay: uint256
bridge_fee_rate: uint256  # in basis points

# Rate limiting
daily_volume: HashMap[uint256, uint256]  # day -> volume
user_daily_volume: HashMap[address, HashMap[uint256, uint256]]  # user -> day -> volume

# Events
event BridgeToPolygon:
    user: indexed(address)
    amount: uint256
    fee: uint256
    request_id: indexed(bytes32)
    nonce: uint256

event BridgeFromPolygon:
    user: indexed(address)
    amount: uint256
    request_id: indexed(bytes32)
    polygon_tx_hash: indexed(bytes32)

event BridgeActivated:
    activated_by: indexed(address)
    timestamp: uint256

event BridgeOperatorChanged:
    old_operator: indexed(address)
    new_operator: indexed(address)

event BridgeConfigUpdated:
    updated_by: indexed(address)
    timestamp: uint256

# Constants
SECONDS_PER_DAY: constant(uint256) = 86400
BASIS_POINTS: constant(uint256) = 10000

@external
def __init__(evmore_token_address: address):
    """Initialize Stage 2 bridge (inactive until activated)"""
    self.evmore_token = IEVMOREToken(evmore_token_address)
    self.owner = msg.sender
    self.bridge_operator = msg.sender  # Initially same as owner
    self.bridge_active = False

    # Conservative Stage 2 limits
    self.min_bridge_amount = 1 * 10**18        # 1 EVMORE minimum
    self.max_bridge_amount = 10000 * 10**18    # 10K EVMORE maximum
    self.daily_limit = 50000 * 10**18          # 50K EVMORE daily limit
    self.withdrawal_delay = 3600               # 1 hour delay
    self.bridge_fee_rate = 20                  # 0.2% fee

@external
def activateBridge():
    """Activate bridge functionality (owner only)"""
    assert msg.sender == self.owner, "Only owner"
    assert not self.bridge_active, "Bridge already active"

    self.bridge_active = True
    log BridgeActivated(msg.sender, block.timestamp)

@external
def setBridgeOperator(new_operator: address):
    """Set bridge operator for manual processing (owner only)"""
    assert msg.sender == self.owner, "Only owner"
    assert new_operator != empty(address), "Invalid operator"

    old_operator: address = self.bridge_operator
    self.bridge_operator = new_operator

    log BridgeOperatorChanged(old_operator, new_operator)

@external
def updateBridgeConfig(
    min_amount: uint256,
    max_amount: uint256,
    daily_limit_new: uint256,
    delay: uint256,
    fee_rate: uint256
):
    """Update bridge configuration (owner only)"""
    assert msg.sender == self.owner, "Only owner"
    assert min_amount > 0, "Invalid min amount"
    assert max_amount > min_amount, "Invalid max amount"
    assert fee_rate <= 1000, "Fee too high (max 10%)"  # 10% max fee
    assert delay <= 86400, "Delay too long (max 24h)"

    self.min_bridge_amount = min_amount
    self.max_bridge_amount = max_amount
    self.daily_limit = daily_limit_new
    self.withdrawal_delay = delay
    self.bridge_fee_rate = fee_rate

    log BridgeConfigUpdated(msg.sender, block.timestamp)

@external
def bridgeToPolygon(amount: uint256) -> bytes32:
    """Bridge EVMORE from Ethereum to Polygon"""
    assert self.bridge_active, "Bridge not active"
    assert amount >= self.min_bridge_amount, "Amount below minimum"
    assert amount <= self.max_bridge_amount, "Amount exceeds maximum"

    # Check daily limits
    today: uint256 = block.timestamp / SECONDS_PER_DAY
    daily_vol: uint256 = self.daily_volume[today]
    user_daily_vol: uint256 = self.user_daily_volume[msg.sender][today]

    assert daily_vol + amount <= self.daily_limit, "Daily limit exceeded"
    assert user_daily_vol + amount <= self.daily_limit / 10, "User daily limit exceeded"  # 10% per user

    # Calculate bridge fee
    fee_amount: uint256 = amount * self.bridge_fee_rate / BASIS_POINTS
    bridge_amount: uint256 = amount - fee_amount

    # Transfer tokens to bridge (includes fee)
    success: bool = self.evmore_token.transferFrom(msg.sender, self, amount)
    assert success, "Token transfer failed"

    # Burn the bridge amount (fee stays in contract as revenue)
    self.evmore_token.bridgeBurn(self, bridge_amount)

    # Generate request ID
    self.requests_count += 1
    request_id: bytes32 = keccak256(concat(
        convert(msg.sender, bytes32),
        convert(bridge_amount, bytes32),
        convert(block.timestamp, bytes32),
        convert(self.requests_count, bytes32)
    ))

    # Record bridge request
    self.bridge_requests[request_id] = BridgeRequest({
        user: msg.sender,
        amount: bridge_amount,
        timestamp: block.timestamp,
        nonce: self.requests_count,
        processed: False,
        bridge_direction: 0  # To Polygon
    })

    # Update volumes
    self.total_bridged_to_polygon += bridge_amount
    self.daily_volume[today] += amount
    self.user_daily_volume[msg.sender][today] += amount

    log BridgeToPolygon(msg.sender, bridge_amount, fee_amount, request_id, self.requests_count)
    return request_id

@external
def processPolygonMint(
    user: address,
    amount: uint256,
    ethereum_request_id: bytes32
) -> bytes32:
    """Process mint on Polygon (operator only) - called after manual verification"""
    assert msg.sender == self.bridge_operator, "Only bridge operator"
    assert self.bridge_active, "Bridge not active"

    # Verify the Ethereum request exists and is unprocessed
    request: BridgeRequest = self.bridge_requests[ethereum_request_id]
    assert request.user == user, "User mismatch"
    assert request.amount == amount, "Amount mismatch"
    assert not request.processed, "Request already processed"
    assert request.bridge_direction == 0, "Invalid direction"

    # Check withdrawal delay
    assert block.timestamp >= request.timestamp + self.withdrawal_delay, "Withdrawal delay not met"

    # Mark as processed
    self.bridge_requests[ethereum_request_id].processed = True

    # This would trigger Polygon mint in production
    # For Stage 2, emit event for off-chain processing
    return ethereum_request_id

@external
def bridgeFromPolygon(
    user: address,
    amount: uint256,
    polygon_tx_hash: bytes32
) -> bytes32:
    """Process bridge from Polygon to Ethereum (operator only)"""
    assert msg.sender == self.bridge_operator, "Only bridge operator"
    assert self.bridge_active, "Bridge not active"
    assert amount >= self.min_bridge_amount, "Amount below minimum"
    assert amount <= self.max_bridge_amount, "Amount exceeds maximum"

    # Generate request ID for return bridge
    self.requests_count += 1
    request_id: bytes32 = keccak256(concat(
        convert(user, bytes32),
        convert(amount, bytes32),
        polygon_tx_hash,
        convert(self.requests_count, bytes32)
    ))

    # Record bridge request
    self.bridge_requests[request_id] = BridgeRequest({
        user: user,
        amount: amount,
        timestamp: block.timestamp,
        nonce: self.requests_count,
        processed: True,  # Already processed on Polygon
        bridge_direction: 1  # From Polygon
    })

    # Mint EVMORE on Ethereum
    self.evmore_token.bridgeMint(user, amount)

    # Update statistics
    self.total_bridged_from_polygon += amount

    log BridgeFromPolygon(user, amount, request_id, polygon_tx_hash)
    return request_id

@external
def emergencyPause():
    """Emergency pause bridge operations (owner or operator)"""
    assert msg.sender == self.owner or msg.sender == self.bridge_operator, "Not authorized"

    self.bridge_active = False

@external
def emergencyUnpause():
    """Resume bridge operations (owner only)"""
    assert msg.sender == self.owner, "Only owner"

    self.bridge_active = True

@external
def withdrawFees():
    """Withdraw accumulated bridge fees (owner only)"""
    assert msg.sender == self.owner, "Only owner"

    fee_balance: uint256 = self.evmore_token.balanceOf(self)
    if fee_balance > 0:
        self.evmore_token.transferFrom(self, self.owner, fee_balance)

@external
def transferOwnership(new_owner: address):
    """Transfer ownership (two-step process would be added in production)"""
    assert msg.sender == self.owner, "Only owner"
    assert new_owner != empty(address), "Invalid owner"

    self.owner = new_owner

# View functions

@view
@external
def getBridgeRequest(request_id: bytes32) -> BridgeRequest:
    """Get bridge request details"""
    return self.bridge_requests[request_id]

@view
@external
def getBridgeStats() -> (uint256, uint256, uint256, bool):
    """Get bridge statistics (to_polygon, from_polygon, total_requests, active)"""
    return (
        self.total_bridged_to_polygon,
        self.total_bridged_from_polygon,
        self.requests_count,
        self.bridge_active
    )

@view
@external
def getBridgeConfig() -> (uint256, uint256, uint256, uint256, uint256):
    """Get bridge configuration (min, max, daily_limit, delay, fee_rate)"""
    return (
        self.min_bridge_amount,
        self.max_bridge_amount,
        self.daily_limit,
        self.withdrawal_delay,
        self.bridge_fee_rate
    )

@view
@external
def getDailyVolume() -> uint256:
    """Get current day bridge volume"""
    today: uint256 = block.timestamp / SECONDS_PER_DAY
    return self.daily_volume[today]

@view
@external
def getUserDailyVolume(user: address) -> uint256:
    """Get user's current day bridge volume"""
    today: uint256 = block.timestamp / SECONDS_PER_DAY
    return self.user_daily_volume[user][today]

@view
@external
def isBridgeActive() -> bool:
    """Check if bridge is active"""
    return self.bridge_active

@view
@external
def getContractInfo() -> (address, address, address):
    """Get contract addresses (token, owner, operator)"""
    return (self.evmore_token.address, self.owner, self.bridge_operator)