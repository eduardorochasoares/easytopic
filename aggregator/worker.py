import pika
import time
from DAO.connection import Connection
import os
import multiprocessing
import json
import logging
import threading

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)


def aggregate_flow(project_id):
    conn = Connection()
    res = conn.async_jobs(project_id)
    while not res:
        print('Not yet', flush=True)
        time.sleep(30)
        conn = Connection()
        res = conn.async_jobs(project_id)
    print(res, flush=True)
    return res


def callback(ch, method, properties, body):

    try:
        print(" [x] Received %r" % body, flush=True)
        oid = json.loads(body)['oid']
        project_id = json.loads(body)['project_id']
        print(str(oid) + '!!!???', flush=True)
        print(str(project_id) + '!!!???', flush=True)
        flows = aggregate_flow(project_id)
        data = {}
        for flow in flows:
            conn = Connection()
            file = conn.get_doc_mongo(file_oid=flow[0])
            data[flow[1]] = file

        print(data.keys(), flush=True)
         # calls the audio extract algorithm
        # print(data,  flush=True)

        conn = Connection()
        try:
            file_oid = conn.insert_doc_mongo(bytes(str(data), encoding='utf-8'))

            conn.insert_jobs('aggregator', 'done', file_oid, project_id)
            message = {'type': 'segmentation', 'status': 'new', 'oid': file_oid, 'project_id': project_id}
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.environ['QUEUE_SERVER']))
            channel = connection.channel()

            channel.queue_declare(queue='segmentation', durable=True)
            channel.basic_publish(exchange='', routing_key='segmentation', body=json.dumps(message))


        except Exception as e:
            print(e, flush=True)


    except Exception as e:
        print(e, flush=True)
    print(" [x] Done", flush=True)
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
            time.sleep(30)

            pass

    channel.queue_declare(queue='aggregator', durable=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='aggregator', on_message_callback=callback)

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