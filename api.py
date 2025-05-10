from fastapi import FastAPI, Response, status
import pymysql.cursors
import json
import credentials

app = FastAPI()

@app.get("/getCharolas")
async def root(response: Response):
    try:
        connection = credentials.get_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM charola")
            result = cursor.fetchall()
            if not result:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "No se encontraron datos"}
            else:
                return result
    except Exception as e:
        error = "Error: " + str(e)
        return error
    
@app.get("/getCharola/{index}")
async def root(index : int, response: Response):
    try:
        connection = credentials.get_connection()

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
    
@app.get("/getDepartamento/{index}")
async def root(index : int, response: Response):
    try:
        connection = credentials.get_connection()

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
    finally:
        connection.close()

@app.put("/updateUsuario/{index}/{campo}/{nuevoValor}")
async def root(index : int, campo : str , nuevoValor : str , response: Response):
    try:
        connection = credentials.get_connection()

        with connection.cursor() as cursor:
            query = f"UPDATE Persona SET {campo} = %s WHERE idPersona = %s"
            cursor.execute(query, (nuevoValor, index))
            connection.commit()
            response.status_code = status.HTTP_200_OK
            return {"message": "Usuario actualizado correctamente"}
    except Exception as e:
        error = "Error: " + str(e)
        return error
    finally:
        connection.close()

@app.get("/getUsuarios")
async def root(response: Response):
    try:
        connection = credentials.get_connection()

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Persona")
            result = cursor.fetchall()
            if not result:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "No se encontraron datos"}
            else:
                return result
    except Exception as e:
        error = "Error: " + str(e)
        return error
    finally:
        connection.close()

@app.get("/getUsuario/{index}")
async def root(index : int, response: Response):
    try:
        connection = credentials.get_connection()

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Persona WHERE idPersona = %s", (index))
            result = cursor.fetchall()
            if not result:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "No se encontraron datos"}
            else:
                return result
    except Exception as e:
        error = "Error: " + str(e)
        return error
    finally:
        connection.close()

@app.post("/postUsuario/{nombre}/{Rol}/{Departamento_idDepartamento}")
async def root(nombre : str, Rol : str, Departamento_idDepartamento : int, response: Response):
    try:
        connection = credentials.get_connection()

        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO Persona (nombre, Rol, Departamento_idDepartamento) VALUES (%s, %s, %s)", (nombre, Rol, Departamento_idDepartamento))
            connection.commit()
            response.status_code = status.HTTP_200_OK
            return {"message": "Usuario insertado correctamente"}
    except Exception as e:
        error = "Error: " + str(e)
        return error
    finally:
        connection.close()

@app.delete("/deleteUsuario/{index}")
async def root(index : int, response: Response):
    try:
        connection = credentials.get_connection()

        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM Persona WHERE idPersona = %s", (index))
            connection.commit()
            response.status_code = status.HTTP_200_OK
            return {"message": "Usuario eliminado correctamente"}
    except Exception as e:
        error = "Error: " + str(e)
        return error
    finally:
        connection.close()

@app.get("/getEspecialidades")
async def root(response: Response):
    try:
        connection = credentials.get_connection()

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Departamento")
            result = cursor.fetchall()
            if not result:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "No se encontraron datos"}
            else:
                return result
    except Exception as e:
        error = "Error: " + str(e)
        return error
    finally:
        connection.close()

@app.post("/postEspecialidad/{nombre}/{descripcion}")
async def root(nombre : str, descripcion : str, response: Response):
    try:
        connection = credentials.get_connection()

        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO Departamento (nombre, descripcion) VALUES (%s, %s)", (nombre, descripcion))
            connection.commit()
            response.status_code = status.HTTP_200_OK
            return {"message": "Especialidad insertada correctamente"}
    except Exception as e:
        error = "Error: " + str(e)
        return error
    finally:
        connection.close()

@app.delete("/deleteEspecialidad/{index}")
async def root(index : int, response: Response):
    try:
        connection = credentials.get_connection()

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Departamento WHERE idDepartamento = %s", (index))
            result = cursor.fetchall()
            if not result:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "No existe la especialidad"}
            else:
                cursor.execute("DELETE FROM Departamento WHERE idDepartamento = %s", (index))
                connection.commit()
                response.status_code = status.HTTP_200_OK
                return {"message": "Especialidad eliminada correctamente"}
    except Exception as e:
        error = "Error: " + str(e)
        return error
    finally:
        connection.close()