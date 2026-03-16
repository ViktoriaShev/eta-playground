# app/app.py
import os
from pathlib import Path
from threading import Event

from flask import Flask, jsonify

from config import load_config
from kafka_consumer import DemoConsumer
from store import get_all_states, get_train_state

app = Flask(__name__)
_started = Event()

PATH = Path(__file__)
CONFIG_PATH = os.path.join(PATH.parent.parent, "config/algorithm.yaml")


@app.route("/config")
def get_config():
    return jsonify(load_config())


@app.route("/eta")
def get_eta():
    cfg = load_config()
    # простая "фейковая" формула для демонстрации
    weights = cfg.get("algorithm", {}).get("weights", {})
    speed = 40  # например
    hist = 0.5
    w_speed = weights.get("speed_based", 0.0)
    w_hist = weights.get("historical", 0.0)
    eta_score = (speed * w_speed) + (hist * 100 * w_hist)
    return jsonify({"eta_score": eta_score, "weights": weights})


@app.before_request
def start_background_consumer() -> None:
    if not _started.is_set():
        DemoConsumer().start()
        _started.set()


@app.get('/health')
def health() -> tuple[dict, int]:
    return {'status': 'ok'}, 200


@app.get('/config')
def get_config() -> tuple[dict, int]:
    return load_config(), 200


@app.get('/state')
def state() -> tuple[dict, int]:
    return jsonify(get_all_states()), 200


@app.get('/eta/<train_id>')
def eta(train_id: str):
    state = get_train_state(train_id)
    if not state:
        return jsonify({'error': 'train not found'}), 404
    return jsonify(
        {
            'train_id': train_id,
            'position': state.get('position'),
            'event': state.get('event'),
            'prediction': state.get('prediction'),
        }
    )


if __name__ == '__main__':
    port = int(os.getenv('PORT', '8080'))
    DemoConsumer().start()
    _started.set()
    app.run(host='0.0.0.0', port=port)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)