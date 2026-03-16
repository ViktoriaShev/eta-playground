from collections import defaultdict
from threading import Lock

_state = defaultdict(dict)
_lock = Lock()


def update_position(train_id: str, payload: dict) -> None:
    with _lock:
        _state[train_id]['position'] = payload


def update_event(train_id: str, payload: dict) -> None:
    with _lock:
        _state[train_id]['event'] = payload


def update_prediction(train_id: str, payload: dict) -> None:
    with _lock:
        _state[train_id]['prediction'] = payload


def get_train_state(train_id: str) -> dict:
    with _lock:
        return dict(_state.get(train_id, {}))


def get_all_states() -> dict:
    with _lock:
        return {train_id: dict(value) for train_id, value in _state.items()}
