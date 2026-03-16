# app/app.py
from flask import Flask, jsonify
import yaml
import os

app = Flask(__name__)

CONFIG_PATH = "/config/algorithm.yaml"

def load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception:
        return {}

@app.route("/config")
def get_config():
    return jsonify(load_config())

@app.route("/eta")
def get_eta():
    cfg = load_config()
    # простая "фейковая" формула для демонстрации
    weights = cfg.get("algorithm", {}).get("weights", {})
    speed = 40  # например
    hist = 0.5
    w_speed = weights.get("speed_based", 0.0)
    w_hist = weights.get("historical", 0.0)
    eta_score = (speed * w_speed) + (hist * 100 * w_hist)
    return jsonify({"eta_score": eta_score, "weights": weights})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)