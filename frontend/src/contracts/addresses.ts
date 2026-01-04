export const CHAIN_IDS = {
  ETHEREUM_MAINNET: 1,
  ETHEREUM_GOERLI: 5,
  ETHEREUM_SEPOLIA: 11155111,
  POLYGON_MAINNET: 137,
  POLYGON_MUMBAI: 80001,
  LOCAL: 31337
} as const

export type ChainId = typeof CHAIN_IDS[keyof typeof CHAIN_IDS]

export const CHAIN_NAMES: Record<ChainId, string> = {
  [CHAIN_IDS.ETHEREUM_MAINNET]: 'Ethereum Mainnet',
  [CHAIN_IDS.ETHEREUM_GOERLI]: 'Goerli Testnet',
  [CHAIN_IDS.ETHEREUM_SEPOLIA]: 'Sepolia Testnet',
  [CHAIN_IDS.POLYGON_MAINNET]: 'Polygon Mainnet',
  [CHAIN_IDS.POLYGON_MUMBAI]: 'Mumbai Testnet',
  [CHAIN_IDS.LOCAL]: 'Local Network'
}

export const SUPPORTED_CHAINS: ChainId[] = [
  CHAIN_IDS.ETHEREUM_MAINNET,
  CHAIN_IDS.ETHEREUM_SEPOLIA,
  CHAIN_IDS.POLYGON_MAINNET,
  CHAIN_IDS.LOCAL
]

// Contract addresses per network
// These will be filled after deployment
export const EVMORE_TOKEN_ADDRESS: Partial<Record<ChainId, string>> = {
  [CHAIN_IDS.ETHEREUM_MAINNET]: '',
  [CHAIN_IDS.ETHEREUM_SEPOLIA]: '',
  [CHAIN_IDS.LOCAL]: '0x5FbDB2315678afecb367f032d93F642f64180aa3' // Default Hardhat deploy address
}

export const VERIFIER_ADDRESS: Partial<Record<ChainId, string>> = {
  [CHAIN_IDS.ETHEREUM_MAINNET]: '',
  [CHAIN_IDS.ETHEREUM_SEPOLIA]: '',
  [CHAIN_IDS.LOCAL]: '0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512'
}

export const BRIDGE_ADDRESS: Partial<Record<ChainId, string>> = {
  [CHAIN_IDS.ETHEREUM_MAINNET]: '',
  [CHAIN_IDS.ETHEREUM_SEPOLIA]: '',
  [CHAIN_IDS.LOCAL]: ''
}

export const WEVMORE_ADDRESS: Partial<Record<ChainId, string>> = {
  [CHAIN_IDS.POLYGON_MAINNET]: '',
  [CHAIN_IDS.POLYGON_MUMBAI]: ''
}

export const RPC_URLS: Partial<Record<ChainId, string>> = {
  [CHAIN_IDS.ETHEREUM_MAINNET]: 'https://eth-mainnet.g.alchemy.com/v2/',
  [CHAIN_IDS.ETHEREUM_SEPOLIA]: 'https://eth-sepolia.g.alchemy.com/v2/',
  [CHAIN_IDS.POLYGON_MAINNET]: 'https://polygon-mainnet.g.alchemy.com/v2/',
  [CHAIN_IDS.LOCAL]: 'http://localhost:8545'
}

export const BLOCK_EXPLORERS: Partial<Record<ChainId, string>> = {
  [CHAIN_IDS.ETHEREUM_MAINNET]: 'https://etherscan.io',
  [CHAIN_IDS.ETHEREUM_SEPOLIA]: 'https://sepolia.etherscan.io',
  [CHAIN_IDS.POLYGON_MAINNET]: 'https://polygonscan.com',
  [CHAIN_IDS.LOCAL]: ''
}

export function getExplorerTxUrl(chainId: ChainId, txHash: string): string {
  const explorer = BLOCK_EXPLORERS[chainId]
  if (!explorer) return ''
  return `${explorer}/tx/${txHash}`
}

export function getExplorerAddressUrl(chainId: ChainId, address: string): string {
  const explorer = BLOCK_EXPLORERS[chainId]
  if (!explorer) return ''
  return `${explorer}/address/${address}`
}

export function isSupportedChain(chainId: number): chainId is ChainId {
  return SUPPORTED_CHAINS.includes(chainId as ChainId)
}
