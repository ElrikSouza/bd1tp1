import os
from dotenv import load_dotenv


def load_connection_string_from_env() -> str:
    load_dotenv()

    dbhost = 'database'
    dbpassword = os.getenv('POSTGRES_PASSWORD')
    dbuser = os.getenv('POSTGRES_USER')
    dbname = os.getenv('POSTGRES_DB')
    dbport = os.getenv('DB_PORT')

    return f"user={dbuser} password={dbpassword} host={dbhost} port={dbport} dbname={dbname}"
