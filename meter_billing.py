#!/usr/bin/env python3

import json
import os
from datetime import datetime

# Константи
DAY_TARIFF = 1.68  # Тариф за день
NIGHT_TARIFF = 0.84  # Тариф за ніч
DAY_ROLLOVER = 100  # Накрутка за день
NIGHT_ROLLOVER = 80  # Накрутка за ніч
DATA_FILE = "meters_data.json"  # Файл для зберігання даних

class MeterBilling:
    def __init__(self, data_file=DATA_FILE):
        self.data_file = data_file
        self.meters_data = self._load_data()
        self.history = self._load_history()
    
    def _load_data(self):
        """Завантаження даних з файлу"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {"meters": {}, "history": []}
        return {"meters": {}, "history": []}
    
    def _load_history(self):
        """Завантаження історії"""
        return self.meters_data.get("history", [])

    def _save_data(self):
        """Збереження даних у файл"""
        with open(self.data_file, 'w') as f:
            json.dump(self.meters_data, f, indent=4)
    
    def process_reading(self, meter_id, day_reading, night_reading):
        """Обробка показників лічильника"""
        meters = self.meters_data.get("meters", {})
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Перевірка чи є лічильник вже у базі
        if meter_id not in meters:
            # Новий лічильник
            meters[meter_id] = {
                "day_reading": day_reading,
                "night_reading": night_reading,
                "last_update": now
            }
            bill = {
                "meter_id": meter_id,
                "date": now,
                "day_consumption": 0,
                "night_consumption": 0,
                "day_cost": 0,
                "night_cost": 0,
                "total_cost": 0,
                "is_new": True
            }
        else:
            # Існуючий лічильник
            prev_day = meters[meter_id]["day_reading"]
            prev_night = meters[meter_id]["night_reading"]
            
            # Розрахунок споживання
            day_consumption = day_reading - prev_day
            night_consumption = night_reading - prev_night
            
            # Перевірка на накрутку показників
            if day_consumption < 0:
                day_consumption = DAY_ROLLOVER
            
            if night_consumption < 0:
                night_consumption = NIGHT_ROLLOVER
            
            # Розрахунок вартості
            day_cost = day_consumption * DAY_TARIFF
            night_cost = night_consumption * NIGHT_TARIFF
            total_cost = day_cost + night_cost
            
            # Оновлення даних лічильника
            meters[meter_id] = {
                "day_reading": day_reading,
                "night_reading": night_reading,
                "last_update": now
            }
            
            bill = {
                "meter_id": meter_id,
                "date": now,
                "day_consumption": day_consumption,
                "night_consumption": night_consumption,
                "day_cost": day_cost,
                "night_cost": night_cost,
                "total_cost": total_cost,
                "is_new": False
            }
        
        # Зберігаємо історію
        self.history.append(bill)
        
        # Оновлюємо дані
        self.meters_data["meters"] = meters
        self.meters_data["history"] = self.history
        self._save_data()
        
        return bill
    
    def get_meter_data(self, meter_id):
        """Отримання даних лічильника"""
        meters = self.meters_data.get("meters", {})
        return meters.get(meter_id)
    
    def get_all_meters(self):
        """Отримання всіх лічильників"""
        return self.meters_data.get("meters", {})
    
    def get_history(self, meter_id=None):
        """Отримання історії показників"""
        if meter_id:
            return [bill for bill in self.history if bill["meter_id"] == meter_id]
        return self.history


if __name__ == "__main__":
    billing = MeterBilling()
    
    while True:
        print("\nСистема обліку показників лічильників")
        print("1. Ввести показники лічильника")
        print("2. Переглянути всі лічильники")
        print("3. Переглянути історію показників")
        print("0. Вихід")
        
        choice = input("Оберіть опцію: ")
        
        if choice == "1":
            meter_id = input("Введіть номер лічильника: ")
            try:
                day_reading = float(input("Введіть денні показники: "))
                night_reading = float(input("Введіть нічні показники: "))
                
                result = billing.process_reading(meter_id, day_reading, night_reading)
                
                if result["is_new"]:
                    print(f"Новий лічильник {meter_id} додано.")
                else:
                    print(f"\nРахунок для лічильника {meter_id}:")
                    print(f"Споживання (день): {result['day_consumption']} кВт")
                    print(f"Споживання (ніч): {result['night_consumption']} кВт")
                    print(f"Вартість (день): {result['day_cost']:.2f} грн")
                    print(f"Вартість (ніч): {result['night_cost']:.2f} грн")
                    print(f"Загальна вартість: {result['total_cost']:.2f} грн")
            except ValueError:
                print("Помилка: введіть числові значення для показників.")
        
        elif choice == "2":
            meters = billing.get_all_meters()
            if not meters:
                print("Немає доданих лічильників.")
            else:
                print("\nСписок лічильників:")
                for meter_id, data in meters.items():
                    print(f"Лічильник {meter_id}:")
                    print(f"  День: {data['day_reading']}")
                    print(f"  Ніч: {data['night_reading']}")
                    print(f"  Останнє оновлення: {data['last_update']}")
        
        elif choice == "3":
            meter_id = input("Введіть номер лічильника (або залиште порожнім для всіх): ")
            history = billing.get_history(meter_id if meter_id else None)
            
            if not history:
                print("Історія порожня.")
            else:
                print("\nІсторія показників:")
                for entry in history:
                    print(f"Лічильник {entry['meter_id']} ({entry['date']}):")
                    if not entry["is_new"]:
                        print(f"  Споживання (день): {entry['day_consumption']} кВт")
                        print(f"  Споживання (ніч): {entry['night_consumption']} кВт")
                        print(f"  Загальна вартість: {entry['total_cost']:.2f} грн")
        
        elif choice == "0":
            print("До побачення!")
            break
        
        else:
            print("Невірний вибір. Спробуйте ще раз.") 