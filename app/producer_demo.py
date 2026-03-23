import json
import os
import time
from datetime import datetime, timedelta, timezone

from confluent_kafka import Producer

KAFKA_BOOTSTRAP = os.getenv('KAFKA_BOOTSTRAP', 'kafka:9092')


def build_messages() -> list[tuple[str, dict]]:
    now = datetime.now(timezone.utc)
    return [
        (
            'metro_positions',
            {
                'train_id': 'train-1',
                'line_id': 'red',
                'station_id': 'station-a',
                'distance_to_station_km': 3.2,
                'speed_kmh': 42.0,
                'ts': now.isoformat(),
            },
        ),
        (
            'metro_positions',
            {
                'train_id': 'train-2',
                'line_id': 'blue',
                'station_id': 'station-b',
                'distance_to_station_km': 4.8,
                'speed_kmh': 38.0,
                'ts': (now + timedelta(seconds=1)).isoformat(),
            },
        ),
        (
            'metro_events',
            {
                'train_id': 'train-1',
                'type': 'delay',
                'delay_sec': 25,
                'ts': (now + timedelta(seconds=2)).isoformat(),
            },
        ),
        (
            'metro_positions',
            {
                'train_id': 'train-1',
                'line_id': 'red',
                'station_id': 'station-a',
                'distance_to_station_km': 1.7,
                'speed_kmh': 34.0,
                'ts': (now + timedelta(seconds=3)).isoformat(),
            },
        ),
        (
            'metro_positions',
            {
                'train_id': 'train-2',
                'line_id': 'blue',
                'station_id': 'station-b',
                'distance_to_station_km': 2.9,
                'speed_kmh': 31.0,
                'ts': (now + timedelta(seconds=4)).isoformat(),
            },
        ),
    ]


def send_demo_messages(pause_sec: float = 0.6) -> int:
    producer = Producer({'bootstrap.servers': KAFKA_BOOTSTRAP})
    count = 0
    for topic, payload in build_messages():
        producer.produce(topic, key=payload['train_id'], value=json.dumps(payload).encode('utf-8'))
        producer.flush()
        count += 1
        if pause_sec:
            time.sleep(pause_sec)
    return count


def main() -> None:
    sent = send_demo_messages()
    print(f'sent {sent} demo messages')


if __name__ == '__main__':
    main()
