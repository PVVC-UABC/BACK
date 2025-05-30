import os
import io
import pymysql
import utils
from jinja2 import Environment, FileSystemLoader
from fastapi import FastAPI, Response, status, HTTPException, Depends, Request
from fastapi.responses import JSONResponse, StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from hashlib import sha256
from pydantic import BaseModel
from datetime import datetime, timedelta, date, time, timedelta, timezone
from typing import Optional, Union, List, Dict
from starlette.responses import StreamingResponse




oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



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
    Contrasena: Union[str,None] = None
    Alias: Optional[str] = None 

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
    idInstrumento: Optional[int] = None
    nombreInstrumento: Optional[str] = None
    nuevaCantidad: int

class GetInstrumentosPorGrupoRequest(BaseModel):
    idInstrumentoGrupo: Union[int, None] = None
    nombreInstrumentoGrupo: Union[str, None] = None

class UpdateIInstrumentoRequest(BaseModel):
    idInstrumentoIndividual: int
    nuevoEstado: Union[str, None] = None
    nuevaUbicacion: Union[str, None] = None
    nuevaEsterilizacion: Union[datetime, None] = None
    idEquipo: Optional[int] = None 
    idPaquete: Optional[int] = None  


class DeleteGInstrumentoRequest(BaseModel):
    idInstrumento: Union[int, None] = None
    nombreInstrumento: Union[str, None] = None

class NewEquipo(BaseModel):
    Nombre: str

class UpdatePaqueteRequest(BaseModel):
    idPaquete: Union[int,None] = None  
    nombrePaquete: Union[str,None] = None  
    idEspecialidad: Union[int,None] = None  

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

class GetPaquetePorEspecialidadRequest(BaseModel):
    idEspecialidad: Union[int, None] = None
    nombreEspecialidad: Union[str, None] = None

class Especialidad(BaseModel):
    idEspecialidad: Union[int, None] = None
    Nombre: str

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
    idInstrumento: Optional[int] = None
    nombreInstrumento: Optional[str] = None

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

class UpdatePaqueteRequest(BaseModel):
    idPaquete: Union[int,None] = None  # Clave primaria
    nombrePaquete: Union[str,None] = None  # Nombre del paquete
    idEspecialidad: Union[int,None] = None  # Clave foránea a Especialidad

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

def obtener_datos_historial_paquetes():
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT hp.idHistorialPaquete, hp.idPaquete, hp.tipoOperacion, 
                       hp.observaciones, hp.fechaCambio, 
                       COALESCE(CONCAT(u.Nombres, ' ', u.ApellidoPaterno, ' ', COALESCE(u.ApellidoMaterno, '')), 'Usuario desconocido') AS usuario,
                       hp.nombrePaquetePrevio, p.Nombre AS nombrePaqueteActual,
                       hp.idEquipo, hp.idInstrumento
                FROM Historial_Paquetes hp
                LEFT JOIN Paquete p ON hp.idPaquete = p.idPaquete
                LEFT JOIN Usuario u ON hp.idUsuario = u.idUsuario
                ORDER BY hp.idHistorialPaquete ASC;
            """)
            historial_paquetes = cursor.fetchall()

            cursor.execute("""
                SELECT e.idEquipo, e.Nombre AS nombreEquipo
                FROM Equipo e;
            """)
            equipos_por_id = {row[0]: row[1] for row in cursor.fetchall()}

            cursor.execute("""
                SELECT he.idEquipo, he.nombreEquipoPrevio
                FROM Historial_Equipos he;
            """)
            historial_equipos_por_id = {row[0]: row[1] for row in cursor.fetchall()}

            cursor.execute("""
                SELECT gi.idInstrumento, gi.Nombre AS nombreInstrumento
                FROM GInstrumento gi;
            """)
            instrumentos_por_id = {row[0]: row[1] for row in cursor.fetchall()}

            cursor.execute("""
                SELECT hgi.idInstrumento, hgi.nombreInstrumentoPrevio
                FROM Historial_GInstrumento hgi;
            """)
            historial_instrumentos_por_id = {row[0]: row[1] for row in cursor.fetchall()}

            historial_completo = []
            paquetes_por_historial = {}

            for paquete in historial_paquetes:
                id_paquete = paquete[1]
                id_equipo = paquete[8]
                id_instrumento = paquete[9]

                nombrePaquete = paquete[6] if paquete[2] == "Eliminado" and paquete[6] else paquete[7]
                nombreEquipo = equipos_por_id.get(id_equipo, historial_equipos_por_id.get(id_equipo, "Sin equipo asociado"))
                nombreInstrumento = instrumentos_por_id.get(id_instrumento, historial_instrumentos_por_id.get(id_instrumento, "Sin instrumento asociado"))

                paquete_data = {
                    "idHistorialPaquete": paquete[0],
                    "idPaquete": id_paquete if id_paquete else "Sin ID",
                    "nombrePaquete": nombrePaquete,
                    "nombreEquipo": nombreEquipo, 
                    "nombreInstrumento": nombreInstrumento, 
                    "observaciones": paquete[3],
                    "fechaCambio": paquete[4],
                    "usuario": paquete[5]
                }

                historial_completo.append(paquete_data)
                paquetes_por_historial[paquete_data["idHistorialPaquete"]] = paquete_data

        return {
            "historial_paquetes": historial_completo,
            "paquetes_por_historial": paquetes_por_historial,
            "fecha_reporte": datetime.now().strftime("%d/%m/%Y %H:%M"),
        }
    except pymysql.Error as e:
        print(f"Error MySQL: {e}")
        return None
    finally:
        connection.close()


def generar_pdf_historial_paquetes():
    """Genera un PDF con el historial de paquetes usando Jinja2."""
    
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    template = env.get_template("historial_paquetes.html")

    datos = obtener_datos_historial_paquetes()
    if not datos:
        raise HTTPException(status_code=500, detail="No se obtuvieron datos de la base de datos")

    html_renderizado = template.render(datos)

    # Convertir el HTML renderizado en un objeto PDF en memoria
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
                SELECT he.idHistorialEquipo, 
                       he.idEquipo,  
                       COALESCE(e.Nombre, he.nombreEquipoPrevio) AS nombreEquipo,  
                       COALESCE(gi.Nombre, (
                           SELECT hg.nombreInstrumentoPrevio  
                           FROM Historial_GInstrumento hg  
                           WHERE hg.idInstrumento = he.idInstrumento  
                           AND hg.nombreInstrumentoPrevio IS NOT NULL  
                           ORDER BY hg.fechaCambio DESC LIMIT 1
                       ), (
                           SELECT hi.nombreHerramientaPrevio  
                           FROM Historial_IInstrumento hi  
                           WHERE hi.idInstrumentoIndividual = he.idInstrumento  
                           AND hi.nombreHerramientaPrevio IS NOT NULL  
                           ORDER BY hi.fechaCambio DESC LIMIT 1
                       )) AS nombreInstrumento,  
                       he.observaciones, he.fechaCambio,  
                       COALESCE(CONCAT(u.Nombres, ' ', u.ApellidoPaterno, ' ', COALESCE(u.ApellidoMaterno, '')), 'Usuario desconocido') AS usuario
                FROM Historial_Equipos he
                LEFT JOIN Equipo e ON he.idEquipo = e.idEquipo
                LEFT JOIN GInstrumento gi ON he.idInstrumento = gi.idInstrumento
                LEFT JOIN Usuario u ON he.idUsuario = u.idUsuario
                ORDER BY he.idHistorialEquipo ASC;
            """)
            historial_equipos = cursor.fetchall()

        historial_equipos = [list(registro) for registro in historial_equipos]

        nombre_por_id = {}  # Diccionario para rastrear nombres por ID
        for registro in historial_equipos:
            id_equipo = registro[1]
            nombre_equipo = registro[2]

            # Si ya hay un nombre registrado para este ID, úsalo en todos los registros con el mismo idEquipo
            if id_equipo in nombre_por_id and (nombre_equipo is None or nombre_equipo == ''):
                registro[2] = nombre_por_id[id_equipo]  # Asignar el nombre correcto
            elif nombre_equipo:  
                nombre_por_id[id_equipo] = nombre_equipo  # Guardar el nombre más reciente

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
            cursor.execute("""
                SELECT hg.idHistorial, 
                       hg.idInstrumento,  
                       COALESCE(gi.Nombre, hg.nombreInstrumentoPrevio) AS nombreInstrumento,  -- 🚀 Toma el nombre actual si aún existe, si no usa el previo
                       hg.observaciones, hg.fechaCambio,  
                       COALESCE(CONCAT(u.Nombres, ' ', u.ApellidoPaterno, ' ', COALESCE(u.ApellidoMaterno, '')), 'Usuario desconocido') AS usuario
                FROM Historial_GInstrumento hg
                LEFT JOIN GInstrumento gi ON hg.idInstrumento = gi.idInstrumento  -- 🚀 Se une con GInstrumento para obtener el nombre actual
                LEFT JOIN Usuario u ON hg.idUsuario = u.idUsuario
                ORDER BY hg.idHistorial ASC;
            """)
            historial_ginstrumento = cursor.fetchall()

        historial_ginstrumento = [list(registro) for registro in historial_ginstrumento]

        nombre_por_id = {}  # Diccionario para rastrear nombres
        for registro in historial_ginstrumento:
            id_instrumento = registro[1]
            nombre = registro[2]

            # Si ya hay un nombre registrado para este ID, úsalo en todos los registros con el mismo idInstrumento
            if id_instrumento in nombre_por_id and (nombre is None or nombre == ''):
                registro[2] = nombre_por_id[id_instrumento]  # Asignar el nombre correcto
            elif nombre:  
                nombre_por_id[id_instrumento] = nombre  # Guardar el nombre más reciente

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
                SELECT hi.idHistorialIndividual, 
                       hi.idInstrumentoIndividual,  
                       hi.nombreHerramientaPrevio,  
                       hi.observaciones, 
                       hi.fechaCambio,  
                       COALESCE(u.Nombres, 'Usuario desconocido') AS usuario
                FROM Historial_IInstrumento hi
                LEFT JOIN Usuario u ON hi.idUsuario = u.idUsuario
                ORDER BY hi.idHistorialIndividual ASC;
            """)
            historial_iinstrumento = cursor.fetchall()

        historial_iinstrumento = [list(registro) for registro in historial_iinstrumento]

        nombre_por_id = {}  # Diccionario para rastrear nombres
        for registro in historial_iinstrumento:
            id_instrumento = registro[1]
            nombre = registro[2]

            # Si ya hay un nombre registrado para este ID, úsalo
            if id_instrumento in nombre_por_id and (nombre is None or nombre == ''):
                registro[2] = nombre_por_id[id_instrumento]
            elif nombre:  
                nombre_por_id[id_instrumento] = nombre  # Guardamos el nombre más reciente

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

def obtener_datos_instrumento():
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT ii.idInstrumentoIndividual, 
                       gi.Nombre AS nombreHerramienta, 
                       gi.CodigoDeBarras, 
                       ii.Estado, ii.Ubicacion, 
                       ii.ultimaEsterilizacion,
                       gi.idInstrumento,
                       (SELECT COUNT(*) FROM IInstrumento WHERE idInstrumentoGrupo = gi.idInstrumento) AS cantidad_total
                FROM IInstrumento ii
                LEFT JOIN GInstrumento gi ON ii.idInstrumentoGrupo = gi.idInstrumento
                ORDER BY gi.idInstrumento, ii.idInstrumentoIndividual ASC;
            """)
            instrumento = cursor.fetchall()

        # Agrupar por idInstrumentoGrupo para mostrar la cantidad total solo al final
        instrumentos_por_grupo = {}
        for item in instrumento:
            id_grupo = item[6]
            if id_grupo not in instrumentos_por_grupo:
                instrumentos_por_grupo[id_grupo] = {"datos": [], "cantidad_total": item[7]}
            instrumentos_por_grupo[id_grupo]["datos"].append(item[:6])

        return {
            "instrumentos_por_grupo": instrumentos_por_grupo,
            "fecha_reporte": datetime.now().strftime("%d/%m/%Y %H:%M"),
        }
    except pymysql.Error as e:
        print(f"Error MySQL: {e}")
        return None
    finally:
        connection.close()

