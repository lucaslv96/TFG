import pandas as pd
import sqlite3
import os
import logging

class DataManager:
    def __init__(self, db_filename='bbdd/equivalencias.sqlite'):
        self.db_filename = db_filename
        self.conn = None
        self.cursor = None
        self._setup_logging()
        self._connect_db()

    def _setup_logging(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def _connect_db(self):
        if not os.path.exists('bbdd'):
            os.makedirs('bbdd')
        self.conn = sqlite3.connect(self.db_filename)
        self.cursor = self.conn.cursor()
        self.logger.info("Connected to the database.")

    def initialize_database(self):
        if not os.path.exists(self.db_filename):
            self._create_tables()
            self.logger.info("Database initialized successfully.")
        else:
            self.logger.info("Database already exists.")

    def _create_tables(self):
        self.cursor.execute('''
            CREATE TABLE google_finance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_dato TEXT NOT NULL,
                dato_inicial TEXT NOT NULL,
                dato_actual TEXT NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE yahoo_finance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_dato TEXT NOT NULL,
                dato_inicial TEXT NOT NULL,
                dato_actual TEXT NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE macrotrends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_dato TEXT NOT NULL,
                dato_inicial TEXT NOT NULL,
                dato_actual TEXT NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE equivalencias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_dato TEXT NOT NULL,
                google_finance_id INTEGER,
                yahoo_finance_id INTEGER,
                macrotrends_id INTEGER,
                FOREIGN KEY (google_finance_id) REFERENCES google_finance(id),
                FOREIGN KEY (yahoo_finance_id) REFERENCES yahoo_finance(id),
                FOREIGN KEY (macrotrends_id) REFERENCES macrotrends(id)
            )
        ''')
        self.conn.commit()
        self.logger.info("Tables created successfully.")

    def load_data(self, data, table_name):
        if table_name not in ['google_finance', 'yahoo_finance', 'macrotrends']:
            self.logger.error(f"Invalid table name: {table_name}")
            return

        for index, row in data.iterrows():
            self.cursor.execute(f'INSERT INTO {table_name} (tipo_dato, dato_inicial, dato_actual) VALUES (?, ?, ?)', 
                                (row['tipo_dato'], row['dato_inicial'], row['dato_actual']))
        self.conn.commit()
        self.logger.info(f"Data loaded into {table_name} successfully.")

    def fetch_data(self, query):
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.logger.info(f"Fetched {len(rows)} rows from the database.")
        return rows

    def close_connection(self):
        self.conn.close()
        self.logger.info("Database connection closed.")

    def validate_data(self, data):
        # Implement data validation logic here
        self.logger.info("Data validation completed.")
        return True

    def transform_data(self, data):
        # Implement data transformation logic here
        self.logger.info("Data transformation completed.")
        return data

    def cache_data(self, key, data):
        # Implement caching logic here
        self.logger.info(f"Data cached with key: {key}")

    def get_cached_data(self, key):
        # Implement logic to retrieve cached data here
        self.logger.info(f"Retrieved cached data with key: {key}")
        return None

    def export_to_sqlite(self, google_df, yahoo_df, macrotrends_df, ticker):
        self._connect_db()
        google_df.to_sql('google_finance', self.conn, if_exists='replace', index=False)
        yahoo_df.to_sql('yahoo_finance', self.conn, if_exists='replace', index=False)
        macrotrends_df.to_sql('macrotrends', self.conn, if_exists='replace', index=False)
        self.conn.commit()
        self.logger.info(f"Data for {ticker} exported to SQLite database.")

    def import_from_sqlite(self, filename):
        self.conn = sqlite3.connect(filename)
        google_df = pd.read_sql_query("SELECT * FROM google_finance", self.conn)
        yahoo_df = pd.read_sql_query("SELECT * FROM yahoo_finance", self.conn)
        macrotrends_df = pd.read_sql_query("SELECT * FROM macrotrends", self.conn)
        self.conn.close()
        self.logger.info(f"Data imported from SQLite database: {filename}")
        return google_df, yahoo_df, macrotrends_df
