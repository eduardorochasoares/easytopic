import pika
import time
from DAO.connection import Connection
import os
import multiprocessing
import json
import logging
import ast
from asr.client import main
import threading
import functools

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)


def callback(channel, method, properties, body, args):

    (connection, threads) = args
    delivery_tag = method.delivery_tag
    t = threading.Thread(target=do_work, args=(connection, channel, delivery_tag, body))
    t.start()
    threads.append(t)


def do_work(connection, channel, delivery_tag, body):
    try:
        print(" [x] Received %r" % body, flush=True)
        oid = json.loads(body)['oid']
        conn = Connection()
        # file = conn.get_file(oid)
        file = conn.get_doc_mongo(file_oid=oid)

        result = ast.literal_eval(file.decode('utf-8'))


        timestamps = [0]
        duration = []
        pause_duration = []
        count = 0
        dict_result = {}
        previous_duration = 0
        for key, value in result.items():
            result = main(value['bytes'])
            count += 1

        payload = bytes(str(dict_result), encoding='utf-8')
        conn = Connection()

        #  inserts the result of processing in database
        file_oid = conn.insert_doc_mongo(payload)
        conn.insert_jobs(type='asr', status='done', file=file_oid)

        message = {'type': 'segmentation', 'status': 'new', 'oid': file_oid}

        #  post a message on topic_segmentation queue
        connection_out = pika.BlockingConnection(pika.ConnectionParameters(host=os.environ['QUEUE_SERVER']))
        channel2 = connection_out.channel()

        channel2.queue_declare(queue='segmentation', durable=True)
        channel2.basic_publish(exchange='', routing_key='segmentation', body=json.dumps(message))

    except Exception as e:
        # print(e, flush=True)
        print('Connection Error %s' % e, flush=True)
    print(" [x] Done", flush=True)
    cb = functools.partial(ack_message, channel, delivery_tag)
    connection.add_callback_threadsafe(cb)

def ack_message(channel, delivery_tag):
    """Note that `channel` must be the same pika channel instance via which
    the message being ACKed was retrieved (AMQP protocol constraint).
    """
    if channel.is_open:
        channel.basic_ack(delivery_tag)
    else:
        # Channel is already closed, so we can't ACK this message;
        # log and/or do something that makes sense for your app in this case.
        pass




def consume():
    logging.info('[x] start consuming')
    success = False
    while not success:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=os.environ['QUEUE_SERVER'], heartbeat=5))
            channel = connection.channel()
            success = True
        except:
            pass


    channel.queue_declare(queue='asr', durable=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.basic_qos(prefetch_count=1)

    threads = []
    on_message_callback = functools.partial(callback, args=(connection, threads))
    channel.basic_consume(queue='asr', on_message_callback=on_message_callback)
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()

    # Wait for all to complete
    for thread in threads:
        thread.join()

    connection.close()

consume()

'''
workers = int(os.environ['NUM_WORKERS'])
pool = multiprocessing.Pool(processes=workers)
for i in range(0, workers):
    pool.apply_async(consume)

# Stay alive
try:
    while True:
        continue
except KeyboardInterrupt:
    print(' [*] Exiting...')
    pool.terminate()
    pool.join()'''