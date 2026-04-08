# Mining Guide

Complete guide to mining EVMORE digital gold, from beginner setup to advanced optimization.

## What is Mining?

Mining is the process of earning EVMORE by solving computational puzzles. It serves two purposes:
1. **Creating new EVMORE**: Miners earn rewards for valid solutions
2. **Securing the network**: Mining ensures fair token distribution

## How EVMORE Mining Works

### The KeccakCollision Algorithm

EVMORE uses a unique algorithm called KeccakCollision:

1. **Challenge**: The network provides a puzzle (derived from blockchain data)
2. **Search**: Miners look for 4 values that create matching hash patterns
3. **Submit**: Valid solutions are submitted to the blockchain
4. **Reward**: Successful miners earn EVMORE tokens

### Why KeccakCollision is Different

| Feature | Traditional Mining | EVMORE Mining |
|---------|-------------------|---------------|
| Hash type | Find leading zeros | Find collision patterns |
| Hardware | ASIC-dominated | GPU/CPU accessible |
| Memory | Low requirements | Memory-hard |
| Verification | Off-chain | On-chain smart contract |
| Fairness | Industrial advantage | Consumer hardware viable |

### Memory-Hard Design

The algorithm requires significant RAM bandwidth:
- Prevents ASIC development
- Makes GPUs and CPUs competitive
- Ensures decentralized participation
- Reduces energy waste

## Hardware Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|-------------|
| CPU | Intel i5 / AMD Ryzen 5 or equivalent |
| RAM | 8 GB DDR4 |
| Storage | 50 GB SSD |
| Internet | Stable broadband |
| OS | Windows 10+, Linux, macOS |

### Recommended Configurations

#### Entry Level ($500 - $1,500)

**CPU Mining Setup**
```
CPU: AMD Ryzen 5 5600X / Intel Core i5-12600K
RAM: 32GB DDR4-3200
Storage: 1TB NVMe SSD
Power: 650W 80+ Gold PSU

Estimated Performance:
- Hashrate: 1,000-2,000 H/s
- Power Draw: 150W
- Monthly Revenue: $150-450 (varies with price/difficulty)
```

**Gaming GPU Setup**
```
GPU: RTX 3060 Ti / RX 6700 XT
CPU: Ryzen 5 5600G
RAM: 32GB DDR4-3200
Power: 750W 80+ Gold PSU

Estimated Performance:
- Hashrate: 8,000-12,000 H/s
- Power Draw: 220W
- Monthly Revenue: $750-1,350 (varies)
```

#### Enthusiast Level ($1,500 - $5,000)

**Multi-GPU Rig**
```
GPUs: 2x RTX 3070 / 4x RX 6600 XT
CPU: Ryzen 7 5700G
RAM: 64GB DDR4-3200
Motherboard: B550 with 4+ PCIe slots
Power: 1200W 80+ Platinum PSU

Estimated Performance:
- Hashrate: 40,000-60,000 H/s
- Power Draw: 800W
- Monthly Revenue: $4,500-7,500 (varies)
```

**High-End CPU Setup**
```
CPU: AMD Threadripper 3970X (32 cores)
RAM: 128GB DDR4-3200 ECC
Motherboard: TRX40 chipset
Power: 1000W 80+ Platinum PSU

Estimated Performance:
- Hashrate: 25,000-35,000 H/s
- Power Draw: 400W
- Monthly Revenue: $3,000-5,400 (varies)
```

#### Professional Level ($5,000+)

**Mining Farm (Per Rig)**
```
GPUs: 6x RTX 4070 / 8x RX 7600 XT
CPU: Intel Core i3-12100F
RAM: 32GB DDR4-3200
Power: 1600W 80+ Titanium PSU

Estimated Performance:
- Hashrate: 120,000-180,000 H/s
- Power Draw: 1,400W
- Monthly Revenue: $15,000-24,000 (varies)
```

## Getting Started

### Step 1: Prepare Your Wallet

1. Set up an Ethereum wallet (see [Quick Start Guide](../getting-started/quick-start.md))
2. Get some ETH for gas fees (at least 0.01 ETH)
3. Note your wallet address

### Step 2: Install Mining Software

```bash
# Clone the EVMORE repository
git clone https://github.com/evmore/evmore-contracts
cd evmore-contracts

# Install Python dependencies
uv sync

# Verify installation
uv run python --version
```

### Step 3: Configure Your Miner

