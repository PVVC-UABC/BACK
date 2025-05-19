import pymysql
import os
from dotenv import load_dotenv
import psutil

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# Obtiene las variables de entorno
__host=os.getenv('DB_HOST')
__port=int(os.getenv('DB_PORT',3306))
__user=os.getenv('DB_USER')
__password=os.getenv('DB_PASSWORD')
__db=os.getenv('DB_DB')

def get_connection():
    return pymysql.connect(
        host=__host,
        port=__port,
        user=__user,
        password=__password,
        db=__db
    )

def tokenize(rows, description):
    columns = [column[0] for column in description]
    return [dict(zip(columns, row)) for row in rows]

def get_memory_usage():
    """
    Obtiene el uso de memoria del sistema en MB.
    """
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    return memory_info.rss / (1024 * 1024)  # Convertir a MB