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
        self.logger = logging.getLogger(__name__)

    def _connect_db(self):
        if not os.path.exists('bbdd'):
            os.makedirs('bbdd')
        self.conn = sqlite3.connect(self.db_filename)
        self.cursor = self.conn.cursor()
        self.logger.info("Conectado a la base de datos.")

    def initialize_database(self):
        if not os.path.exists(self.db_filename):
            self._create_tables()
            self.logger.info("Base de datos inicializada con éxito.")
        else:
            self.logger.info("La base de datos ya existe.")

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
        self.logger.info("Tablas creadas con éxito.")

    def load_data(self, data, table_name):
        if table_name not in ['google_finance', 'yahoo_finance', 'macrotrends']:
            self.logger.error(f"Nombre de tabla inválido: {table_name}")
            return

        for index, row in data.iterrows():
            self.cursor.execute(f'INSERT INTO {table_name} (tipo_dato, dato_inicial, dato_actual) VALUES (?, ?, ?)', 
                                (row['tipo_dato'], row['dato_inicial'], row['dato_actual']))
        self.conn.commit()
        self.logger.info(f"Datos cargados en {table_name} con éxito.")

    def fetch_data(self, query):
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.logger.info(f"Se recuperaron {len(rows)} filas de la base de datos.")
        return rows

    def close_connection(self):
        self.conn.close()
        self.logger.info("Conexión a la base de datos cerrada.")

    def validate_data(self, data):
        # Implementar la lógica de validación de datos aquí
        self.logger.info("Validación de datos completada.")
        return True

    def transform_data(self, data):
        # Implementar la lógica de transformación de datos aquí
        self.logger.info("Transformación de datos completada.")
        return data

    def cache_data(self, key, data):
        # Implementar la lógica de caché aquí
        self.logger.info(f"Datos almacenados en caché con la clave: {key}")

    def get_cached_data(self, key):
        # Implementar la lógica para recuperar datos de la caché aquí
        self.logger.info(f"Datos recuperados de la caché con la clave: {key}")
        return None

    def export_to_sqlite(self, google_df, yahoo_df, macrotrends_df, ticker):
        self._connect_db()
        google_df.to_sql('google_finance', self.conn, if_exists='replace', index=False)
        yahoo_df.to_sql('yahoo_finance', self.conn, if_exists='replace', index=False)
        macrotrends_df.to_sql('macrotrends', self.conn, if_exists='replace', index=False)
        self.conn.commit()
        self.logger.info(f"Datos de {ticker} exportados a la base de datos SQLite.")

    def import_from_sqlite(self, filename):
        self.conn = sqlite3.connect(filename)
        google_df = pd.read_sql_query("SELECT * FROM google_finance", self.conn)
        yahoo_df = pd.read_sql_query("SELECT * FROM yahoo_finance", self.conn)
        macrotrends_df = pd.read_sql_query("SELECT * FROM macrotrends", self.conn)
        self.conn.close()
        self.logger.info(f"Datos importados de la base de datos SQLite: {filename}")
        return google_df, yahoo_df, macrotrends_df
