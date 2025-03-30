#!/usr/bin/env python3

import unittest
import os
from unittest.mock import MagicMock, patch
from datetime import datetime
from db_meter_billing import DBMeterBilling

class TestDBMeterBilling(unittest.TestCase):
    
    def setUp(self):
        self.db_mock = MagicMock()
        
        self.db_storage_patch = patch('db_meter_billing.DBStorage', return_value=self.db_mock)
        self.db_storage_mock = self.db_storage_patch.start()
        self.billing = DBMeterBilling()
    
    def tearDown(self):
        self.db_storage_patch.stop()
    
    def test_update_existing_meter(self):
        """Тест на оновлення показників вже існуючого лічильника"""
        meter_id = "123456"
        prev_day = 1000
        prev_night = 500
        new_day = 1100
        new_night = 550
        now = datetime.now()
        
        self.db_mock.get_meter.return_value = {
            "meter_id": meter_id,
            "day_reading": prev_day,
            "night_reading": prev_night,
            "last_update": now
        }
        
        result = self.billing.process_reading(meter_id, new_day, new_night)
        
        # Перевірка результатів
        self.assertEqual(result["day_consumption"], 100)
        self.assertEqual(result["night_consumption"], 50)
        self.assertEqual(result["day_cost"], 100 * 1.68)
        self.assertEqual(result["night_cost"], 50 * 0.84)
        self.assertEqual(result["total_cost"], 100 * 1.68 + 50 * 0.84)
        self.assertFalse(result["is_new"])
        
        self.db_mock.get_meter.assert_called_once_with(meter_id)
        self.db_mock.save_meter.assert_called_once_with(meter_id, new_day, new_night)
        self.db_mock.save_bill.assert_called_once()
    
    def test_new_meter(self):
        """Тест на отримання показників від нового лічильника"""
        meter_id = "987654"
        day_reading = 2000
        night_reading = 1000
        
        self.db_mock.get_meter.return_value = None
        
        result = self.billing.process_reading(meter_id, day_reading, night_reading)
        
        self.assertEqual(result["day_consumption"], 0)
        self.assertEqual(result["night_consumption"], 0)
        self.assertEqual(result["day_cost"], 0)
        self.assertEqual(result["night_cost"], 0)
        self.assertEqual(result["total_cost"], 0)
        self.assertTrue(result["is_new"])
        
        self.db_mock.get_meter.assert_called_once_with(meter_id)
        self.db_mock.save_meter.assert_called_once_with(meter_id, day_reading, night_reading)
        self.db_mock.save_bill.assert_called_once()
    
    def test_lower_night_readings(self):
        """Тест на отримання показників з заниженими нічними показниками"""
        meter_id = "111111"
        prev_day = 1000
        prev_night = 500
        new_day = 1100
        new_night = 400  
        now = datetime.now()
        
        self.db_mock.get_meter.return_value = {
            "meter_id": meter_id,
            "day_reading": prev_day,
            "night_reading": prev_night,
            "last_update": now
        }
        
        result = self.billing.process_reading(meter_id, new_day, new_night)
        
        self.assertEqual(result["day_consumption"], 100)
        self.assertEqual(result["night_consumption"], 80)  # Накрутка
        self.assertEqual(result["day_cost"], 100 * 1.68)
        self.assertEqual(result["night_cost"], 80 * 0.84)
        self.assertEqual(result["total_cost"], 100 * 1.68 + 80 * 0.84)
    
    def test_lower_day_readings(self):
        """Тест на отримання показників з заниженими денними показниками"""
        meter_id = "222222"
        prev_day = 1000
        prev_night = 500
        new_day = 900  
        new_night = 550
        now = datetime.now()
        
        self.db_mock.get_meter.return_value = {
            "meter_id": meter_id,
            "day_reading": prev_day,
            "night_reading": prev_night,
            "last_update": now
        }
        
        result = self.billing.process_reading(meter_id, new_day, new_night)
        
        self.assertEqual(result["day_consumption"], 100)  # Накрутка
        self.assertEqual(result["night_consumption"], 50)
        self.assertEqual(result["day_cost"], 100 * 1.68)
        self.assertEqual(result["night_cost"], 50 * 0.84)
        self.assertEqual(result["total_cost"], 100 * 1.68 + 50 * 0.84)
    
    def test_lower_both_readings(self):
        """Тест на отримання показників з заниженими денними та нічними показниками"""
        meter_id = "333333"
        prev_day = 1000
        prev_night = 500
        new_day = 900  
        new_night = 400  
        now = datetime.now()
        
        self.db_mock.get_meter.return_value = {
            "meter_id": meter_id,
            "day_reading": prev_day,
            "night_reading": prev_night,
            "last_update": now
        }
        
        result = self.billing.process_reading(meter_id, new_day, new_night)
        
        self.assertEqual(result["day_consumption"], 100)  # Накрутка день
        self.assertEqual(result["night_consumption"], 80)  # Накрутка ніч
        self.assertEqual(result["day_cost"], 100 * 1.68)
        self.assertEqual(result["night_cost"], 80 * 0.84)
        self.assertEqual(result["total_cost"], 100 * 1.68 + 80 * 0.84)
    
    def test_get_meter_data(self):
        """Тест на отримання даних лічильника"""
        meter_id = "444444"
        self.billing.get_meter_data(meter_id)
        self.db_mock.get_meter.assert_called_once_with(meter_id)
    
    def test_get_all_meters(self):
        """Тест на отримання всіх лічильників"""
        self.billing.get_all_meters()
        self.db_mock.get_all_meters.assert_called_once()
    
    def test_get_history(self):
        """Тест на отримання історії"""
        meter_id = "555555"
        self.billing.get_history(meter_id)
        self.db_mock.get_history.assert_called_once_with(meter_id)
        
        self.db_mock.get_history.reset_mock()
        self.billing.get_history()
        self.db_mock.get_history.assert_called_once_with(None)

if __name__ == "__main__":
    unittest.main() 