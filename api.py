import os
import io
# import pdfkit
import pymysql
import utils
from fpdf import FPDF
from jinja2 import Environment, FileSystemLoader
from fastapi import FastAPI, Response, status, HTTPException, Depends, Request
from fastapi.responses import JSONResponse, StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from hashlib import sha256
from pydantic import BaseModel
from datetime import datetime, timedelta, date, time, timedelta, timezone
from typing import Optional, Union, List, Dict


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



app = FastAPI()

origins = ["https://hospitalinfantil.org.mx"]

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

class login(BaseModel):
    Correo: str
    Contrasena: str

class GInstrumento(BaseModel):
    CodigoDeBarras: str
    Cantidad: int
    Nombre: str

class GetInstrumentoRequest(BaseModel):
    idInstrumentoIndividual: Union[int, None] = None
    nombreInstrumentoIndividual: Union[str, None] = None

class UpdateGInstrumentoRequest(BaseModel):
    idInstrumento: Union[int, None] = None
    nombreInstrumento: Union[str, None] = None
    nuevaCantidad: int

class GetInstrumentosPorGrupoRequest(BaseModel):
    idInstrumentoGrupo: Union[int, None] = None
    nombreInstrumentoGrupo: Union[str, None] = None

class NewEquipo(BaseModel):
    Nombre: str

class PutEquipo(BaseModel):
    idEquipo: int 
    Nombre: str

class DeleteEquipoRequest(BaseModel):
    idEquipo: Union[int, None] = None
    nombreEquipo: Union[str, None] = None

class GetEquipoRequest(BaseModel):
    idEquipo: Union[int, None] = None
    nombreEquipo: Union[str, None] = None

class UpdateEquipoInstrumentoRequest(BaseModel):
    idEquipo: int
    herramientas: List[Dict] 

class DeleteEquipoInstrumentoRequest(BaseModel):
    idEquipo: int
    herramientas: List[Dict] 

class Paquete(BaseModel):
    idPaquete: Union[int, None] = None
    Nombre: str
    idEspecialidad: int

class PostPaqueteRequest(BaseModel):
    Nombre: str
    idEspecialidad: int
    equipos: List[Dict] 

class GetPaquetePorEspecialidadRequest(BaseModel):
    idEspecialidad: Union[int, None] = None
    nombreEspecialidad: Union[str, None] = None

class PaqueteInstrumento(BaseModel):
    idPaquete: int
    instrumentos: List[Dict] 

class PaqueteEquipo(BaseModel):
    idPaquete: int
    equipos: List[int] 

class Pedido(BaseModel):
    idPedido: Union[int, None] = None
    Fecha: date
    Hora: time
    Estado: str = "Pedido"
    idPaquete: Union[int, None] = None
    idEnfermero: Union[int, None] = None
    nombreEnfermero: Union[str, None] = None
    Cirugia: str
    Ubicacion: str

class UpdatePedidoRequest(BaseModel):
    idPedido: int
    Fecha: Union[date, None] = None
    Hora: Union[time, None] = None
    Estado: Union[str, None] = None
    idPaquete: Union[int, None] = None
    idEnfermero: Union[int, None] = None
    nombreEnfermero: Union[str, None] = None
    Cirugia: Union[str, None] = None
    Ubicacion: Union[str, None] = None

class PedidoEquipo(BaseModel):
    idPedido: int
    equipos: List[int]  

class Instrumento(BaseModel):
    idInstrumento: Union[int, None] = None  
    nombreInstrumento: Union[str, None] = None  
    cantidad: int  

class PedidoInstrumento(BaseModel):
    idPedido: int 
    instrumentos: List[Instrumento]  

class DeletePedidoEquipoRequest(BaseModel):
    idPedido: int
    equipos: List[int]  

class GetPedidoRequest(BaseModel):
    idPedido: int

class Equipo(BaseModel):
    idEquipo: Union[int, None] = None  
    nombreEquipo: Union[str, None] = None 

class PedidoEquipo(BaseModel):
    idPedido: int  
    equipos: List[Equipo]  

class DeletePedidoEquipoRequest(BaseModel):
    idPedido: int  
    equipos: List[Equipo]  

class DeletePedidoRequest(BaseModel):
    idPedido: int

class DeletePaqueteEquipoRequest(BaseModel):
    idPaquete: int
    equipos: List[Dict] 

class DeletePaqueteRequest(BaseModel):
    idPaquete: Union[int, None] = None
    nombrePaquete: Union[str, None] = None

class GetPaqueteRequest(BaseModel):
    idPaquete: Union[int, None] = None
    nombrePaquete: Union[str, None] = None



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')



def obtener_datos_historial_paquetes():
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            # ✅ Obtener el historial con nombres de paquetes y usuarios
            cursor.execute("""
                SELECT hp.idHistorialPaquete, p.Nombre AS nombrePaquete, hp.tipoOperacion, 
                       hp.campo, hp.valorAnterior, hp.valorNuevo, hp.observaciones, hp.fechaCambio, 
                       COALESCE(CONCAT(u.Nombres, ' ', u.ApellidoPaterno, ' ', COALESCE(u.ApellidoMaterno, '')), 'Usuario desconocido') AS usuario
                FROM Historial_Paquetes hp
                LEFT JOIN Paquete p ON hp.idPaquete = p.idPaquete
                LEFT JOIN Usuario u ON hp.idUsuario = u.idUsuario
                ORDER BY hp.fechaCambio DESC;
            """)
            historial_paquetes = cursor.fetchall()

            # ✅ Obtener los nombres de los equipos directamente desde la tabla `Equipo`
            cursor.execute("""
                SELECT e.idEquipo, e.Nombre AS nombreEquipo
                FROM Equipo e;
            """)
            equipos_por_id = {row[0]: row[1] for row in cursor.fetchall()}

            cursor.execute("""
                SELECT gi.idInstrumento, gi.Nombre AS nombreInstrumento
                FROM GInstrumento gi;
            """)
            instrumentos_por_id = {row[0]: row[1] for row in cursor.fetchall()}

            historial_completo = []
            for paquete in historial_paquetes:
                nombreEquipo = equipos_por_id.get(paquete[0], "Sin equipo asociado")
                nombreInstrumento = instrumentos_por_id.get(paquete[0], "Sin instrumento asociado")
                
                historial_completo.append(paquete + (nombreEquipo, nombreInstrumento))

        return {
            "historial_paquetes": historial_completo,
            "fecha_reporte": datetime.now().strftime("%d/%m/%Y %H:%M"),
        }
    except pymysql.Error as e:
        print(f"Error MySQL: {e}")
        return None
    finally:
        connection.close()

def generar_pdf_historial_paquetes():
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    template = env.get_template("historial_paquetes.html")

    datos = obtener_datos_historial_paquetes()
    if not datos:
        raise HTTPException(status_code=500, detail="No se obtuvieron datos de la base de datos")

    pdf_options = {
        "page-size": "A4",
        "margin-top": "15mm",
        "encoding": "UTF-8",
        "footer-right": "[page]/[topage]",
        "quiet": "",
    }

    html_renderizado = template.render(datos)

    return io.BytesIO(html_renderizado.encode("utf-8"))

def obtener_datos_historial_pedido():
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT hp.idHistorialPedido, hp.idPedido, hp.estadoAnterior, hp.estadoNuevo, 
                       hp.fechaCambio, 
                       COALESCE(CONCAT(u.Nombres, ' ', u.ApellidoPaterno, ' ', COALESCE(u.ApellidoMaterno, '')), 'Usuario desconocido') AS usuario
                FROM Historial_Pedido hp
                LEFT JOIN Usuario u ON hp.idUsuario = u.idUsuario
                ORDER BY hp.idHistorialPedido ASC; 
            """)
            historial_pedido = cursor.fetchall()

        return {
            "historial_pedido": historial_pedido,
            "fecha_reporte": datetime.now().strftime("%d/%m/%Y %H:%M"),
        }
    except pymysql.Error as e:
        print(f"Error MySQL: {e}")
        return None
    finally:
        connection.close()

def generar_html_historial_pedido():
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    template = env.get_template("historial_pedido.html")

    datos = obtener_datos_historial_pedido()
    if not datos:
        raise HTTPException(status_code=500, detail="No se obtuvieron datos de la base de datos")

    return template.render(datos)

def obtener_datos_historial_equipos():
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT he.idHistorialEquipo, e.Nombre AS nombreEquipo, gi.Nombre AS nombreInstrumento, 
                       he.tipoOperacion, he.campo, he.valorAnterior, he.valorNuevo, 
                       he.observaciones, he.fechaCambio, 
                       COALESCE(CONCAT(u.Nombres, ' ', u.ApellidoPaterno, ' ', COALESCE(u.ApellidoMaterno, '')), 'Usuario desconocido') AS usuario
                FROM Historial_Equipos he
                LEFT JOIN Equipo e ON he.idEquipo = e.idEquipo
                LEFT JOIN GInstrumento gi ON he.idInstrumento = gi.idInstrumento
                LEFT JOIN Usuario u ON he.idUsuario = u.idUsuario
                ORDER BY he.idHistorialEquipo ASC; 
            """)
            historial_equipos = cursor.fetchall()

        return {
            "historial_equipos": historial_equipos,
            "fecha_reporte": datetime.now().strftime("%d/%m/%Y %H:%M"),
        }
    except pymysql.Error as e:
        print(f"Error MySQL: {e}")
        return None
    finally:
        connection.close()

