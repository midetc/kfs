#!/usr/bin/env python3

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.rabbitmq_service import RabbitMQService
from services.billing_service import BillingService
from config import QUEUE_READINGS, QUEUE_BILLING

class BillingWorker:
    
    def __init__(self):
        self.rabbitmq = RabbitMQService()
        self.billing_service = BillingService()
        
    def start(self):
        print("Запуск обробника показників лічильників...")
        self.rabbitmq.consume_messages(QUEUE_READINGS, self.process_reading)
    
    def process_reading(self, message):
        try:
            meter_id = message.get("meter_id")
            day_reading = message.get("day_reading")
            night_reading = message.get("night_reading")
            
            if not all([meter_id, day_reading is not None, night_reading is not None]):
                print("Отримано неповні дані")
                return
            
            print(f"Обробка показників для лічильника {meter_id}: {day_reading} (день), {night_reading} (ніч)")
            
            result = self.billing_service.process_reading(meter_id, day_reading, night_reading)
            
            self.rabbitmq.send_message(QUEUE_BILLING, result)
            
            print(f"Показники оброблено: {result}")
            return result
        except Exception as e:
            print(f"Помилка обробки показників: {e}")
            return None

if __name__ == "__main__":
    worker = BillingWorker()
    worker.start()