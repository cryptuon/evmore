# Troubleshooting Guide

Solutions to common problems when using EVMORE.

---

## Wallet Issues

### I can't see EVMORE in my wallet

**Symptoms:**
- EVMORE balance shows as 0
- Token doesn't appear in token list
- Sent EVMORE but it's not showing

**Solutions:**

1. **Add EVMORE as a custom token**
   - Open MetaMask → Import tokens → Custom token
   - Enter the EVMORE contract address
   - Click Add

2. **Check you're on the correct network**
   - EVMORE is on Ethereum Mainnet
   - Switch network in MetaMask if needed

3. **Refresh your wallet**
   - Close and reopen the wallet
   - Clear cache if available

4. **Verify the transaction**
   - Check Etherscan using your address
   - Confirm the tokens were actually sent

### My wallet password isn't working

**Solutions:**

1. **Check caps lock** - passwords are case-sensitive

2. **Try your recovery phrase**
   - If you have your 12/24 word phrase
   - Use "Import wallet" instead of unlocking

3. **Check for updates**
   - Update your wallet software
   - Old versions may have bugs

### I lost my recovery phrase

**If you still have wallet access:**
1. Create a new wallet immediately
2. Write down the new recovery phrase
3. Transfer all funds to the new wallet

**If you've lost wallet access:**
- Unfortunately, funds cannot be recovered
- This is a feature, not a bug - it prevents theft
- Learn from this for future wallets

---

## Transaction Issues

### Transaction is stuck (pending)

**Causes:**
- Gas price too low
- Network congestion
- Nonce issues

**Solutions:**

1. **Wait** - transactions often confirm eventually

2. **Speed up the transaction** (MetaMask)
   - Click the pending transaction
   - Select "Speed up"
   - Increase gas price
   - Confirm

3. **Cancel and retry**
   - Click pending transaction
   - Select "Cancel"
   - Re-submit with higher gas

