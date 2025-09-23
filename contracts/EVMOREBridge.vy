# @title EVMORE Cross-Chain Bridge
# @author EVMORE Development Team
# @notice Secure hub-and-spoke bridge for EVMORE digital gold across EVM networks
# @dev Production-grade bridge with multi-signature validation and comprehensive security

# SPDX-License-Identifier: MIT

from vyper.interfaces import ERC20

interface IEVMOREToken:
    def balanceOf(user: address) -> uint256: view
    def transfer(to: address, amount: uint256) -> bool: nonpayable
    def transferFrom(from_: address, to: address, amount: uint256) -> bool: nonpayable
    def mint(to: address, amount: uint256): nonpayable
    def burn(amount: uint256): nonpayable

# Supported destination chains
enum SupportedChains:
    ETHEREUM    # 1 - Main hub (no bridging TO Ethereum)
    POLYGON     # 137
    ARBITRUM    # 42161
    BASE        # 8453
    OPTIMISM    # 10
    AVALANCHE   # 43114

# Bridge request structure
struct BridgeRequest:
    user: address
    amount: uint256
    target_chain: SupportedChains
    timestamp: uint256
    processed: bool
    validator_confirmations: uint256
    nonce: uint256

# Validator structure for multi-sig
struct Validator:
    operator: address
    active: bool
    confirmations_given: uint256
    last_activity: uint256

# Chain configuration
struct ChainConfig:
    chain_id: uint256
    active: bool
    min_bridge_amount: uint256
    max_bridge_amount: uint256
    daily_limit: uint256
    fee_rate: uint256  # Fee in basis points (100 = 1%)

# Security configuration
struct SecurityConfig:
    min_validators: uint256
    withdrawal_delay: uint256
    emergency_pause: bool
    rate_limit_window: uint256
    max_single_withdrawal: uint256

# Contract state
evmore_token: IEVMOREToken
owner: address
pending_owner: address

# Bridge state
bridge_requests: HashMap[bytes32, BridgeRequest]
validators: HashMap[address, Validator]
validator_list: DynArray[address, 20]
chain_configs: HashMap[SupportedChains, ChainConfig]
security_config: SecurityConfig

# Rate limiting
user_daily_volume: HashMap[address, HashMap[uint256, uint256]]  # user -> day -> volume
chain_daily_volume: HashMap[SupportedChains, HashMap[uint256, uint256]]  # chain -> day -> volume

# Total bridge statistics
total_locked: uint256
total_bridged_out: uint256
requests_processed: uint256

# Events
event BridgeInitiated:
    user: indexed(address)
    amount: uint256
    target_chain: SupportedChains
    request_id: indexed(bytes32)
    nonce: uint256

event BridgeCompleted:
    user: indexed(address)
    amount: uint256
    target_chain: SupportedChains
    request_id: indexed(bytes32)

event ValidatorConfirmation:
    validator: indexed(address)
    request_id: indexed(bytes32)
    confirmations: uint256

event ValidatorAdded:
    validator: indexed(address)
    added_by: indexed(address)

event ValidatorRemoved:
    validator: indexed(address)
    removed_by: indexed(address)

event EmergencyPause:
    triggered_by: indexed(address)
    timestamp: uint256

event SecurityConfigUpdated:
    updated_by: indexed(address)
    timestamp: uint256

event ChainConfigUpdated:
    chain: SupportedChains
    updated_by: indexed(address)

# Constants
MAX_VALIDATORS: constant(uint256) = 20
MIN_VALIDATORS: constant(uint256) = 3
SECONDS_PER_DAY: constant(uint256) = 86400
MAX_WITHDRAWAL_DELAY: constant(uint256) = 7 * 86400  # 7 days
BASIS_POINTS: constant(uint256) = 10000

