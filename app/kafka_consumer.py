import json
import os
import threading
import time

from confluent_kafka import Consumer

from config import load_config
from eta_engine import calculate_eta
from store import add_message, get_train_state, update_event, update_position, update_prediction
from tsdb import TsdbClient

KAFKA_BOOTSTRAP = os.getenv('KAFKA_BOOTSTRAP', 'kafka:9092')
TOPICS = os.getenv('KAFKA_TOPICS', 'metro_positions,metro_events').split(',')
GROUP_ID = os.getenv('KAFKA_GROUP_ID', 'eta-demo-consumer')


class DemoConsumer(threading.Thread):
    daemon = True

    def run(self) -> None:
        tsdb = TsdbClient()
        consumer = Consumer(
            {
                'bootstrap.servers': KAFKA_BOOTSTRAP,
                'group.id': GROUP_ID,
                'auto.offset.reset': 'earliest',
            }
        )
        consumer.subscribe(TOPICS)
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                time.sleep(1)
                continue

            payload = json.loads(msg.value().decode('utf-8'))
            train_id = payload['train_id']
            topic = msg.topic()
            add_message(topic, payload)

            if topic == 'metro_positions':
                update_position(train_id, payload)
                tsdb.write_position(payload)
            elif topic == 'metro_events':
                update_event(train_id, payload)

            state = get_train_state(train_id)
            if 'position' in state:
                cfg = load_config()
                position = state['position']
                event = state.get('event')
                historical_avg = tsdb.get_historical_average(
                    line_id=position.get('line_id', 'demo'),
                    station_id=position.get('station_id', 'unknown'),
                )
                prediction = calculate_eta(position, event, historical_avg, cfg)
                update_prediction(train_id, prediction)
                tsdb.write_prediction(prediction)
