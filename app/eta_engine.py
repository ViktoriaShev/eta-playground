from datetime import datetime, timezone


def _parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(timezone.utc)


def calculate_eta(position: dict, event: dict | None, historical_avg_sec: float, cfg: dict) -> dict:
    algorithm = cfg.get('algorithm', {})
    weights = algorithm.get('weights', {})

    distance_km = float(position.get('distance_to_station_km', 1.0))
    speed_kmh = max(float(position.get('speed_kmh', 1.0)), 1.0)
    current_eta_sec = distance_km / speed_kmh * 3600

    w_speed = float(weights.get('speed_based', 0.6))
    w_hist = float(weights.get('historical', 0.4))

    eta_sec = (current_eta_sec * w_speed) + (historical_avg_sec * w_hist)

    delay_sec = 0.0
    if event and event.get('type') == 'delay':
        delay_sec = float(event.get('delay_sec', 0.0))
        eta_sec += delay_sec

    generated_at = position.get('ts') or datetime.now(timezone.utc).isoformat()
    return {
        'train_id': position['train_id'],
        'line_id': position.get('line_id', 'demo'),
        'station_id': position.get('station_id', 'unknown'),
        'eta_sec': round(eta_sec, 2),
        'historical_avg_sec': round(historical_avg_sec, 2),
        'current_eta_sec': round(current_eta_sec, 2),
        'delay_sec': round(delay_sec, 2),
        'generated_at': generated_at,
        'event_ts_lag_sec': round((_parse_ts(generated_at) - _parse_ts(position['ts'])).total_seconds(), 2) if position.get('ts') else 0.0,
    }
