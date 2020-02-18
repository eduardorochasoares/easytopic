import pymongo
import glob
import requests
import json
from DAO.postgresql import Postgresql
import time
from DAO.mongodb import MongoDB
import ast
import argparse
API_REST_ADDRESS = None
ENDPOINT = None
def send_request(lecture):
    return json.loads(requests.post(API_REST_ADDRESS + ENDPOINT, files={'file': open(lecture, 'rb')}).content)['project_id']


def check_job_done(project_id):

    pgsql = Postgresql()
    return pgsql.get_jobs_done(project_id)

def get_result_file(file_oid):
    mongodb = MongoDB()
    file = mongodb.get_doc_mongo(file_oid)
    #print(file)
    return file


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--server_ip', default='localhost')
    parser.add_argument('--port', default='5000')

    args = parser.parse_args()

    API_REST_ADDRESS = 'http://' + args.server_ip + ':' + args.port
    ENDPOINT = '/segmentation'
    ids = []
    files = glob.glob('data/*.mp4')
    for file in files:
        ids.append((send_request(file), file))

    results = []
    while ids:
        for id, video, in ids:
            res = check_job_done(id)
            if res:

                dc = ast.literal_eval(get_result_file(res['result']['oid']).decode('utf-8'))

                print('Job completed: ' + str(dc))
                results.append({'video': video, 'segmentation': dc})
                ids.remove((id, video))

        print('Sleep before checking again...')
        time.sleep(30)
    print('All jobs done:')
    print(results)
