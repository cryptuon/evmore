mod config;
mod state;
mod chain;
mod price;
mod routes;

use std::net::SocketAddr;
use std::path::PathBuf;
use std::sync::Arc;

use axum::Router;
use tower_http::compression::CompressionLayer;
use tower_http::cors::{Any, CorsLayer};
use tower_http::services::{ServeDir, ServeFile};
use tower_http::trace::TraceLayer;
use tracing_subscriber::EnvFilter;

use crate::state::AppState;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::fmt()
        .with_env_filter(EnvFilter::try_from_default_env().unwrap_or_else(|_| EnvFilter::new("info")))
        .init();

    let cfg = config::Config::from_env()?;
    let port = cfg.port;
    let static_dir = cfg.static_dir.clone();
    let state = Arc::new(AppState::new(cfg));

    let api = routes::router(state.clone());

    let app = build_app(api, static_dir);

    let addr: SocketAddr = ([0, 0, 0, 0], port).into();
    tracing::info!("evmore-dashboard listening on http://{addr}");

    let listener = tokio::net::TcpListener::bind(addr).await?;
    axum::serve(listener, app.into_make_service()).await?;
    Ok(())
}

fn build_app(api: Router, static_dir: PathBuf) -> Router {
    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods(Any)
        .allow_headers(Any);

    let spa_fallback = ServeFile::new(static_dir.join("404.html"));
    let static_service = ServeDir::new(&static_dir).not_found_service(spa_fallback);

    Router::new()
        .nest("/api", api)
        .fallback_service(static_service)
        .layer(CompressionLayer::new())
        .layer(cors)
        .layer(TraceLayer::new_for_http())
}