def generar_pdf_instrumento():
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("instrumento.html")

    datos = obtener_datos_instrumento()
    if not datos:
        raise HTTPException(status_code=500, detail="No se obtuvieron datos de la base de datos")

    html_renderizado = template.render(datos)

    return io.BytesIO(html_renderizado.encode("utf-8"))

def obtener_datos_paquete():
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            # 🚀 Obtener los paquetes y sus equipos desde `Paquete_Equipo`
            cursor.execute("""
                SELECT p.idPaquete, p.Nombre AS nombrePaquete, p.idEspecialidad,
                       e.idEquipo, e.Nombre AS nombreEquipo,
                       gi.idInstrumento, gi.Nombre AS nombreInstrumento,
                       gi.CodigoDeBarras, COALESCE(ei.cantidad, 0) AS cantidadInstrumento
                FROM Paquete p
                LEFT JOIN Paquete_Equipo pe ON p.idPaquete = pe.idPaquete
                LEFT JOIN Equipo e ON pe.idEquipo = e.idEquipo
                LEFT JOIN Equipo_Instrumento ei ON e.idEquipo = ei.idEquipo
                LEFT JOIN GInstrumento gi ON ei.idInstrumento = gi.idInstrumento
                ORDER BY p.idPaquete, e.idEquipo, gi.idInstrumento ASC;
            """)
            paquete_datos = cursor.fetchall()

            cursor.execute("""
                SELECT p.idPaquete, gi.idInstrumento, gi.Nombre, gi.CodigoDeBarras, COALESCE(pi.cantidad, 0)
                FROM Paquete p
                LEFT JOIN Paquete_Instrumento pi ON p.idPaquete = pi.idPaquete
                LEFT JOIN GInstrumento gi ON pi.idInstrumento = gi.idInstrumento
                ORDER BY p.idPaquete, gi.idInstrumento ASC;
            """)
            paquete_instrumentos = cursor.fetchall()

        paquetes_por_grupo = {}
        for item in paquete_datos:
            id_paquete = item[0]
            if id_paquete not in paquetes_por_grupo:
                paquetes_por_grupo[id_paquete] = {
                    "nombrePaquete": item[1],
                    "idEspecialidad": item[2],
                    "datos": [],
                    "instrumentos_paquete": [],
                    "cantidad_total_instrumentos": 0,
                    "cantidad_total_instrumentos_paquete": 0
                }

            paquete_info = [
                item[3],  # ID Equipo
                item[4],  # Nombre Equipo
                item[5],  # ID Instrumento
                item[6],  # Nombre Instrumento
                item[7],  # Código de Barras
                item[8]   # Cantidad Instrumento
            ]

            paquetes_por_grupo[id_paquete]["datos"].append(paquete_info)
            paquetes_por_grupo[id_paquete]["cantidad_total_instrumentos"] += item[8]

        for item in paquete_instrumentos:
            id_paquete = item[0]
            if id_paquete in paquetes_por_grupo:
                instrumento_info = [
                    item[1],  # ID Instrumento
                    item[2],  # Nombre Instrumento
                    item[3],  # Código de Barras
                    item[4]   # Cantidad Instrumento
                ]
                paquetes_por_grupo[id_paquete]["instrumentos_paquete"].append(instrumento_info)
                paquetes_por_grupo[id_paquete]["cantidad_total_instrumentos_paquete"] += item[4]

        return {
            "paquetes_por_grupo": paquetes_por_grupo,
            "fecha_reporte": datetime.now().strftime("%d/%m/%Y %H:%M"),
        }

    except pymysql.Error as e:
        print(f"Error MySQL: {e}")
        return None
    finally:
        connection.close()

def generar_pdf_paquete():
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("paquete_instrumentos.html")

    datos = obtener_datos_paquete()
    if not datos:
        raise HTTPException(status_code=500, detail="No se obtuvieron datos de la base de datos")

    html_renderizado = template.render(datos)

    return io.BytesIO(html_renderizado.encode("utf-8"))