def generar_pdf_historial_equipos():
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    template = env.get_template("historial_equipos.html")

    datos = obtener_datos_historial_equipos()
    if not datos:
        raise HTTPException(status_code=500, detail="No se obtuvieron datos de la base de datos")

    html_renderizado = template.render(datos)

    return io.BytesIO(html_renderizado.encode("utf-8"))

def obtener_datos_historial_ginstrumento():
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            # ✅ Obtener historial con nombres de instrumentos y usuarios
            cursor.execute("""
                SELECT hg.idHistorial, gi.Nombre AS nombreInstrumento, 
                       hg.observaciones, hg.fechaCambio, 
                       COALESCE(CONCAT(u.Nombres, ' ', u.ApellidoPaterno, ' ', COALESCE(u.ApellidoMaterno, '')), 'Usuario desconocido') AS usuario
                FROM Historial_GInstrumento hg
                LEFT JOIN GInstrumento gi ON hg.idInstrumento = gi.idInstrumento
                LEFT JOIN Usuario u ON hg.idUsuario = u.idUsuario
                ORDER BY hg.idHistorial ASC; 
            """)
            historial_ginstrumento = cursor.fetchall()

        return {
            "historial_ginstrumento": historial_ginstrumento,
            "fecha_reporte": datetime.now().strftime("%d/%m/%Y %H:%M"),
        }
    except pymysql.Error as e:
        print(f"Error MySQL: {e}")
        return None
    finally:
        connection.close()

def generar_pdf_historial_ginstrumento():
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    template = env.get_template("historial_ginstrumento.html")

    datos = obtener_datos_historial_ginstrumento()
    if not datos:
        raise HTTPException(status_code=500, detail="No se obtuvieron datos de la base de datos")

    html_renderizado = template.render(datos)

    return io.BytesIO(html_renderizado.encode("utf-8"))

