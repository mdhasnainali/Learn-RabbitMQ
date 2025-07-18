import pika
import sys

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='logs', exchange_type='fanout')

# The fanout exchange is very simple. As you can probably guess from the name, it just broadcasts all the messages it receives to all the queues it knows. And that's exactly what we need for our logger.

message = ' '.join(sys.argv[1:]) or "Hello World!"
channel.basic_publish(
    exchange='logs',
    routing_key='',
    body=message)
print(f" [x] Sent {message}")
connection.close()


# Temporary queues
# Bindings is 