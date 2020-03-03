import json
import psycopg2


class Postgresql:

    def __init__(self, api_rest_host):
        with open('DAO/pg_credentials.json') as cred_file:
            creds = json.load(cred_file)
            self._user = creds['credentials']['pg_user']
            self._password = creds['credentials']['pg_password']
            self._port = creds['credentials']['pg_port']
            self._host = creds['credentials']['pg_host']
            self._host = api_rest_host
            self._db = creds['credentials']['pg_db']

        self._conn = psycopg2.connect(user=self._user, password=self._password, host=self._host, port=self._port,
                                      database=self._db)

    def get_jobs_done(self, id):
        results = []

        cursor = self._conn.cursor()
        query = "SELECT file_id FROM jobs WHERE project_id = %s AND status = 'done' AND type = 'segmentation'"
        cursor.execute(query, (id,))
        self._conn.commit()
        result = cursor.fetchone()
        if result:
            file = result[0]
            return {'result': {'project_id': id, 'oid': file}}
        else:
            return None
