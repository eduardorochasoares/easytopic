from data_structures import Shot
import numpy as np
from scipy.io import wavfile
import re
from sys import argv
import os, sys
import glob
import evaluate_method
import multiprocessing
import time
import random
import json
sys.path.insert(0, 'document_similarity/')
from document_similarity import DocSim
from gensim.models.keyedvectors import KeyedVectors
from genetic_algorithm import GA
from aubio import source
from aubio import pitch as pt
import pika
import time
from DAO.connection import Connection
import os
import multiprocessing
import json
import logging
import ast
import threading
import functools

import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

stopwords = None
googlenews_model_path = '/word2vec/GoogleNews-vectors-negative300.bin'
stopwords_path = "/word2vec/stopwords_en.txt"
docSim = None
with open(stopwords_path, 'r') as fh:
    stopwords = fh.read().split(",")
model = KeyedVectors.load_word2vec_format(googlenews_model_path, binary=True, limit=1000000)
docSim = DocSim.DocSim(model, stopwords=stopwords)
#


class Summary:
    def __init__(self, video_path):
        self.video_path = video_path
        self.video_file = None
        self.chunks_path = self.video_path + "chunks/"
        self.n_chunks = len(glob.glob(self.chunks_path+ "chunk*"))
        self.chunks = []
        self.video_length = 0


    '''Method that create a audio chunk object passing the extracted features'''
    def createShots(self, i, pause, ocr_on, time,end_time,  docSim, prosodic_file):
        pitch = 0
        volume = 0
        try:
            with open(prosodic_file) as f:
                data = json.load(f)
                pitch = float(data[str(i)][0])
                volume = float(data[str(i)][1])

        except FileNotFoundError:
            print('Prosodic features not found')

        s = Shot(i, pitch, volume, pause, [], init_time=time, end_time=end_time)

        s.extractTranscriptAndConcepts(self.video_path, ocr_on, docSim=docSim)

        return s

