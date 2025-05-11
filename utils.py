import pymysql
import credentials

def get_connection():
    return pymysql.connect(
        host=credentials.get_host(),
        port=credentials.get_port(),
        user=credentials.get_user(),
        password=credentials.get_password(),
        db=credentials.get_db()
    )

def tokenize(rows, description):
    columns = [column[0] for column in description]
    return [dict(zip(columns, row)) for row in rows]
