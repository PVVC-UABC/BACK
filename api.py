from fastapi import FastAPI, Response, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Header, Response, status
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
    Nombre: str
    Rol: str
    Correo: str
    Contraseña: str

class GInstrumento(BaseModel):
    Nombre: str
    CodigoDeBarras: str
    Cantidad: int
    Activo: bool


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
async def crear_usuario(usuario: Usuario,
                        response: Response,
                        idusuario: int = Header(..., alias="idUsuario")):
    try:
        if not usuario.Correo or not usuario.Contraseña:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"message": "Correo o contraseña vacíos"}

        connection = utils.get_connection()
        with connection.cursor() as cursor:

            cursor.execute("SET @idUsuario = %s", (idusuario,))
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
        
@app.put("/updateUsuario/{index}")
async def root(
    index: int,
    usuario: Usuario,
    response: Response,
    idusuario: int = Header(..., alias="idUsuario")
):
    try:
        connection = utils.get_connection()

        with connection.cursor() as cursor:
            # Establecer la variable de sesión en la base de datos
            cursor.execute("SET @idUsuario = %s", (idusuario,))

            # Validar si existe el usuario
            cursor.execute("SELECT * FROM usuario WHERE idUsuario = %s", (index,))
            result = cursor.fetchall()
            if not result:
                return JSONResponse(
                    content={"message": "No se encontraron datos"},
                    media_type="application/json",
                    status_code=status.HTTP_404_NOT_FOUND
                )

            # Realizar la actualización
            cursor.execute(
                "UPDATE usuario SET Nombre = %s, Rol = %s, Correo = %s, Contraseña = %s WHERE idUsuario = %s",
                (usuario.Nombre, usuario.Rol, usuario.Correo, usuario.Contraseña, index)
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
async def root(index : int,
               response: Response,
               idusuario: int = Header(..., alias="idUsuario")):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            cursor.execute("SET @idUsuario = %s", (idusuario,))

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
        

#asd
@app.post("/postEspecialidad/{nombre}")
async def root(nombre : str,
               response: Response,
               idusuario: int = Header(..., alias="idUsuario")):
    try:
        connection = utils.get_connection()

        with connection.cursor() as cursor:
            cursor.execute("SET @idUsuario = %s", (idusuario,))

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
async def root(index : int,
               response: Response,
               idusuario: int = Header(..., alias="idUsuario")
):
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

@app.get("/getInstrumentos")
async def root(response: Response):
    try:
        connection = utils.get_connection()

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM GInstrumento")
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

@app.get("/getInstrumento/{index}")
async def root(index : int, response: Response):
    try:
        connection = utils.get_connection()

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM GInstrumento WHERE idInstrumento = %s", (index))
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

@app.post("/postInstrumento")
async def root(
    instrumento: GInstrumento,
    response: Response,
    idusuario: int = Header(..., alias="idUsuario")
):
    try:
        connection = utils.get_connection()

        with connection.cursor() as cursor:
            cursor.execute("SET @idUsuario = %s", (idusuario,))
            
            cursor.execute("SELECT * FROM GInstrumento WHERE Nombre = %s", (instrumento.Nombre))
            result = cursor.fetchall()
            if result:
                return JSONResponse(
                    content={"message": "Ya existe el instrumento"},
                    media_type="application/json",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            cursor.execute("INSERT INTO GInstrumento (Nombre, CodigoDeBarras, Cantidad) VALUES (%s, %s, %s)", (instrumento.Nombre, instrumento.CodigoDeBarras, instrumento.Cantidad))
            connection.commit()
            return JSONResponse(
                content={"message": "Instrumento insertado correctamente"},
                media_type="application/json",
                status_code=status.HTTP_200_OK
            )
    except Exception as e:
        error = "Error: " + str(e)
        return error
    finally:
        connection.close()

@app.put("/updateInstrumento/{index}")
async def root(
    index: int,
    instrumento: GInstrumento,
    response: Response,
    idusuario: int = Header(..., alias="idUsuario")
):
    try:
        connection = utils.get_connection()

        with connection.cursor() as cursor:
            # Establecer la variable de sesión en la base de datos
            cursor.execute("SET @idUsuario = %s", (idusuario,))

            # Validar si existe el instrumento
            cursor.execute("SELECT * FROM GInstrumento WHERE idInstrumento = %s", (index,))
            result = cursor.fetchall()
            if not result:
                return JSONResponse(
                    content={"message": "No se encontraron datos"},
                    media_type="application/json",
                    status_code=status.HTTP_404_NOT_FOUND
                )

            # Realizar la actualización
            cursor.execute(
                "UPDATE GInstrumento SET Nombre = %s, CodigoDeBarras = %s, Cantidad = %s, Activo = %s WHERE idInstrumento = %s",
                (instrumento.Nombre, instrumento.CodigoDeBarras, instrumento.Cantidad, instrumento.Activo, index)
            )
            connection.commit()
            return JSONResponse(
                content={"message": "Instrumento actualizado correctamente"},
                media_type="application/json",
                status_code=status.HTTP_200_OK
            )
    except Exception as e:
        error = "Error: " + str(e)
        return JSONResponse(
            content={"message": error},
            media_type="application/json",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    finally:
        connection.close()

@app.delete("/deleteInstrumento/{index}")
async def root(index : int,
               response: Response,
               idusuario: int = Header(..., alias="idUsuario")):
    try:
        connection = utils.get_connection()

        with connection.cursor() as cursor:
            cursor.execute("SET @idUsuario = %s", (idusuario,))

            cursor.execute("SELECT * FROM GInstrumento WHERE idInstrumento = %s", (index))
            result = cursor.fetchall()
            if not result:
                return JSONResponse(
                    content={"message": "No existe el instrumento"},
                    media_type="application/json",
                    status_code=status.HTTP_404_NOT_FOUND
                )
            cursor.execute("DELETE FROM GInstrumento WHERE idInstrumento = %s", (index))
            connection.commit()
            return JSONResponse(
                content={"message": "Instrumento eliminado correctamente"},
                media_type="application/json",
                status_code=status.HTTP_200_OK
            )
    except Exception as e:
        error = "Error: " + str(e)
        return error
    finally:
        connection.close()