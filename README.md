# ETA playground demo

Учебный пример, который показывает базовую связку:

- Kafka как шина событий
- InfluxDB как БД временных рядов
- Flask как простой API-сервис ETA

## Что делает проект

1. `producer_demo.py` публикует несколько событий в Kafka.
2. `kafka_consumer.py` читает `metro_positions` и `metro_events`.
3. Последнее состояние по поезду хранится в памяти.
4. Историческое среднее ETA читается из InfluxDB.
5. Новое предсказание ETA снова пишется в InfluxDB.
6. API отдает состояние по `/eta/train-1`.

## Быстрый запуск

```bash
docker compose up --build -d
python app/producer_demo.py
curl http://localhost:8080/eta/train-1
```

> Если запускаешь `producer_demo.py` с хоста, поставь зависимости локально и экспортируй `KAFKA_BOOTSTRAP=localhost:9092`.
