from fastapi import FastAPI, Response, status
from fastapi.responses import JSONResponse
import pymysql.cursors
import json
import utils
from hashlib import sha256
from pydantic import BaseModel

app = FastAPI()

class Usuario(BaseModel):
    Nombre: str
    Rol: str
    Correo: str
    Contraseña: str

@app.get("/getCharolas")
async def root(response: Response):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM charola")
            result = cursor.fetchall()
            if not result:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "No se encontraron datos"}
            return JSONResponse(
                content=utils.tokenize(result, cursor.description),
                media_type="application/json",
                status_code=status.HTTP_200_OK
            )

    except Exception as e:
        error = "Error: " + str(e)
        return error
    
@app.get("/getCharola/{index}")
async def root(index : int, response: Response):
    try:
        connection = utils.get_connection()

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM charola WHERE idCharola = %s", (index))
            result = cursor.fetchall()
            if not result:
                return JSONResponse(content={"message": "No se encontraron datos"}, media_type="application/json", status_code=status.HTTP_404_NOT_FOUND)
            return JSONResponse(
                content=utils.tokenize(result, cursor.description),
                media_type="application/json",
                status_code=status.HTTP_200_OK
            )   
    except Exception as e:
        error = "Error: " + str(e)
        return error
    

@app.post("/postUsuario")
async def crear_usuario(usuario: Usuario, response: Response):
    try:
        if not usuario.Correo or not usuario.Contraseña:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"message": "Correo o contraseña vacíos"}

        connection = utils.get_connection()
        with connection.cursor() as cursor:
            hashed_password = sha256(usuario.Contraseña.encode()).hexdigest()
            cursor.execute(
                "INSERT INTO usuario (Nombre, Rol, Correo, Contraseña) VALUES (%s, %s, %s, %s)",
                (usuario.Nombre, usuario.Rol, usuario.Correo, hashed_password)
            )
            connection.commit()
            return {"message": "Usuario insertado correctamente"}

    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}
    finally:
        connection.close()
        
@app.put("/updateUsuario/{index}/{campo}/{nuevoValor}")
async def root(index : int, campo : str , nuevoValor : str , response: Response):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            if campo not in ("Nombre", "Rol", "Correo", "Contraseña"):
                response.status_code = status.HTTP_400_BAD_REQUEST
                return {"message": "Campo no permitido"}
            if campo == "Contraseña":
                nuevoValor = sha256(nuevoValor.encode()).hexdigest()
                cursor.execute("UPDATE usuario SET Contraseña = %s WHERE idUsuario = %s", (nuevoValor, index))
                connection.commit() 
                return JSONResponse(
                    content={"message": "Contraseña actualizada correctamente"},
                    media_type="application/json",
                    status_code=status.HTTP_200_OK
                )
            cursor.execute(f"UPDATE usuario SET {campo} = %s WHERE idUsuario = %s", (nuevoValor, index))
            connection.commit()
            return JSONResponse(
                content={"message": "Campo actualizado correctamente"},
                media_type="application/json",
                status_code=status.HTTP_200_OK
            )
    except Exception as e:
        error = "Error: " + str(e)
        return error
    finally:
        connection.close()

@app.get("/getUsuarios")
async def root(response: Response):
    try:
        connection = utils.get_connection()

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM usuario")
            result = cursor.fetchall()
            if not result:
                return JSONResponse(
                    content={"message": "No se encontraron datos"},
                    media_type="application/json",
                    status_code=status.HTTP_404_NOT_FOUND
                )
            return JSONResponse(
                content=utils.tokenize(result, cursor.description),
                media_type="application/json",
                status_code=status.HTTP_200_OK
            )
    except Exception as e:
        error = "Error: " + str(e)
        return error
    finally:
        connection.close()

@app.get("/getUsuario/{index}")
async def root(index : int, response: Response):
    try:
        connection = utils.get_connection()

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM usuario WHERE idUsuario = %s", (index))
            result = cursor.fetchall()
            if not result:
                return JSONResponse(
                    content={"message": "No se encontraron datos"},
                    media_type="application/json",
                    status_code=status.HTTP_404_NOT_FOUND
                )
            else:
                return JSONResponse(
                    content=utils.tokenize(result, cursor.description),
                    media_type="application/json",
                    status_code=status.HTTP_200_OK
                )
    except Exception as e:
        error = "Error: " + str(e)
        return error
    finally:
        connection.close()

@app.delete("/deleteUsuario/{index}")
async def root(index : int, response: Response):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM usuario WHERE idUsuario = %s", (index))
            result = cursor.fetchall()
            if not result:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "No existe el usuario"}
            cursor.execute("DELETE FROM usuario WHERE idUsuario = %s", (index))
            connection.commit()
            return JSONResponse(
                content={"message": "Usuario eliminado correctamente"},
                media_type="application/json",
                status_code=status.HTTP_200_OK
            )
    except Exception as e:
        error = "Error: " + str(e)
        return error
    finally:
        connection.close()

@app.get("/getEspecialidades")
async def root(response: Response):
    try:
        connection = utils.get_connection()

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM especialidad")
            result = cursor.fetchall()
            if not result:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "No se encontraron datos"}
            else:
                return JSONResponse(
                    content=utils.tokenize(result, cursor.description),
                    media_type="application/json",
                    status_code=status.HTTP_200_OK
                )
    except Exception as e:
        error = "Error: " + str(e)
        return error
    finally:
        connection.close()

@app.get("/getEspecialidad/{index}")
async def root(index : int, response: Response):
    try:
        connection = utils.get_connection()

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM especialidad WHERE idEspecialidad = %s", (index))
            result = cursor.fetchall()
            if not result:
                return JSONResponse(
                    content={"message": "No se encontraron datos"},
                    media_type="application/json",
                    status_code=status.HTTP_404_NOT_FOUND
                )

            return JSONResponse(
                content=utils.tokenize(result, cursor.description),
                media_type="application/json",
                status_code=status.HTTP_200_OK
            )
    except Exception as e:
        error = "Error: " + str(e)
        return error
    finally:
        connection.close()
        
@app.post("/postEspecialidad/{nombre}")
async def root(nombre : str, response: Response):
    try:
        connection = utils.get_connection()

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM especialidad WHERE Nombre = %s", (nombre))
            result = cursor.fetchall()
            if result:
                return JSONResponse(
                    content={"message": "Ya existe la especialidad"},
                    media_type="application/json",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            cursor.execute("INSERT INTO especialidad (Nombre) VALUES (%s)", (nombre))
            connection.commit()
            return JSONResponse(
                content={"message": "Especialidad insertada correctamente"},
                media_type="application/json",
                status_code=status.HTTP_200_OK
            )
    except Exception as e:
        error = "Error: " + str(e)
        return error
    finally:
        connection.close()

@app.delete("/deleteEspecialidad/{index}")
async def root(index : int, response: Response):
    try:
        connection = utils.get_connection()

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM especialidad WHERE idEspecialidad = %s", (index))
            result = cursor.fetchall()
            if not result:
                return JSONResponse(
                    content={"message": "No existe la especialidad"},
                    media_type="application/json",
                    status_code=status.HTTP_404_NOT_FOUND
                )
            cursor.execute("DELETE FROM especialidad WHERE idEspecialidad = %s", (index))
            connection.commit()
            return JSONResponse(
                content={"message": "Especialidad eliminada correctamente"},
                media_type="application/json",
                status_code=status.HTTP_200_OK
            )
    except Exception as e:
        error = "Error: " + str(e)
        return error
    finally:
        connection.close()