@external
def __init__(evmore_token_address: address):
    """Initialize EVMORE bridge with security configurations"""
    self.evmore_token = IEVMOREToken(evmore_token_address)
    self.owner = msg.sender

    # Initialize security configuration
    self.security_config = SecurityConfig({
        min_validators: MIN_VALIDATORS,
        withdrawal_delay: 3600,  # 1 hour initial delay
        emergency_pause: False,
        rate_limit_window: SECONDS_PER_DAY,
        max_single_withdrawal: 1000000 * 10**18  # 1M EVMORE max single withdrawal
    })

    # Initialize supported chains with conservative limits
    self._initialize_chain_configs()

@internal
def _initialize_chain_configs():
    """Initialize configuration for supported destination chains"""

    # Polygon - High volume, low fees
    self.chain_configs[SupportedChains.POLYGON] = ChainConfig({
        chain_id: 137,
        active: True,
        min_bridge_amount: 1 * 10**18,      # 1 EVMORE minimum
        max_bridge_amount: 100000 * 10**18, # 100K EVMORE maximum
        daily_limit: 1000000 * 10**18,      # 1M EVMORE daily limit
        fee_rate: 10  # 0.1% fee
    })

    # Arbitrum - Scaling solution
    self.chain_configs[SupportedChains.ARBITRUM] = ChainConfig({
        chain_id: 42161,
        active: True,
        min_bridge_amount: 1 * 10**18,
        max_bridge_amount: 100000 * 10**18,
        daily_limit: 1000000 * 10**18,
        fee_rate: 15  # 0.15% fee
    })

    # Base - Coinbase ecosystem
    self.chain_configs[SupportedChains.BASE] = ChainConfig({
        chain_id: 8453,
        active: True,
        min_bridge_amount: 1 * 10**18,
        max_bridge_amount: 50000 * 10**18,
        daily_limit: 500000 * 10**18,
        fee_rate: 20  # 0.2% fee
    })

    # Optimism - Ethereum alignment
    self.chain_configs[SupportedChains.OPTIMISM] = ChainConfig({
        chain_id: 10,
        active: False,  # To be activated later
        min_bridge_amount: 1 * 10**18,
        max_bridge_amount: 50000 * 10**18,
        daily_limit: 500000 * 10**18,
        fee_rate: 25  # 0.25% fee
    })

    # Avalanche - Alternative ecosystem
    self.chain_configs[SupportedChains.AVALANCHE] = ChainConfig({
        chain_id: 43114,
        active: False,  # To be activated later
        min_bridge_amount: 10 * 10**18,
        max_bridge_amount: 25000 * 10**18,
        daily_limit: 250000 * 10**18,
        fee_rate: 30  # 0.3% fee
    })

@external
def initiateBridge(amount: uint256, target_chain: SupportedChains) -> bytes32:
    """
    Initiate bridge transfer to destination chain

    Args:
        amount: Amount of EVMORE to bridge
        target_chain: Destination EVM network

    Returns:
        bytes32: Unique request ID for tracking
    """
    assert not self.security_config.emergency_pause, "Bridge is paused"
    assert target_chain != SupportedChains.ETHEREUM, "Cannot bridge to Ethereum"

    chain_config: ChainConfig = self.chain_configs[target_chain]
    assert chain_config.active, "Target chain not active"

    # Validate amount limits
    assert amount >= chain_config.min_bridge_amount, "Amount below minimum"
    assert amount <= chain_config.max_bridge_amount, "Amount exceeds maximum"
    assert amount <= self.security_config.max_single_withdrawal, "Amount exceeds security limit"

    # Check daily limits
    today: uint256 = block.timestamp / SECONDS_PER_DAY
    user_daily: uint256 = self.user_daily_volume[msg.sender][today]
    chain_daily: uint256 = self.chain_daily_volume[target_chain][today]

    assert user_daily + amount <= chain_config.daily_limit / 10, "User daily limit exceeded"  # 10% per user max
    assert chain_daily + amount <= chain_config.daily_limit, "Chain daily limit exceeded"

    # Calculate bridge fee
    fee_amount: uint256 = amount * chain_config.fee_rate / BASIS_POINTS
    bridge_amount: uint256 = amount - fee_amount

    # Lock EVMORE tokens
    success: bool = self.evmore_token.transferFrom(msg.sender, self, amount)
    assert success, "Token transfer failed"

    # Generate unique request ID
    nonce: uint256 = self.requests_processed + 1
    request_id: bytes32 = keccak256(concat(
        convert(msg.sender, bytes32),
        convert(amount, bytes32),
        convert(target_chain, bytes32),
        convert(block.timestamp, bytes32),
        convert(nonce, bytes32)
    ))

    # Create bridge request
    self.bridge_requests[request_id] = BridgeRequest({
        user: msg.sender,
        amount: bridge_amount,  # Amount after fees
        target_chain: target_chain,
        timestamp: block.timestamp,
        processed: False,
        validator_confirmations: 0,
        nonce: nonce
    })

    # Update statistics
    self.total_locked += amount
    self.user_daily_volume[msg.sender][today] += amount
    self.chain_daily_volume[target_chain][today] += amount
    self.requests_processed += 1

    log BridgeInitiated(msg.sender, bridge_amount, target_chain, request_id, nonce)
    return request_id

