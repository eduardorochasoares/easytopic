from pymongo import MongoClient
import gridfs
from bson import ObjectId
import json
class MongoDB:
    def __init__(self, api_rest_ip):
        with open('DAO/mongo_db_credentials.json') as f:
            credentials = json.load(f)
            self.mongo_host = credentials['credentials']['mongo_host']
            self.mongo_host = api_rest_ip
            self.mongo_user = credentials['credentials']['mongo_user']
            self.mongo_password = credentials['credentials']['mongo_password']
            self.mongo_port = credentials['credentials']['mongo_port']

    def get_doc_mongo(self, file_oid):
        client = MongoClient(self.mongo_host, int(self.mongo_port), username=self.mongo_user, password=self.mongo_password)

        db = client['topic_segmentation']
        fs = gridfs.GridFS(db, collection='fs')
        # collection = db.files

        out = fs.get(file_id=ObjectId(file_oid))
        #print(out.read(), flush=True)
        # post = {'file_bytes': file, "date": datetime.datetime.utcnow()}
        # posts = db.posts
        # post_id = posts.insert_one(post).inserted_id
        return out.read()
