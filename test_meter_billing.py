#!/usr/bin/env python3

import unittest
import os
import json
from meter_billing import MeterBilling

class TestMeterBilling(unittest.TestCase):
    
    def setUp(self):
        # Використовуємо тестовий файл для даних
        self.test_file = "test_meters_data.json"
        
        # Видалення тестового файлу перед кожним тестом
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
            
        # Створюємо екземпляр класу з тестовим файлом
        self.billing = MeterBilling(self.test_file)
    
    def tearDown(self):
        # Видалення тестового файлу після кожного тесту
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_update_existing_meter(self):
        """Тест на оновлення показників вже існуючого лічильника"""
        # Додаємо новий лічильник
        self.billing.process_reading("123456", 1000, 500)
        
        # Оновлюємо показники
        result = self.billing.process_reading("123456", 1100, 550)
        
        # Перевіряємо результати
        self.assertEqual(result["day_consumption"], 100)
        self.assertEqual(result["night_consumption"], 50)
        self.assertEqual(result["day_cost"], 100 * 1.68)
        self.assertEqual(result["night_cost"], 50 * 0.84)
        self.assertEqual(result["total_cost"], 100 * 1.68 + 50 * 0.84)
        self.assertFalse(result["is_new"])
    
    def test_new_meter(self):
        """Тест на отримання показників від нового лічильника"""
        # Додаємо новий лічильник
        result = self.billing.process_reading("987654", 2000, 1000)
        
        # Перевіряємо результати
        self.assertEqual(result["day_consumption"], 0)
        self.assertEqual(result["night_consumption"], 0)
        self.assertEqual(result["day_cost"], 0)
        self.assertEqual(result["night_cost"], 0)
        self.assertEqual(result["total_cost"], 0)
        self.assertTrue(result["is_new"])
        
        # Перевіряємо, що лічильник збережений
        meter_data = self.billing.get_meter_data("987654")
        self.assertIsNotNone(meter_data)
        self.assertEqual(meter_data["day_reading"], 2000)
        self.assertEqual(meter_data["night_reading"], 1000)
    
    def test_lower_night_readings(self):
        """Тест на отримання показників з заниженими нічними показниками"""
        # Додаємо новий лічильник
        self.billing.process_reading("111111", 1000, 500)
        
        # Оновлюємо з заниженими нічними показниками
        result = self.billing.process_reading("111111", 1100, 400)
        
        # Перевіряємо результати (має бути накрутка NIGHT_ROLLOVER)
        self.assertEqual(result["day_consumption"], 100)
        self.assertEqual(result["night_consumption"], 80)  # Накрутка
        self.assertEqual(result["day_cost"], 100 * 1.68)
        self.assertEqual(result["night_cost"], 80 * 0.84)
        self.assertEqual(result["total_cost"], 100 * 1.68 + 80 * 0.84)
    
    def test_lower_day_readings(self):
        """Тест на отримання показників з заниженими денними показниками"""
        # Додаємо новий лічильник
        self.billing.process_reading("222222", 1000, 500)
        
        # Оновлюємо з заниженими денними показниками
        result = self.billing.process_reading("222222", 900, 550)
        
        # Перевіряємо результати (має бути накрутка DAY_ROLLOVER)
        self.assertEqual(result["day_consumption"], 100)  # Накрутка
        self.assertEqual(result["night_consumption"], 50)
        self.assertEqual(result["day_cost"], 100 * 1.68)
        self.assertEqual(result["night_cost"], 50 * 0.84)
        self.assertEqual(result["total_cost"], 100 * 1.68 + 50 * 0.84)
    
    def test_lower_both_readings(self):
        """Тест на отримання показників з заниженими денними та нічними показниками"""
        # Додаємо новий лічильник
        self.billing.process_reading("333333", 1000, 500)
        
        # Оновлюємо з заниженими показниками
        result = self.billing.process_reading("333333", 900, 400)
        
        # Перевіряємо результати (мають бути обидві накрутки)
        self.assertEqual(result["day_consumption"], 100)  # Накрутка день
        self.assertEqual(result["night_consumption"], 80)  # Накрутка ніч
        self.assertEqual(result["day_cost"], 100 * 1.68)
        self.assertEqual(result["night_cost"], 80 * 0.84)
        self.assertEqual(result["total_cost"], 100 * 1.68 + 80 * 0.84)
    
    def test_history_is_saved(self):
        """Тест на перевірку збереження історії"""
        # Додаємо кілька показників
        self.billing.process_reading("444444", 1000, 500)
        self.billing.process_reading("444444", 1100, 550)
        self.billing.process_reading("555555", 2000, 1000)
        
        # Перевіряємо історію для конкретного лічильника
        history_444444 = self.billing.get_history("444444")
        self.assertEqual(len(history_444444), 2)
        
        # Перевіряємо загальну історію
        all_history = self.billing.get_history()
        self.assertEqual(len(all_history), 3)

if __name__ == "__main__":
    unittest.main() 