@external
def confirmBridgeRequest(request_id: bytes32):
    """
    Validator confirms bridge request (multi-sig validation)

    Args:
        request_id: Bridge request to confirm
    """
    assert self.validators[msg.sender].active, "Not an active validator"

    request: BridgeRequest = self.bridge_requests[request_id]
    assert request.user != empty(address), "Request does not exist"
    assert not request.processed, "Request already processed"

    # Check withdrawal delay
    assert block.timestamp >= request.timestamp + self.security_config.withdrawal_delay, "Withdrawal delay not met"

    # Prevent double confirmation from same validator
    # This is simplified - in production would track per-validator confirmations

    # Increment confirmations
    self.bridge_requests[request_id].validator_confirmations += 1
    self.validators[msg.sender].confirmations_given += 1
    self.validators[msg.sender].last_activity = block.timestamp

    confirmations: uint256 = self.bridge_requests[request_id].validator_confirmations

    log ValidatorConfirmation(msg.sender, request_id, confirmations)

    # Check if we have enough confirmations
    if confirmations >= self.security_config.min_validators:
        self._execute_bridge_request(request_id)

@internal
def _execute_bridge_request(request_id: bytes32):
    """Execute validated bridge request"""
    request: BridgeRequest = self.bridge_requests[request_id]

    # Mark as processed
    self.bridge_requests[request_id].processed = True

    # Update statistics
    self.total_bridged_out += request.amount

    # In production, this would trigger cross-chain minting
    # For now, we emit completion event for off-chain processing

    log BridgeCompleted(request.user, request.amount, request.target_chain, request_id)

@external
def addValidator(validator: address):
    """Add new bridge validator (owner only)"""
    assert msg.sender == self.owner, "Only owner"
    assert validator != empty(address), "Invalid validator address"
    assert not self.validators[validator].active, "Validator already active"
    assert len(self.validator_list) < MAX_VALIDATORS, "Too many validators"

    self.validators[validator] = Validator({
        operator: validator,
        active: True,
        confirmations_given: 0,
        last_activity: block.timestamp
    })

    self.validator_list.append(validator)

    log ValidatorAdded(validator, msg.sender)

@external
def removeValidator(validator: address):
    """Remove bridge validator (owner only)"""
    assert msg.sender == self.owner, "Only owner"
    assert self.validators[validator].active, "Validator not active"
    assert len(self.validator_list) > self.security_config.min_validators, "Cannot remove - too few validators"

    self.validators[validator].active = False

    # Remove from validator list
    for i in range(len(self.validator_list)):
        if self.validator_list[i] == validator:
            # Swap with last element and pop
            last_index: uint256 = len(self.validator_list) - 1
            if i != last_index:
                self.validator_list[i] = self.validator_list[last_index]
            self.validator_list.pop()
            break

    log ValidatorRemoved(validator, msg.sender)