def obtener_datos_pedido():
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            # 🚀 Obtener información del pedido con enfermero y paquete asignado
            cursor.execute("""
                SELECT p.idPedido, p.Fecha, p.Hora, p.Ubicacion, p.Cirugia, p.Estado,
                       CONCAT(u.nombres, ' ', u.apellidoPaterno, ' ', u.apellidoMaterno) AS nombreEnfermero,
                       pa.idPaquete, pa.Nombre AS nombrePaquete, e.Nombre AS especialidad
                FROM Pedido p
                LEFT JOIN Usuario u ON p.idEnfermero = u.idUsuario
                LEFT JOIN Paquete pa ON p.idPaquete = pa.idPaquete
                LEFT JOIN Especialidad e ON pa.idEspecialidad = e.idEspecialidad
                ORDER BY p.idPedido ASC;
            """)
            pedidos_datos = cursor.fetchall()

            # 🚀 Obtener equipos asignados al pedido
            cursor.execute("""
                SELECT pe.idPedido, e.idEquipo, e.Nombre AS nombreEquipo
                FROM Pedido_Equipo pe
                LEFT JOIN Equipo e ON pe.idEquipo = e.idEquipo
                ORDER BY pe.idPedido, pe.idEquipo ASC;
            """)
            equipos_pedido_datos = cursor.fetchall()

            # 🚀 Obtener instrumentos dentro de los equipos
            cursor.execute("""
                SELECT ei.idEquipo, gi.idInstrumento, gi.Nombre AS nombreInstrumento, gi.CodigoDeBarras, ei.cantidad
                FROM Equipo_Instrumento ei
                LEFT JOIN GInstrumento gi ON ei.idInstrumento = gi.idInstrumento
                ORDER BY ei.idEquipo, gi.idInstrumento ASC;
            """)
            instrumentos_equipo_datos = cursor.fetchall()

            # 🚀 Obtener instrumentos grupales del pedido desde `Pedido_IInstrumento`
            cursor.execute("""
                SELECT pi.idPedido, gi.idInstrumento, gi.Nombre AS nombreInstrumento, gi.CodigoDeBarras
                FROM Pedido_IInstrumento pi
                LEFT JOIN GInstrumento gi ON pi.idInstrumento = gi.idInstrumento
                ORDER BY pi.idPedido, gi.idInstrumento ASC;
            """)
            instrumentos_pedido_datos = cursor.fetchall()

            # 🚀 Obtener los equipos dentro del paquete
            cursor.execute("""
                SELECT pa.idPaquete, e.idEquipo, e.Nombre AS nombreEquipo
                FROM Paquete_Equipo pe
                LEFT JOIN Paquete pa ON pe.idPaquete = pa.idPaquete
                LEFT JOIN Equipo e ON pe.idEquipo = e.idEquipo
                ORDER BY pa.idPaquete, e.idEquipo ASC;
            """)
            paquetes_equipos_datos = cursor.fetchall()

            # 🚀 Obtener los instrumentos dentro de los paquetes
            cursor.execute("""
                SELECT pa.idPaquete, gi.idInstrumento, gi.Nombre AS nombreInstrumento, gi.CodigoDeBarras, COALESCE(pi.cantidad, 0)
                FROM Paquete_Instrumento pi
                LEFT JOIN Paquete pa ON pi.idPaquete = pa.idPaquete
                LEFT JOIN GInstrumento gi ON pi.idInstrumento = gi.idInstrumento
                ORDER BY pa.idPaquete, gi.idInstrumento ASC;
            """)
            paquetes_instrumentos_datos = cursor.fetchall()

        pedidos_por_grupo = {}
        paquetes_equipos = {}
        paquetes_instrumentos = {}

        # 🚀 Organizar pedidos por grupo
        for item in pedidos_datos:
            id_pedido = str(item[0])
            pedidos_por_grupo[id_pedido] = {
                "fecha": item[1],
                "hora": item[2],
                "ubicacion": item[3],
                "cirugia": item[4],
                "estado": item[5],
                "enfermero": item[6],
                "idPaquete": str(item[7]),
                "nombrePaquete": item[8],
                "especialidad": item[9],
                "equipos": [],
                "instrumentos_grupo": [],
                "total_instrumentos_equipo": 0,
                "total_instrumentos_grupo": 0
            }

        # 🚀 Organizar equipos asignados al pedido
        for item in equipos_pedido_datos:
            id_pedido = str(item[0])
            id_equipo = str(item[1])
            pedidos_por_grupo[id_pedido]["equipos"].append({
                "idEquipo": id_equipo,
                "nombreEquipo": item[2],
                "instrumentos": [],
                "total_instrumentos": 0
            })

        # 🚀 Organizar instrumentos dentro de los equipos
        for item in instrumentos_equipo_datos:
            id_equipo = str(item[0])
            for pedido in pedidos_por_grupo.values():
                for equipo in pedido["equipos"]:
                    if equipo["idEquipo"] == id_equipo:
                        equipo["instrumentos"].append({
                            "idInstrumento": item[1],
                            "nombreInstrumento": item[2],
                            "codigoBarras": item[3],
                            "cantidad": item[4]
                        })
                        equipo["total_instrumentos"] += item[4]
                        pedido["total_instrumentos_equipo"] += item[4]

        # 🚀 Organizar instrumentos grupales del pedido
        for item in instrumentos_pedido_datos:
            id_pedido = str(item[0])
            pedidos_por_grupo[id_pedido]["instrumentos_grupo"].append({
                "idInstrumento": item[1],
                "nombreInstrumentoGrupo": item[2],
                "codigoBarras": item[3]
            })

        return {
            "pedidos_por_grupo": pedidos_por_grupo,
            "paquetes_equipos": paquetes_equipos,
            "paquetes_instrumentos": paquetes_instrumentos,
            "fecha_reporte": datetime.now().strftime("%d/%m/%Y %H:%M"),
        }

    except pymysql.Error as e:
        print(f"Error MySQL: {e}")
        return None
    finally:
        connection.close()

def generar_html_pedido():
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("pedido_instrumentos.html")

    datos = obtener_datos_pedido()
    if not datos:
        raise HTTPException(status_code=500, detail="No se obtuvieron datos de la base de datos")

    html_renderizado = template.render(datos)
    return io.BytesIO(html_renderizado.encode("utf-8"))

