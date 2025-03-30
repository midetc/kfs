from datetime import datetime
from db_storage import DBStorage

DAY_TARIFF = 1.68  # Тариф за день
NIGHT_TARIFF = 0.84  # Тариф за ніч
DAY_ROLLOVER = 100  # Накрутка за день
NIGHT_ROLLOVER = 80  # Накрутка за ніч

class DBMeterBilling:
    def __init__(self, db_params=None):
        """Ініціалізація класу з підключенням до бази даних"""
        self.db = DBStorage(**db_params) if db_params else DBStorage()
    
    def process_reading(self, meter_id, day_reading, night_reading):
        """Обробка показників лічильника"""
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d %H:%M:%S")
        
        meter_data = self.db.get_meter(meter_id)
        
        if meter_data is None:
            is_new = self.db.save_meter(meter_id, day_reading, night_reading)
            
            bill = {
                "meter_id": meter_id,
                "date": date_str,
                "day_consumption": 0,
                "night_consumption": 0,
                "day_cost": 0,
                "night_cost": 0,
                "total_cost": 0,
                "is_new": True
            }
            
            self.db.save_bill(
                meter_id,
                now,
                0, 0, 0, 0, 0,
                True
            )
        else:
            prev_day = meter_data["day_reading"]
            prev_night = meter_data["night_reading"]
            
            day_consumption = day_reading - prev_day
            night_consumption = night_reading - prev_night
            
            # Перевірка на накрутку показників
            if day_consumption < 0:
                day_consumption = DAY_ROLLOVER
            
            if night_consumption < 0:
                night_consumption = NIGHT_ROLLOVER
            
            day_cost = day_consumption * DAY_TARIFF
            night_cost = night_consumption * NIGHT_TARIFF
            total_cost = day_cost + night_cost
            
            self.db.save_meter(meter_id, day_reading, night_reading)
            
            bill = {
                "meter_id": meter_id,
                "date": date_str,
                "day_consumption": day_consumption,
                "night_consumption": night_consumption,
                "day_cost": day_cost,
                "night_cost": night_cost,
                "total_cost": total_cost,
                "is_new": False
            }
            
            self.db.save_bill(
                meter_id,
                now,
                day_consumption,
                night_consumption,
                day_cost,
                night_cost,
                total_cost,
                False
            )
        
        return bill
    
    def get_meter_data(self, meter_id):
        """Отримання даних лічильника"""
        return self.db.get_meter(meter_id)
    
    def get_all_meters(self):
        """Отримання всіх лічильників"""
        return self.db.get_all_meters()
    
    def get_history(self, meter_id=None):
        """Отримання історії показників"""
        return self.db.get_history(meter_id)

if __name__ == "__main__":
    try:
        billing = DBMeterBilling()
        
        while True:
            print("\nСистема обліку показників лічильників (PostgreSQL)")
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
                    
                    meter_data = billing.get_meter_data(meter_id)
                    if meter_data:
                        # Перевіряємо, чи нові показники не менші за попередні
                        if day_reading < meter_data["day_reading"]:
                            print(f"УВАГА: Денні показники ({day_reading}) менші за попередні ({meter_data['day_reading']})!")
                            confirm = input("Все одно продовжити? (так/ні): ")
                            if confirm.lower() != "так":
                                continue
                        
                        if night_reading < meter_data["night_reading"]:
                            print(f"УВАГА: Нічні показники ({night_reading}) менші за попередні ({meter_data['night_reading']})!")
                            confirm = input("Все одно продовжити? (так/ні): ")
                            if confirm.lower() != "так":
                                continue
                    
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
    except Exception as e:
        print(f"Помилка підключення до бази даних: {e}")
        print("Переконайтеся, що PostgreSQL запущено та бази даних доступна.") 