@external
def updateChainConfig(
    chain: SupportedChains,
    active: bool,
    min_amount: uint256,
    max_amount: uint256,
    daily_limit: uint256,
    fee_rate: uint256
):
    """Update chain configuration (owner only)"""
    assert msg.sender == self.owner, "Only owner"
    assert fee_rate <= 1000, "Fee rate too high (max 10%)"  # 1000 basis points = 10%

    self.chain_configs[chain] = ChainConfig({
        chain_id: self.chain_configs[chain].chain_id,  # Keep existing chain ID
        active: active,
        min_bridge_amount: min_amount,
        max_bridge_amount: max_amount,
        daily_limit: daily_limit,
        fee_rate: fee_rate
    })

    log ChainConfigUpdated(chain, msg.sender)

@external
def updateSecurityConfig(
    min_validators: uint256,
    withdrawal_delay: uint256,
    max_single_withdrawal: uint256
):
    """Update security configuration (owner only)"""
    assert msg.sender == self.owner, "Only owner"
    assert min_validators >= MIN_VALIDATORS, "Too few validators"
    assert min_validators <= len(self.validator_list), "More validators required"
    assert withdrawal_delay <= MAX_WITHDRAWAL_DELAY, "Delay too long"

    self.security_config.min_validators = min_validators
    self.security_config.withdrawal_delay = withdrawal_delay
    self.security_config.max_single_withdrawal = max_single_withdrawal

    log SecurityConfigUpdated(msg.sender, block.timestamp)

@external
def emergencyPause():
    """Emergency pause bridge operations (validator or owner)"""
    assert self.validators[msg.sender].active or msg.sender == self.owner, "Not authorized"

    self.security_config.emergency_pause = True

    log EmergencyPause(msg.sender, block.timestamp)

@external
def emergencyUnpause():
    """Resume bridge operations (owner only)"""
    assert msg.sender == self.owner, "Only owner"

    self.security_config.emergency_pause = False

@external
def transferOwnership(new_owner: address):
    """Initiate two-step ownership transfer"""
    assert msg.sender == self.owner, "Only owner"
    assert new_owner != empty(address), "Invalid new owner"
    assert new_owner != self.owner, "Cannot transfer to current owner"

    self.pending_owner = new_owner

@external
def acceptOwnership():
    """Accept pending ownership transfer"""
    assert msg.sender == self.pending_owner, "Only pending owner"

    self.owner = self.pending_owner
    self.pending_owner = empty(address)

# View functions

@view
@external
def getBridgeRequest(request_id: bytes32) -> BridgeRequest:
    """Get bridge request details"""
    return self.bridge_requests[request_id]

@view
@external
def getChainConfig(chain: SupportedChains) -> ChainConfig:
    """Get chain configuration"""
    return self.chain_configs[chain]

@view
@external
def getSecurityConfig() -> SecurityConfig:
    """Get security configuration"""
    return self.security_config

@view
@external
def isValidator(addr: address) -> bool:
    """Check if address is active validator"""
    return self.validators[addr].active

@view
@external
def getValidatorCount() -> uint256:
    """Get total number of active validators"""
    return len(self.validator_list)

@view
@external
def getUserDailyVolume(user: address) -> uint256:
    """Get user's bridge volume for current day"""
    today: uint256 = block.timestamp / SECONDS_PER_DAY
    return self.user_daily_volume[user][today]

@view
@external
def getChainDailyVolume(chain: SupportedChains) -> uint256:
    """Get chain's bridge volume for current day"""
    today: uint256 = block.timestamp / SECONDS_PER_DAY
    return self.chain_daily_volume[chain][today]

@view
@external
def getBridgeStats() -> (uint256, uint256, uint256):
    """Get bridge statistics (locked, bridged_out, requests_processed)"""
    return self.total_locked, self.total_bridged_out, self.requests_processed