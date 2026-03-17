# Обзор файлов проекта ETA Playground

## Корень репозитория

- `README.md` — основная документация проекта: архитектура пайплайна (Kafka → consumer/ETA engine → InfluxDB → Flask API), запуск через Docker Compose и Kubernetes, а также ограничения демо-версии.
- `docker-compose.yml` — локальная оркестрация 3 сервисов (`kafka`, `influxdb`, `app`) с переменными окружения и пробросом портов.
- `FILES_OVERVIEW.md` — этот файл: краткое объяснение назначения каждого файла в репозитории.

## Папка `app/`

- `app/app.py` — Flask API-приложение. Поднимает фоновый Kafka consumer, отдает эндпоинты `/health`, `/config`, `/state`, `/eta/<train_id>`.
- `app/kafka_consumer.py` — потоковый consumer Kafka (`metro_positions`, `metro_events`): читает события, обновляет in-memory state, пишет в InfluxDB и запускает расчет ETA.
- `app/eta_engine.py` — расчет ETA на основе текущей позиции/скорости, исторического среднего и delay-события.
- `app/tsdb.py` — клиентский слой к InfluxDB: запись позиций и прогнозов ETA + получение исторического среднего ETA.
- `app/store.py` — потокобезопасное in-memory хранилище текущего состояния поездов (`position`, `event`, `prediction`).
- `app/config.py` — загрузка YAML-конфига алгоритма по пути из `CONFIG_PATH`.
- `app/producer_demo.py` — генерация и отправка демонстрационных сообщений в Kafka для проверки пайплайна.
- `app/requirements.txt` — Python-зависимости runtime (`Flask`, `PyYAML`, `confluent-kafka`, `influxdb-client`).
- `app/Dockerfile` — сборка контейнера приложения (Python 3.11 slim, установка зависимостей, запуск `app.py`).

## Папка `config/`

- `config/algorithm.yaml` — локальный конфиг алгоритма ETA: флаги, веса, погодные/трафиковые коэффициенты и пороги.

## Папка `k8s/`

- `k8s/deployment.yaml` — Deployment для приложения `eta-service` (образ, env, подключение config map).
- `k8s/service.yaml` — Service для API приложения (ClusterIP, порт 80 → 8080).
- `k8s/configmap-algorithm.yaml` — ConfigMap с содержимым `algorithm.yaml` для контейнера приложения.
- `k8s/influxdb.yaml` — Service + Deployment для InfluxDB (инициализация через env).
- `k8s/kafka.yaml` — Service + Deployment для Kafka в режиме KRaft (single-node демо-конфигурация).