def obtener_datos_equipo():
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT eq.idEquipo, eq.Nombre AS nombreEquipo, 
                    gi.idInstrumento AS idInstrumentoGrupo, gi.Nombre AS nombreInstrumento, 
                    gi.CodigoDeBarras, ei.cantidad AS cantidadInstrumento
                FROM Equipo eq
                INNER JOIN Equipo_Instrumento ei ON eq.idEquipo = ei.idEquipo
                INNER JOIN GInstrumento gi ON ei.idInstrumento = gi.idInstrumento
                ORDER BY eq.idEquipo, gi.idInstrumento ASC;
            """)
            equipo_instrumentos = cursor.fetchall()

        # Agrupar por idEquipo para mostrar la cantidad total por instrumento
        equipos_por_grupo = {}
        for item in equipo_instrumentos:
            id_equipo = item[0]
            if id_equipo not in equipos_por_grupo:
                equipos_por_grupo[id_equipo] = {
                    "nombreEquipo": item[1],
                    "datos": [],
                    "cantidad_total_equipo": 0
                }
            equipos_por_grupo[id_equipo]["datos"].append({
                "idInstrumentoGrupo": item[2],
                "nombreInstrumento": item[3],
                "codigoBarras": item[4],
                "cantidadInstrumento": item[5]
            })
            equipos_por_grupo[id_equipo]["cantidad_total_equipo"] += item[5]  # Sumar cantidad total de instrumentos en el equipo

        datos = {
            "equipos_por_grupo": equipos_por_grupo,
            "fecha_reporte": datetime.now().strftime("%d/%m/%Y %H:%M"),
        }

        return datos
    except pymysql.Error as e:
        print(f"Error MySQL: {e}")
        return None
    finally:
        connection.close()

def generar_pdf_equipo():
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("equipo_instrumentos.html")

    datos = obtener_datos_equipo()
    if not datos:
        raise HTTPException(status_code=500, detail="No se obtuvieron datos de la base de datos")

    html_renderizado = template.render(datos)

    return io.BytesIO(html_renderizado.encode("utf-8"))

@app.get("/getEquipoInstrumentos")
async def descargar_equipo():
    html_file = generar_pdf_equipo()
    return StreamingResponse(html_file, media_type="text/html",
                             headers={"Content-Disposition": "inline; filename=Equipo_Instrumentos.html"})

@app.get("/getPedidoInstrumentos")
async def descargar_pedido():
    html_file = generar_html_pedido()
    return StreamingResponse(html_file, media_type="text/html",
                             headers={"Content-Disposition": "inline; filename=Pedido_Instrumentos.html"})

@app.get("/getPaqueteEquiposInstrumentos")
async def descargar_paquete():
    pdf_file = generar_pdf_paquete()
    return StreamingResponse(pdf_file, media_type="text/html",
                             headers={"Content-Disposition": "inline; filename=Paquete_Equipos_Instrumentos.html"})

@app.get("/getInstrumento")
async def descargar_instrumento():
    html_file = generar_pdf_instrumento()
    return StreamingResponse(html_file, media_type="text/html",
                             headers={"Content-Disposition": "inline; filename=Instrumento.html"})

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
    pdf_file = generar_html_historial_pedido()
    return StreamingResponse(pdf_file, media_type="text/html",
                             headers={"Content-Disposition": "inline; filename=Historial_Paquetes.html"})

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
    

@app.post("/postUsuario")
async def crear_usuario(usuario: Usuario, response: Response):
    try:
        if not usuario.Correo or not usuario.Contrasena:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"message": "Correo o contraseña vacíos"}

        connection = utils.get_connection()
        with connection.cursor() as cursor:
            hashed_password = sha256(usuario.Contrasena.encode()).hexdigest()

            # Si el alias no se proporciona, se asigna el rol por defecto
            alias_final = usuario.Alias if usuario.Alias else usuario.Rol

            cursor.execute(
                "INSERT INTO Usuario (Nombres, ApellidoPaterno, ApellidoMaterno, Rol, Correo, Contrasena, Alias) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (usuario.Nombres, usuario.ApellidoPaterno, usuario.ApellidoMaterno, usuario.Rol, usuario.Correo, hashed_password, alias_final)
            )
            connection.commit()
            return {"message": "Usuario insertado correctamente"}

    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}
    finally:
        connection.close()

@app.put("/updateUsuario/{index}")
async def actualizar_usuario(index: int, usuario: Usuario, response: Response):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Usuario WHERE idUsuario = %s", (index,))
            result = cursor.fetchone()
            if not result:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "No existe el usuario"}

            # Si la contraseña no se proporciona, se mantiene la actual
            contrasena_final = result[5] if not usuario.Contrasena else sha256(usuario.Contrasena.encode()).hexdigest()

            # Si el alias no se proporciona o está vacío, usa el rol del usuario en lugar del correo
            alias_final = usuario.Alias if usuario.Alias and usuario.Alias.strip() else usuario.Rol

            cursor.execute(
                "UPDATE Usuario SET Nombres = %s, ApellidoPaterno = %s, ApellidoMaterno = %s, Rol = %s, Correo = %s, Contrasena = %s, Alias = %s WHERE idUsuario = %s",
                (usuario.Nombres, usuario.ApellidoPaterno, usuario.ApellidoMaterno, usuario.Rol, usuario.Correo, contrasena_final, alias_final, index)
            )
            connection.commit()
            return {"message": "Usuario actualizado correctamente"}

    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}
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

@app.put("/updateEspecialidad")
async def root(response: Response, especialidad: Especialidad):
    try:
        connection = utils.get_connection()

        with connection.cursor() as cursor:
            if especialidad.idEspecialidad is None:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return {"message": "Debe proporcionar un idEspecialidad o un Nombre"}
            elif especialidad.Nombre is None:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return {"message": "No hay cambios"}
            cursor.execute("SELECT * FROM Especialidad WHERE idEspecialidad = %s", (especialidad.idEspecialidad))
            result = cursor.fetchall()
            if not result:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "No existe la especialidad"}
            cursor.execute("UPDATE Especialidad SET Nombre = %s WHERE idEspecialidad = %s", (especialidad.Nombre, especialidad.idEspecialidad))
            connection.commit()
            return JSONResponse(
                content={"message": "Especialidad actualizada correctamente"},
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

@app.post("/getInstrumento")
async def obtener_instrumento(data: GetInstrumentoRequest, response: Response):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            if data.idInstrumentoIndividual:
                consulta = """SELECT 
                                i.idInstrumentoIndividual, 
                                g.Nombre AS nombreInstrumentoGrupo, 
                                i.ultimaEsterilizacion, 
                                i.Estado, 
                                i.Ubicacion, 
                                i.idInstrumentoGrupo,
                                i.idEquipo, 
                                e.Nombre AS nombreEquipo, 
                                i.idPaquete, 
                                p.Nombre AS nombrePaquete
                              FROM IInstrumento i
                              JOIN GInstrumento g ON i.idInstrumentoGrupo = g.idInstrumento
                              LEFT JOIN Equipo e ON i.idEquipo = e.idEquipo
                              LEFT JOIN Paquete p ON i.idPaquete = p.idPaquete
                              WHERE i.idInstrumentoIndividual = %s"""
                cursor.execute(consulta, (data.idInstrumentoIndividual,))
                instrumento = cursor.fetchone()

            elif data.nombreInstrumentoIndividual:
                consulta = """SELECT 
                                i.idInstrumentoIndividual, 
                                g.Nombre AS nombreInstrumentoGrupo, 
                                i.ultimaEsterilizacion, 
                                i.Estado, 
                                i.Ubicacion, 
                                i.idInstrumentoGrupo,
                                i.idEquipo, 
                                e.Nombre AS nombreEquipo, 
                                i.idPaquete, 
                                p.Nombre AS nombrePaquete
                              FROM IInstrumento i
                              JOIN GInstrumento g ON i.idInstrumentoGrupo = g.idInstrumento
                              LEFT JOIN Equipo e ON i.idEquipo = e.idEquipo
                              LEFT JOIN Paquete p ON i.idPaquete = p.idPaquete
                              WHERE g.Nombre = %s"""
                cursor.execute(consulta, (data.nombreInstrumentoIndividual,))
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
                "idInstrumentoGrupo": instrumento[5],
                "idEquipo": instrumento[6],
                "nombreEquipo": instrumento[7] if instrumento[7] else "Sin asignación",
                "idPaquete": instrumento[8],
                "nombrePaquete": instrumento[9] if instrumento[9] else "Sin asignación"
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
            # Consultar los instrumentos con sus equipos y paquetes asociados
            cursor.execute("""
                SELECT 
                    i.idInstrumentoIndividual, 
                    i.idInstrumentoGrupo, 
                    g.Nombre AS nombreInstrumentoGrupo, 
                    i.ultimaEsterilizacion, 
                    i.Estado, 
                    i.Ubicacion,
                    i.idEquipo, 
                    e.Nombre AS nombreEquipo,
                    i.idPaquete, 
                    p.Nombre AS nombrePaquete
                FROM IInstrumento i
                JOIN GInstrumento g ON i.idInstrumentoGrupo = g.idInstrumento
                LEFT JOIN Equipo e ON i.idEquipo = e.idEquipo
                LEFT JOIN Paquete p ON i.idPaquete = p.idPaquete
            """)
            instrumentos = cursor.fetchall()

            return [
                {
                    "idInstrumentoIndividual": i[0], 
                    "idInstrumentoGrupo": i[1], 
                    "Nombre": i[2], 
                    "ultimaEsterilizacion": i[3], 
                    "Estado": i[4], 
                    "Ubicacion": i[5],
                    "idEquipo": i[6],
                    "nombreEquipo": i[7] if i[7] else "Sin asignación",
                    "idPaquete": i[8],
                    "nombrePaquete": i[9] if i[9] else "Sin asignación"
                } 
                for i in instrumentos
            ]
    
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}

    finally:
        connection.close()

@app.post("/getInstrumentosPorGrupo")
async def obtener_instrumentos_por_grupo(data: GetInstrumentosPorGrupoRequest, response: Response):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            if data.idInstrumentoGrupo:
                consulta = """SELECT 
                                i.idInstrumentoIndividual, 
                                g.Nombre AS nombreInstrumentoGrupo, 
                                i.ultimaEsterilizacion, 
                                i.Estado, 
                                i.Ubicacion, 
                                i.idInstrumentoGrupo,
                                i.idEquipo, 
                                e.Nombre AS nombreEquipo, 
                                i.idPaquete, 
                                p.Nombre AS nombrePaquete
                              FROM IInstrumento i
                              JOIN GInstrumento g ON i.idInstrumentoGrupo = g.idInstrumento
                              LEFT JOIN Equipo e ON i.idEquipo = e.idEquipo
                              LEFT JOIN Paquete p ON i.idPaquete = p.idPaquete
                              WHERE i.idInstrumentoGrupo = %s"""
                cursor.execute(consulta, (data.idInstrumentoGrupo,))
                instrumentos = cursor.fetchall()

            elif data.nombreInstrumentoGrupo:
                consulta = """SELECT 
                                i.idInstrumentoIndividual, 
                                g.Nombre AS nombreInstrumentoGrupo, 
                                i.ultimaEsterilizacion, 
                                i.Estado, 
                                i.Ubicacion, 
                                i.idInstrumentoGrupo,
                                i.idEquipo, 
                                e.Nombre AS nombreEquipo, 
                                i.idPaquete, 
                                p.Nombre AS nombrePaquete
                              FROM IInstrumento i
                              JOIN GInstrumento g ON i.idInstrumentoGrupo = g.idInstrumento
                              LEFT JOIN Equipo e ON i.idEquipo = e.idEquipo
                              LEFT JOIN Paquete p ON i.idPaquete = p.idPaquete
                              WHERE g.Nombre = %s"""
                cursor.execute(consulta, (data.nombreInstrumentoGrupo,))
                instrumentos = cursor.fetchall()

            else:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return {"message": "Debe proporcionar un idInstrumentoGrupo o un nombreInstrumentoGrupo"}

            if not instrumentos:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "No se encontraron instrumentos en este grupo"}

            return [
                {
                    "idInstrumentoIndividual": i[0],
                    "Nombre": i[1],
                    "ultimaEsterilizacion": i[2],
                    "Estado": i[3],
                    "Ubicacion": i[4],
                    "idInstrumentoGrupo": i[5],
                    "idEquipo": i[6],
                    "nombreEquipo": i[7] if i[7] else "Sin asignación",
                    "idPaquete": i[8],
                    "nombrePaquete": i[9] if i[9] else "Sin asignación"
                } 
                for i in instrumentos
            ]

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
            # Determinar si se busca por ID o Nombre
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
                        INSERT INTO IInstrumento (idInstrumentoGrupo, Estado, Ubicacion, ultimaEsterilizacion, idEquipo, idPaquete)
                        VALUES (%s, %s, %s, NOW(), NULL, NULL)
                    """, (idInstrumento, "Disponible", "Almacén"))

            elif diferencia < 0:
                cantidad_a_eliminar = abs(diferencia)

                cursor.execute("""
                    SELECT idInstrumentoIndividual 
                    FROM IInstrumento 
                    WHERE idInstrumentoGrupo = %s 
                    AND Estado = 'Disponible' 
                    AND idEquipo IS NULL 
                    AND idPaquete IS NULL
                    LIMIT %s
                """, (idInstrumento, cantidad_a_eliminar))

                instrumentos_disponibles = cursor.fetchall()

                if len(instrumentos_disponibles) < cantidad_a_eliminar:
                    response.status_code = status.HTTP_400_BAD_REQUEST
                    return {"message": "No hay suficientes instrumentos sin asignación para eliminar"}

                # Eliminar los instrumentos seleccionados
                for instrumento in instrumentos_disponibles:
                    cursor.execute("DELETE FROM IInstrumento WHERE idInstrumentoIndividual = %s", (instrumento[0],))

            if data.nuevaCantidad == 0:
                cursor.execute("DELETE FROM IInstrumento WHERE idInstrumentoGrupo = %s", (idInstrumento,))
                
            cursor.execute("UPDATE GInstrumento SET Cantidad = %s WHERE idInstrumento = %s", (data.nuevaCantidad, idInstrumento))
            connection.commit()

            return {"message": "Grupo de instrumentos actualizado correctamente"}

    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}

    finally:
        connection.close()

