import json
import logging
import os
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler

LOG_FILENAME = "metrics.log"
JSON_FILENAME = "metrics.json"


class MetricsManager:
    def __init__(self):
        # --- logger ---
        self.logger = logging.getLogger("metrics_logger")
        self.logger.setLevel(logging.INFO)

        handler = RotatingFileHandler(LOG_FILENAME, maxBytes=1_000_000, backupCount=3)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # --- Cargar métricas persistentes ---
        self.metrics = self._load_metrics()

        # Control de sesión
        self.session_start = None

    # -----------------------------
    #   JSON
    # -----------------------------
    def _load_metrics(self):
        if not os.path.exists(JSON_FILENAME):
            return {"total_presses": 0, "sessions": [], "last_session": None}

        try:
            with open(JSON_FILENAME, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error cargando {JSON_FILENAME}: {e}")
            return {"total_presses": 0, "sessions": [], "last_session": None}

    def _save_metrics(self):
        try:
            with open(JSON_FILENAME, "w", encoding="utf-8") as f:
                json.dump(self.metrics, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Error guardando {JSON_FILENAME}: {e}")

    # -----------------------------
    #   Sesiones
    # -----------------------------
    def start_session(self):
        self.session_start = time.time()
        self.logger.info("session_start")

    def end_session(self):
        if not self.session_start:
            return

        duration = time.time() - self.session_start
        record = {
            "start": datetime.utcfromtimestamp(self.session_start).isoformat() + "Z",
            "end": datetime.utcnow().isoformat() + "Z",
            "duration_seconds": round(duration, 2)
        }

        self.metrics.setdefault("sessions", []).append(record)
        self.metrics["last_session"] = record

        self._save_metrics()
        self.logger.info(f"session_end duration={duration:.2f}s")

        self.session_start = None

    # -----------------------------
    #   Eventos
    # -----------------------------
    def register_button_press(self):
        total = self.metrics.get("total_presses", 0) + 1
        self.metrics["total_presses"] = total
        self._save_metrics()

        self.logger.info(f"button_press total_presses={total}")
        return total

    def register_reset(self):
        self.logger.info("counter_reset")