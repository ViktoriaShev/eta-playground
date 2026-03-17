import os
from threading import Event

from flask import Flask, jsonify

from config import load_config
from kafka_consumer import DemoConsumer
from store import get_all_states, get_train_state

app = Flask(__name__)
_started = Event()


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
