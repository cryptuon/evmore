use std::sync::Arc;

use axum::extract::{Query, State};
use axum::http::StatusCode;
use axum::response::{IntoResponse, Response};
use axum::routing::get;
use axum::{Json, Router};
use serde::Deserialize;
use serde_json::{json, Value};

use crate::chain;
use crate::price;
use crate::state::AppState;

pub fn router(state: Arc<AppState>) -> Router {
    Router::new()
        .route("/health", get(health))
        .route("/config", get(get_config))
        .route("/overview", get(get_overview))
        .route("/price", get(get_price))
        .with_state(state)
}

async fn health() -> impl IntoResponse {
    Json(json!({ "status": "ok", "service": "evmore-dashboard" }))
}

async fn get_config(State(state): State<Arc<AppState>>) -> impl IntoResponse {
    let chains: Vec<_> = state.config.chains.values().collect();
    Json(json!({ "chains": chains }))
}

#[derive(Deserialize)]
struct ChainQuery {
    chain: String,
}

async fn get_overview(
    State(state): State<Arc<AppState>>,
    Query(q): Query<ChainQuery>,
) -> Result<Json<Value>, ApiError> {
    let cache_key = format!("overview:{}", q.chain);
    if let Some(v) = state.cache.get(&cache_key).await {
        return Ok(Json(v));
    }

    let cfg = state
        .config
        .chains
        .get(&q.chain)
        .ok_or_else(|| ApiError::not_found(format!("unknown chain: {}", q.chain)))?;

    let overview = chain::fetch_overview(cfg)
        .await
        .map_err(|e| ApiError::upstream(format!("overview failed: {e:#}")))?;

    let value = serde_json::to_value(&overview).map_err(ApiError::internal)?;
    state.cache.insert(cache_key, value.clone()).await;
    Ok(Json(value))
}

async fn get_price(State(state): State<Arc<AppState>>) -> Result<Json<Value>, ApiError> {
    let key = "price:global".to_string();
    if let Some(v) = state.cache.get(&key).await {
        return Ok(Json(v));
    }
    let snap = price::fetch_prices(&state)
        .await
        .map_err(|e| ApiError::upstream(format!("price failed: {e:#}")))?;
    let value = serde_json::to_value(&snap).map_err(ApiError::internal)?;
    state.cache.insert(key, value.clone()).await;
    Ok(Json(value))
}

#[derive(Debug)]
pub struct ApiError {
    status: StatusCode,
    message: String,
}

impl ApiError {
    fn not_found(msg: impl Into<String>) -> Self {
        Self { status: StatusCode::NOT_FOUND, message: msg.into() }
    }
    fn upstream(msg: impl Into<String>) -> Self {
        Self { status: StatusCode::BAD_GATEWAY, message: msg.into() }
    }
    fn internal<E: std::fmt::Display>(e: E) -> Self {
        Self { status: StatusCode::INTERNAL_SERVER_ERROR, message: e.to_string() }
    }
}

impl IntoResponse for ApiError {
    fn into_response(self) -> Response {
        (self.status, Json(json!({ "error": self.message }))).into_response()
    }
}
