import { formatUnits, parseUnits } from 'ethers'

/**
 * Format a token amount with decimals
 */
export function formatTokenAmount(
  amount: bigint,
  decimals: number = 18,
  maxDecimals: number = 4
): string {
  const formatted = formatUnits(amount, decimals)
  const num = parseFloat(formatted)

  if (num === 0) return '0'
  if (num < 0.0001) return '< 0.0001'

  return num.toLocaleString('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: maxDecimals
  })
}

/**
 * Parse a token amount string to bigint
 */
export function parseTokenAmount(amount: string, decimals: number = 18): bigint {
  try {
    return parseUnits(amount, decimals)
  } catch {
    return 0n
  }
}

/**
 * Format an address with ellipsis
 */
export function formatAddress(address: string, chars: number = 4): string {
  if (!address) return ''
  if (address.length <= chars * 2 + 2) return address
  return `${address.slice(0, chars + 2)}...${address.slice(-chars)}`
}

/**
 * Format a hash with ellipsis
 */
export function formatHash(hash: string, chars: number = 8): string {
  if (!hash) return ''
  if (hash.length <= chars * 2) return hash
  return `${hash.slice(0, chars)}...${hash.slice(-chars)}`
}

/**
 * Format ETH balance
 */
export function formatEthBalance(balance: bigint): string {
  return formatTokenAmount(balance, 18, 6)
}

/**
 * Format a percentage
 */
export function formatPercentage(value: number, decimals: number = 2): string {
  return `${value.toFixed(decimals)}%`
}

/**
 * Format a large number with K, M, B suffixes
 */
export function formatLargeNumber(value: number): string {
  if (value >= 1_000_000_000) {
    return `${(value / 1_000_000_000).toFixed(2)}B`
  }
  if (value >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(2)}M`
  }
  if (value >= 1_000) {
    return `${(value / 1_000).toFixed(2)}K`
  }
  return value.toFixed(2)
}

/**
 * Format hash rate (hashes per second)
 */
export function formatHashRate(hashRate: number): string {
  if (hashRate >= 1_000_000_000) {
    return `${(hashRate / 1_000_000_000).toFixed(2)} GH/s`
  }
  if (hashRate >= 1_000_000) {
    return `${(hashRate / 1_000_000).toFixed(2)} MH/s`
  }
  if (hashRate >= 1_000) {
    return `${(hashRate / 1_000).toFixed(2)} KH/s`
  }
  return `${hashRate.toFixed(2)} H/s`
}

/**
 * Format time duration
 */
export function formatDuration(seconds: number): string {
  if (seconds < 60) {
    return `${Math.floor(seconds)}s`
  }
  if (seconds < 3600) {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return secs > 0 ? `${mins}m ${secs}s` : `${mins}m`
  }
  if (seconds < 86400) {
    const hours = Math.floor(seconds / 3600)
    const mins = Math.floor((seconds % 3600) / 60)
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`
  }
  const days = Math.floor(seconds / 86400)
  const hours = Math.floor((seconds % 86400) / 3600)
  return hours > 0 ? `${days}d ${hours}h` : `${days}d`
}

/**
 * Format a timestamp to relative time
 */
export function formatRelativeTime(timestamp: number): string {
  const now = Date.now()
  const diff = now - timestamp

  if (diff < 60_000) return 'just now'
  if (diff < 3600_000) return `${Math.floor(diff / 60_000)} min ago`
  if (diff < 86400_000) return `${Math.floor(diff / 3600_000)} hours ago`
  if (diff < 604800_000) return `${Math.floor(diff / 86400_000)} days ago`

  return new Date(timestamp).toLocaleDateString()
}

/**
 * Format difficulty as a readable number
 */
export function formatDifficulty(difficulty: bigint): string {
  return difficulty.toString()
}

/**
 * Format blocks count
 */
export function formatBlocks(blocks: bigint): string {
  return blocks.toLocaleString()
}
