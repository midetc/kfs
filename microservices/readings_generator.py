#!/usr/bin/env python3

import sys
import os
import time
import random
from datetime import datetime

# Додаємо батьківський каталог до шляху для імпорту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.rabbitmq_service import RabbitMQService
from config import QUEUE_READINGS

class ReadingsGenerator:
    """Генератор показників лічильників для тестування системи"""
    
    def __init__(self):
        """Ініціалізація генератора"""
        self.rabbitmq = RabbitMQService()
        self.meters = {
            "123456": {"day": 1000, "night": 500},
            "987654": {"day": 2000, "night": 1000},
            "111111": {"day": 3000, "night": 1500},
            "222222": {"day": 4000, "night": 2000},
            "333333": {"day": 5000, "night": 2500}
        }
    
    def generate_readings(self, count=5, interval=2):
        """Генерація та відправка показників"""
        print(f"Генерація {count} показників з інтервалом {interval} секунд...")
        
        for i in range(count):
            # Вибір випадкового лічильника або створення нового
            if random.random() < 0.8 and self.meters:  # 80% існуючі лічильники
                meter_id = random.choice(list(self.meters.keys()))
                last_readings = self.meters[meter_id]
                
                # Випадкове збільшення показників
                day_increase = random.randint(10, 50)
                night_increase = random.randint(5, 30)
                
                # 10% ймовірність зниження показників для тестування накрутки
                if random.random() < 0.1:
                    if random.random() < 0.5:
                        day_increase = -random.randint(1, 50)
                    if random.random() < 0.5:
                        night_increase = -random.randint(1, 30)
                
                day_reading = last_readings["day"] + day_increase
                night_reading = last_readings["night"] + night_increase
                
                # Оновлення останніх показників
                self.meters[meter_id] = {"day": day_reading, "night": night_reading}
            else:  # 20% нові лічильники
                # Генерація випадкового номера лічильника
                meter_id = str(random.randint(100000, 999999))
                while meter_id in self.meters:
                    meter_id = str(random.randint(100000, 999999))
                
                # Випадкові початкові показники
                day_reading = random.randint(1000, 5000)
                night_reading = random.randint(500, 3000)
                
                # Збереження лічильника
                self.meters[meter_id] = {"day": day_reading, "night": night_reading}
            
            # Формування повідомлення
            message = {
                "meter_id": meter_id,
                "day_reading": day_reading,
                "night_reading": night_reading,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Відправка повідомлення
            if self.rabbitmq.send_message(QUEUE_READINGS, message):
                print(f"Відправлено показники: {message}")
            else:
                print(f"Помилка відправки показників: {message}")
            
            # Пауза між генераціями
            if i < count - 1:
                time.sleep(interval)
        
        print("Генерацію завершено")
    
    def close(self):
        """Закриття підключення"""
        self.rabbitmq.close()

if __name__ == "__main__":
    generator = ReadingsGenerator()
    
    try:
        count = int(input("Введіть кількість показників для генерації (за замовчуванням 5): ") or "5")
        interval = float(input("Введіть інтервал між генераціями в секундах (за замовчуванням 2): ") or "2")
        
        generator.generate_readings(count, interval)
    except KeyboardInterrupt:
        print("Генерацію перервано")
    except ValueError as e:
        print(f"Помилка введення: {e}")
    finally:
        generator.close() 