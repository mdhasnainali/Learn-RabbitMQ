import pika, os, sys, time

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()


    channel.queue_declare(queue='hello') # we can run the command as many times as we like, and only one will be created.
    # Why declare again? 
    # We're not yet sure which program to run first

    def callback(ch, method, properties, body):
        print(f" [x] Received {body.decode()}")
        time.sleep(body.count(b'.')) # Sleep for number of bytes '.' in the message
        print(" [x] Done")

    channel.basic_consume(queue='hello',
                        auto_ack=True,  # Manual message acknowledgments are turned off 
                        on_message_callback=callback)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

# Run 2 worker.py and wait for tasks
# new_task.py will run multiple times to test how 2 workers takes from the queue and process randomly
# What happens if a consumer starts a long task and it terminates before it completes?
# With our current code once RabbitMQ delivers message to the consumer, it immediately marks it for deletion. In this case, if you terminate a worker, the message it was just processing is lost. 
# To solve this: RabbitMQ supports message acknowledgments
# An acknowledgement is sent back by the consumer to tell RabbitMQ that a particular message had been received, processed and that RabbitMQ is free to delete it.
# If a consumer dies (its channel is closed, connection is closed, or TCP connection is lost) without sending an ack, RabbitMQ will understand that a message wasn't processed fully and will re-queue it. 
# A timeout (30 minutes by default) is enforced on consumer delivery acknowledgement. This helps detect buggy (stuck) consumers that never acknowledge deliveries. You can increase this timeout as described in Delivery Acknowledgement Timeout.

# def callback(ch, method, properties, body):
#     print(f" [x] Received {body.decode()}")
#     time.sleep(body.count(b'.') )
#     print(" [x] Done")
#     ch.basic_ack(delivery_tag = method.delivery_tag)

# channel.basic_consume(queue='hello', on_message_callback=callback)

# ======================================
# What if the RabbitMQ dies (queue)? We need to ensure it's durability just like the acknowledgements. 

# channel.queue_declare(queue='hello', durable=True)

# Although this command is correct by itself, it won't work in our setup. That's because we've already defined a queue called hello which is not durable. RabbitMQ doesn't allow you to redefine an existing queue with different parameters and will return an error to any program that tries to do that.

# channel.basic_publish(exchange='',
#                       routing_key="task_queue",
#                       body=message,
#                       properties=pika.BasicProperties(
#                          delivery_mode = pika.DeliveryMode.Persistent
#                       ))

# You may see that there are a unfairness in the work distribution. The first worker do most of the works. 
# So resolve this unfair dispatch. We can tell the system that RabbitMQ not to give more than one message to a worker at a time. Or, in other words, don't dispatch a new message to a worker until it has processed and acknowledged the previous one. Instead, it will dispatch it to the next worker that is not still busy.

# channel.basic_qos(prefetch_count=1)