def obtener_datos_historial_iinstrumento():
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT hi.idHistorialIndividual, gi.Nombre AS nombreHerramienta, 
                       hi.observaciones, hi.fechaCambio, 
                       COALESCE(CONCAT(u.Nombres, ' ', u.ApellidoPaterno, ' ', COALESCE(u.ApellidoMaterno, '')), 'Usuario desconocido') AS usuario
                FROM Historial_IInstrumento hi
                LEFT JOIN IInstrumento ii ON hi.idInstrumentoIndividual = ii.idInstrumentoIndividual
                LEFT JOIN GInstrumento gi ON ii.idInstrumentoGrupo = gi.idInstrumento
                LEFT JOIN Usuario u ON hi.idUsuario = u.idUsuario
                ORDER BY hi.idHistorialIndividual ASC; 
            """)
            historial_iinstrumento = cursor.fetchall()

        return {
            "historial_iinstrumento": historial_iinstrumento,
            "fecha_reporte": datetime.now().strftime("%d/%m/%Y %H:%M"),
        }
    except pymysql.Error as e:
        print(f"Error MySQL: {e}")
        return None
    finally:
        connection.close()

def generar_pdf_historial_iinstrumento():
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    template = env.get_template("historial_iinstrumento.html")

    datos = obtener_datos_historial_iinstrumento()
    if not datos:
        raise HTTPException(status_code=500, detail="No se obtuvieron datos de la base de datos")

    html_renderizado = template.render(datos)

    return io.BytesIO(html_renderizado.encode("utf-8"))

@app.get("/getHistorialIInstrumento")
async def descargar_historial_iinstrumento():
    pdf_file = generar_pdf_historial_iinstrumento()
    return StreamingResponse(pdf_file, media_type="text/html",
                             headers={"Content-Disposition": "inline; filename=Historial_IInstrumento.html"})

@app.get("/getHistorialGInstrumento")
async def descargar_historial_ginstrumento():
    pdf_file = generar_pdf_historial_ginstrumento()
    return StreamingResponse(pdf_file, media_type="text/html",
                             headers={"Content-Disposition": "inline; filename=Historial_GInstrumento.html"})

@app.get("/getHistorialEquipos")
async def descargar_historial_equipos():
    pdf_file = generar_pdf_historial_equipos()
    return StreamingResponse(pdf_file, media_type="text/html",
                             headers={"Content-Disposition": "inline; filename=Historial_Equipos.html"})

@app.get("/getHistorialPedido")
async def descargar_historial_pedido():
    html_content = generar_html_historial_pedido()
    return HTMLResponse(content=html_content)

@app.get("/getHistorialPaquetes")
async def descargar_historial_paquetes():
    pdf_file = generar_pdf_historial_paquetes()
    return StreamingResponse(pdf_file, media_type="text/html",
                             headers={"Content-Disposition": "inline; filename=Historial_Paquetes.html"})

@app.post("/logout")
async def root(response: Response):
    try:
        response.delete_cookie("access_token",path="/")
        return {"message": "Logout exitoso"}
    except:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "Token inválido"}
    
@app.post("/login")
async def root(response: Response, login: login):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            hashed_password = sha256(login.Contrasena.encode()).hexdigest()
            cursor.execute("SELECT * FROM Usuario WHERE Correo = %s AND Contrasena = %s", (login.Correo, hashed_password))
            result = cursor.fetchall()
            
            if not result:
                return JSONResponse(
                    content={"message": "Usuario o contraseña incorrectos"},
                    status_code=status.HTTP_401_UNAUTHORIZED
                )
            
            token = utils.create_access_token(data={
                "idUsuario": result[0][0],
                "correo": result[0][4],
                "rol": result[0][5]
            })

            response = JSONResponse(
                content={"message": "Login exitoso"},
                status_code=status.HTTP_200_OK
            )
            response.set_cookie(
                key="access_token",
                value=token,
                httponly=True,
                secure=False,  # Solo en desarrollo
                samesite="lax",
                max_age=int(timedelta(days=10).total_seconds()),
                path="/"
            )
            return response

    except Exception as e:
        return JSONResponse(
            content={"message": "Error interno", "detail": str(e)},
            status_code=500
        )
    finally:
        connection.close()
        
@app.get("/fetchRol")
async def root(response: Response):
    try:
        payload = utils.verify_token(token)
        if not payload:
            response.status_code = status.HTTP_401_UNAUTHORIZED
            return {"message": "Token inválido"}
        return JSONResponse(
            content={"rol": payload["rol"]},
            media_type="application/json",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        error = "Error: " + str(e)
        return error

@app.get("/protectedAdmin")
async def root(response: Response):
    try:
        payload = utils.verify_token(token)
        if payload["rol"] != "Administrador":
            response.status_code = status.HTTP_403_FORBIDDEN
            return {"message": "No tienes permiso para acceder a esta ruta"}
        return JSONResponse(
            content={"message": "Acceso permitido"},
            media_type="application/json",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        error = "Error: " + str(e)
        return error

    
@app.get("/protectedAlmacenista")
async def root(response: Response):
    try:
        payload = utils.verify_token(token)
        if payload["rol"] != "Almacenista" and payload["rol"] != "Administrador":
            response.status_code = status.HTTP_403_FORBIDDEN
            return {"message": "No tienes permiso para acceder a esta ruta"}
        return JSONResponse(
            content={"message": "Acceso permitido"},
            media_type="application/json",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        error = "Error: " + str(e)
        return error
    
@app.get("/protectedEnfermero")
async def root(response: Response):
    try:
        payload = utils.verify_token(token)
        if payload["rol"] != "Enfermero" and payload["rol"] != "Administrador":
            response.status_code = status.HTTP_403_FORBIDDEN
            return {"message": "No tienes permiso para acceder a esta ruta"}
        return JSONResponse(
            content={"message": "Acceso permitido"},
            media_type="application/json",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        error = "Error: " + str(e)
        return error

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
    # payload = utils.verify_token(token)
    # if payload["rol"] != "Administrador":
    #     response.status_code = status.HTTP_403_FORBIDDEN
    #     return {"message": "No tienes permiso para acceder a esta ruta"}
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            contrasena = 0
            cursor.execute("SELECT * FROM Usuario WHERE idUsuario = %s", (index))
            result = cursor.fetchall()
            if not result:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "No existe el usuario"}
            if usuario.Contrasena == "":
                contrasena = result[0][6]
            else:
                contrasena = sha256(usuario.Contrasena.encode()).hexdigest()
            cursor.execute(
                "UPDATE Usuario SET Nombres = %s, ApellidoPaterno = %s, ApellidoMaterno = %s, Rol = %s, Correo = %s, Contrasena = %s WHERE idUsuario = %s",
                (usuario.Nombres, usuario.ApellidoPaterno, usuario.ApellidoMaterno , usuario.Rol, usuario.Correo, contrasena, index)
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

@app.post("/postGInstrumento")
async def crear_ginstrumento(grupo: GInstrumento, response: Response):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
        #     payload = utils.verify_token(token)
        #     if payload["rol"] != "Administrador":
        #         response.status_code = status.HTTP_403_FORBIDDEN
        #         return {"message": "No tienes permiso para acceder a esta ruta"}
            # cursor.execute("SET @idUsuario = %s", (payload["idUsuario"]))

            cursor.execute("SELECT idInstrumento FROM GInstrumento WHERE CodigoDeBarras = %s", (grupo.CodigoDeBarras,))
            existe = cursor.fetchone()
            
            if existe:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return {"message": "Error: El código de barras ya existe en la base de datos"}

            cursor.execute("""
                INSERT INTO GInstrumento (CodigoDeBarras, Cantidad, Nombre)
                VALUES (%s, %s, %s)
            """, (grupo.CodigoDeBarras, grupo.Cantidad, grupo.Nombre))
            connection.commit()
            
            id_grupo = cursor.lastrowid

            for _ in range(grupo.Cantidad):
                cursor.execute("""
                    INSERT INTO IInstrumento (idInstrumentoGrupo, Estado, Ubicacion, ultimaEsterilizacion)
                    VALUES (%s, %s, %s, NOW())
                """, (id_grupo, "Disponible", "Almacén"))
            
            connection.commit()
            return {"message": "Grupo de instrumentos registrado y cantidad reflejada en IInstrumento"}
    
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}
    
    finally:
        connection.close()

@app.get("/getInstrumento")
async def obtener_instrumento(data: GetInstrumentoRequest, response: Response):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            # payload = utils.verify_token(token)
            # if payload["rol"] != "Administrador":
            #     response.status_code = status.HTTP_403_FORBIDDEN
            #     return {"message": "No tienes permiso para acceder a esta ruta"}

            # cursor.execute("SET @idUsuario = %s", (payload["idUsuario"]))

            if data.idInstrumentoIndividual:
                cursor.execute("""SELECT i.idInstrumentoIndividual, g.Nombre, i.ultimaEsterilizacion, i.Estado, i.Ubicacion, i.idInstrumentoGrupo
                                  FROM IInstrumento i
                                  JOIN GInstrumento g ON i.idInstrumentoGrupo = g.idInstrumento
                                  WHERE i.idInstrumentoIndividual = %s""", (data.idInstrumentoIndividual,))
                instrumento = cursor.fetchone()
            elif data.nombreInstrumentoIndividual:
                cursor.execute("""SELECT i.idInstrumentoIndividual, g.Nombre, i.ultimaEsterilizacion, i.Estado, i.Ubicacion, i.idInstrumentoGrupo
                                  FROM IInstrumento i
                                  JOIN GInstrumento g ON i.idInstrumentoGrupo = g.idInstrumento
                                  WHERE g.Nombre = %s""", (data.nombreInstrumentoIndividual,))
                instrumento = cursor.fetchone()
            else:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return {"message": "Debe proporcionar un idInstrumentoIndividual o un nombreInstrumentoIndividual"}

            if not instrumento:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "Instrumento no encontrado"}

            return {
                "idInstrumentoIndividual": instrumento[0],
                "Nombre": instrumento[1],
                "ultimaEsterilizacion": instrumento[2],
                "Estado": instrumento[3],
                "Ubicacion": instrumento[4],
                "idInstrumentoGrupo": instrumento[5]
            }

    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}

    finally:
        connection.close()

@app.get("/getInstrumentos")
async def obtener_todos_los_instrumentos(response: Response):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            # payload = utils.verify_token(token)
            # if payload["rol"] != "Administrador":
            #     response.status_code = status.HTTP_403_FORBIDDEN
            #     return {"message": "No tienes permiso para acceder a esta ruta"}
            cursor.execute("""
                SELECT i.idInstrumentoIndividual, i.idInstrumentoGrupo, g.Nombre, i.ultimaEsterilizacion, i.Estado, i.Ubicacion
                FROM IInstrumento i
                JOIN GInstrumento g ON i.idInstrumentoGrupo = g.idInstrumento
            """)
            instrumentos = cursor.fetchall()

            return [{"idInstrumentoIndividual": i[0], "idInstrumentoGrupo": i[1], "Nombre": i[2], 
                     "ultimaEsterilizacion": i[3], "Estado": i[4], "Ubicacion": i[5]} for i in instrumentos]
    
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}

    finally:
        connection.close()

@app.get("/getInstrumentosPorGrupo")
async def obtener_instrumentos_por_grupo(data: GetInstrumentosPorGrupoRequest, response: Response):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            # payload = utils.verify_token(token)
            # if payload["rol"] != "Administrador":
            #     response.status_code = status.HTTP_403_FORBIDDEN
            #     return {"message": "No tienes permiso para acceder a esta ruta"}

            if data.idInstrumentoGrupo:
                cursor.execute("""SELECT i.idInstrumentoIndividual, g.Nombre, i.ultimaEsterilizacion, i.Estado, i.Ubicacion
                                  FROM IInstrumento i
                                  JOIN GInstrumento g ON i.idInstrumentoGrupo = g.idInstrumento
                                  WHERE i.idInstrumentoGrupo = %s""", (data.idInstrumentoGrupo,))
                instrumentos = cursor.fetchall()
            elif data.nombreInstrumentoGrupo:
                cursor.execute("""SELECT i.idInstrumentoIndividual, g.Nombre, i.ultimaEsterilizacion, i.Estado, i.Ubicacion
                                  FROM IInstrumento i
                                  JOIN GInstrumento g ON i.idInstrumentoGrupo = g.idInstrumento
                                  WHERE g.Nombre = %s""", (data.nombreInstrumentoGrupo,))
                instrumentos = cursor.fetchall()
            else:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return {"message": "Debe proporcionar un idInstrumentoGrupo o un nombreInstrumentoGrupo"}

            if not instrumentos:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "No se encontraron instrumentos en este grupo"}

            return [{"idInstrumentoIndividual": i[0], "Nombre": i[1], "ultimaEsterilizacion": i[2], 
                     "Estado": i[3], "Ubicacion": i[4]} for i in instrumentos]

    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}

    finally:
        connection.close()


@app.put("/updateGInstrumento")
async def actualizar_ginstrumento(data: UpdateGInstrumentoRequest, response: Response):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            # payload = utils.verify_token(token)
            # if payload["rol"] != "Administrador":
            #     response.status_code = status.HTTP_403_FORBIDDEN
            #     return {"message": "No tienes permiso para acceder a esta ruta"}

            # cursor.execute("SET @idUsuario = %s", (payload["idUsuario"]))

            if data.idInstrumento:
                cursor.execute("SELECT idInstrumento, Cantidad FROM GInstrumento WHERE idInstrumento = %s", (data.idInstrumento,))
                grupo = cursor.fetchone()
            elif data.nombreInstrumento:
                cursor.execute("SELECT idInstrumento, Cantidad FROM GInstrumento WHERE Nombre = %s", (data.nombreInstrumento,))
                grupo = cursor.fetchone()
            else:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return {"message": "Debe proporcionar un idInstrumento o un nombreInstrumento"}

            if not grupo:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "Grupo de instrumentos no encontrado"}

            idInstrumento = grupo[0]
            cantidad_actual = grupo[1]
            diferencia = data.nuevaCantidad - cantidad_actual

            if diferencia > 0:  
                for _ in range(diferencia):
                    cursor.execute("""
                        INSERT INTO IInstrumento (idInstrumentoGrupo, Estado, Ubicacion, ultimaEsterilizacion)
                        VALUES (%s, %s, %s, NOW())
                    """, (idInstrumento, "Disponible", "Almacén"))
            
            elif diferencia < 0:  
                cantidad_a_eliminar = abs(diferencia)

                cursor.execute("""
                    SELECT idInstrumentoIndividual FROM IInstrumento 
                    WHERE idInstrumentoGrupo = %s AND Estado = 'Disponible' LIMIT %s
                """, (idInstrumento, cantidad_a_eliminar))

                instrumentos_disponibles = cursor.fetchall()
                if len(instrumentos_disponibles) < cantidad_a_eliminar:
                    response.status_code = status.HTTP_400_BAD_REQUEST
                    return {"message": "No hay suficientes instrumentos disponibles para eliminar"}

                for instrumento in instrumentos_disponibles:
                    cursor.execute("DELETE FROM IInstrumento WHERE idInstrumentoIndividual = %s", (instrumento[0],))

                cursor.execute("""
                    UPDATE Equipo_Instrumento 
                    SET cantidad = GREATEST(cantidad - %s, 0) 
                    WHERE idInstrumento = %s
                """, (cantidad_a_eliminar, idInstrumento))

                cursor.execute("""
                    UPDATE Paquete_Instrumento 
                    SET cantidad = GREATEST(cantidad - %s, 0) 
                    WHERE idInstrumento = %s
                """, (cantidad_a_eliminar, idInstrumento))

                cursor.execute("""
                    UPDATE Pedido_GInstrumento 
                    SET cantidad = GREATEST(cantidad - %s, 0) 
                    WHERE idInstrumento = %s
                """, (cantidad_a_eliminar, idInstrumento))

            cursor.execute("UPDATE GInstrumento SET Cantidad = %s WHERE idInstrumento = %s", (data.nuevaCantidad, idInstrumento))
            connection.commit()

            return {"message": f"Grupo de instrumentos actualizado correctamente en todas las tablas dependientes"}

    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}

    finally:
        connection.close()

@app.post("/postEquipo")
async def crear_equipo(equipo: NewEquipo, response: Response):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            # payload = utils.verify_token(token)
            # if payload["rol"] != "Administrador":
            #     response.status_code = status.HTTP_403_FORBIDDEN
            #     return {"message": "No tienes permiso para acceder a esta ruta"}
            # cursor.execute("SET @idUsuario = %s", (payload["idUsuario"]))
            cursor.execute("INSERT INTO Equipo (Nombre) VALUES (%s)", (equipo.Nombre,))
            connection.commit()
            return {"message": "Equipo registrado correctamente"}
    
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}
    
    finally:
        connection.close()

@app.put("/updateEquipo")
async def actualizar_equipo(equipo: PutEquipo, response: Response):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            # payload = utils.verify_token(token)
            # if payload["rol"] != "Administrador":
            #     response.status_code = status.HTTP_403_FORBIDDEN
            #     return {"message": "No tienes permiso para acceder a esta ruta"}
            # cursor.execute("SET @idUsuario = %s", (payload["idUsuario"]))
            idEquipo = equipo.idEquipo
            nuevoNombre = equipo.Nombre

            if not idEquipo or not nuevoNombre:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return {"message": "Faltan parámetros en el JSON"}

            cursor.execute("SELECT * FROM Equipo WHERE idEquipo = %s", (idEquipo,))
            existe = cursor.fetchone()
            
            if not existe:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "Equipo no encontrado"}
            
            cursor.execute("UPDATE Equipo SET Nombre = %s WHERE idEquipo = %s", (nuevoNombre, idEquipo))
            connection.commit()
            return {"message": "Equipo actualizado correctamente"}
    
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}
    
    finally:
        connection.close()

@app.get("/getEquipo")
async def obtener_equipo(data: GetEquipoRequest, response: Response):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            # payload = utils.verify_token(token)
            # if payload["rol"] != "Administrador":
            #     response.status_code = status.HTTP_403_FORBIDDEN
            #     return {"message": "No tienes permiso para acceder a esta ruta"}

            # cursor.execute("SET @idUsuario = %s", (payload["idUsuario"]))

            if data.idEquipo:
                cursor.execute("""SELECT idEquipo, Nombre FROM Equipo WHERE idEquipo = %s""", (data.idEquipo,))
                equipo = cursor.fetchone()
            elif data.nombreEquipo:
                cursor.execute("""SELECT idEquipo, Nombre FROM Equipo WHERE Nombre = %s""", (data.nombreEquipo,))
                equipo = cursor.fetchone()
            else:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return {"message": "Debe proporcionar un idEquipo o un nombreEquipo"}

            if not equipo:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "Equipo no encontrado"}

            cursor.execute("""SELECT g.Nombre, ei.cantidad 
                              FROM Equipo_Instrumento ei
                              JOIN GInstrumento g ON ei.idInstrumento = g.idInstrumento
                              WHERE ei.idEquipo = %s""", (equipo[0],))
            herramientas = cursor.fetchall()

            return {
                "idEquipo": equipo[0],
                "Nombre": equipo[1],
                "herramientas": [{"nombreInstrumento": h[0], "cantidad": h[1]} for h in herramientas]
            }

    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}

    finally:
        connection.close()

@app.get("/getEquipos")
async def obtener_todos_los_equipos(response: Response):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            # payload = utils.verify_token(token)
            # if payload["rol"] != "Administrador":
            #     response.status_code = status.HTTP_403_FORBIDDEN
            #     return {"message": "No tienes permiso para acceder a esta ruta"}

            # cursor.execute("SET @idUsuario = %s", (payload["idUsuario"]))
            cursor.execute("SELECT idEquipo, Nombre FROM Equipo")
            equipos = cursor.fetchall()

            return [{"idEquipo": equipo[0], "Nombre": equipo[1]} for equipo in equipos]

    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}

    finally:
        connection.close()


@app.delete("/deleteEquipo")
async def eliminar_equipo(data: DeleteEquipoRequest, response: Response):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            # payload = utils.verify_token(token)
            # if payload["rol"] != "Administrador":
            #     response.status_code = status.HTTP_403_FORBIDDEN
            #     return {"message": "No tienes permiso para acceder a esta ruta"}
            # cursor.execute("SET @idUsuario = %s", (payload["idUsuario"]))

            if data.idEquipo:
                cursor.execute("SELECT idEquipo FROM Equipo WHERE idEquipo = %s", (data.idEquipo,))
                equipo = cursor.fetchone()
            elif data.nombreEquipo:
                cursor.execute("SELECT idEquipo FROM Equipo WHERE Nombre = %s", (data.nombreEquipo,))
                equipo = cursor.fetchone()
            else:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return {"message": "Debe proporcionar un idEquipo o un nombreEquipo"}

            if not equipo:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "Equipo no encontrado"}

            cursor.execute("DELETE FROM Equipo_Instrumento WHERE idEquipo = %s", (equipo[0],))
            cursor.execute("DELETE FROM Equipo WHERE idEquipo = %s", (equipo[0],))

            connection.commit()
            return {"message": f"Equipo {equipo[0]} eliminado correctamente junto con sus herramientas asociadas"}

    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}

    finally:
        connection.close()

@app.put("/updateEquipoInstrumento")
async def actualizar_herramientas_equipo(data: UpdateEquipoInstrumentoRequest, response: Response):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            # payload = utils.verify_token(token)
            # if payload["rol"] != "Administrador":
            #     response.status_code = status.HTTP_403_FORBIDDEN
            #     return {"message": "No tienes permiso para acceder a esta ruta"}
            # cursor.execute("SET @idUsuario = %s", (payload["idUsuario"]))

            cursor.execute("SELECT idEquipo FROM Equipo WHERE idEquipo = %s", (data.idEquipo,))
            equipo_existente = cursor.fetchone()
            if not equipo_existente:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "Equipo no encontrado"}

            for herramienta in data.herramientas:
                idInstrumento = herramienta.get("idInstrumento")
                nombreInstrumento = herramienta.get("nombreInstrumento")
                cantidad = herramienta["cantidad"]

                if cantidad <= 0:  
                    response.status_code = status.HTTP_400_BAD_REQUEST
                    return {"message": f"No se puede agregar o modificar un instrumento con cantidad {cantidad}"}

                if nombreInstrumento:
                    cursor.execute("SELECT idInstrumento FROM GInstrumento WHERE Nombre = %s", (nombreInstrumento,))
                    instrumento_data = cursor.fetchone()
                    if not instrumento_data:
                        response.status_code = status.HTTP_404_NOT_FOUND
                        return {"message": f"Instrumento con nombre '{nombreInstrumento}' no encontrado"}
                    idInstrumento = instrumento_data[0]

                cursor.execute("SELECT Cantidad FROM GInstrumento WHERE idInstrumento = %s", (idInstrumento,))
                instrumento_existente = cursor.fetchone()
                if not instrumento_existente:
                    response.status_code = status.HTTP_404_NOT_FOUND
                    return {"message": f"Instrumento con id {idInstrumento} no encontrado"}

                cantidad_disponible = instrumento_existente[0]

                if cantidad_disponible <= 0:  
                    response.status_code = status.HTTP_400_BAD_REQUEST
                    return {"message": f"No hay unidades disponibles del instrumento con id {idInstrumento}, no se puede agregar"}

                cantidad_final = min(cantidad, cantidad_disponible)
                cursor.execute("""
                    INSERT INTO Equipo_Instrumento (idEquipo, idInstrumento, cantidad)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE cantidad = %s
                """, (data.idEquipo, idInstrumento, cantidad_final, cantidad_final))

            connection.commit()
            return {"message": "Cantidad de herramientas modificada o agregada correctamente"}

    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}

    finally:
        connection.close()


@app.delete("/deleteEquipoInstrumento")
async def eliminar_herramientas_equipo(data: DeleteEquipoInstrumentoRequest, response: Response):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            # payload = utils.verify_token(token)
            # if payload["rol"] != "Administrador":
            #     response.status_code = status.HTTP_403_FORBIDDEN
            #     return {"message": "No tienes permiso para acceder a esta ruta"}
            # cursor.execute("SET @idUsuario = %s", (payload["idUsuario"]))

            cursor.execute("SELECT idEquipo FROM Equipo WHERE idEquipo = %s", (data.idEquipo,))
            equipo_existente = cursor.fetchone()
            if not equipo_existente:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "Equipo no encontrado"}

            eliminados = []

            for herramienta in data.herramientas:
                idInstrumento = herramienta.get("idInstrumento")
                nombreInstrumento = herramienta.get("nombreInstrumento")

                if nombreInstrumento:
                    cursor.execute("SELECT idInstrumento FROM GInstrumento WHERE Nombre = %s", (nombreInstrumento,))
                    instrumento_data = cursor.fetchone()
                    if not instrumento_data:
                        response.status_code = status.HTTP_404_NOT_FOUND
                        return {"message": f"Instrumento con nombre '{nombreInstrumento}' no encontrado"}
                    idInstrumento = instrumento_data[0]

                cursor.execute("SELECT cantidad FROM Equipo_Instrumento WHERE idEquipo = %s AND idInstrumento = %s",
                               (data.idEquipo, idInstrumento))
                instrumento_equipo = cursor.fetchone()
                if not instrumento_equipo:
                    response.status_code = status.HTTP_404_NOT_FOUND
                    return {"message": f"Instrumento con id {idInstrumento} no está en el equipo"}

                cursor.execute("DELETE FROM Equipo_Instrumento WHERE idEquipo = %s AND idInstrumento = %s",
                               (data.idEquipo, idInstrumento))
                eliminados.append(f"ID {idInstrumento}" if nombreInstrumento is None else f"Nombre '{nombreInstrumento}'")

            connection.commit()
            return {"message": f"Herramientas eliminadas correctamente del equipo {data.idEquipo}: {', '.join(eliminados)}"}

    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}

    finally:
        connection.close()


@app.post("/postPaquete")
async def crear_paquete(data: PostPaqueteRequest, response: Response):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            # payload = utils.verify_token(token)
            # if payload["rol"] != "Administrador":
            #     response.status_code = status.HTTP_403_FORBIDDEN
            #     return {"message": "No tienes permiso para acceder a esta ruta"}
            # cursor.execute("SET @idUsuario = %s", (payload["idUsuario"]))

            cursor.execute("SELECT idEspecialidad FROM Especialidad WHERE idEspecialidad = %s", (data.idEspecialidad,))
            especialidad_existente = cursor.fetchone()
            if not especialidad_existente:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "Especialidad no encontrada"}

            cursor.execute("INSERT INTO Paquete (Nombre, idEspecialidad) VALUES (%s, %s)", 
                           (data.Nombre, data.idEspecialidad))
            paquete_id = cursor.lastrowid  

            equipos_asociados = []
            for equipo in data.equipos:
                idEquipo = equipo.get("idEquipo")
                nombreEquipo = equipo.get("nombreEquipo")

                if idEquipo:
                    cursor.execute("SELECT idEquipo FROM Equipo WHERE idEquipo = %s", (idEquipo,))
                    equipo_existente = cursor.fetchone()
                    if not equipo_existente:
                        response.status_code = status.HTTP_404_NOT_FOUND
                        return {"message": f"Equipo con id {idEquipo} no encontrado"}
                elif nombreEquipo:
                    cursor.execute("SELECT idEquipo FROM Equipo WHERE Nombre = %s", (nombreEquipo,))
                    equipo_data = cursor.fetchone()
                    if not equipo_data:
                        response.status_code = status.HTTP_404_NOT_FOUND
                        return {"message": f"Equipo con nombre '{nombreEquipo}' no encontrado"}
                    idEquipo = equipo_data[0]
                else:
                    response.status_code = status.HTTP_400_BAD_REQUEST
                    return {"message": "Cada equipo debe tener un idEquipo o un nombreEquipo"}

                cursor.execute("INSERT INTO Paquete_Equipo (idPaquete, idEquipo) VALUES (%s, %s)", (paquete_id, idEquipo))
                equipos_asociados.append(idEquipo)

            connection.commit()
            return {"message": "Paquete registrado correctamente", "idPaquete": paquete_id, "equiposAsociados": equipos_asociados}

    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}

    finally:
        connection.close()


@app.get("/getPaquetes")
async def obtener_todos_los_paquetes(response: Response):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            # payload = utils.verify_token(token)
            # if payload["rol"] != "Administrador":
            #     response.status_code = status.HTTP_403_FORBIDDEN
            #     return {"message": "No tienes permiso para acceder a esta ruta"}
            # cursor.execute("SET @idUsuario = %s", (payload["idUsuario"]))
            cursor.execute("""
                SELECT p.idPaquete, p.Nombre, e.Nombre AS Especialidad
                FROM Paquete p
                JOIN Especialidad e ON p.idEspecialidad = e.idEspecialidad
            """)
            paquetes = cursor.fetchall()

            return [{"idPaquete": p[0], "Nombre": p[1], "Especialidad": p[2]} for p in paquetes]
    
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}
    
    finally:
        connection.close()

@app.get("/getPaquete")
async def obtener_paquete(data: GetPaqueteRequest, response: Response):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            # payload = utils.verify_token(token)
            # if payload["rol"] != "Administrador":
            #     response.status_code = status.HTTP_403_FORBIDDEN
            #     return {"message": "No tienes permiso para acceder a esta ruta"}

            # cursor.execute("SET @idUsuario = %s", (payload["idUsuario"]))

            if data.idPaquete:
                cursor.execute("""SELECT p.idPaquete, p.Nombre, e.Nombre AS Especialidad
                                  FROM Paquete p
                                  JOIN Especialidad e ON p.idEspecialidad = e.idEspecialidad
                                  WHERE p.idPaquete = %s""", (data.idPaquete,))
                paquete = cursor.fetchone()
            elif data.nombrePaquete:
                cursor.execute("""SELECT p.idPaquete, p.Nombre, e.Nombre AS Especialidad
                                  FROM Paquete p
                                  JOIN Especialidad e ON p.idEspecialidad = e.idEspecialidad
                                  WHERE p.Nombre = %s""", (data.nombrePaquete,))
                paquete = cursor.fetchone()
            else:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return {"message": "Debe proporcionar un idPaquete o un nombrePaquete"}

            if not paquete:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "Paquete no encontrado"}

            cursor.execute("""SELECT eq.Nombre FROM Paquete_Equipo pe
                              JOIN Equipo eq ON pe.idEquipo = eq.idEquipo
                              WHERE pe.idPaquete = %s""", (paquete[0],))
            equipos = cursor.fetchall()

            cursor.execute("""SELECT gi.Nombre, pi.cantidad FROM Paquete_Instrumento pi
                              JOIN GInstrumento gi ON pi.idInstrumento = gi.idInstrumento
                              WHERE pi.idPaquete = %s""", (paquete[0],))
            instrumentos = cursor.fetchall()

            return {
                "idPaquete": paquete[0],
                "Nombre": paquete[1],
                "Especialidad": paquete[2],
                "Equipos": [e[0] for e in equipos],
                "Instrumentos": [{"nombre": i[0], "cantidad": i[1]} for i in instrumentos]
            }

    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}

    finally:
        connection.close()

@app.get("/getPaquetePorEspecialidad")
async def obtener_paquete_por_especialidad(data: GetPaquetePorEspecialidadRequest, response: Response):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            # payload = utils.verify_token(token)
            # if payload["rol"] != "Administrador":
            #     response.status_code = status.HTTP_403_FORBIDDEN
            #     return {"message": "No tienes permiso para acceder a esta ruta"}

            # cursor.execute("SET @idUsuario = %s", (payload["idUsuario"]))

            if data.idEspecialidad:
                cursor.execute("""SELECT p.idPaquete, p.Nombre, e.Nombre AS Especialidad
                                  FROM Paquete p
                                  JOIN Especialidad e ON p.idEspecialidad = e.idEspecialidad
                                  WHERE e.idEspecialidad = %s""", (data.idEspecialidad,))
                paquetes = cursor.fetchall()
            elif data.nombreEspecialidad:
                cursor.execute("""SELECT p.idPaquete, p.Nombre, e.Nombre AS Especialidad
                                  FROM Paquete p
                                  JOIN Especialidad e ON p.idEspecialidad = e.idEspecialidad
                                  WHERE e.Nombre = %s""", (data.nombreEspecialidad,))
                paquetes = cursor.fetchall()
            else:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return {"message": "Debe proporcionar un idEspecialidad o un nombreEspecialidad"}

            if not paquetes:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "No se encontraron paquetes para esta especialidad"}

            return [{"idPaquete": p[0], "Nombre": p[1], "Especialidad": p[2]} for p in paquetes]

    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}

    finally:
        connection.close()

@app.delete("/deletePaquete")
async def eliminar_paquete(data: DeletePaqueteRequest, response: Response):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            # payload = utils.verify_token(token)
            # if payload["rol"] != "Administrador":
            #     response.status_code = status.HTTP_403_FORBIDDEN
            #     return {"message": "No tienes permiso para acceder a esta ruta"}

            # cursor.execute("SET @idUsuario = %s", (payload["idUsuario"]))

            if data.idPaquete:
                cursor.execute("SELECT idPaquete FROM Paquete WHERE idPaquete = %s", (data.idPaquete,))
                paquete_existente = cursor.fetchone()
            elif data.nombrePaquete:
                cursor.execute("SELECT idPaquete FROM Paquete WHERE Nombre = %s", (data.nombrePaquete,))
                paquete_data = cursor.fetchone()
                if paquete_data:
                    data.idPaquete = paquete_data[0]
                    paquete_existente = paquete_data
                else:
                    paquete_existente = None
            else:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return {"message": "Debe proporcionar un idPaquete o un nombrePaquete"}

            if not paquete_existente:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "Paquete no encontrado"}

            cursor.execute("DELETE FROM Paquete_Equipo WHERE idPaquete = %s", (data.idPaquete,))
            cursor.execute("DELETE FROM Paquete_Instrumento WHERE idPaquete = %s", (data.idPaquete,))
            cursor.execute("DELETE FROM Paquete WHERE idPaquete = %s", (data.idPaquete,))

            connection.commit()
            return {"message": f"Paquete {data.idPaquete} eliminado correctamente junto con sus asociaciones"}

    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}

    finally:
        connection.close()


@app.put("/updatePaqueteInstrumento")
async def actualizar_instrumentos_paquete(data: PaqueteInstrumento, response: Response):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            # payload = utils.verify_token(token)
            # if payload["rol"] != "Administrador":
            #     response.status_code = status.HTTP_403_FORBIDDEN
            #     return {"message": "No tienes permiso para acceder a esta ruta"}
            # cursor.execute("SET @idUsuario = %s", (payload["idUsuario"]))

            cursor.execute("SELECT idPaquete FROM Paquete WHERE idPaquete = %s", (data.idPaquete,))
            paquete_existente = cursor.fetchone()
            if not paquete_existente:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": f"Paquete con id {data.idPaquete} no encontrado"}

            eliminados = []  
            agregados = []  

            for instrumento in data.instrumentos:
                idInstrumento = instrumento["idInstrumento"]
                cantidad = instrumento["cantidad"]

                cursor.execute("SELECT Cantidad FROM GInstrumento WHERE idInstrumento = %s", (idInstrumento,))
                instrumento_existente = cursor.fetchone()
                if not instrumento_existente:
                    response.status_code = status.HTTP_404_NOT_FOUND
                    return {"message": f"Instrumento con id {idInstrumento} no encontrado"}

                cantidad_disponible_g = instrumento_existente[0]

                cursor.execute("SELECT SUM(cantidad) FROM Equipo_Instrumento WHERE idInstrumento = %s", (idInstrumento,))
                cantidad_en_equipos = cursor.fetchone()[0] or 0

                cantidad_total_disponible = cantidad_disponible_g - cantidad_en_equipos

                if cantidad > cantidad_total_disponible:
                    response.status_code = status.HTTP_400_BAD_REQUEST
                    return {"message": f"La cantidad requerida ({cantidad}) excede la disponibilidad ({cantidad_total_disponible})"}

                cursor.execute("SELECT cantidad FROM Paquete_Instrumento WHERE idPaquete = %s AND idInstrumento = %s",
                               (data.idPaquete, idInstrumento))
                instrumento_paquete = cursor.fetchone()

                if cantidad == 0:
                    cursor.execute("DELETE FROM Paquete_Instrumento WHERE idPaquete = %s AND idInstrumento = %s", 
                                   (data.idPaquete, idInstrumento))
                    eliminados.append(idInstrumento) 
                elif instrumento_paquete:
                    cursor.execute("""
                        UPDATE Paquete_Instrumento 
                        SET cantidad = %s 
                        WHERE idPaquete = %s AND idInstrumento = %s
                    """, (cantidad, data.idPaquete, idInstrumento))
                else:
                    cursor.execute("""
                        INSERT INTO Paquete_Instrumento (idPaquete, idInstrumento, cantidad)
                        VALUES (%s, %s, %s)
                    """, (data.idPaquete, idInstrumento, cantidad))
                    agregados.append(idInstrumento)

            connection.commit()
            
            mensajes = []
            if eliminados:
                mensajes.append(f"Instrumentos eliminados: {', '.join(map(str, eliminados))}")
            if agregados:
                mensajes.append(f"Instrumentos agregados: {', '.join(map(str, agregados))}")
            if not mensajes:
                mensajes.append("Instrumentos actualizados correctamente en el paquete")

            return {"message": " | ".join(mensajes)}

    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}

    finally:
        connection.close()

@app.post("/postPaqueteEquipo")
async def agregar_equipos_paquete(data: PaqueteEquipo, response: Response):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            # payload = utils.verify_token(token)
            # if payload["rol"] != "Administrador":
            #     response.status_code = status.HTTP_403_FORBIDDEN
            #     return {"message": "No tienes permiso para acceder a esta ruta"}
            # cursor.execute("SET @idUsuario = %s", (payload["idUsuario"]))
            cursor.execute("SELECT idPaquete FROM Paquete WHERE idPaquete = %s", (data.idPaquete,))
            paquete_existente = cursor.fetchone()
            if not paquete_existente:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "Paquete no encontrado"}

            for idEquipo in data.equipos:
                cursor.execute("SELECT idEquipo FROM Equipo WHERE idEquipo = %s", (idEquipo,))
                equipo_existente = cursor.fetchone()
                if not equipo_existente:
                    response.status_code = status.HTTP_404_NOT_FOUND
                    return {"message": f"Equipo con id {idEquipo} no encontrado"}

                cursor.execute("""
                    INSERT INTO Paquete_Equipo (idPaquete, idEquipo)
                    VALUES (%s, %s)
                """, (data.idPaquete, idEquipo))

            connection.commit()
            return {"message": "Equipos agregados correctamente al paquete"}
    
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}
    
    finally:
        connection.close()

@app.delete("/deletePaqueteEquipo")
async def eliminar_paquete_equipo(data: DeletePaqueteEquipoRequest, response: Response):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            # payload = utils.verify_token(token)
            # if payload["rol"] != "Administrador":
            #     response.status_code = status.HTTP_403_FORBIDDEN
            #     return {"message": "No tienes permiso para acceder a esta ruta"}

            # cursor.execute("SET @idUsuario = %s", (payload["idUsuario"]))

            cursor.execute("SELECT idPaquete FROM Paquete WHERE idPaquete = %s", (data.idPaquete,))
            paquete_existente = cursor.fetchone()
            if not paquete_existente:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": f"Paquete con id {data.idPaquete} no encontrado"}

            eliminados = []  

            for equipo in data.equipos:
                idEquipo = equipo.get("idEquipo")
                nombreEquipo = equipo.get("nombreEquipo")

                if idEquipo:
                    cursor.execute("SELECT idEquipo FROM Paquete_Equipo WHERE idPaquete = %s AND idEquipo = %s", 
                                   (data.idPaquete, idEquipo))
                    equipo_existente = cursor.fetchone()
                    if not equipo_existente:
                        response.status_code = status.HTTP_404_NOT_FOUND
                        return {"message": f"Equipo con id {idEquipo} no está en el paquete {data.idPaquete}"}

                    cursor.execute("DELETE FROM Paquete_Equipo WHERE idPaquete = %s AND idEquipo = %s", (data.idPaquete, idEquipo))
                    eliminados.append(f"ID {idEquipo}")

                elif nombreEquipo:
                    cursor.execute("SELECT idEquipo FROM Equipo WHERE Nombre = %s", (nombreEquipo,))
                    equipo_data = cursor.fetchone()
                    if not equipo_data:
                        response.status_code = status.HTTP_404_NOT_FOUND
                        return {"message": f"Equipo con nombre '{nombreEquipo}' no encontrado"}

                    idEquipo = equipo_data[0]
                    cursor.execute("SELECT idEquipo FROM Paquete_Equipo WHERE idPaquete = %s AND idEquipo = %s", 
                                   (data.idPaquete, idEquipo))
                    equipo_existente = cursor.fetchone()
                    if not equipo_existente:
                        response.status_code = status.HTTP_404_NOT_FOUND
                        return {"message": f"Equipo con nombre '{nombreEquipo}' no está en el paquete {data.idPaquete}"}

                    cursor.execute("DELETE FROM Paquete_Equipo WHERE idPaquete = %s AND idEquipo = %s", (data.idPaquete, idEquipo))
                    eliminados.append(f"Nombre '{nombreEquipo}'")

            connection.commit()
            return {"message": f"Equipos eliminados correctamente del paquete {data.idPaquete}: {', '.join(eliminados)}"}

    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}

    finally:
        connection.close()

@app.post("/postPedido")
async def crear_pedido(pedido: Pedido, response: Response):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            # payload = utils.verify_token(token)
            # if payload["rol"] != "Administrador":
            #     response.status_code = status.HTTP_403_FORBIDDEN
            #     return {"message": "No tienes permiso para acceder a esta ruta"}

            # cursor.execute("SET @idUsuario = %s", (payload["idUsuario"]))

            if pedido.idPaquete:
                cursor.execute("SELECT idPaquete FROM Paquete WHERE idPaquete = %s", (pedido.idPaquete,))
                paquete_existente = cursor.fetchone()
                if not paquete_existente:
                    response.status_code = status.HTTP_404_NOT_FOUND
                    return {"message": "Paquete no encontrado"}

            idEnfermero = pedido.idEnfermero
            if not idEnfermero and pedido.nombreEnfermero:
                cursor.execute("""
                    SELECT idUsuario FROM Usuario 
                    WHERE CONCAT(Nombres, ' ', ApellidoPaterno, ' ', ApellidoMaterno) = %s
                """, (pedido.nombreEnfermero,))
                enfermero_data = cursor.fetchone()
                if not enfermero_data:
                    response.status_code = status.HTTP_404_NOT_FOUND
                    return {"message": f"Enfermero con nombre completo '{pedido.nombreEnfermero}' no encontrado"}
                idEnfermero = enfermero_data[0]  # Asignar el id encontrado

            if not idEnfermero:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return {"message": "Debe proporcionar un idEnfermero o un nombreEnfermero"}

            cursor.execute("""
                INSERT INTO Pedido (Fecha, Hora, Estado, idPaquete, idEnfermero, Cirugia, Ubicacion)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (pedido.Fecha, pedido.Hora, pedido.Estado, pedido.idPaquete, idEnfermero, pedido.Cirugia, pedido.Ubicacion))

            connection.commit()
            return {"message": "Pedido registrado correctamente"}

    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}

    finally:
        connection.close()

