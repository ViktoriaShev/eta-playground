# ETA playground demo

Учебный проект, который показывает базовый pipeline:

`Kafka (events) -> consumer/ETA engine -> InfluxDB (time-series) -> Flask API`

## Что делает каждый модуль

- `app/producer_demo.py` — отправляет демо-события в Kafka-топики `metro_positions` и `metro_events`.
- `app/kafka_consumer.py` — читает топики, обновляет in-memory state, пишет данные в InfluxDB и запускает расчет ETA.
- `app/eta_engine.py` — считает ETA на основе:
  - текущей скорости/дистанции,
  - исторического среднего ETA из InfluxDB,
  - события задержки (`delay_sec`), если пришло.
- `app/tsdb.py` — слой записи/чтения time-series данных в InfluxDB.
- `app/store.py` — простое in-memory хранилище текущего состояния по поезду.
- `app/app.py` — Flask API:
  - `GET /health`
  - `GET /config`
  - `GET /state`
  - `GET /eta/<train_id>`

## Как работает поток данных

1. Producer публикует события позиции/события.
2. Consumer читает сообщения из Kafka.
3. Позиции сохраняются в InfluxDB (`train_positions`).
4. Consumer берет историческое среднее из `eta_predictions`.
5. ETA engine рассчитывает новое значение ETA.
6. Новое предсказание сохраняется в InfluxDB (`eta_predictions`).
7. API отдает последнюю агрегацию состояния.

## Запуск через Docker Compose

```bash
docker compose up --build -d
```

Отправить тестовые события:

```bash
export KAFKA_BOOTSTRAP=localhost:9092
python app/producer_demo.py
```

Проверить API:

```bash
curl http://localhost:8080/health
curl http://localhost:8080/state
curl http://localhost:8080/eta/train-1
```

Остановить:

```bash
docker compose down
```

---

## Запуск в Kubernetes (локальный кластер: kind/minikube)

> В этом демо Kafka и InfluxDB разворачиваются прямо в k8s-манифестах (single-node/single-replica, без персистентных томов).

### 1) Собрать образ приложения

```bash
docker build -t eta-playground:dev ./app
```

Для `kind` загрузить образ в кластер:

```bash
kind load docker-image eta-playground:dev
```

### 2) Применить манифесты

```bash
kubectl apply -f k8s/configmap-algorithm.yaml
kubectl apply -f k8s/kafka.yaml
kubectl apply -f k8s/influxdb.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

### 3) Проверить готовность

```bash
kubectl get pods
kubectl get svc
```

### 4) Открыть API локально

```bash
kubectl port-forward svc/eta-service 8080:80
```

В отдельном терминале:

```bash
curl http://localhost:8080/health
curl http://localhost:8080/state
```

### 5) Отправить демо-сообщения в Kafka внутри кластера

```bash
kubectl run producer --rm -it --restart=Never \
  --image=eta-playground:dev \
  --env="KAFKA_BOOTSTRAP=kafka:9092" \
  --command -- python producer_demo.py
```

После этого:

```bash
curl http://localhost:8080/eta/train-1
```

## Ограничения учебного варианта

- Нет персистентного хранения (после рестарта данные теряются).
- Нет отдельного deployment для consumer (consumer запускается в Flask-процессе).
- Нет auth/TLS и production hardening.
- Kafka/InfluxDB конфигурация минимальная, только для локальной демонстрации.


## Веб-интерфейс

После запуска откройте в браузере:

```bash
http://localhost:8080/
```

На странице можно:

- отправить демонстрационные события в Kafka кнопкой;
- увидеть последние полученные сообщения;
- посмотреть текущее состояние поездов;
- увидеть рассчитанное ETA в простом интерфейсе.
