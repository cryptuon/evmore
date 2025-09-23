# @title Wrapped EVMORE (wEVMORE) - Polygon Contract
# @notice ERC-20 wrapped EVMORE for Polygon network (Stage 2)
# @dev Simple wrapped token with bridge integration

# SPDX-License-Identifier: MIT

implements: ERC20

# ERC-20 standard events
event Transfer:
    sender: indexed(address)
    receiver: indexed(address)
    value: uint256

event Approval:
    owner: indexed(address)
    spender: indexed(address)
    value: uint256

# Bridge-specific events
event BridgeMint:
    recipient: indexed(address)
    amount: uint256
    ethereum_tx_hash: indexed(bytes32)

event BridgeBurn:
    sender: indexed(address)
    amount: uint256
    ethereum_recipient: address

# Token state
name: public(String[32])
symbol: public(String[32])
decimals: public(uint8)
totalSupply: public(uint256)
balanceOf: public(HashMap[address, uint256])
allowance: public(HashMap[address, HashMap[address, uint256]])

# Bridge state
bridge_operator: address
owner: address
bridge_active: bool

# Bridge statistics
total_minted: uint256
total_burned: uint256
bridge_operations: uint256

# Rate limiting for safety
daily_mint_limit: uint256
daily_burn_limit: uint256
daily_mints: HashMap[uint256, uint256]  # day -> amount
daily_burns: HashMap[uint256, uint256]  # day -> amount

# Constants
SECONDS_PER_DAY: constant(uint256) = 86400

@external
def __init__():
    """Initialize wrapped EVMORE on Polygon"""
    self.name = "Wrapped EVMORE"
    self.symbol = "wEVMORE"
    self.decimals = 18
    self.totalSupply = 0

    self.owner = msg.sender
    self.bridge_operator = msg.sender
    self.bridge_active = False

    # Conservative limits for Stage 2
    self.daily_mint_limit = 50000 * 10**18   # 50K wEVMORE daily mint limit
    self.daily_burn_limit = 50000 * 10**18   # 50K wEVMORE daily burn limit

@external
def activateBridge():
    """Activate bridge functionality (owner only)"""
    assert msg.sender == self.owner, "Only owner"
    assert not self.bridge_active, "Bridge already active"

    self.bridge_active = True

@external
def setBridgeOperator(new_operator: address):
    """Set bridge operator (owner only)"""
    assert msg.sender == self.owner, "Only owner"
    assert new_operator != empty(address), "Invalid operator"

    self.bridge_operator = new_operator

@external
def bridgeMint(
    recipient: address,
    amount: uint256,
    ethereum_tx_hash: bytes32
):
    """Mint wEVMORE when bridged from Ethereum (operator only)"""
    assert msg.sender == self.bridge_operator, "Only bridge operator"
    assert self.bridge_active, "Bridge not active"
    assert recipient != empty(address), "Invalid recipient"
    assert amount > 0, "Invalid amount"

    # Check daily limits
    today: uint256 = block.timestamp / SECONDS_PER_DAY
    daily_mints_today: uint256 = self.daily_mints[today]
    assert daily_mints_today + amount <= self.daily_mint_limit, "Daily mint limit exceeded"

    # Mint tokens
    self.totalSupply += amount
    self.balanceOf[recipient] += amount
    self.total_minted += amount
    self.bridge_operations += 1
    self.daily_mints[today] += amount

    log Transfer(empty(address), recipient, amount)
    log BridgeMint(recipient, amount, ethereum_tx_hash)

@external
def bridgeBurn(amount: uint256, ethereum_recipient: address):
    """Burn wEVMORE to bridge back to Ethereum"""
    assert self.bridge_active, "Bridge not active"
    assert amount > 0, "Invalid amount"
    assert self.balanceOf[msg.sender] >= amount, "Insufficient balance"
    assert ethereum_recipient != empty(address), "Invalid recipient"

    # Check daily limits
    today: uint256 = block.timestamp / SECONDS_PER_DAY
    daily_burns_today: uint256 = self.daily_burns[today]
    assert daily_burns_today + amount <= self.daily_burn_limit, "Daily burn limit exceeded"

    # Burn tokens
    self.balanceOf[msg.sender] -= amount
    self.totalSupply -= amount
    self.total_burned += amount
    self.bridge_operations += 1
    self.daily_burns[today] += amount

    log Transfer(msg.sender, empty(address), amount)
    log BridgeBurn(msg.sender, amount, ethereum_recipient)

@external
def updateLimits(mint_limit: uint256, burn_limit: uint256):
    """Update daily limits (owner only)"""
    assert msg.sender == self.owner, "Only owner"

    self.daily_mint_limit = mint_limit
    self.daily_burn_limit = burn_limit

@external
def emergencyPause():
    """Emergency pause bridge (owner or operator)"""
    assert msg.sender == self.owner or msg.sender == self.bridge_operator, "Not authorized"

    self.bridge_active = False

@external
def emergencyUnpause():
    """Resume bridge operations (owner only)"""
    assert msg.sender == self.owner, "Only owner"

    self.bridge_active = True

# Standard ERC-20 functions

@external
def transfer(recipient: address, amount: uint256) -> bool:
    """Transfer wEVMORE tokens"""
    assert recipient != empty(address), "Invalid recipient"
    assert self.balanceOf[msg.sender] >= amount, "Insufficient balance"

    self.balanceOf[msg.sender] -= amount
    self.balanceOf[recipient] += amount

    log Transfer(msg.sender, recipient, amount)
    return True

@external
def transferFrom(sender: address, recipient: address, amount: uint256) -> bool:
    """Transfer wEVMORE tokens from approved account"""
    assert sender != empty(address), "Invalid sender"
    assert recipient != empty(address), "Invalid recipient"
    assert self.balanceOf[sender] >= amount, "Insufficient balance"
    assert self.allowance[sender][msg.sender] >= amount, "Insufficient allowance"

    self.balanceOf[sender] -= amount
    self.balanceOf[recipient] += amount
    self.allowance[sender][msg.sender] -= amount

    log Transfer(sender, recipient, amount)
    return True

@external
def approve(spender: address, amount: uint256) -> bool:
    """Approve spender to transfer tokens"""
    assert spender != empty(address), "Invalid spender"

    self.allowance[msg.sender][spender] = amount

    log Approval(msg.sender, spender, amount)
    return True

@external
def transferOwnership(new_owner: address):
    """Transfer contract ownership"""
    assert msg.sender == self.owner, "Only owner"
    assert new_owner != empty(address), "Invalid owner"

    self.owner = new_owner

# View functions

@view
@external
def getBridgeStats() -> (uint256, uint256, uint256, bool):
    """Get bridge statistics (minted, burned, operations, active)"""
    return (self.total_minted, self.total_burned, self.bridge_operations, self.bridge_active)

@view
@external
def getDailyLimits() -> (uint256, uint256):
    """Get daily mint and burn limits"""
    return (self.daily_mint_limit, self.daily_burn_limit)

@view
@external
def getDailyUsage() -> (uint256, uint256):
    """Get today's mint and burn usage"""
    today: uint256 = block.timestamp / SECONDS_PER_DAY
    return (self.daily_mints[today], self.daily_burns[today])

@view
@external
def getContractInfo() -> (address, address, bool):
    """Get contract info (owner, operator, active)"""
    return (self.owner, self.bridge_operator, self.bridge_active)