@app.put("/updatePedido")
async def actualizar_pedido(pedido: UpdatePedidoRequest, response: Response):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            # payload = utils.verify_token(token)
            # if payload["rol"] != "Administrador":
            #     response.status_code = status.HTTP_403_FORBIDDEN
            #     return {"message": "No tienes permiso para acceder a esta ruta"}

            # cursor.execute("SET @idUsuario = %s", (payload["idUsuario"]))

            cursor.execute("SELECT idPedido FROM Pedido WHERE idPedido = %s", (pedido.idPedido,))
            pedido_existente = cursor.fetchone()
            if not pedido_existente:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "Pedido no encontrado"}

            if pedido.idPaquete:
                cursor.execute("SELECT idPaquete FROM Paquete WHERE idPaquete = %s", (pedido.idPaquete,))
                paquete_existente = cursor.fetchone()
                if not paquete_existente:
                    response.status_code = status.HTTP_404_NOT_FOUND
                    return {"message": "Paquete no encontrado"}

            idEnfermero = pedido.idEnfermero
            if not idEnfermero and pedido.nombreEnfermero:
                cursor.execute("""
                    SELECT idUsuario FROM Usuario 
                    WHERE CONCAT(Nombre, ' ', ApellidoPaterno, ' ', ApellidoMaterno) = %s
                """, (pedido.nombreEnfermero,))
                enfermero_data = cursor.fetchone()
                if not enfermero_data:
                    response.status_code = status.HTTP_404_NOT_FOUND
                    return {"message": f"Enfermero con nombre completo '{pedido.nombreEnfermero}' no encontrado"}
                idEnfermero = enfermero_data[0]  

            campos_a_actualizar = []
            valores = []

            if pedido.Fecha:
                campos_a_actualizar.append("Fecha = %s")
                valores.append(pedido.Fecha)
            if pedido.Hora:
                campos_a_actualizar.append("Hora = %s")
                valores.append(pedido.Hora)
            if pedido.Estado:
                campos_a_actualizar.append("Estado = %s")
                valores.append(pedido.Estado)
            if pedido.idPaquete:
                campos_a_actualizar.append("idPaquete = %s")
                valores.append(pedido.idPaquete)
            if idEnfermero:
                campos_a_actualizar.append("idEnfermero = %s")
                valores.append(idEnfermero)
            if pedido.Cirugia:
                campos_a_actualizar.append("Cirugia = %s")
                valores.append(pedido.Cirugia)
            if pedido.Ubicacion:
                campos_a_actualizar.append("Ubicacion = %s")
                valores.append(pedido.Ubicacion)

            if campos_a_actualizar:
                consulta_update = f"UPDATE Pedido SET {', '.join(campos_a_actualizar)} WHERE idPedido = %s"
                valores.append(pedido.idPedido)
                cursor.execute(consulta_update, tuple(valores))
                connection.commit()

            return {"message": "Pedido actualizado correctamente"}

    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}

    finally:
        connection.close()