#
# if __name__ == '__main__':
#     stopwords = None
#     googlenews_model_path = 'document_similarity/data/GoogleNews-vectors-negative300.bin'
#     stopwords_path = "document_similarity/data/stopwords_en.txt"
#     docSim = None
#
#     try:
#         root_database = sys.argv[1]
#     except IndexError:
#         print('Please, provide the path from the videolecture to be processed ')
#         print('Usage:\n python3 summary path_from_the_video_lecture')
#         sys.exit(0)
#
#
#     '''loads google word embeddings model'''
#     with open(stopwords_path, 'r') as fh:
#         stopwords = fh.read().split(",")
#     model = KeyedVectors.load_word2vec_format(googlenews_model_path, binary=True, limit=1000000)
#     docSim = DocSim.DocSim(model, stopwords=stopwords)
#
#
#     # saves the random seed in the seeds.txt file
#     seed  =  random.randrange(sys.maxsize)
#     seed_file = open("seeds.txt", 'a')
#     seed_file.write(str(seed) + '\n')
#     seed_file.close()
#     random.seed(seed)
#
#
#     start_time = time.time()
#
#     print(root_database)
#     summary = Summary(root_database)
#     ocr_on = False
#     pauses, times, times_end = summary.extractPauseDuration()
#     duration = [times_end[i] - times[i] for i in range(len(times))]
#     summary.video_length = np.sum(duration)
#     chunks = []
#     summary.n_chunks = len(times)
#     '''create the audio chunks structure'''
#     for i in range(summary.n_chunks):
#         chunks.append(summary.createShots(i, pauses[i], ocr_on, times[i], times_end[i], docSim, summary.video_path + "prosodic.json"))
#
#     old_chunks = chunks
#     chunks = [s for s in chunks if s.valid_vector]
#
#     summary.chunks = chunks
#     summary.n_chunks = len(chunks)
#
#     boundaries = []
#     if summary.n_chunks < 2:
#         boundaries = [0]
#     else:
#         '''calls the genetic algorithm'''
#         ga = GA.GeneticAlgorithm(population_size=100, constructiveHeuristic_percent=0.3, mutation_rate=0.05,
#                                  cross_over_rate=0.4, docSim=docSim, shots=summary.chunks,
#                                  n_chunks=summary.n_chunks, generations=500, local_search_percent=0.3,
#                                  video_length=summary.video_length, stopwords=stopwords, ocr_on=ocr_on)
#         boundaries = ga.run()
#
#     '''print the indexes of the points that are topic boundaries'''
#     print(boundaries)
#
#

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
        project_id = json.loads(body)['project_id']
        conn = Connection()
        # file = conn.get_file(oid)
        file = conn.get_doc_mongo(file_oid=oid)

        result = ast.literal_eval(file.decode('utf-8'))
        #print(result.keys(), flush=True)
        chunks = []
        low_features_dict = ast.literal_eval(result['low_level_features'].decode('utf-8'))
        asr_dict = ast.literal_eval(result['asr'].decode('utf-8'))
        print(low_features_dict, flush=True)
        print(asr_dict, flush=True)
        for k, v in low_features_dict.items():
            s = Shot(k, low_features_dict[k]['pitch'], low_features_dict[k]['volume'],
                     low_features_dict[k]['pause'], [], init_time=low_features_dict[k]['init_time'], end_time=0)
            s.extractTranscriptAndConcepts(asr_dict[k], False, docSim=docSim)
            chunks.append(s)
        # print(result['low_level_features'], flush=True)
        # print(result['asr'], flush=True)
        chunks = [s for s in chunks if s.valid_vector]
        if len(chunks) < 2:
            boundaries = [0]
        else:
            '''calls the genetic algorithm'''
            ga = GA.GeneticAlgorithm(population_size=100, constructiveHeuristic_percent=0.3, mutation_rate=0.05,
                                     cross_over_rate=0.4, docSim=docSim, shots=chunks,
                                     n_chunks=len(chunks), generations=500, local_search_percent=0.3,
                                     video_length=100, stopwords=stopwords, ocr_on=False)
            boundaries = ga.run()
        #print(chunks, flush=True)
        print(boundaries, flush=True)
        topics = {}
        topics["topics"] = boundaries
        payload = bytes(str(topics), encoding='utf-8')

        file_oid = conn.insert_doc_mongo(payload)
        conn = Connection()
        conn.insert_jobs(type='segmentation', status='done', file=file_oid, project_id=project_id)
        #
        # #print(result, flush=True)
        # count = 0
        # dict_result = {}
        # previous_duration = 0
        # for key, value in result.items():
        #     result = main(value['bytes'])
        #     dict_result[count] = result
        #     count += 1
        #     #time.sleep(1)
        #
        # payload = bytes(str(dict_result), encoding='utf-8')
        # conn = Connection()
        #
        # #  inserts the result of processing in database
        # file_oid = conn.insert_doc_mongo(payload)
        # conn.insert_jobs(type='asr', status='done', file=file_oid, project_id=project_id)
        #
        # message = {'type': 'aggregator', 'status': 'new', 'oid': file_oid, 'project_id': project_id}
        #
        # #  post a message on topic_segmentation queue
        # connection_out = pika.BlockingConnection(pika.ConnectionParameters(host=os.environ['QUEUE_SERVER']))
        # channel2 = connection_out.channel()
        #
        # channel2.queue_declare(queue='aggregator', durable=True)
        # channel2.basic_publish(exchange='', routing_key='aggregator', body=json.dumps(message))

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
            time.sleep(30)

            pass


    channel.queue_declare(queue='segmentation', durable=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.basic_qos(prefetch_count=1)

    threads = []
    on_message_callback = functools.partial(callback, args=(connection, threads))
    channel.basic_consume(queue='segmentation', on_message_callback=on_message_callback)
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