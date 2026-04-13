use serde::Serialize;
use serde_json::Value;

use crate::state::AppState;

#[derive(Debug, Serialize)]
pub struct PriceSnapshot {
    pub eth_usd: Option<f64>,
    pub eth_usd_24h_change: Option<f64>,
    pub evmore_usd: Option<f64>,
    pub evmore_usd_24h_change: Option<f64>,
    pub source: &'static str,
}

pub async fn fetch_prices(state: &AppState) -> anyhow::Result<PriceSnapshot> {
    let url = format!(
        "{}/simple/price?ids=ethereum&vs_currencies=usd&include_24hr_change=true",
        state.config.coingecko_base
    );
    let resp: Value = state.http.get(&url).send().await?.json().await?;

    let eth = resp.get("ethereum");
    let eth_usd = eth.and_then(|e| e.get("usd")).and_then(Value::as_f64);
    let eth_usd_24h_change = eth
        .and_then(|e| e.get("usd_24h_change"))
        .and_then(Value::as_f64);

    Ok(PriceSnapshot {
        eth_usd,
        eth_usd_24h_change,
        evmore_usd: None,
        evmore_usd_24h_change: None,
        source: "coingecko",
    })
}