@app.delete("/deletePedido")
async def eliminar_pedido(data: DeletePedidoRequest, response: Response):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            # payload = utils.verify_token(token)
            # if payload["rol"] != "Administrador":
            #     response.status_code = status.HTTP_403_FORBIDDEN
            #     return {"message": "No tienes permiso para acceder a esta ruta"}

            # cursor.execute("SET @idUsuario = %s", (payload["idUsuario"]))

            cursor.execute("SELECT idPedido FROM Pedido WHERE idPedido = %s", (data.idPedido,))
            pedido_existente = cursor.fetchone()
            if not pedido_existente:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "Pedido no encontrado"}

            cursor.execute("DELETE FROM Pedido_Equipo WHERE idPedido = %s", (data.idPedido,))
            cursor.execute("DELETE FROM Pedido_GInstrumento WHERE idPedido = %s", (data.idPedido,))
            cursor.execute("DELETE FROM Pedido WHERE idPedido = %s", (data.idPedido,))

            connection.commit()
            return {"message": f"Pedido {data.idPedido} y sus asociaciones eliminados correctamente"}

    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}

    finally:
        connection.close()

@app.get("/getPedidos")
async def obtener_todos_los_pedidos(response: Response):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            # payload = utils.verify_token(token)
            # if payload["rol"] != "Administrador":
            #     response.status_code = status.HTTP_403_FORBIDDEN
            #     return {"message": "No tienes permiso para acceder a esta ruta"}

            # cursor.execute("SET @idUsuario = %s", (payload["idUsuario"]))

            cursor.execute("""
                SELECT idPedido, Fecha, TIME_FORMAT(Hora, '%H:%i:%s'), Estado, idPaquete, idEnfermero, Cirugia, Ubicacion
                FROM Pedido
            """)
            pedidos = cursor.fetchall()

            return [
                {
                    "idPedido": p[0],
                    "Fecha": p[1],
                    "Hora": p[2] if p[2] else "00:00:00",  
                    "Estado": p[3],
                    "idPaquete": p[4],
                    "idEnfermero": p[5],
                    "Cirugia": p[6],
                    "Ubicacion": p[7]
                } for p in pedidos
            ]

    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}

    finally:
        connection.close()


