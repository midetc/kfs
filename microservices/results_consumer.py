#!/usr/bin/env python3

import sys
import os
import json
from datetime import datetime

# Додаємо батьківський каталог до шляху для імпорту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.rabbitmq_service import RabbitMQService
from config import QUEUE_BILLING

class ResultsConsumer:
    """Мікросервіс для отримання результатів обробки показників"""
    
    def __init__(self, output_file="billing_results.json"):
        """Ініціалізація споживача результатів"""
        self.rabbitmq = RabbitMQService()
        self.output_file = output_file
        self.results = self._load_results()
    
    def _load_results(self):
        """Завантаження раніше збережених результатів"""
        if os.path.exists(self.output_file):
            try:
                with open(self.output_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []
    
    def _save_results(self):
        """Збереження результатів у файл"""
        with open(self.output_file, 'w') as f:
            json.dump(self.results, f, indent=4)
    
    def start(self):
        """Запуск отримання результатів"""
        print(f"Запуск споживача результатів обробки показників (зберігання у {self.output_file})...")
        self.rabbitmq.consume_messages(QUEUE_BILLING, self.process_result)
    
    def process_result(self, result):
        """Обробка отриманого результату"""
        try:
            # Додавання результату до списку
            self.results.append(result)
            
            # Збереження оновленого списку
            self._save_results()
            
            # Виведення інформації про результат
            print(f"Отримано результат для лічильника {result['meter_id']} ({result['date']}):")
            if result["is_new"]:
                print(f"  Новий лічильник")
            else:
                print(f"  Споживання (день): {result['day_consumption']} кВт")
                print(f"  Споживання (ніч): {result['night_consumption']} кВт")
                print(f"  Вартість (день): {result['day_cost']:.2f} грн")
                print(f"  Вартість (ніч): {result['night_cost']:.2f} грн")
                print(f"  Загальна вартість: {result['total_cost']:.2f} грн")
            
            return True
        except Exception as e:
            print(f"Помилка обробки результату: {e}")
            return False

if __name__ == "__main__":
    try:
        output_file = input("Введіть ім'я файлу для збереження результатів (за замовчуванням billing_results.json): ") or "billing_results.json"
        consumer = ResultsConsumer(output_file)
        consumer.start()
    except KeyboardInterrupt:
        print("Споживання результатів перервано")
    except Exception as e:
        print(f"Помилка: {e}")