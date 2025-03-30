import json
import pika
import sys
import time
from config import RABBITMQ_CONFIG

class RabbitMQService:
    
    def __init__(self):
        self.connection = None
        self.channel = None
        self.connected = False
        self._connect()
    
    def _connect(self):
        max_retries = 5
        current_retry = 0
        
        while current_retry < max_retries:
            try:
                credentials = pika.PlainCredentials(
                    RABBITMQ_CONFIG["user"],
                    RABBITMQ_CONFIG["password"]
                )
                
                parameters = pika.ConnectionParameters(
                    host=RABBITMQ_CONFIG["host"],
                    port=RABBITMQ_CONFIG["port"],
                    credentials=credentials,
                    connection_attempts=3,
                    retry_delay=2
                )
                
                print(f"Спроба підключення до RabbitMQ на {RABBITMQ_CONFIG['host']}:{RABBITMQ_CONFIG['port']}")
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()
                
                self.channel.queue_declare(queue="meter_readings", durable=True)
                self.channel.queue_declare(queue="billing_results", durable=True)
                
                self.connected = True
                print("Успішне підключення до RabbitMQ")
                return True
                
            except Exception as e:
                current_retry += 1
                print(f"Помилка підключення до RabbitMQ: {e}")
                print(f"Спроба {current_retry} з {max_retries}")
                
                if current_retry < max_retries:
                    time.sleep(5)
                else:
                    print(f"Не вдалося підключитися до RabbitMQ після {max_retries} спроб")
                    self.connected = False
                    return False
    
    def send_message(self, queue, message):
        if not self.connected:
            print("Неможливо відправити повідомлення: немає з'єднання з RabbitMQ")
            return False
            
        try:
            if not self.connection or self.connection.is_closed:
                if not self._connect():
                    return False
                    
            self.channel.basic_publish(
                exchange="",
                routing_key=queue,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                )
            )
            return True
        except Exception as e:
            print(f"Помилка відправки повідомлення: {e}")
            self.connected = False
            return False
    
    def consume_messages(self, queue, callback):
        if not self.connected:
            print("Неможливо отримувати повідомлення: немає з'єднання з RabbitMQ")
            return False
            
        try:
            if not self.connection or self.connection.is_closed:
                if not self._connect():
                    return False
                    
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=queue,
                on_message_callback=self._process_message(callback),
                auto_ack=False
            )
            
            print(f"Очікування повідомлень з черги {queue}. Для виходу натисніть CTRL+C")
            self.channel.start_consuming()
            return True
        except KeyboardInterrupt:
            self.channel.stop_consuming()
            self.connection.close()
            return True
        except Exception as e:
            print(f"Помилка отримання повідомлень: {e}")
            self.connected = False
            return False
    
    def _process_message(self, callback):
        def process(ch, method, properties, body):
            try:
                message = json.loads(body)
                result = callback(message)
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return result
            except Exception as e:
                print(f"Помилка обробки повідомлення: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        return process
    
    def close(self):
        if self.connection and self.connection.is_open:
            self.connection.close() 