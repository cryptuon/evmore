use std::collections::BTreeMap;
use std::path::PathBuf;

use serde::Serialize;

#[derive(Debug, Clone)]
pub struct Config {
    pub port: u16,
    pub static_dir: PathBuf,
    pub coingecko_base: String,
    pub chains: BTreeMap<String, ChainConfig>,
}

#[derive(Debug, Clone, Serialize)]
pub struct ChainConfig {
    pub key: String,
    pub name: String,
    pub chain_id: u64,
    #[serde(skip_serializing)]
    pub rpc_url: String,
    pub public_rpc_url: Option<String>,
    pub token_address: Option<String>,
    pub verifier_address: Option<String>,
    pub bridge_address: Option<String>,
    pub explorer: Option<String>,
    pub is_testnet: bool,
}

impl Config {
    pub fn from_env() -> anyhow::Result<Self> {
        let port: u16 = std::env::var("PORT")
            .ok()
            .and_then(|v| v.parse().ok())
            .unwrap_or(8080);

        let static_dir = std::env::var("STATIC_DIR")
            .map(PathBuf::from)
            .unwrap_or_else(|_| PathBuf::from("/app/public"));

        let coingecko_base = std::env::var("COINGECKO_BASE")
            .unwrap_or_else(|_| "https://api.coingecko.com/api/v3".to_string());

        let mut chains = BTreeMap::new();

        for (key, name, default_chain_id, is_testnet) in [
            ("mainnet", "Ethereum Mainnet", 1u64, false),
            ("sepolia", "Sepolia Testnet", 11155111, true),
            ("devnet", "Local Devnet", 31337, true),
        ] {
            if let Some(cc) = load_chain(key, name, default_chain_id, is_testnet) {
                chains.insert(key.to_string(), cc);
            }
        }

        if chains.is_empty() {
            tracing::warn!(
                "No chains configured. Set RPC_MAINNET / RPC_SEPOLIA / RPC_DEVNET env vars."
            );
        }

        Ok(Config {
            port,
            static_dir,
            coingecko_base,
            chains,
        })
    }
}

fn load_chain(key: &str, name: &str, default_id: u64, is_testnet: bool) -> Option<ChainConfig> {
    let upper = key.to_uppercase();
    let rpc = std::env::var(format!("RPC_{upper}")).ok()?;
    let chain_id = std::env::var(format!("CHAIN_ID_{upper}"))
        .ok()
        .and_then(|v| v.parse().ok())
        .unwrap_or(default_id);
    let public_rpc = std::env::var(format!("PUBLIC_RPC_{upper}")).ok();
    let token = std::env::var(format!("TOKEN_{upper}")).ok().filter(|s| !s.is_empty());
    let verifier = std::env::var(format!("VERIFIER_{upper}")).ok().filter(|s| !s.is_empty());
    let bridge = std::env::var(format!("BRIDGE_{upper}")).ok().filter(|s| !s.is_empty());
    let explorer = std::env::var(format!("EXPLORER_{upper}")).ok().filter(|s| !s.is_empty());

    Some(ChainConfig {
        key: key.to_string(),
        name: name.to_string(),
        chain_id,
        rpc_url: rpc,
        public_rpc_url: public_rpc,
        token_address: token,
        verifier_address: verifier,
        bridge_address: bridge,
        explorer,
        is_testnet,
    })
}
