#!/usr/bin/env python3

import psycopg2
from psycopg2 import sql
from datetime import datetime

class DBStorage:
    def __init__(self, dbname="meters_db", user="postgres", password="markaha317", host="localhost", port="5432"):
        self.connection_params = {
            "dbname": dbname,
            "user": user,
            "password": password,
            "host": host,
            "port": port
        }
        self._create_tables()
    
    def _connect(self):
        return psycopg2.connect(**self.connection_params)
    
    def _create_tables(self):
        conn = self._connect()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS meters (
                    meter_id VARCHAR(50) PRIMARY KEY,
                    day_reading FLOAT NOT NULL,
                    night_reading FLOAT NOT NULL,
                    last_update TIMESTAMP NOT NULL
                )
            """)
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS meter_history (
                    id SERIAL PRIMARY KEY,
                    meter_id VARCHAR(50) NOT NULL,
                    date TIMESTAMP NOT NULL,
                    day_consumption FLOAT NOT NULL,
                    night_consumption FLOAT NOT NULL,
                    day_cost FLOAT NOT NULL,
                    night_cost FLOAT NOT NULL,
                    total_cost FLOAT NOT NULL,
                    is_new BOOLEAN NOT NULL,
                    FOREIGN KEY (meter_id) REFERENCES meters(meter_id)
                )
            """)
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()
            conn.close()
    
    def save_meter(self, meter_id, day_reading, night_reading):
        conn = self._connect()
        cur = conn.cursor()
        now = datetime.now()
        
        try:
            cur.execute("SELECT * FROM meters WHERE meter_id = %s", (meter_id,))
            if cur.fetchone() is None:
                cur.execute("""
                    INSERT INTO meters (meter_id, day_reading, night_reading, last_update)
                    VALUES (%s, %s, %s, %s)
                """, (meter_id, day_reading, night_reading, now))
                is_new = True
            else:
                cur.execute("""
                    UPDATE meters
                    SET day_reading = %s, night_reading = %s, last_update = %s
                    WHERE meter_id = %s
                """, (day_reading, night_reading, now, meter_id))
                is_new = False
            
            conn.commit()
            return is_new
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()
            conn.close()
    
    def get_meter(self, meter_id):
        conn = self._connect()
        cur = conn.cursor()
        
        try:
            cur.execute("SELECT meter_id, day_reading, night_reading, last_update FROM meters WHERE meter_id = %s", (meter_id,))
            result = cur.fetchone()
            
            if result is None:
                return None
            
            return {
                "meter_id": result[0],
                "day_reading": result[1],
                "night_reading": result[2],
                "last_update": result[3]
            }
        finally:
            cur.close()
            conn.close()
    
    def get_all_meters(self):
        conn = self._connect()
        cur = conn.cursor()
        
        try:
            cur.execute("SELECT meter_id, day_reading, night_reading, last_update FROM meters")
            meters = {}
            
            for row in cur.fetchall():
                meters[row[0]] = {
                    "day_reading": row[1],
                    "night_reading": row[2],
                    "last_update": row[3]
                }
            
            return meters
        finally:
            cur.close()
            conn.close()
    
    def save_bill(self, meter_id, date, day_consumption, night_consumption, day_cost, night_cost, total_cost, is_new):
        conn = self._connect()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                INSERT INTO meter_history 
                (meter_id, date, day_consumption, night_consumption, day_cost, night_cost, total_cost, is_new)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (meter_id, date, day_consumption, night_consumption, day_cost, night_cost, total_cost, is_new))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()
            conn.close()
    
    def get_history(self, meter_id=None):
        conn = self._connect()
        cur = conn.cursor()
        
        try:
            if meter_id:
                cur.execute("""
                    SELECT meter_id, date, day_consumption, night_consumption, day_cost, night_cost, total_cost, is_new
                    FROM meter_history
                    WHERE meter_id = %s
                    ORDER BY date
                """, (meter_id,))
            else:
                cur.execute("""
                    SELECT meter_id, date, day_consumption, night_consumption, day_cost, night_cost, total_cost, is_new
                    FROM meter_history
                    ORDER BY date
                """)
            
            history = []
            for row in cur.fetchall():
                history.append({
                    "meter_id": row[0],
                    "date": row[1],
                    "day_consumption": row[2],
                    "night_consumption": row[3],
                    "day_cost": row[4],
                    "night_cost": row[5],
                    "total_cost": row[6],
                    "is_new": row[7]
                })
            
            return history
        finally:
            cur.close()
            conn.close() 