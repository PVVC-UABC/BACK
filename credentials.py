import pymysql

host='proyectosfcqi.tij.uabc.mx'
port=3306
user='becerra20242'
password='2532'
db='bd2becerra20242'

def get_connection():
    return pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        db=db
    )