use std::str::FromStr;

use alloy::primitives::{Address, U256};
use alloy::providers::{ProviderBuilder, Provider};
use alloy::sol;
use anyhow::{anyhow, Context};
use serde::Serialize;
use url::Url;

use crate::config::ChainConfig;

sol! {
    #[sol(rpc)]
    interface IEvmoreToken {
        function totalSupply() external view returns (uint256);
        function blocksMined() external view returns (uint256);
        function currentDifficulty() external view returns (uint256);
        function currentChallenge() external view returns (bytes32);
        function lastMiningTimestamp() external view returns (uint256);
        function currentEpoch() external view returns (uint256);
    }
}

const MAX_SUPPLY_WEI: u128 = 21_000_000u128 * 1_000_000_000_000_000_000u128;
const INITIAL_REWARD_WEI: u128 = 50u128 * 1_000_000_000_000_000_000u128;
const HALVING_INTERVAL: u128 = 210_000;

#[derive(Debug, Serialize)]
pub struct Overview {
    pub chain_key: String,
    pub chain_id: u64,
    pub token_address: String,
    pub total_supply: String,
    pub max_supply: String,
    pub circulating_percent: f64,
    pub blocks_mined: String,
    pub current_difficulty: String,
    pub current_challenge: String,
    pub last_mining_timestamp: u64,
    pub seconds_since_last_block: u64,
    pub current_reward: String,
    pub next_halving_block: String,
    pub blocks_until_halving: String,
    pub latest_block: u64,
}

pub async fn fetch_overview(cfg: &ChainConfig) -> anyhow::Result<Overview> {
    let token_addr = cfg
        .token_address
        .as_ref()
        .ok_or_else(|| anyhow!("no token address configured for chain {}", cfg.key))?;
    let token = Address::from_str(token_addr).context("invalid token address")?;

    let rpc = Url::parse(&cfg.rpc_url).context("invalid RPC URL")?;
    let provider = ProviderBuilder::new().on_http(rpc);

    let contract = IEvmoreToken::new(token, &provider);

    let total_supply = contract.totalSupply().call().await?._0;
    let blocks_mined = contract.blocksMined().call().await?._0;
    let current_difficulty = contract.currentDifficulty().call().await?._0;
    let current_challenge = contract.currentChallenge().call().await?._0;
    let last_mining_timestamp = contract.lastMiningTimestamp().call().await?._0;
    let latest_block = provider.get_block_number().await.unwrap_or(0);

    let now = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|d| d.as_secs())
        .unwrap_or(0);

    let last_ts = u256_to_u64(last_mining_timestamp);
    let seconds_since = now.saturating_sub(last_ts);

    let (current_reward, next_halving_block, blocks_until_halving) = reward_schedule(blocks_mined);

    let circulating_percent = {
        let ts = u256_to_f64(total_supply);
        let max = MAX_SUPPLY_WEI as f64;
        if max > 0.0 { (ts / max) * 100.0 } else { 0.0 }
    };

    Ok(Overview {
        chain_key: cfg.key.clone(),
        chain_id: cfg.chain_id,
        token_address: token_addr.clone(),
        total_supply: total_supply.to_string(),
        max_supply: MAX_SUPPLY_WEI.to_string(),
        circulating_percent,
        blocks_mined: blocks_mined.to_string(),
        current_difficulty: current_difficulty.to_string(),
        current_challenge: format!("0x{}", hex::encode(current_challenge.as_slice())),
        last_mining_timestamp: last_ts,
        seconds_since_last_block: seconds_since,
        current_reward: current_reward.to_string(),
        next_halving_block: next_halving_block.to_string(),
        blocks_until_halving: blocks_until_halving.to_string(),
        latest_block,
    })
}

fn reward_schedule(blocks_mined: U256) -> (U256, U256, U256) {
    let blocks = u256_to_u128(blocks_mined);
    let halvings = blocks / HALVING_INTERVAL;
    let capped_halvings = halvings.min(63);
    let reward = INITIAL_REWARD_WEI >> capped_halvings;
    let next_halving_block = (halvings + 1) * HALVING_INTERVAL;
    let blocks_until = next_halving_block.saturating_sub(blocks);
    (
        U256::from(reward),
        U256::from(next_halving_block),
        U256::from(blocks_until),
    )
}

fn u256_to_u64(v: U256) -> u64 {
    let limbs = v.as_limbs();
    limbs[0]
}

fn u256_to_u128(v: U256) -> u128 {
    let limbs = v.as_limbs();
    (limbs[0] as u128) | ((limbs[1] as u128) << 64)
}

fn u256_to_f64(v: U256) -> f64 {
    u256_to_u128(v) as f64
}

mod hex {
    pub fn encode(bytes: &[u8]) -> String {
        let mut s = String::with_capacity(bytes.len() * 2);
        for b in bytes {
            s.push_str(&format!("{b:02x}"));
        }
        s
    }
}
