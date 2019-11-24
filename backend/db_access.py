from mysql.connector import connect

# Download driver
# https://dev.mysql.com/downloads/connector/python/

conn = connect(
    host="localhost",
    port='5001',
    user="root",
    passwd="rootpw"
)

class DbAccess():
    def __init__(self):
        self.conn = conn
        self.cursor = conn.cursor()

    def __call__(self):
        self.cursor = conn.cursor()

    def create_db_and_tables_if_not_exists(self):
        self.cursor.execute("""
            CREATE DATABASE IF NOT EXISTS test
        """)
        
        self.cursor.execute("""
            USE test;
        """)

        self.create_table('user')

    def create_table(self,
                     table):
        self.cursor.execute(
            ('''
            CREATE TABLE IF NOT EXISTS {0}
            (
            id             INTEGER     PRIMARY KEY     AUTO_INCREMENT
            )
            ''').format(table))

    def drop_database(self,
                      table):
        self.cursor.execute("""
            USE mysql;
        """)

        self.cursor.execute("""
            DROP DATABASE {0}
        """.format(table))