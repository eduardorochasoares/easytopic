import pika
import time
from DAO.connection import Connection
import os
import multiprocessing
import json
import logging
import ast
from extract_prosodic.main import extract

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)


def callback(ch, method, properties, body):
    try:
        print(" [x] Received %r" % body, flush=True)
        oid = json.loads(body)['oid']
        conn = Connection()
        file = conn.get_file(oid=oid)
        result = ast.literal_eval(file.tobytes().decode('utf-8'))
        timestamps = [0]
        duration = []
        pause_duration = []
        count = 0
        dict_result = {}
        previous_duration = 0
        for key, value in result.items():
            dict_result[count] = {}
            if count == 0:
                dict_result[count]['pause'] = float(value['timestamp'])
            else:
                dict_result[count]['pause'] = float(value['timestamp']) - previous_duration

            previous_duration = float(value['timestamp']) + float(value['duration'])
            dict_result[count]['pitch'],  dict_result[count]['volume'] = extract(value['bytes'])
            count += 1

        payload = bytes(str(dict_result), encoding='utf8')
        conn = Connection()

        #  inserts the result of processing in database
        oid = conn.insert_jobs(type='low_level_features', status='done', file=payload)

        message = {'type': 'segmentation', 'status': 'new', 'oid': oid}

        #  post a message on topic_segmentation queue
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.environ['QUEUE_SERVER']))
        channel = connection.channel()

        channel.queue_declare(queue='segmentation', durable=True)
        channel.basic_publish(exchange='', routing_key='segmentation', body=json.dumps(message))

    except Exception as e:
        # print(e, flush=True)
        print('Connection Error %s' % e, flush=True)
        print(" [x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)


def consume():
    logging.info('[x] start consuming')
    success = False
    while not success:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=os.environ['QUEUE_SERVER']))
            channel = connection.channel()
            success = True
        except:
            pass

    channel.queue_declare(queue='low_level_features', durable=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='low_level_features', on_message_callback=callback)

    channel.start_consuming()

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