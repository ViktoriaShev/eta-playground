import os
from threading import Event, Thread

from flask import Flask, jsonify, render_template

from config import load_config
from kafka_consumer import DemoConsumer
from producer_demo import send_demo_messages
from store import get_all_states, get_recent_messages, get_train_state

app = Flask(__name__)
_started = Event()


def ensure_background_consumer() -> None:
    if not _started.is_set():
        DemoConsumer().start()
        _started.set()


@app.before_request
def start_background_consumer() -> None:
    ensure_background_consumer()


@app.get('/')
def index():
    return render_template('index.html')


@app.get('/health')
def health() -> tuple[dict, int]:
    return {'status': 'ok'}, 200


@app.get('/config')
def get_config() -> tuple[dict, int]:
    return load_config(), 200


@app.get('/state')
def state() -> tuple[dict, int]:
    return jsonify(get_all_states()), 200


@app.get('/events')
def events() -> tuple[dict, int]:
    return jsonify({'items': get_recent_messages()}), 200


@app.post('/demo/send')
def demo_send() -> tuple[dict, int]:
    try:
        count = send_demo_messages(pause_sec=0.2)
        return {'status': 'ok', 'sent': count}, 200
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500


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
    ensure_background_consumer()
    app.run(host='0.0.0.0', port=port)