@app.delete("/deleteGInstrumento")
async def eliminar_ginstrumento(data: DeleteGInstrumentoRequest, response: Response):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            if data.idInstrumento:
                cursor.execute("SELECT idInstrumento, Nombre FROM GInstrumento WHERE idInstrumento = %s", (data.idInstrumento,))
                grupo = cursor.fetchone()
            elif data.nombreInstrumento:
                cursor.execute("SELECT idInstrumento, Nombre FROM GInstrumento WHERE Nombre = %s", (data.nombreInstrumento,))
                grupo = cursor.fetchone()
            else:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return {"message": "Debe proporcionar un idInstrumento o un nombreInstrumento"}

            if not grupo:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "Grupo de instrumentos no encontrado"}

            idInstrumento = grupo[0]
            nombreInstrumento = grupo[1]  

            cursor.execute("""
                UPDATE Historial_IInstrumento 
                SET nombreHerramientaPrevio = %s 
                WHERE idInstrumentoIndividual IN (
                    SELECT idInstrumentoIndividual FROM IInstrumento WHERE idInstrumentoGrupo = %s
                )
            """, (nombreInstrumento, idInstrumento))

            cursor.execute("""
                UPDATE Historial_GInstrumento 
                SET nombreInstrumentoPrevio = %s 
                WHERE idInstrumento = %s
            """, (nombreInstrumento, idInstrumento))

            cursor.execute("DELETE FROM IInstrumento WHERE idInstrumentoGrupo = %s", (idInstrumento,))
            cursor.execute("DELETE FROM Equipo_Instrumento WHERE idInstrumento = %s", (idInstrumento,))
            cursor.execute("DELETE FROM Paquete_Instrumento WHERE idInstrumento = %s", (idInstrumento,))
            cursor.execute("DELETE FROM Pedido_IInstrumento WHERE idInstrumento = %s", (idInstrumento,))
            cursor.execute("DELETE FROM GInstrumento WHERE idInstrumento = %s", (idInstrumento,))
            
            connection.commit()

            return {"message": f"Grupo de instrumentos '{nombreInstrumento}' eliminado correctamente junto con sus instrumentos asociados"}

    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}

    finally:
        connection.close()

