from fastapi import FastAPI, Response, status
import pymysql.cursors
import json


app = FastAPI()

@app.get("/getCharolas", status_code=status.HTTP_200_OK)
async def root(response: Response):
    try:
        connection = pymysql.connect(
            host='proyectosfcqi.tij.uabc.mx',
            port=3306,
            user='becerra20242',
            password='2532',
            db='bd1becerra20242'
        )
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Charola")
            result = cursor.fetchall()
            if not result:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "No se encontraron datos"}
            else:
                return result
    except Exception as e:
        error = "Error: " + str(e)
        return error
    
@app.get("/getCharola/{index}", status_code=status.HTTP_200_OK)
async def root(index : int, response: Response):
    try:
        connection = pymysql.connect(
            host='proyectosfcqi.tij.uabc.mx',
            port=3306,
            user='becerra20242',
            password='2532',
            db='bd1becerra20242'
        )
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Instrumento WHERE idCharola = %s", (index))
            result = cursor.fetchall()
            if not result:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "No se encontraron datos"}
            else:
                return result
    except Exception as e:
        error = "Error: " + str(e)
        return error
    
@app.get("/getDepartamento/{index}", status_code=status.HTTP_200_OK)
async def root(index : int, response: Response):
    try:
        connection = pymysql.connect(
            host='proyectosfcqi.tij.uabc.mx',
            port=3306,
            user='becerra20242',
            password='2532',
            db='bd1becerra20242'
        )
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Departamento WHERE idDepartamento = %s", (index))
            result = cursor.fetchall()
            if not result:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "No se encontraron datos"}
            else:
                return result
    except Exception as e:
        error = "Error: " + str(e)
        return error