@app.get("/getPedido")
async def obtener_pedido(data: GetPedidoRequest, response: Response):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            # payload = utils.verify_token(token)
            # if payload["rol"] != "Administrador":
            #     response.status_code = status.HTTP_403_FORBIDDEN
            #     return {"message": "No tienes permiso para acceder a esta ruta"}

            # cursor.execute("SET @idUsuario = %s", (payload["idUsuario"]))

            cursor.execute("""
                SELECT p.idPedido, p.Fecha, 
                SEC_TO_TIME(CAST(p.Hora AS UNSIGNED)) AS Hora,
                p.Estado, pa.Nombre AS Paquete, p.idEnfermero, p.Cirugia, p.Ubicacion
                FROM Pedido p
                LEFT JOIN Paquete pa ON p.idPaquete = pa.idPaquete
                WHERE p.idPedido = %s
            """, (data.idPedido,))
            pedido = cursor.fetchone()

            if not pedido:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "Pedido no encontrado"}

            cursor.execute("""
                SELECT e.idEquipo, e.Nombre 
                FROM Pedido_Equipo pe
                JOIN Equipo e ON pe.idEquipo = e.idEquipo
                WHERE pe.idPedido = %s
            """, (data.idPedido,))
            equipos = [{"idEquipo": equipo[0], "nombreEquipo": equipo[1]} for equipo in cursor.fetchall()]

            cursor.execute("""
                SELECT gi.idInstrumento, gi.Nombre, pi.cantidad
                FROM Pedido_GInstrumento pi
                JOIN GInstrumento gi ON pi.idInstrumento = gi.idInstrumento
                WHERE pi.idPedido = %s
            """, (data.idPedido,))
            instrumentos = [{"idInstrumento": instrumento[0], "nombreInstrumento": instrumento[1], "cantidad": instrumento[2]} for instrumento in cursor.fetchall()]

            return {
                "idPedido": pedido[0],
                "Fecha": pedido[1],
                "Hora": pedido[2] if pedido[2] else "00:00:00", 
                "Estado": pedido[3],
                "Paquete": pedido[4],
                "idEnfermero": pedido[5],
                "Cirugia": pedido[6],
                "Ubicacion": pedido[7],
                "Equipos": equipos, 
                "Instrumentos": instrumentos  
            }

    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}

    finally:
        connection.close()

