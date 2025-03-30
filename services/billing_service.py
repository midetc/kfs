#!/usr/bin/env python3

from datetime import datetime
from db_storage import DBStorage
from config import DAY_TARIFF, NIGHT_TARIFF, DAY_ROLLOVER, NIGHT_ROLLOVER, DB_CONFIG

class BillingService:
    
    def __init__(self):
        self.db = DBStorage(**DB_CONFIG)
    
    def process_reading(self, meter_id, day_reading, night_reading):
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d %H:%M:%S")
        
        meter_data = self.db.get_meter(meter_id)
        
        if meter_data is None:
            self.db.save_meter(meter_id, day_reading, night_reading)
            
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
        return self.db.get_meter(meter_id)
    
    def get_all_meters(self):
        return self.db.get_all_meters()
    
    def get_history(self, meter_id=None):
        return self.db.get_history(meter_id) 