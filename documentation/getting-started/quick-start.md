# Quick Start Guide

Get started with EVMORE digital gold in just a few steps. This guide covers everything from setting up your wallet to acquiring your first EVMORE.

## Prerequisites

Before you begin, you'll need:

- **A computer** with internet access
- **An Ethereum wallet** (we'll help you set one up)
- **Some ETH** for transaction fees (even small amounts work)
- **10-15 minutes** of your time

## Step 1: Set Up Your Wallet

Your wallet is where you'll store your EVMORE. It's like a digital vault for your digital gold.

### Option A: MetaMask (Recommended for Beginners)

MetaMask is the most popular Ethereum wallet, available as a browser extension and mobile app.

#### Installation

1. **Browser Extension**
   - Visit [metamask.io](https://metamask.io)
   - Click "Download" and select your browser (Chrome, Firefox, Brave, Edge)
   - Click "Add to Browser" and confirm the installation
   - The MetaMask fox icon will appear in your browser toolbar

2. **Mobile App**
   - Download from App Store (iOS) or Google Play (Android)
   - Search for "MetaMask" - look for the orange fox icon

#### Creating Your Wallet

1. Click the MetaMask icon and select "Create a new wallet"
2. Create a strong password (you'll use this to unlock the wallet)
3. **CRITICAL: Write down your Secret Recovery Phrase**
   - MetaMask will show you 12 words
   - Write these down on paper (not digital!)
   - Store in a secure location (safe, lockbox, etc.)
   - Never share these words with anyone
   - Anyone with these words can access your funds
4. Confirm your recovery phrase by selecting the words in order
5. Your wallet is now ready!

#### Security Tips

- **Never share your recovery phrase** - not with support, not with friends, not online
- **Never store it digitally** - no photos, no cloud storage, no text files
- **Consider making multiple copies** stored in different secure locations
- **Test your backup** by restoring on a different device before adding significant funds

### Option B: Hardware Wallets (For Larger Holdings)

For significant holdings, consider a hardware wallet:

- **Ledger Nano S Plus / Nano X** - Popular choice, good mobile support
- **Trezor Model One / Model T** - Open-source firmware

Hardware wallets keep your private keys offline, providing maximum security.

### Option C: Other Software Wallets

- **Rabby** - Feature-rich alternative to MetaMask
- **Rainbow** - Beautiful mobile-first wallet
- **Coinbase Wallet** - Good for beginners, integrates with Coinbase exchange

## Step 2: Get Some ETH

You need a small amount of ETH to pay for transaction fees (called "gas"). Even $10-20 worth is plenty to start.

### Ways to Get ETH

#### From a Centralized Exchange

1. **Create an account** on an exchange (Coinbase, Kraken, Binance, etc.)
2. **Complete verification** (usually requires ID)
3. **Deposit funds** via bank transfer or card
4. **Buy ETH**
5. **Withdraw to your wallet**
   - In the exchange, go to Withdraw
   - Select ETH (make sure it's on Ethereum mainnet)
   - Paste your wallet address (from MetaMask)
   - Confirm the withdrawal

#### From a Friend

Ask someone who already has ETH to send you a small amount. Just share your wallet address.

#### From a Decentralized Exchange

If you have other cryptocurrencies, you can swap them for ETH on Uniswap, Sushi, or similar.

### Finding Your Wallet Address

1. Open MetaMask
2. Your address is shown at the top (starts with 0x...)
3. Click to copy the full address
4. This is safe to share - it's like an email address for receiving crypto

## Step 3: Add EVMORE to Your Wallet

By default, your wallet won't show EVMORE. You need to add it as a "custom token."

### Adding EVMORE to MetaMask

1. Open MetaMask
2. Scroll down and click "Import tokens"
3. Select "Custom token"
4. Enter the EVMORE contract address:
   ```
   [Contract address will be available after mainnet launch]
   ```
5. The token symbol (EVMORE) and decimals (18) should auto-fill
6. Click "Add custom token"
7. Confirm by clicking "Import tokens"

Now EVMORE will appear in your token list, even if your balance is 0.

## Step 4: Get Your First EVMORE

There are several ways to acquire EVMORE:

### Option A: Trade on a Decentralized Exchange

Once EVMORE is listed on DEXs:

1. Go to [Uniswap](https://app.uniswap.org) or similar DEX
2. Connect your wallet (click "Connect Wallet")
3. In the "You pay" field, select ETH
4. In the "You receive" field, paste the EVMORE contract address
5. Enter the amount you want to trade
6. Click "Swap" and confirm in your wallet
7. Wait for the transaction to confirm (usually 1-5 minutes)

### Option B: Mine EVMORE

Earn EVMORE by contributing computing power to the network.

**Basic Requirements:**
- Computer with GPU or modern CPU
- 8GB+ RAM
- Stable internet connection
- Small amount of ETH for submitting proofs

See the [Mining Guide](../mining/mining-guide.md) for detailed instructions.

### Option C: Receive from Others

Anyone can send EVMORE to your wallet address. Simply share your address (the 0x... string from Step 2).

### Option D: Centralized Exchanges

Once EVMORE is listed on centralized exchanges, you can:
1. Deposit fiat or crypto
2. Buy EVMORE
3. Withdraw to your personal wallet

## Step 5: Basic Operations

### Checking Your Balance

1. Open MetaMask
2. Make sure you're on Ethereum Mainnet
3. Your EVMORE balance appears in your token list
4. Click on EVMORE to see more details

### Sending EVMORE

1. Open MetaMask
2. Click on EVMORE in your token list
3. Click "Send"
4. Enter the recipient's address
   - Double-check this! Transactions cannot be reversed
5. Enter the amount to send
6. Review the gas fee (paid in ETH)
7. Click "Confirm"
8. Wait for confirmation (usually 1-5 minutes)

### Receiving EVMORE

1. Copy your wallet address from MetaMask
2. Share this address with the sender
3. Wait for them to send
4. Transaction will appear automatically once confirmed

### Viewing Transaction History

1. Open MetaMask
2. Click "Activity" tab
3. See all your transactions
4. Click any transaction for details
5. Or view on Etherscan by clicking the transaction hash

## Step 6: Stay Safe

### Security Checklist

- [ ] Recovery phrase written down and stored securely
- [ ] Strong wallet password set
- [ ] Verified official contract addresses before interacting
- [ ] Small test transactions before sending large amounts
- [ ] Regular security reviews of connected sites

### Common Scams to Avoid

1. **Fake Websites**
   - Always verify you're on the correct URL
   - Bookmark official sites
   - Don't click links from unknown sources

2. **Impersonators**
   - Support will never ask for your recovery phrase
   - No legitimate airdrop requires you to send crypto first
   - Verify official social accounts

3. **Malicious Tokens**
   - Only add tokens from verified contract addresses
   - Be cautious of "free" tokens appearing in your wallet
   - Don't interact with unknown tokens

4. **Phishing**
   - MetaMask will never email you
   - Don't enter your recovery phrase anywhere except MetaMask itself
   - Verify all transaction details before signing

### If Something Goes Wrong

- **Lost password?** Use your recovery phrase to restore
- **Lost recovery phrase?** If you still have wallet access, transfer funds to a new wallet immediately
- **Sent to wrong address?** Unfortunately, blockchain transactions are irreversible
- **Suspicious transaction?** Revoke permissions on [Revoke.cash](https://revoke.cash)

## Understanding Gas Fees

Every Ethereum transaction requires a "gas" fee, paid in ETH.

### What Affects Gas Fees

- **Network congestion**: Busier network = higher fees
- **Transaction complexity**: Simple transfers are cheaper
- **Gas price**: You can set higher gas for faster confirmation

### Saving on Gas

- Check gas prices at [Etherscan Gas Tracker](https://etherscan.io/gastracker)
- Transact during off-peak hours (weekends, early morning US time)
- Use Layer 2 solutions when available
- Set appropriate gas limits (don't overpay)

### Typical Gas Costs

| Operation | Approximate Cost |
|-----------|-----------------|
| Simple transfer | $1-10 |
| DEX swap | $5-30 |
| Mining proof submission | $5-20 |

*Costs vary significantly based on network conditions*

## Using EVMORE in DeFi

Once you have EVMORE, you can use it in various DeFi protocols:

### Decentralized Exchanges (DEXs)

- **Trade**: Swap EVMORE for other tokens
- **Provide Liquidity**: Earn trading fees by providing liquidity
- Popular DEXs: Uniswap, Sushiswap, Curve

### Lending Protocols

- **Supply**: Lend your EVMORE to earn interest
- **Borrow**: Use EVMORE as collateral to borrow other assets
- Popular protocols: Aave, Compound

### Yield Aggregators

- **Optimize yields**: Automatically move funds to highest-yielding opportunities
- Popular aggregators: Yearn, Beefy

### Important DeFi Considerations

- **Smart contract risk**: All DeFi protocols carry risk
- **Impermanent loss**: Providing liquidity can result in losses
- **Start small**: Learn with small amounts first
- **Do your research**: Understand protocols before using them

## Next Steps

Now that you're set up, explore further:

- **[What is EVMORE?](what-is-evmore.md)** - Understand the fundamentals
- **[Mining Guide](../mining/mining-guide.md)** - Start earning EVMORE
- **[Economics](economics.md)** - Learn about EVMORE's value model
- **[FAQ](faq.md)** - Common questions answered
- **[Troubleshooting](troubleshooting.md)** - Solve common problems
- **[Community](../community/resources.md)** - Connect with others

## Quick Reference

### Key Information

| Item | Details |
|------|---------|
| Token Name | EVMORE |
| Token Symbol | EVMORE |
| Decimals | 18 |
| Network | Ethereum Mainnet |
| Max Supply | 21,000,000 |
| Contract | [To be announced] |

### Useful Links

- Official Website: [Coming soon]
- Block Explorer: [Etherscan link after launch]
- DEX Trading: Uniswap / Sushiswap
- Community Discord: [Coming soon]
- GitHub: [Repository link]