Create a configuration file:

```python
# mining_config.py
WALLET_ADDRESS = "0xYourWalletAddressHere"
RPC_URL = "https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY"
NUM_WORKERS = 4  # Number of CPU cores to use
```

### Step 4: Start Mining

**Solo Mining:**
```bash
uv run python scripts/mining/optimized_miner.py
```

**Pool Mining:**
```bash
uv run python scripts/mining/mining_pool.py --pool POOL_ADDRESS --wallet YOUR_WALLET
```

### Step 5: Monitor Your Mining

Watch for these outputs:
```
⛏️  Mining started...
📊 Hashrate: 10,000 H/s
🎯 Difficulty: 16 bits
✅ Solution found!
📤 Submitting proof...
🎉 Reward earned: 50 EVMORE
```

## Solo Mining vs Pool Mining

### Solo Mining

You mine independently and receive full block rewards.

**Pros:**
- Keep 100% of rewards
- No pool fees
- Complete independence
- No pool downtime risk

**Cons:**
- Highly variable income
- May go days without rewards
- Requires significant hashrate
- Higher technical complexity

**Best for:**
- Large mining operations
- Experienced miners
- Those who want maximum control

### Pool Mining

You join a group of miners and share rewards proportionally.

**Pros:**
- Steady, predictable income
- Lower variance
- Easier setup
- Shared infrastructure

**Cons:**
- Pool takes 1-3% fee
- Dependent on pool reliability
- Shared rewards

**Best for:**
- Most individual miners
- Beginners
- Those preferring stability

### Choosing the Right Approach

| Your Hashrate | Recommendation |
|---------------|----------------|
| < 10,000 H/s | Pool mining |
| 10,000 - 100,000 H/s | Pool (or solo if patient) |
| > 100,000 H/s | Consider solo mining |

## Profitability Calculator

### Factors Affecting Profitability

1. **Your hashrate**: Higher = more chances to find solutions
2. **Network hashrate**: Total competition
3. **Block reward**: Currently 50 EVMORE, halves over time
4. **EVMORE price**: Market value of rewards
5. **Electricity cost**: Your power rates
6. **Hardware efficiency**: Hash per watt

### Calculating Profitability

```
Daily Revenue = (Your Hashrate / Network Hashrate) × Daily Blocks × Block Reward × EVMORE Price

Daily Cost = Power Draw (kW) × 24 hours × Electricity Rate ($/kWh)

Daily Profit = Daily Revenue - Daily Cost
```

### Example Calculation

```
Setup: Gaming GPU (10,000 H/s, 220W)
Network Hashrate: 1,000,000 H/s
Block Reward: 50 EVMORE
Daily Blocks: 144
EVMORE Price: $100
Electricity: $0.10/kWh

Daily Revenue:
= (10,000 / 1,000,000) × 144 × 50 × $100
= 0.01 × 144 × 50 × $100
= $7,200 × 0.01
= $72

Daily Cost:
= 0.220 × 24 × $0.10
= $0.53

Daily Profit:
= $72 - $0.53
= $71.47
```

*Note: This is an example. Actual results vary significantly with network conditions.*

### Electricity Cost Impact

| Setup | Hashrate | Power | Profit at $0.05/kWh | Profit at $0.15/kWh |
|-------|----------|-------|---------------------|---------------------|
| CPU | 1,500 H/s | 150W | $10.52 | $10.16 |
| Gaming GPU | 10,000 H/s | 220W | $71.14 | $70.35 |
| Multi-GPU | 50,000 H/s | 800W | $355.04 | $352.16 |
| Pro Farm | 150,000 H/s | 1,400W | $1,063.32 | $1,058.28 |

## Optimization Tips

### Hardware Optimization

#### CPU Mining
```bash
# Linux: Set CPU governor to performance
echo 'performance' | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Enable huge pages for memory optimization
echo 'always' | sudo tee /sys/kernel/mm/transparent_hugepage/enabled

# Set process priority
nice -n -10 ./evmore_miner
```

#### GPU Mining
```bash
# NVIDIA: Enable persistence mode
nvidia-smi -pm 1

# Set power limit (adjust based on your card)
nvidia-smi -pl 200

# Optimize memory clocks
nvidia-settings -a [gpu:0]/GPUMemoryTransferRateOffset[3]=1000
```

### Software Optimization