@app.put("/updateIInstrumento")
async def actualizar_instrumento(data: UpdateIInstrumentoRequest, response: Response):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            # Validar si el instrumento existe
            cursor.execute("SELECT idInstrumentoIndividual, idEquipo, idPaquete FROM IInstrumento WHERE idInstrumentoIndividual = %s", 
                           (data.idInstrumentoIndividual,))
            instrumento = cursor.fetchone()

            if not instrumento:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "Instrumento no encontrado"}

            id_equipo_actual, id_paquete_actual = instrumento[1], instrumento[2]

            # Validar que el instrumento solo puede estar en un equipo **o** en un paquete, no ambos
            if data.idEquipo and data.idPaquete:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return {"message": "Un instrumento solo puede pertenecer a un equipo o a un paquete, pero no a ambos"}

            # Construir la consulta de actualización
            campos_actualizar = []
            valores = []

            if data.nuevoEstado:
                estados_validos = ["Disponible", "En Uso", "Limpieza", "Pendiente", "Autoclave"]
                if data.nuevoEstado not in estados_validos:
                    response.status_code = status.HTTP_400_BAD_REQUEST
                    return {"message": "Estado inválido. Debe ser uno de: Disponible, En Uso, Limpieza, Pendiente, Autoclave"}
                campos_actualizar.append("Estado = %s")
                valores.append(data.nuevoEstado)

            if data.nuevaUbicacion:
                campos_actualizar.append("Ubicacion = %s")
                valores.append(data.nuevaUbicacion)

            if data.nuevaEsterilizacion:
                if isinstance(data.nuevaEsterilizacion, datetime):
                    fecha_hora_esterilizacion = data.nuevaEsterilizacion.strftime("%Y-%m-%d %H:%M:%S")  
                else:
                    try:
                        fecha_hora_esterilizacion = datetime.strptime(data.nuevaEsterilizacion, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        response.status_code = status.HTTP_400_BAD_REQUEST
                        return {"message": "Formato de fecha/hora inválido. Debe ser YYYY-MM-DD HH:MM:SS"}
                campos_actualizar.append("ultimaEsterilizacion = %s")
                valores.append(fecha_hora_esterilizacion)

            if data.idEquipo is None and id_equipo_actual:
                cursor.execute("""
                    UPDATE Equipo_Instrumento 
                    SET cantidad = GREATEST(cantidad - 1, 0) 
                    WHERE idEquipo = %s AND idInstrumento = (SELECT idInstrumentoGrupo FROM IInstrumento WHERE idInstrumentoIndividual = %s)
                """, (id_equipo_actual, data.idInstrumentoIndividual))
                campos_actualizar.append("idEquipo = NULL")

            if data.idPaquete is None and id_paquete_actual:
                cursor.execute("""
                    UPDATE Paquete_Instrumento 
                    SET cantidad = GREATEST(cantidad - 1, 0) 
                    WHERE idPaquete = %s AND idInstrumento = (SELECT idInstrumentoGrupo FROM IInstrumento WHERE idInstrumentoIndividual = %s)
                """, (id_paquete_actual, data.idInstrumentoIndividual))
                campos_actualizar.append("idPaquete = NULL")

            if data.idEquipo and data.idEquipo != id_equipo_actual:
                cursor.execute("""
                    INSERT INTO Equipo_Instrumento (idEquipo, idInstrumento, cantidad)
                    VALUES (%s, (SELECT idInstrumentoGrupo FROM IInstrumento WHERE idInstrumentoIndividual = %s), 1)
                    ON DUPLICATE KEY UPDATE cantidad = cantidad + 1
                """, (data.idEquipo, data.idInstrumentoIndividual))
                campos_actualizar.append("idEquipo = %s")
                valores.append(data.idEquipo)

            if data.idPaquete and data.idPaquete != id_paquete_actual:
                cursor.execute("""
                    INSERT INTO Paquete_Instrumento (idPaquete, idInstrumento, cantidad)
                    VALUES (%s, (SELECT idInstrumentoGrupo FROM IInstrumento WHERE idInstrumentoIndividual = %s), 1)
                    ON DUPLICATE KEY UPDATE cantidad = cantidad + 1
                """, (data.idPaquete, data.idInstrumentoIndividual))
                campos_actualizar.append("idPaquete = %s")
                valores.append(data.idPaquete)

            if not campos_actualizar:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return {"message": "Debe proporcionar al menos un campo para actualizar"}

            valores.append(data.idInstrumentoIndividual)
            consulta_sql = f"UPDATE IInstrumento SET {', '.join(campos_actualizar)} WHERE idInstrumentoIndividual = %s"
            cursor.execute(consulta_sql, valores)

            connection.commit()
            return {"message": "Instrumento actualizado correctamente"}

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

@app.post("/getEquipo")
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
            # 🚀 **Validar si se proporciona ID o nombre del equipo**
            if data.idEquipo:
                cursor.execute("SELECT idEquipo, Nombre FROM Equipo WHERE idEquipo = %s", (data.idEquipo,))
                equipo = cursor.fetchone()
            elif data.nombreEquipo:
                cursor.execute("SELECT idEquipo, Nombre FROM Equipo WHERE Nombre = %s", (data.nombreEquipo,))
                equipo = cursor.fetchone()
            else:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return {"message": "Debe proporcionar un idEquipo o un nombreEquipo"}

            if not equipo:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "Equipo no encontrado"}

            idEquipo = equipo[0]
            nombreEquipo = equipo[1]  # 🚀 **Guardar el nombre antes de eliminar**

            # 🚀 **Actualizar `Historial_Equipos` con el nombre previo**
            cursor.execute("""
                UPDATE Historial_Equipos 
                SET nombreEquipoPrevio = %s 
                WHERE idEquipo = %s
            """, (nombreEquipo, idEquipo))

            # 🚀 **Eliminar relaciones antes de eliminar el equipo**
            cursor.execute("DELETE FROM Equipo_Instrumento WHERE idEquipo = %s", (idEquipo,))
            cursor.execute("UPDATE IInstrumento SET idEquipo = NULL WHERE idEquipo = %s", (idEquipo,))
            cursor.execute("DELETE FROM Equipo WHERE idEquipo = %s", (idEquipo,))

            connection.commit()
            return {"message": f"Equipo '{nombreEquipo}' eliminado correctamente junto con sus relaciones asociadas"}

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
            # Validar que el equipo exista
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
                    return {"message": f"No se puede agregar un instrumento con cantidad {cantidad}"}

                if nombreInstrumento and not idInstrumento:
                    cursor.execute("SELECT idInstrumento FROM GInstrumento WHERE Nombre = %s", (nombreInstrumento,))
                    instrumento_existente = cursor.fetchone()
                    if not instrumento_existente:
                        response.status_code = status.HTTP_404_NOT_FOUND
                        return {"message": f"Instrumento '{nombreInstrumento}' no encontrado"}
                    idInstrumento = instrumento_existente[0]

                # Validar existencia de instrumento
                cursor.execute("SELECT Cantidad FROM GInstrumento WHERE idInstrumento = %s", (idInstrumento,))
                instrumento_existente = cursor.fetchone()
                if not instrumento_existente:
                    response.status_code = status.HTTP_404_NOT_FOUND
                    return {"message": f"Instrumento con id {idInstrumento} no encontrado"}

                cantidad_disponible = instrumento_existente[0]

                # Obtener cantidad ya asignada a otros equipos
                cursor.execute("SELECT SUM(cantidad) FROM Equipo_Instrumento WHERE idInstrumento = %s", (idInstrumento,))
                cantidad_asignada = cursor.fetchone()[0] or 0

                # Validar si hay suficiente inventario disponible
                cantidad_restante = cantidad_disponible - cantidad_asignada
                if cantidad > cantidad_restante:
                    response.status_code = status.HTTP_400_BAD_REQUEST
                    return {"message": f"No hay suficientes unidades disponibles del instrumento {idInstrumento}. Quedan {cantidad_restante} disponibles."}

                # Insertar o actualizar la cantidad en `Equipo_Instrumento`
                cursor.execute("""
                    INSERT INTO Equipo_Instrumento (idEquipo, idInstrumento, cantidad)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE cantidad = cantidad + %s
                """, (data.idEquipo, idInstrumento, cantidad, cantidad))

                # ✅ **Actualizar `idEquipo` en `IInstrumento` para reflejar la asignación**
                cursor.execute("""
                    UPDATE IInstrumento 
                    SET idEquipo = %s 
                    WHERE idInstrumentoGrupo = %s 
                    AND idEquipo IS NULL 
                    LIMIT %s
                """, (data.idEquipo, idInstrumento, cantidad))

            connection.commit()
            return {"message": "Cantidad de herramientas modificada correctamente y asignación reflejada en Instrumentos"}

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
            # Validar que el equipo exista
            cursor.execute("SELECT idEquipo FROM Equipo WHERE idEquipo = %s", (data.idEquipo,))
            equipo_existente = cursor.fetchone()
            if not equipo_existente:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "Equipo no encontrado"}

            eliminados = []

            for herramienta in data.herramientas:
                idInstrumento = herramienta.get("idInstrumento")
                nombreInstrumento = herramienta.get("nombreInstrumento")

                # 🚀 **Si se envía nombreInstrumento, obtener su ID**
                if nombreInstrumento and not idInstrumento:
                    cursor.execute("SELECT idInstrumento FROM GInstrumento WHERE Nombre = %s", (nombreInstrumento,))
                    instrumento_data = cursor.fetchone()
                    if not instrumento_data:
                        response.status_code = status.HTTP_404_NOT_FOUND
                        return {"message": f"Instrumento con nombre '{nombreInstrumento}' no encontrado"}
                    idInstrumento = instrumento_data[0]

                # Validar existencia en `Equipo_Instrumento`
                cursor.execute("SELECT cantidad FROM Equipo_Instrumento WHERE idEquipo = %s AND idInstrumento = %s",
                               (data.idEquipo, idInstrumento))
                instrumento_equipo = cursor.fetchone()
                if not instrumento_equipo:
                    response.status_code = status.HTTP_404_NOT_FOUND
                    return {"message": f"Instrumento con id {idInstrumento} no está en el equipo"}

                # 🚨 **Eliminar relación en `Equipo_Instrumento`**
                cursor.execute("DELETE FROM Equipo_Instrumento WHERE idEquipo = %s AND idInstrumento = %s",
                               (data.idEquipo, idInstrumento))

                # ✅ **Eliminar asignación en `IInstrumento`**
                cursor.execute("UPDATE IInstrumento SET idEquipo = NULL WHERE idInstrumentoGrupo = %s AND idEquipo = %s",
                               (idInstrumento, data.idEquipo))

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

            # Validar que la especialidad existe
            cursor.execute("SELECT idEspecialidad FROM Especialidad WHERE idEspecialidad = %s", (data.idEspecialidad,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Especialidad no encontrada")

            # Validar que el nombre del paquete no esté vacío
            if not data.Nombre or data.Nombre.strip() == "":
                raise HTTPException(status_code=400, detail="El nombre del paquete no puede estar vacío")

            # Insertar el paquete en la tabla
            cursor.execute("INSERT INTO Paquete (Nombre, idEspecialidad) VALUES (%s, %s)", 
                           (data.Nombre, data.idEspecialidad))
            paquete_id = cursor.lastrowid  

            connection.commit()
            return {"message": "Paquete registrado correctamente"}

    except pymysql.Error as e:
        raise HTTPException(status_code=500, detail=f"Error MySQL: {e}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {e}")

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

@app.post("/getPaquete")
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
        
@app.put("/updatePaquete")
async def actualizar_paquete(data: UpdatePaqueteRequest, response: Response):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
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

            # Construir la consulta de actualización dinámicamente
            campos_a_actualizar = []
            valores = []

            if data.nombrePaquete:
                campos_a_actualizar.append("Nombre = %s")
                valores.append(data.nombrePaquete)
            if data.idEspecialidad:
                campos_a_actualizar.append("idEspecialidad = %s")
                valores.append(data.idEspecialidad)

            if campos_a_actualizar:
                consulta_update = f"UPDATE Paquete SET {', '.join(campos_a_actualizar)} WHERE idPaquete = %s"
                valores.append(data.idPaquete)
                cursor.execute(consulta_update, tuple(valores))
                connection.commit()

            return {"message": f"Paquete {data.idPaquete} actualizado correctamente"}

    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}

    finally:
        connection.close()

@app.post("/getPaquetePorEspecialidad")
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
            if data.idPaquete:
                cursor.execute("SELECT idPaquete, Nombre FROM Paquete WHERE idPaquete = %s", (data.idPaquete,))
                paquete_existente = cursor.fetchone()
            elif data.nombrePaquete:
                cursor.execute("SELECT idPaquete, Nombre FROM Paquete WHERE Nombre = %s", (data.nombrePaquete,))
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

            idPaquete = data.idPaquete
            nombrePaquete = paquete_existente[1]  # 🚀 **Guardar el nombre antes de eliminar**

            cursor.execute("""
                UPDATE Historial_Paquetes 
                SET nombrePaquetePrevio = %s 
                WHERE idPaquete = %s
            """, (nombrePaquete, idPaquete))

            cursor.execute("DELETE FROM Paquete_Equipo WHERE idPaquete = %s", (idPaquete,))
            cursor.execute("DELETE FROM Paquete_Instrumento WHERE idPaquete = %s", (idPaquete,))
            cursor.execute("UPDATE IInstrumento SET idPaquete = NULL WHERE idPaquete = %s", (idPaquete,))
            cursor.execute("DELETE FROM Paquete WHERE idPaquete = %s", (idPaquete,))

            connection.commit()
            return {"message": f"Paquete '{nombrePaquete}' eliminado correctamente junto con sus asociaciones"}

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
            # Validar existencia del paquete
            cursor.execute("SELECT idPaquete FROM Paquete WHERE idPaquete = %s", (data.idPaquete,))
            paquete_existente = cursor.fetchone()
            if not paquete_existente:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": f"Paquete con id {data.idPaquete} no encontrado"}

            eliminados = []  
            agregados = []  
            cantidad_total_agregada = 0  

            for instrumento in data.instrumentos:
                idInstrumento = instrumento["idInstrumento"]
                cantidad_solicitada = instrumento["cantidad"]

                cursor.execute("SELECT Cantidad FROM GInstrumento WHERE idInstrumento = %s", (idInstrumento,))
                instrumento_existente = cursor.fetchone()
                if not instrumento_existente:
                    response.status_code = status.HTTP_404_NOT_FOUND
                    return {"message": f"Instrumento con id {idInstrumento} no encontrado"}

                cursor.execute("""
                    SELECT COUNT(*) FROM IInstrumento 
                    WHERE idInstrumentoGrupo = %s 
                    AND idEquipo IS NULL 
                    AND idPaquete IS NULL
                """, (idInstrumento,))
                cantidad_disponible = cursor.fetchone()[0]

                if cantidad_disponible == 0:
                    response.status_code = status.HTTP_400_BAD_REQUEST
                    return {"message": f"No hay instrumentos disponibles del grupo {idInstrumento} para asignar al paquete"}

                cantidad_a_insertar = min(cantidad_solicitada, cantidad_disponible)
                cantidad_total_agregada += cantidad_a_insertar  

                cursor.execute("SELECT cantidad FROM Paquete_Instrumento WHERE idPaquete = %s AND idInstrumento = %s",
                               (data.idPaquete, idInstrumento))
                instrumento_paquete = cursor.fetchone()

                if cantidad_a_insertar == 0:
                    cursor.execute("DELETE FROM Paquete_Instrumento WHERE idPaquete = %s AND idInstrumento = %s", 
                                   (data.idPaquete, idInstrumento))
                    eliminados.append(idInstrumento)  
                elif instrumento_paquete:
                    cursor.execute("""
                        UPDATE Paquete_Instrumento 
                        SET cantidad = %s 
                        WHERE idPaquete = %s AND idInstrumento = %s
                    """, (cantidad_a_insertar, data.idPaquete, idInstrumento))
                else:
                    cursor.execute("""
                        INSERT INTO Paquete_Instrumento (idPaquete, idInstrumento, cantidad)
                        VALUES (%s, %s, %s)
                    """, (data.idPaquete, idInstrumento, cantidad_a_insertar))
                    agregados.append(idInstrumento)

            connection.commit()
            
            mensajes = []
            if eliminados:
                mensajes.append(f"Instrumentos eliminados: {', '.join(map(str, eliminados))}")
            if agregados:
                mensajes.append(f"Instrumentos agregados: {', '.join(map(str, agregados))}")
            if not mensajes:
                mensajes.append("Instrumentos actualizados correctamente en el paquete")

            return {
                "message": " | ".join(mensajes),
                "cantidad_total_agregada": cantidad_total_agregada  # 🚀 **Incluye cantidad total agregada**
            }

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
            # Verificar que el paquete existe
            cursor.execute("SELECT idPaquete FROM Paquete WHERE idPaquete = %s", (data.idPaquete,))
            paquete_existente = cursor.fetchone()
            if not paquete_existente:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "Paquete no encontrado"}

            equipos_agregados = []
            equipos_duplicados = []

            for idEquipo in data.equipos:
                # Verificar que el equipo existe
                cursor.execute("SELECT idEquipo FROM Equipo WHERE idEquipo = %s", (idEquipo,))
                equipo_existente = cursor.fetchone()
                if not equipo_existente:
                    response.status_code = status.HTTP_404_NOT_FOUND
                    return {"message": f"Equipo con id {idEquipo} no encontrado"}

                # Verificar si el equipo ya está en el paquete
                cursor.execute("SELECT idPaquete FROM Paquete_Equipo WHERE idPaquete = %s AND idEquipo = %s", 
                               (data.idPaquete, idEquipo))
                equipo_asociado = cursor.fetchone()

                if equipo_asociado:
                    equipos_duplicados.append(idEquipo)
                else:
                    # Insertar el equipo si no está registrado aún en el paquete
                    cursor.execute("""
                        INSERT INTO Paquete_Equipo (idPaquete, idEquipo)
                        VALUES (%s, %s)
                    """, (data.idPaquete, idEquipo))
                    equipos_agregados.append(idEquipo)

            connection.commit()

            mensajes = []
            if equipos_duplicados:
                mensajes.append({
                    "message": f"Estos equipos ya estaban en el paquete y no se agregaron nuevamente: {equipos_duplicados}"
                })
            if equipos_agregados:
                mensajes.append({
                    "message": f"Equipos agregados correctamente al paquete: {equipos_agregados}"
                })

            return mensajes

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
            #payload = utils.verify_token(token)
            #if payload["rol"] != "Administrador":
            #    response.status_code = status.HTTP_403_FORBIDDEN
            #    return {"message": "No tienes permiso para acceder a esta ruta"}

            #cursor.execute("SET @idUsuario = %s", (payload["idUsuario"],))

            if pedido.idPaquete:
                cursor.execute("SELECT idPaquete FROM Paquete WHERE idPaquete = %s", (pedido.idPaquete,))
                if not cursor.fetchone():
                    response.status_code = status.HTTP_404_NOT_FOUND
                    return {"message": "Paquete no encontrado"}

            cursor.execute("SELECT rol FROM Usuario WHERE idUsuario = %s", (pedido.idEnfermero,))
            enfermero_rol = cursor.fetchone()
            if not enfermero_rol or enfermero_rol[0] != "Enfermero":
                response.status_code = status.HTTP_403_FORBIDDEN
                return {"message": "El usuario asignado no tiene el rol de Enfermero"}

            cursor.execute("""
                INSERT INTO Pedido (Fecha, Hora, Estado, idPaquete, idEnfermero, Cirugia, Ubicacion)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (pedido.Fecha, pedido.Hora, pedido.Estado, pedido.idPaquete, pedido.idEnfermero, pedido.Cirugia, pedido.Ubicacion))

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
            #payload = utils.verify_token(token)
            #if payload["rol"] != "Administrador":
             #   response.status_code = status.HTTP_403_FORBIDDEN
              #  return {"message": "No tienes permiso para acceder a esta ruta"}

            #cursor.execute("SET @idUsuario = %s", (payload["idUsuario"],))

            cursor.execute("SELECT idPedido FROM Pedido WHERE idPedido = %s", (pedido.idPedido,))
            if not cursor.fetchone():
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "Pedido no encontrado"}

            if pedido.idPaquete:
                cursor.execute("SELECT idPaquete FROM Paquete WHERE idPaquete = %s", (pedido.idPaquete,))
                if not cursor.fetchone():
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

            cursor.execute("SELECT rol FROM Usuario WHERE idUsuario = %s", (idEnfermero,))
            enfermero_rol = cursor.fetchone()
            if not enfermero_rol or enfermero_rol[0] != "Enfermero":
                response.status_code = status.HTTP_403_FORBIDDEN
                return {"message": "El usuario asignado no tiene el rol de Enfermero"}

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


@app.post("/getPedido")
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
            # Validar que el pedido existe
            cursor.execute("SELECT idPedido FROM Pedido WHERE idPedido = %s", (data.idPedido,))
            pedido_existente = cursor.fetchone()
            if not pedido_existente:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": f"Pedido con id {data.idPedido} no encontrado"}

            cantidad_total_agregada = 0  

            for instrumento in data.instrumentos:
                idInstrumento = instrumento.idInstrumento
                nombreInstrumento = instrumento.nombreInstrumento

                if not idInstrumento and nombreInstrumento:
                    cursor.execute("SELECT idInstrumento FROM GInstrumento WHERE Nombre = %s", (nombreInstrumento,))
                    instrumento_grupo = cursor.fetchone()
                    if not instrumento_grupo:
                        response.status_code = status.HTTP_404_NOT_FOUND
                        return {"message": f"Instrumento con nombre '{nombreInstrumento}' no encontrado"}
                    idInstrumentoGrupo = instrumento_grupo[0]

                    cursor.execute("""
                        SELECT idInstrumentoIndividual FROM IInstrumento 
                        WHERE idInstrumentoGrupo = %s 
                        AND idEquipo IS NULL 
                        AND idPaquete IS NULL 
                        LIMIT 1
                    """, (idInstrumentoGrupo,))
                    instrumento_disponible = cursor.fetchone()

                    if not instrumento_disponible:
                        response.status_code = status.HTTP_400_BAD_REQUEST
                        return {"message": f"No hay instrumentos disponibles para '{nombreInstrumento}'"}

                    idInstrumento = instrumento_disponible[0]  # Asignar el `idInstrumentoIndividual` disponible

                cursor.execute("""
                    INSERT INTO Pedido_IInstrumento (idPedido, idInstrumento) 
                    VALUES (%s, %s)
                """, (data.idPedido, idInstrumento))

                cantidad_total_agregada += 1  # 🚀 **Sumar al total agregado**

            connection.commit()
            return {
                "message": "Instrumentos agregados correctamente al pedido",
                "cantidad_total_agregada": cantidad_total_agregada  # 🚀 **Incluye cantidad total agregada**
            }

    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}

    finally:
        connection.close()


@app.delete("/deletePedidoInstrumento")
async def eliminar_instrumentos_pedido(data: PedidoInstrumento, response: Response):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            # Validar que el pedido existe
            cursor.execute("SELECT idPedido FROM Pedido WHERE idPedido = %s", (data.idPedido,))
            pedido_existente = cursor.fetchone()
            if not pedido_existente:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": f"Pedido con id {data.idPedido} no encontrado"}

            eliminados = []

            for instrumento in data.instrumentos:
                idInstrumento = instrumento.idInstrumento  
                nombreInstrumento = instrumento.nombreInstrumento  

                if not idInstrumento and nombreInstrumento:
                    cursor.execute("SELECT idInstrumento FROM GInstrumento WHERE Nombre = %s", (nombreInstrumento,))
                    instrumento_grupo = cursor.fetchone()
                    if not instrumento_grupo:
                        response.status_code = status.HTTP_404_NOT_FOUND
                        return {"message": f"Instrumento con nombre '{nombreInstrumento}' no encontrado"}
                    idInstrumentoGrupo = instrumento_grupo[0]

                    cursor.execute("""
                        SELECT idInstrumento FROM Pedido_IInstrumento 
                        WHERE idPedido = %s AND idInstrumento IN (
                            SELECT idInstrumentoIndividual FROM IInstrumento 
                            WHERE idInstrumentoGrupo = %s
                        ) 
                        LIMIT 1
                    """, (data.idPedido, idInstrumentoGrupo))
                    instrumento_pedido = cursor.fetchone()

                    if not instrumento_pedido:
                        response.status_code = status.HTTP_404_NOT_FOUND
                        return {"message": f"No hay instrumentos disponibles en el pedido para '{nombreInstrumento}'"}

                    idInstrumento = instrumento_pedido[0]

                cursor.execute("DELETE FROM Pedido_IInstrumento WHERE idPedido = %s AND idInstrumento = %s",
                               (data.idPedido, idInstrumento))

                eliminados.append(nombreInstrumento if nombreInstrumento else f"ID {idInstrumento}")

            connection.commit()

            respuesta = {
                "message": "Instrumentos eliminados correctamente del pedido",
                "instrumentos_eliminados": eliminados
            }

            return respuesta

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

