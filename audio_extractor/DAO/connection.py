import os
import psycopg2
from pymongo import MongoClient
import gridfs
from bson import ObjectId

class Connection:
    def __init__(self):
        self._user = os.environ['POSTGRES_USER']
        self._password = os.environ['POSTGRES_PASSWORD']
        self._port = os.environ['POSTGRES_PORT']
        self._host = os.environ['POSTGRES_HOST']
        self._db = os.environ['POSTGRES_DB']

        self._conn = psycopg2.connect(user=self._user, password=self._password, host=self._host, port=self._port,
                                      database=self._db)

    def insert_jobs(self, type, status, file):

        cursor = self._conn.cursor()
        query = "INSERT INTO jobs (type, status, file_id, project_id) VALUES(%s, %s, %s, %s)  RETURNING oid"
        cursor.execute(query, (type, status, file, 1))

        self._conn.commit()

        oid = cursor.fetchone()[0]
        self._conn.close()

        return oid

    def get_file(self, oid):
        cursor = self._conn.cursor()
        query = "SELECT file FROM jobs WHERE oid = %s"
        cursor.execute(query, (oid,))
        self._conn.commit()
        file = cursor.fetchone()[0]
        self._conn.close()
        return file

    def insert_doc_mongo(self, file):
        client = MongoClient(os.environ['HOST_MONGO'], int(os.environ['MONGO_PORT']),
                             username=os.environ['ME_CONFIG_MONGODB_ADMINUSERNAME'],
                             password=os.environ['ME_CONFIG_MONGODB_ADMINPASSWORD'])

        db = client['topic_segmentation']
        fs = gridfs.GridFS(db)
        # collection = db.files

        post_id = fs.put(file)
        # post = {'file_bytes': file, "date": datetime.datetime.utcnow()}
        # posts = db.posts
        # post_id = posts.insert_one(post).inserted_id
        return str(post_id)

    def get_doc_mongo(self, file_oid):
        client = MongoClient(os.environ['HOST_MONGO'], int(os.environ['MONGO_PORT']),
                             username=os.environ['ME_CONFIG_MONGODB_ADMINUSERNAME'],
                             password=os.environ['ME_CONFIG_MONGODB_ADMINPASSWORD'])

        db = client['topic_segmentation']
        fs = gridfs.GridFS(db, collection='fs')
        # collection = db.files

        out = fs.get(file_id=ObjectId(file_oid))
        #print(out.read(), flush=True)

        # post = {'file_bytes': file, "date": datetime.datetime.utcnow()}
        # posts = db.posts
        # post_id = posts.insert_one(post).inserted_id
        return out.read()

