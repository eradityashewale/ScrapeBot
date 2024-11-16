import psycopg2
from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini')
dbname=config["DB"]['dbname'],

def get_db_connection():
    # Load database configuration from config.ini
    config = ConfigParser()
    config.read('config.ini')
        
    # Establish a connection to the PostgreSQL database
    conn = psycopg2.connect(
        dbname=config["DB"]['dbname'],
        user=config["DB"]['user'],
        password=config["DB"]['password'],
        host=config["DB"]['host'],
        port=config["DB"]['port']
    )
    return conn
