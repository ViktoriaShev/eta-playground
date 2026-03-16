import json
import os
import time
from datetime import datetime, timezone

from confluent_kafka import Producer

KAFKA_BOOTSTRAP = os.getenv('KAFKA_BOOTSTRAP', 'kafka:9092')


def build_messages() -> list[tuple[str, dict]]:
    now = datetime.now(timezone.utc).isoformat()
    return [
        (
            'metro_positions',
            {
                'train_id': 'train-1',
                'line_id': 'red',
                'station_id': 'station-a',
                'distance_to_station_km': 2.4,
                'speed_kmh': 36.0,
                'ts': now,
            },
        ),
        (
            'metro_events',
            {
                'train_id': 'train-1',
                'type': 'delay',
                'delay_sec': 25,
                'ts': now,
            },
        ),
        (
            'metro_positions',
            {
                'train_id': 'train-1',
                'line_id': 'red',
                'station_id': 'station-a',
                'distance_to_station_km': 1.8,
                'speed_kmh': 34.0,
                'ts': datetime.now(timezone.utc).isoformat(),
            },
        ),
    ]


def main() -> None:
    producer = Producer({'bootstrap.servers': KAFKA_BOOTSTRAP})
    for topic, payload in build_messages():
        producer.produce(topic, key=payload['train_id'], value=json.dumps(payload).encode('utf-8'))
        producer.flush()
        print(f'sent to {topic}: {payload}')
        time.sleep(1)


if __name__ == '__main__':
    main()
