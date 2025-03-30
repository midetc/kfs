import sys
import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.rabbitmq_service import RabbitMQService
from services.billing_service import BillingService
from config import QUEUE_READINGS, API_PORT

app = Flask(__name__)
CORS(app)

rabbitmq = RabbitMQService()
billing_service = BillingService()

@app.route('/health', methods=['GET'])
def health_check():
    status = {
        "status": "ok",
        "services": {
            "rabbitmq": "ok" if rabbitmq.connected else "down",
            "api": "ok"
        }
    }
    
    if not rabbitmq.connected:
        return jsonify(status), 503
    
    return jsonify(status)

@app.route('/meters', methods=['GET'])
def get_meters():
    try:
        meters = billing_service.get_all_meters()
        return jsonify({"meters": meters})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/meters/<meter_id>', methods=['GET'])
def get_meter(meter_id):
    try:
        meter = billing_service.get_meter_data(meter_id)
        if meter:
            return jsonify({"meter": meter})
        else:
            return jsonify({"error": "Лічильник не знайдено"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/readings', methods=['POST'])
def submit_readings():
    try:
        if not rabbitmq.connected:
            return jsonify({"error": "Сервіс RabbitMQ недоступний. Показники не можуть бути оброблені зараз."}), 503
        
        data = request.json
        
        if not data or not all(key in data for key in ['meter_id', 'day_reading', 'night_reading']):
            return jsonify({"error": "Неповні дані. Необхідні поля: meter_id, day_reading, night_reading"}), 400
        
        try:
            meter_id = str(data['meter_id'])
            day_reading = float(data['day_reading'])
            night_reading = float(data['night_reading'])
        except (ValueError, TypeError):
            return jsonify({"error": "Неправильний формат даних"}), 400
        
        if day_reading < 0 or night_reading < 0:
            return jsonify({"error": "Показники не можуть бути від'ємними"}), 400
        
        meter_data = billing_service.get_meter_data(meter_id)
        
        warnings = []
        if meter_data:
            if day_reading < meter_data["day_reading"]:
                warnings.append(f"Денні показники ({day_reading}) менші за попередні ({meter_data['day_reading']})")
            
            if night_reading < meter_data["night_reading"]:
                warnings.append(f"Нічні показники ({night_reading}) менші за попередні ({meter_data['night_reading']})")
        
        message = {
            "meter_id": meter_id,
            "day_reading": day_reading,
            "night_reading": night_reading
        }
        
        if rabbitmq.send_message(QUEUE_READINGS, message):
            response = {
                "message": "Показники успішно відправлено на обробку",
                "meter_id": meter_id
            }
            
            if warnings:
                response["warnings"] = warnings
            
            return jsonify(response)
        else:
            return jsonify({"error": "Помилка відправки показників. Сервіс RabbitMQ недоступний."}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/history', methods=['GET'])
def get_history():
    try:
        history = billing_service.get_history()
        return jsonify({"history": history})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/history/<meter_id>', methods=['GET'])
def get_meter_history(meter_id):
    try:
        history = billing_service.get_history(meter_id)
        return jsonify({"history": history})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print(f"Запуск API-сервера на порту {API_PORT}")
    app.run(host='0.0.0.0', port=API_PORT, debug=True) 