1. **Use latest software**: Keep mining software updated
2. **Optimize worker count**: Match CPU cores or GPU count
3. **Reduce latency**: Use low-latency network connections
4. **Monitor temps**: Keep hardware cool for stability

### Infrastructure Tips

**Home Mining:**
- Dedicated electrical circuit (20A recommended)
- Adequate ventilation/cooling
- Consider noise (basement/garage)
- UPS for power stability

**Larger Operations:**
- 208V/240V power infrastructure
- Proper cooling systems
- Redundant internet
- Remote monitoring

## Power Efficiency

### Hash Per Watt Matters

More efficient hardware = higher profits, especially with electricity costs.

| Hardware | Hashrate | Power | H/W Ratio |
|----------|----------|-------|-----------|
| Old CPU | 500 H/s | 125W | 4 H/W |
| Modern CPU | 1,500 H/s | 100W | 15 H/W |
| Gaming GPU | 10,000 H/s | 220W | 45 H/W |
| Efficient GPU | 15,000 H/s | 200W | 75 H/W |

### Reducing Power Consumption

1. **Undervolting**: Reduce GPU voltage for same performance
2. **Efficient PSUs**: 80+ Gold or better
3. **Remove unnecessary components**: Extra drives, RGB
4. **Optimize cooling**: Better airflow = lower fan speeds

## Troubleshooting

### No Solutions Found

**Possible causes:**
- Hardware issue
- Software misconfiguration
- Network connectivity problems
- Challenge has changed

**Solutions:**
1. Restart mining software
2. Check hardware temperatures
3. Verify network connection
4. Update to latest software

### Low Hashrate

**Possible causes:**
- Thermal throttling
- Power limits
- Background processes
- Driver issues

**Solutions:**
1. Improve cooling
2. Check power settings
3. Close other applications
4. Update drivers

### Transaction Failures

**Possible causes:**
- Insufficient ETH for gas
- Gas price too low
- Network congestion
- Invalid solution

**Solutions:**
1. Add more ETH to wallet
2. Increase gas price
3. Wait for lower congestion
4. Verify solution is valid

### High Rejected Shares

**Possible causes:**
- Stale solutions
- Network latency
- Pool issues

**Solutions:**
1. Use closer pool server
2. Check internet stability
3. Reduce submission batch size

## Advanced Topics

### Building a Mining Rig

**Components checklist:**
- [ ] GPUs (research efficiency)
- [ ] CPU (doesn't need to be powerful)
- [ ] Motherboard (multiple PCIe slots)
- [ ] RAM (32GB minimum)
- [ ] PSU (calculate total power + 20% headroom)
- [ ] Frame/case (open-air for cooling)
- [ ] Risers (for GPU connections)
- [ ] Storage (SSD, 128GB+)
- [ ] Cooling (fans, AC if needed)

### Remote Management

For multiple rigs or unattended operation:
- SSH access for remote control
- Monitoring dashboards
- Alert systems for downtime
- Remote reboot capability
- Hashrate tracking

### Tax Considerations

Mining income may be taxable. Keep records of:
- Date and time of each mining reward
- Amount of EVMORE received
- Market value at time of receipt
- Electricity costs (may be deductible)
- Hardware costs (may be depreciable)

*Consult a tax professional for specific advice.*

## Resources

### Official Resources
- [Hardware Efficiency Guide](../../docs/mining/hardware-efficiency-guide.md)
- [Mining Pool Software](../../scripts/mining/mining_pool.py)
- [Optimized Miner](../../scripts/mining/optimized_miner.py)

### Community Resources
- Discord mining channels
- Community mining pools
- Hardware optimization guides

### Tools
- [Etherscan Gas Tracker](https://etherscan.io/gastracker)
- [WhatToMine Calculator](https://whattomine.com)
- GPU-Z / HWiNFO for monitoring

## Summary

### Quick Start Checklist

- [ ] Set up Ethereum wallet
- [ ] Get some ETH for gas
- [ ] Check hardware meets requirements
- [ ] Install mining software
- [ ] Configure wallet address
- [ ] Start mining
- [ ] Monitor performance
- [ ] Claim rewards

### Key Takeaways

1. **EVMORE is GPU/CPU mineable** - no ASICs required
2. **Memory matters** - the algorithm is memory-hard
3. **Pool mining is easier** - especially for beginners
4. **Monitor costs** - electricity is your main expense
5. **Stay updated** - follow community for optimization tips
