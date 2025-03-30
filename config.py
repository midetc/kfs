import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "meters_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "7893"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432")
}

RABBITMQ_CONFIG = {
    "host": os.getenv("RABBITMQ_HOST", "localhost"),
    "port": int(os.getenv("RABBITMQ_PORT", "5672")),
    "user": os.getenv("RABBITMQ_USER", "guest"),
    "password": os.getenv("RABBITMQ_PASSWORD", "guest")
}

DAY_TARIFF = float(os.getenv("DAY_TARIFF", "1.68"))
NIGHT_TARIFF = float(os.getenv("NIGHT_TARIFF", "0.84"))
DAY_ROLLOVER = float(os.getenv("DAY_ROLLOVER", "100"))
NIGHT_ROLLOVER = float(os.getenv("NIGHT_ROLLOVER", "80"))

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "5000"))

QUEUE_READINGS = "meter_readings"
QUEUE_BILLING = "billing_results" 