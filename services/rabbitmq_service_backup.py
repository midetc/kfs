import json
import pika
import sys
import time
from config import RABBITMQ_CONFIG

class RabbitMQService:
    """Ð¡ÐµÑ€Ð²Ñ–Ñ Ð´Ð»Ñ Ñ€Ð¾Ð±Ð¾Ñ‚Ð¸ Ð· RabbitMQ"""
    
    def __init__(self):
        """Ð†Ð½Ñ–Ñ†Ñ–Ð°Ð»Ñ–Ð·Ð°Ñ†Ñ–Ñ Ð¿Ñ–Ð´ÐºÐ»ÑŽÑ‡ÐµÐ½Ð½Ñ Ð´Ð¾ RabbitMQ"""
        self.connection = None
        self.channel = None
        self.connected = False
        self._connect()
    
    def _connect(self):
        """Ð’ÑÑ‚Ð°Ð½Ð¾Ð²Ð»ÐµÐ½Ð½Ñ Ð¿Ñ–Ð´ÐºÐ»ÑŽÑ‡ÐµÐ½Ð½Ñ Ð´Ð¾ RabbitMQ"""
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
                
                print(f"Ð¡Ð¿Ñ€Ð¾Ð±Ð° Ð¿Ñ–Ð´ÐºÐ»ÑŽÑ‡ÐµÐ½Ð½Ñ Ð´Ð¾ RabbitMQ Ð½Ð° {RABBITMQ_CONFIG['host']}:{RABBITMQ_CONFIG['port']}")
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()
                
                # ÐžÐ³Ð¾Ð»Ð¾ÑˆÐµÐ½Ð½Ñ Ñ‡ÐµÑ€Ð³
                self.channel.queue_declare(queue="meter_readings", durable=True)
                self.channel.queue_declare(queue="billing_results", durable=True)
                
                self.connected = True
                print("Ð£ÑÐ¿Ñ–ÑˆÐ½Ðµ Ð¿Ñ–Ð´ÐºÐ»ÑŽÑ‡ÐµÐ½Ð½Ñ Ð´Ð¾ RabbitMQ")
                return True
                
            except Exception as e:
                current_retry += 1
                print(f"ÐŸÐ¾Ð¼Ð¸Ð»ÐºÐ° Ð¿Ñ–Ð´ÐºÐ»ÑŽÑ‡ÐµÐ½Ð½Ñ Ð´Ð¾ RabbitMQ: {e}")
                print(f"Ð¡Ð¿Ñ€Ð¾Ð±Ð° {current_retry} Ð· {max_retries}")
                
                if current_retry < max_retries:
                    time.sleep(5)  # Ð§ÐµÐºÐ°Ñ”Ð¼Ð¾ Ð¿ÐµÑ€ÐµÐ´ Ð½Ð°ÑÑ‚ÑƒÐ¿Ð½Ð¾ÑŽ ÑÐ¿Ñ€Ð¾Ð±Ð¾ÑŽ
                else:
                    print(f"ÐÐµ Ð²Ð´Ð°Ð»Ð¾ÑÑ Ð¿Ñ–Ð´ÐºÐ»ÑŽÑ‡Ð¸Ñ‚Ð¸ÑÑ Ð´Ð¾ RabbitMQ Ð¿Ñ–ÑÐ»Ñ {max_retries} ÑÐ¿Ñ€Ð¾Ð±")
                    self.connected = False
                    return False
    
    def send_message(self, queue, message):
        """Ð’Ñ–Ð´Ð¿Ñ€Ð°Ð²ÐºÐ° Ð¿Ð¾Ð²Ñ–Ð´Ð¾Ð¼Ð»ÐµÐ½Ð½Ñ Ð² Ñ‡ÐµÑ€Ð³Ñƒ"""
        if not self.connected:
            print("ÐÐµÐ¼Ð¾Ð¶Ð»Ð¸Ð²Ð¾ Ð²Ñ–Ð´Ð¿Ñ€Ð°Ð²Ð¸Ñ‚Ð¸ Ð¿Ð¾Ð²Ñ–Ð´Ð¾Ð¼Ð»ÐµÐ½Ð½Ñ: Ð½ÐµÐ¼Ð°Ñ” Ð·'Ñ”Ð´Ð½Ð°Ð½Ð½Ñ Ð· RabbitMQ")
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
                    delivery_mode=2,  # make message persistent
                )
            )
            return True
        except Exception as e:
            print(f"ÐŸÐ¾Ð¼Ð¸Ð»ÐºÐ° Ð²Ñ–Ð´Ð¿Ñ€Ð°Ð²ÐºÐ¸ Ð¿Ð¾Ð²Ñ–Ð´Ð¾Ð¼Ð»ÐµÐ½Ð½Ñ: {e}")
            self.connected = False
            return False
    
    def consume_messages(self, queue, callback):
        """ÐžÑ‚Ñ€Ð¸Ð¼Ð°Ð½Ð½Ñ Ð¿Ð¾Ð²Ñ–Ð´Ð¾Ð¼Ð»ÐµÐ½ÑŒ Ð· Ñ‡ÐµÑ€Ð³Ð¸"""
        if not self.connected:
            print("ÐÐµÐ¼Ð¾Ð¶Ð»Ð¸Ð²Ð¾ Ð¾Ñ‚Ñ€Ð¸Ð¼ÑƒÐ²Ð°Ñ‚Ð¸ Ð¿Ð¾Ð²Ñ–Ð´Ð¾Ð¼Ð»ÐµÐ½Ð½Ñ: Ð½ÐµÐ¼Ð°Ñ” Ð·'Ñ”Ð´Ð½Ð°Ð½Ð½Ñ Ð· RabbitMQ")
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
            
            print(f"ÐžÑ‡Ñ–ÐºÑƒÐ²Ð°Ð½Ð½Ñ Ð¿Ð¾Ð²Ñ–Ð´Ð¾Ð¼Ð»ÐµÐ½ÑŒ Ð· Ñ‡ÐµÑ€Ð³Ð¸ {queue}. Ð”Ð»Ñ Ð²Ð¸Ñ…Ð¾Ð´Ñƒ Ð½Ð°Ñ‚Ð¸ÑÐ½Ñ–Ñ‚ÑŒ CTRL+C")
            self.channel.start_consuming()
            return True
        except KeyboardInterrupt:
            self.channel.stop_consuming()
            self.connection.close()
            return True
        except Exception as e:
            print(f"ÐŸÐ¾Ð¼Ð¸Ð»ÐºÐ° Ð¾Ñ‚Ñ€Ð¸Ð¼Ð°Ð½Ð½Ñ Ð¿Ð¾Ð²Ñ–Ð´Ð¾Ð¼Ð»ÐµÐ½ÑŒ: {e}")
            self.connected = False
            return False
    
    def _process_message(self, callback):
        """ÐžÐ±Ð³Ð¾Ñ€Ñ‚ÐºÐ° Ð´Ð»Ñ Ð¾Ð±Ñ€Ð¾Ð±ÐºÐ¸ Ð¿Ð¾Ð²Ñ–Ð´Ð¾Ð¼Ð»ÐµÐ½ÑŒ"""
        def process(ch, method, properties, body):
            try:
                message = json.loads(body)
                result = callback(message)
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return result
            except Exception as e:
                print(f"ÐŸÐ¾Ð¼Ð¸Ð»ÐºÐ° Ð¾Ð±Ñ€Ð¾Ð±ÐºÐ¸ Ð¿Ð¾Ð²Ñ–Ð´Ð¾Ð¼Ð»ÐµÐ½Ð½Ñ: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        return process
    
    def close(self):
        """Ð—Ð°ÐºÑ€Ð¸Ñ‚Ñ‚Ñ Ð¿Ñ–Ð´ÐºÐ»ÑŽÑ‡ÐµÐ½Ð½Ñ Ð´Ð¾ RabbitMQ"""
        if self.connection and self.connection.is_open:
            self.connection.close() 
