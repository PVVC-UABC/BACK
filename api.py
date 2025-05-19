from fastapi import FastAPI, Response, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pymysql.cursors
import json
import utils
from hashlib import sha256
from pydantic import BaseModel

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Usuario(BaseModel):
    Nombres: str
    ApellidoPaterno: str
    ApellidoMaterno: str
    Rol: str
    Correo: str
    Contrasena: str

@app.get("/getMemoryUsage")
async def root(response: Response):
    try:
        memory_usage = utils.get_memory_usage()
        return JSONResponse(
            content={"memory_usage": memory_usage},
            media_type="application/json",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        error = "Error: " + str(e)
        return error

@app.get("/getEquipos")
async def root(response: Response):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Equipo")
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
    
@app.get("/getEquipo/{index}")
async def root(index : int, response: Response):
    try:
        connection = utils.get_connection()

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Equipo WHERE idEquipo = %s", (index))
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
        if not usuario.Correo or not usuario.Contrasena:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"message": "Correo o contraseña vacíos"}

        connection = utils.get_connection()
        with connection.cursor() as cursor:
            hashed_password = sha256(usuario.Contrasena.encode()).hexdigest()
            cursor.execute(
                "INSERT INTO Usuario (Nombres, ApellidoPaterno, ApellidoMaterno, Rol, Correo, Contrasena) VALUES (%s, %s, %s, %s, %s, %s)",
                (usuario.Nombres, usuario.ApellidoPaterno, usuario.ApellidoMaterno , usuario.Rol, usuario.Correo, hashed_password)
            )
            connection.commit()
            return {"message": "Usuario insertado correctamente"}

    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}
    finally:
        connection.close()
        
@app.put("/updateUsuario/{index}")
async def root(index: int, response: Response, usuario: Usuario):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Usuario WHERE idUsuario = %s", (index))
            result = cursor.fetchall()
            if not result:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "No existe el usuario"}
            cursor.execute(
                "UPDATE Usuario SET Nombres = %s, ApellidoPaterno = %s, ApellidoMaterno = %s, Rol = %s, Correo = %s, Contrasena = %s WHERE idUsuario = %s",
                (usuario.Nombres, usuario.ApellidoPaterno, usuario.ApellidoMaterno , usuario.Rol, usuario.Correo, sha256(usuario.Contrasena.encode()).hexdigest(), index)
            )
            connection.commit()
            return JSONResponse(
                content={"message": "Usuario actualizado correctamente"},
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
            cursor.execute("SELECT * FROM Usuario")
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
            cursor.execute("SELECT * FROM Usuario WHERE idUsuario = %s", (index))
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
            cursor.execute("SELECT * FROM Usuario WHERE idUsuario = %s", (index))
            result = cursor.fetchall()
            if not result:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "No existe el usuario"}
            cursor.execute("DELETE FROM Usuario WHERE idUsuario = %s", (index))
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
            cursor.execute("SELECT * FROM Especialidad")
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
            cursor.execute("SELECT * FROM Especialidad WHERE idEspecialidad = %s", (index))
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
            cursor.execute("SELECT * FROM Especialidad WHERE Nombre = %s", (nombre))
            result = cursor.fetchall()
            if result:
                return JSONResponse(
                    content={"message": "Ya existe la especialidad"},
                    media_type="application/json",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            cursor.execute("INSERT INTO Especialidad (Nombre) VALUES (%s)", (nombre))
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
            cursor.execute("SELECT * FROM Especialidad WHERE idEspecialidad = %s", (index))
            result = cursor.fetchall()
            if not result:
                return JSONResponse(
                    content={"message": "No existe la especialidad"},
                    media_type="application/json",
                    status_code=status.HTTP_404_NOT_FOUND
                )
            cursor.execute("DELETE FROM Especialidad WHERE idEspecialidad = %s", (index))
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