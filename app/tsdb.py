import os
from datetime import datetime, timedelta, timezone

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

INFLUX_URL = os.getenv('INFLUX_URL', 'http://influxdb:8086')
INFLUX_TOKEN = os.getenv('INFLUX_TOKEN', 'demo-token-demo-token-demo-token')
INFLUX_ORG = os.getenv('INFLUX_ORG', 'demo-org')
INFLUX_BUCKET = os.getenv('INFLUX_BUCKET', 'eta-demo')


class TsdbClient:
    def __init__(self) -> None:
        self.client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()

    def write_position(self, payload: dict) -> None:
        point = (
            Point('train_positions')
            .tag('train_id', payload['train_id'])
            .tag('line_id', payload.get('line_id', 'demo'))
            .tag('station_id', payload.get('station_id', 'unknown'))
            .field('distance_to_station_km', float(payload.get('distance_to_station_km', 0.0)))
            .field('speed_kmh', float(payload.get('speed_kmh', 0.0)))
            .time(payload.get('ts', datetime.now(timezone.utc).isoformat()), WritePrecision.NS)
        )
        self.write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)

    def write_prediction(self, payload: dict) -> None:
        point = (
            Point('eta_predictions')
            .tag('train_id', payload['train_id'])
            .tag('line_id', payload.get('line_id', 'demo'))
            .tag('station_id', payload.get('station_id', 'unknown'))
            .field('eta_sec', float(payload['eta_sec']))
            .field('historical_avg_sec', float(payload['historical_avg_sec']))
            .field('current_eta_sec', float(payload['current_eta_sec']))
            .field('delay_sec', float(payload['delay_sec']))
            .time(payload.get('generated_at', datetime.now(timezone.utc).isoformat()), WritePrecision.NS)
        )
        self.write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)

    def get_historical_average(self, line_id: str, station_id: str, lookback_minutes: int = 60) -> float:
        start = datetime.now(timezone.utc) - timedelta(minutes=lookback_minutes)
        flux = f'''
from(bucket: "{INFLUX_BUCKET}")
  |> range(start: {start.isoformat()})
  |> filter(fn: (r) => r._measurement == "eta_predictions")
  |> filter(fn: (r) => r.line_id == "{line_id}" and r.station_id == "{station_id}")
  |> filter(fn: (r) => r._field == "eta_sec")
  |> mean()
'''
        tables = self.query_api.query(org=INFLUX_ORG, query=flux)
        for table in tables:
            for record in table.records:
                value = record.get_value()
                if value is not None:
                    return float(value)
        return 120.0