4. **Check gas prices**
   - Visit [Etherscan Gas Tracker](https://etherscan.io/gastracker)
   - Use "Fast" gas price for urgent transactions

### Transaction failed

**Common causes:**

| Error | Meaning | Solution |
|-------|---------|----------|
| Out of gas | Gas limit too low | Increase gas limit |
| Reverted | Contract rejected it | Check requirements |
| Insufficient funds | Not enough ETH | Add more ETH |
| Nonce too low | Transaction already processed | Reset nonce |

**General solutions:**

1. Check you have enough ETH for gas
2. Increase gas limit by 20-50%
3. Verify the receiving address is correct
4. Check the contract isn't paused

### I sent to the wrong address

**Unfortunately:**
- Blockchain transactions are irreversible
- There is no undo button
- Funds are likely permanently lost

**If you sent to:**
- **A typo address** → Funds are lost (address likely doesn't exist)
- **Wrong but valid address** → Contact recipient, ask for return
- **Smart contract** → Funds may be recoverable if contract has function

**Prevention:**
- Always double-check addresses
- Send a small test amount first
- Use address book for frequent recipients

### Gas fees are too high

**Immediate solutions:**

1. **Wait for lower congestion**
   - Weekends typically have lower fees
   - Early morning (US time) often cheaper
   - Check [Etherscan Gas Tracker](https://etherscan.io/gastracker)

2. **Set custom gas price**
   - Use "Slow" option if not urgent
   - Set manual gas price below current average

3. **Optimize transaction**
   - Batch multiple operations when possible
   - Avoid peak times

**Long-term solutions:**
- Use Layer 2 when EVMORE bridges are available
- Plan transactions during low-fee periods

---

## Mining Issues

### Mining software won't start

**Checklist:**

1. **Check dependencies**
   ```bash
   poetry --version  # Should show version
   python --version  # Python 3.12+
   ```

2. **Reinstall dependencies**
   ```bash
   poetry install --no-cache
   ```

3. **Check for error messages**
   - Read the full error output
   - Common issues: missing packages, wrong Python version

4. **Verify configuration**
   - Check wallet address format
   - Verify RPC URL is accessible

### No solutions found

**Possible causes:**
- Hardware working correctly but low probability
- Configuration issues
- Network connectivity problems

**Solutions:**

1. **Be patient** - mining is probabilistic
   - Solutions may take minutes or hours
   - This is normal, not a problem

2. **Check hashrate**
   - If hashrate is 0, there's a problem
   - If hashrate is normal, just wait

3. **Verify challenge is current**
   - Old challenges won't be accepted
   - Restart miner to get fresh challenge

4. **Check network connection**
   - Test RPC endpoint is responding
   - Verify internet is stable

### Low hashrate

**Causes and solutions:**

| Cause | Symptom | Solution |
|-------|---------|----------|
| Thermal throttling | High temps | Improve cooling |
| Power limits | GPU limiting power | Increase power limit |
| Background apps | High CPU/GPU usage | Close other apps |
| Driver issues | Errors in logs | Update drivers |
| Memory issues | Low RAM available | Close apps, add RAM |

**Optimization steps:**

1. **Monitor temperatures**
   - GPU should be under 80°C
   - CPU should be under 85°C

2. **Check power settings**
   - Set Windows to High Performance
   - Disable power saving on GPU

3. **Update drivers**
   - Latest GPU drivers
   - Chipset drivers for CPU mining

4. **Verify RAM is accessible**
   - Mining needs significant memory
   - Close memory-heavy applications

### Submitted solution rejected

**Causes:**

1. **Stale solution** - challenge changed before submission
2. **Invalid solution** - computation error
3. **Duplicate** - someone else submitted first
4. **Low gas** - transaction not included in time

**Solutions:**

1. **Reduce time between finding and submitting**
   - Use faster RPC endpoint
   - Increase gas for faster confirmation

2. **Verify solution locally before submitting**
   - Check logs for validation errors

3. **Switch pools if using pool mining**
   - Some pools have lower latency

### Gas too expensive for mining

**Solutions:**

1. **Batch submissions**
   - If possible, submit multiple proofs together

2. **Time your submissions**
   - Submit during low gas periods
   - Set gas price alerts

3. **Calculate profitability**
   - Ensure mining profit > gas costs
   - May need to wait for better conditions

4. **Consider pool mining**
   - Pool handles submissions
   - Lower individual gas costs

---

## DeFi Issues

### Swap failed on DEX

**Common causes:**

1. **Slippage too low**
   - Increase slippage tolerance (try 1-3%)
   - High volatility needs higher slippage

2. **Insufficient liquidity**
   - Large trades may not have enough liquidity
   - Try smaller amounts

3. **Token approval needed**
   - First transaction approves token spending
   - Second transaction is the actual swap

4. **Insufficient balance**
   - Check you have enough tokens AND ETH for gas

**Solutions:**
- Increase slippage to 2-3%
- Split large trades into smaller ones
- Approve token first, then swap
- Add more ETH for gas

### Can't add liquidity

**Checklist:**

1. Do you have both tokens in correct ratio?
2. Have you approved both tokens?
3. Is there enough ETH for gas?
4. Is the pool accepting new liquidity?

### Impermanent loss concerns

**Understanding IL:**
- IL occurs when token prices change after providing liquidity
- You end up with different ratios than you deposited
- It's "impermanent" until you withdraw

**Mitigation:**
- Only provide liquidity for stable pairs
- Consider LP token yield vs IL risk
- Monitor your positions regularly
- Understand IL fully before providing liquidity

---

## Security Issues

### I think my wallet was compromised

**Immediate actions:**

1. **Don't panic, but act fast**

2. **Create a new wallet**
   - On a clean device if possible
   - Write down new recovery phrase

3. **Transfer remaining funds**
   - Move all tokens to new wallet
   - Revoke all token approvals first if safe

4. **Check what happened**
   - Review transaction history on Etherscan
   - Identify the malicious transaction

5. **Revoke approvals**
   - Use [Revoke.cash](https://revoke.cash)
   - Remove all unnecessary token approvals

**Prevention for future:**
- Never share recovery phrase
- Use hardware wallet for significant funds
- Be cautious of phishing sites
- Don't click unknown links

### Suspicious tokens in my wallet

**What they are:**
- Scam tokens airdropped to your address
- Usually valueless or malicious
- May have fake high values

**What to do:**
- **Do NOT interact with them**
- Don't try to sell or transfer
- Hide them in your wallet if possible
- They can't harm you if you don't interact

**Why ignoring is important:**
- Interacting may trigger malicious code
- Could lead to approvals you don't want
- Selling may incur unexpected costs

### Phishing attempt detected

**Signs of phishing:**
- Unexpected emails/DMs asking for recovery phrase
- Websites that look slightly wrong
- Urgent requests for action
- Offers that seem too good to be true

**Protection:**
- Never share your recovery phrase
- Bookmark official sites, don't click links
- Verify URLs carefully (evmore.org vs evmor3.org)
- Enable 2FA on exchanges

---

## Getting More Help

### Before asking for help

1. **Search existing resources**
   - Check this troubleshooting guide
   - Read the [FAQ](faq.md)
   - Search community Discord

2. **Gather information**
   - Error messages (exact text)
   - Transaction hashes
   - Steps to reproduce
   - Screenshots if helpful

### Where to get help

| Issue Type | Where to Ask |
|------------|--------------|
| General questions | Discord - #help channel |
| Technical bugs | GitHub Issues |
| Transaction issues | Include TX hash |
| Security concerns | DM trusted moderators |

### What NOT to do

- **Never share your recovery phrase** - real support never asks
- **Don't trust DMs** - scammers pretend to be support
- **Don't click links from strangers** - use official links only
- **Don't download files** - malware risk

---

## Quick Fixes Summary

| Problem | Quick Fix |
|---------|-----------|
| Token not showing | Add as custom token |
| Transaction stuck | Speed up with more gas |
| High gas fees | Wait for off-peak times |
| Mining no solutions | Be patient, check hashrate |
| Swap failed | Increase slippage |
| Wallet compromised | Move funds to new wallet |

---

*Still having issues? Join the [community Discord](../community/resources.md) for support.*