@app.post("/postPedidoInstrumento")
async def agregar_instrumentos_pedido(data: PedidoInstrumento, response: Response):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            # payload = utils.verify_token(token)
            # if payload["rol"] != "Administrador":
            #     response.status_code = status.HTTP_403_FORBIDDEN
            #     return {"message": "No tienes permiso para acceder a esta ruta"}

            # cursor.execute("SET @idUsuario = %s", (payload["idUsuario"]))

            cursor.execute("SELECT idPedido FROM Pedido WHERE idPedido = %s", (data.idPedido,))
            pedido_existente = cursor.fetchone()
            if not pedido_existente:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": f"Pedido con id {data.idPedido} no encontrado"}

            for instrumento in data.instrumentos:
                idInstrumento = instrumento.idInstrumento
                nombreInstrumento = instrumento.nombreInstrumento
                cantidad = instrumento.cantidad

                if not idInstrumento and nombreInstrumento:
                    cursor.execute("SELECT idInstrumento FROM GInstrumento WHERE Nombre = %s", (nombreInstrumento,))
                    instrumento_data = cursor.fetchone()
                    if not instrumento_data:
                        response.status_code = status.HTTP_404_NOT_FOUND
                        return {"message": f"Instrumento con nombre '{nombreInstrumento}' no encontrado"}
                    idInstrumento = instrumento_data[0]  

                cursor.execute("SELECT Cantidad FROM GInstrumento WHERE idInstrumento = %s", (idInstrumento,))
                instrumento_existente = cursor.fetchone()
                if not instrumento_existente:
                    response.status_code = status.HTTP_404_NOT_FOUND
                    return {"message": f"Instrumento con id {idInstrumento} no encontrado"}

                cantidad_disponible = instrumento_existente[0]

                cursor.execute("""
                    SELECT COALESCE(SUM(cantidad), 0) FROM Paquete_Instrumento WHERE idInstrumento = %s
                """, (idInstrumento,))
                cantidad_en_paquetes = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT COALESCE(SUM(cantidad), 0) FROM Equipo_Instrumento WHERE idInstrumento = %s
                """, (idInstrumento,))
                cantidad_en_equipos = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT COALESCE(SUM(cantidad), 0) FROM Pedido_GInstrumento WHERE idInstrumento = %s
                """, (idInstrumento,))
                cantidad_en_pedidos = cursor.fetchone()[0]

                cantidad_total_usada = cantidad_en_equipos + cantidad_en_paquetes + cantidad_en_pedidos

                if cantidad_total_usada + cantidad > cantidad_disponible:
                    response.status_code = status.HTTP_400_BAD_REQUEST
                    return {"message": f"La cantidad requerida ({cantidad}) excede la disponibilidad ({cantidad_disponible - cantidad_total_usada}) en el almacén"}

                cursor.execute("""
                    INSERT INTO Pedido_GInstrumento (idPedido, idInstrumento, cantidad)
                    VALUES (%s, %s, %s)
                """, (data.idPedido, idInstrumento, cantidad))

            connection.commit()
            return {"message": "Instrumentos agregados correctamente al pedido"}

    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}

    finally:
        connection.close()


