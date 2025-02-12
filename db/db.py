import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


class Database:
    def __init__(self):
        self.db_name = os.getenv("DB_NAME")
        self.db_user = os.getenv("DB_USER")
        self.password = os.getenv("PASSWORD")
        self.host = os.getenv("HOST")
        self.port = os.getenv("PORT")
        self.sql_folder = os.path.join(os.path.dirname(__file__), "sql")
        self.conn = None

    def db_connection(self):
        if self.conn is None:
            try:
                self.conn = psycopg2.connect(
                    dbname=self.db_name,
                    user=self.db_user,
                    password=self.password,
                    host=self.host,
                    port=self.port,
                )
            except psycopg2.Error as e:
                print(f"Error database connect: {e}")
                self.conn = None
        return self.conn

    def close_connection(self):
        if self.conn:
            self.conn.close()
            self.conn = None
        else:
            pass

    def execute_query(self, query_file):
        query_path = os.path.join(self.sql_folder, query_file)

        if not os.path.isfile(query_path):
            print(f"❌ SQL file '{query_path}' do not find")
            return None

        conn = self.db_connection()
        if not conn:
            print(f"❌ error connected to database {query_file}")
            return None

        try:
            with open(query_path, "r") as file:
                query = file.read()
            with conn.cursor() as cursor:
                cursor.execute(query)
                column_names = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()

            df = pd.DataFrame(rows, columns=column_names)

            if df.empty:
                print(f"Not data: {query_file}")
                return None

            return df

        except psycopg2.Error as e:
            print(f"❌ Error query {query_file}: {e}")
            return None

    def execute_query_get(self, query_file, params):
        query_path = os.path.join(self.sql_folder, query_file)

        if not os.path.isfile(query_path):
            print(f"❌ SQL file '{query_path}' do not find")
            return None

        conn = self.db_connection()
        if not conn:
            print(f"❌ error connected to database {query_file}")
            return None

        try:
            with open(query_path, "r") as file:
                query = file.read()
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                column_names = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()

            df = pd.DataFrame(rows, columns=column_names)

            if df.empty:
                print(f"Not data: {query_file}")
                return None

            return df

        except psycopg2.Error as e:
            print(f"❌ Error query {query_file}: {e}")
            return None


database = Database()
