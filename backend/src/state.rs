use std::time::Duration;

use moka::future::Cache;
use serde_json::Value;

use crate::config::Config;

pub struct AppState {
    pub config: Config,
    pub http: reqwest::Client,
    pub cache: Cache<String, Value>,
}

impl AppState {
    pub fn new(config: Config) -> Self {
        let http = reqwest::Client::builder()
            .timeout(Duration::from_secs(15))
            .user_agent("evmore-dashboard/0.1")
            .build()
            .expect("reqwest client");

        let cache = Cache::builder()
            .max_capacity(256)
            .time_to_live(Duration::from_secs(10))
            .build();

        Self { config, http, cache }
    }
}
