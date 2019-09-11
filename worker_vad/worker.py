import pika
import os


success = False
while not success:
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=os.environ['QUEUE_SERVER'], socket_timeout=2))
        success = True
    except:
        pass
channel = connection.channel()

channel.queue_declare(queue='vad')


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)


channel.basic_consume(
    queue='vad', on_message_callback=callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()