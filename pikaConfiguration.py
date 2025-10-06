import pika
import json

# Konfiguracja połączenia z RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
# channel.queue_declare(queue='olx')  # Tworzy kolejkę jeśli nie istnieje

def send_to_rabbitmq(queue_name, batch):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    message = json.dumps(batch)
    channel.basic_publish(exchange='', routing_key=queue_name, body=message)
    connection.close()