@app.put("/updatePedidoInstrumento")
async def actualizar_instrumentos_pedido(data: PedidoInstrumento, response: Response):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            # payload = utils.verify_token(token)
            # if payload["rol"] != "Administrador":
            #     response.status_code = status.HTTP_403_FORBIDDEN
            #     return {"message": "No tienes permiso para acceder a esta ruta"}

            # cursor.execute("SET @idUsuario = %s", (payload["idUsuario"]))

            cursor.execute("SELECT idPedido FROM Pedido WHERE idPedido = %s", (data.idPedido,))
            pedido_existente = cursor.fetchone()
            if not pedido_existente:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": f"Pedido con id {data.idPedido} no encontrado"}

            eliminados = []

            for instrumento in data.instrumentos:
                idInstrumento = instrumento.idInstrumento  
                nombreInstrumento = instrumento.nombreInstrumento  
                cantidad = instrumento.cantidad  

                if not idInstrumento and nombreInstrumento:
                    cursor.execute("SELECT idInstrumento FROM GInstrumento WHERE Nombre = %s", (nombreInstrumento,))
                    instrumento_data = cursor.fetchone()
                    if not instrumento_data:
                        response.status_code = status.HTTP_404_NOT_FOUND
                        return {"message": f"Instrumento con nombre '{nombreInstrumento}' no encontrado"}
                    idInstrumento = instrumento_data[0]

                cursor.execute("SELECT Nombre, Cantidad FROM GInstrumento WHERE idInstrumento = %s", (idInstrumento,))
                instrumento_existente = cursor.fetchone()
                if not instrumento_existente:
                    response.status_code = status.HTTP_404_NOT_FOUND
                    return {"message": f"Instrumento con id {idInstrumento} no encontrado"}

                nombreInstrumento = instrumento_existente[0] 
                cantidad_disponible = instrumento_existente[1]

                cursor.execute("SELECT COALESCE(SUM(cantidad), 0) FROM Paquete_Instrumento WHERE idInstrumento = %s", (idInstrumento,))
                cantidad_en_paquetes = cursor.fetchone()[0]

                cursor.execute("SELECT COALESCE(SUM(cantidad), 0) FROM Equipo_Instrumento WHERE idInstrumento = %s", (idInstrumento,))
                cantidad_en_equipos = cursor.fetchone()[0]

                cursor.execute("SELECT COALESCE(SUM(cantidad), 0) FROM Pedido_GInstrumento WHERE idInstrumento = %s", (idInstrumento,))
                cantidad_en_pedidos = cursor.fetchone()[0]

                cantidad_total_usada = cantidad_en_equipos + cantidad_en_paquetes + cantidad_en_pedidos

                if cantidad_total_usada + cantidad > cantidad_disponible:
                    response.status_code = status.HTTP_400_BAD_REQUEST
                    return {"message": f"La cantidad requerida ({cantidad}) excede la disponibilidad ({cantidad_disponible - cantidad_total_usada}) en el almacén"}

                cursor.execute("SELECT cantidad FROM Pedido_GInstrumento WHERE idPedido = %s AND idInstrumento = %s", (data.idPedido, idInstrumento))
                instrumento_pedido = cursor.fetchone()

                if cantidad == 0:
                    cursor.execute("DELETE FROM Pedido_GInstrumento WHERE idPedido = %s AND idInstrumento = %s", (data.idPedido, idInstrumento))
                    eliminados.append(nombreInstrumento)  
                elif instrumento_pedido:
                    cursor.execute("""
                        UPDATE Pedido_GInstrumento 
                        SET cantidad = %s 
                        WHERE idPedido = %s AND idInstrumento = %s
                    """, (cantidad, data.idPedido, idInstrumento))
                else:
                    cursor.execute("""
                        INSERT INTO Pedido_GInstrumento (idPedido, idInstrumento, cantidad)
                        VALUES (%s, %s, %s)
                    """, (data.idPedido, idInstrumento, cantidad))

            connection.commit()
            
            if eliminados:
                return {"message": f"Instrumentos eliminados: {', '.join(eliminados)}"}  # ✅ Muestra nombres eliminados
            
            return {"message": "Instrumentos actualizados correctamente en el pedido"}

    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}

    finally:
        connection.close()

@app.put("/updatePedidoEquipo")
async def actualizar_equipos_pedido(data: PedidoEquipo, response: Response):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            # payload = utils.verify_token(token)
            # if payload["rol"] != "Administrador":
            #     response.status_code = status.HTTP_403_FORBIDDEN
            #     return {"message": "No tienes permiso para acceder a esta ruta"}

            # cursor.execute("SET @idUsuario = %s", (payload["idUsuario"]))

            cursor.execute("SELECT idPedido FROM Pedido WHERE idPedido = %s", (data.idPedido,))
            pedido_existente = cursor.fetchone()
            if not pedido_existente:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": f"Pedido con id {data.idPedido} no encontrado"}

            cursor.execute("SELECT idEquipo FROM Pedido_Equipo WHERE idPedido = %s", (data.idPedido,))
            equipos_actuales = {row[0] for row in cursor.fetchall()}

            equipos_a_eliminar = equipos_actuales - {eq.idEquipo for eq in data.equipos if eq.idEquipo}
            for idEquipo in equipos_a_eliminar:
                cursor.execute("DELETE FROM Pedido_Equipo WHERE idPedido = %s AND idEquipo = %s", (data.idPedido, idEquipo))

            for equipo in data.equipos:
                idEquipo = equipo.idEquipo
                nombreEquipo = equipo.nombreEquipo

                if not idEquipo and nombreEquipo:
                    cursor.execute("SELECT idEquipo FROM Equipo WHERE Nombre = %s", (nombreEquipo,))
                    equipo_data = cursor.fetchone()
                    if not equipo_data:
                        response.status_code = status.HTTP_404_NOT_FOUND
                        return {"message": f"Equipo con nombre '{nombreEquipo}' no encontrado"}
                    idEquipo = equipo_data[0]

                if idEquipo not in equipos_actuales:
                    cursor.execute("SELECT idEquipo FROM Equipo WHERE idEquipo = %s", (idEquipo,))
                    equipo_existente = cursor.fetchone()
                    if not equipo_existente:
                        response.status_code = status.HTTP_404_NOT_FOUND
                        return {"message": f"Equipo con id {idEquipo} no encontrado"}

                    cursor.execute("INSERT INTO Pedido_Equipo (idPedido, idEquipo) VALUES (%s, %s)", (data.idPedido, idEquipo))

            connection.commit()
            return {"message": "Equipos actualizados y agregados correctamente en el pedido"}

    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}

    finally:
        connection.close()

@app.delete("/deletePedidoEquipo")
async def eliminar_equipos_pedido(data: DeletePedidoEquipoRequest, response: Response):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            # payload = utils.verify_token(token)
            # if payload["rol"] != "Administrador":
            #     response.status_code = status.HTTP_403_FORBIDDEN
            #     return {"message": "No tienes permiso para acceder a esta ruta"}

            # cursor.execute("SET @idUsuario = %s", (payload["idUsuario"]))

            cursor.execute("SELECT idPedido FROM Pedido WHERE idPedido = %s", (data.idPedido,))
            pedido_existente = cursor.fetchone()
            if not pedido_existente:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": f"Pedido con id {data.idPedido} no encontrado"}

            eliminados = []

            for equipo in data.equipos:
                idEquipo = equipo.idEquipo
                nombreEquipo = equipo.nombreEquipo

                if not idEquipo and nombreEquipo:
                    cursor.execute("SELECT idEquipo FROM Equipo WHERE Nombre = %s", (nombreEquipo,))
                    equipo_data = cursor.fetchone()
                    if not equipo_data:
                        response.status_code = status.HTTP_404_NOT_FOUND
                        return {"message": f"Equipo con nombre '{nombreEquipo}' no encontrado"}
                    idEquipo = equipo_data[0]

                cursor.execute("SELECT Nombre FROM Equipo WHERE idEquipo = %s", (idEquipo,))
                equipo_nombre_data = cursor.fetchone()
                if not equipo_nombre_data:
                    response.status_code = status.HTTP_404_NOT_FOUND
                    return {"message": f"Equipo con id {idEquipo} no encontrado"}
                nombreEquipo = equipo_nombre_data[0]  

                cursor.execute("SELECT idEquipo FROM Pedido_Equipo WHERE idPedido = %s AND idEquipo = %s", (data.idPedido, idEquipo))
                equipo_existente = cursor.fetchone()
                if not equipo_existente:
                    response.status_code = status.HTTP_404_NOT_FOUND
                    return {"message": f"Equipo con id {idEquipo} no está en el pedido {data.idPedido}"}

                cursor.execute("DELETE FROM Pedido_Equipo WHERE idPedido = %s AND idEquipo = %s", (data.idPedido, idEquipo))
                eliminados.append(nombreEquipo if nombreEquipo else f"Equipo ID {idEquipo}")  

            connection.commit()
            return {"message": f"Equipos eliminados correctamente del pedido: {', '.join(eliminados)}"}

    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}

    finally:
        connection.close()

