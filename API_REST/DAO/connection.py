import os
import psycopg2


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
        query = "INSERT INTO jobs (type, status, file, project_id) VALUES(%s, %s, %s, %s)  RETURNING oid"
        cursor.execute(query, (type, status, file, 1))

        self._conn.commit()

        oid = cursor.fetchone()[0]
        self._conn.close()

        return oid