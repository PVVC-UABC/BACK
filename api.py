import os
import io
import pdfkit
import pymysql
from jinja2 import Environment, FileSystemLoader
from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
import utils
from hashlib import sha256
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


ACCESS_TOKEN_EXPIRE_DAYS = 10

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

class login(BaseModel):
    Correo: str
    Contrasena: str

class GInstrumento(BaseModel):
    CodigoDeBarras: str
    Cantidad: int
    Nombre: str

class UpdateGInstrumento(BaseModel):
    idInstrumento: int
    nuevaCantidad: int  

class Equipo(BaseModel):
    idEquipo: int | None = None  
    Nombre: str

class EquipoInstrumento(BaseModel):
    idEquipo: int
    herramientas: list[dict]


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

# Configuración de pdfkit
try:
    PDF_CONFIG = pdfkit.configuration()
except Exception as e:
    raise RuntimeError(
        "Requisito faltante: wkhtmltopdf no está instalado.\n"
        "Instalar con: sudo apt install wkhtmltopdf"
    ) from e

def obtener_datos(id_instrumento: Optional[int] = None):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            # Estado actual de todos los instrumentos y su ubicación
            cursor.execute("""
                SELECT idInstrumentoIndividual AS id, Estado, Ubicacion, ultimaEsterilizacion
                FROM IInstrumento
            """)
            estado_instrumentos = cursor.fetchall()

            # Historial de un instrumento específico (si se proporciona un ID)
            historial_instrumento = []
            if id_instrumento:
                cursor.execute("""
                    SELECT hi.Nombre, hi.CodigoDeBarras, hi.tipoCambio, hi.observaciones, hi.fechaCambio, 
                           CONCAT(u.Nombres, ' ', u.ApellidoPaterno, ' ', COALESCE(u.ApellidoMaterno, '')) AS usuario
                    FROM Historial_GInstrumento hi
                    JOIN Usuario u ON hi.idUsuario = u.idUsuario
                    WHERE hi.idInstrumento = %s
                    ORDER BY hi.fechaCambio DESC
                """, (id_instrumento,))
                historial_instrumento = cursor.fetchall()

            # Historial de todos los instrumentos
            cursor.execute("""
                SELECT hi.Nombre, hi.CodigoDeBarras, hi.tipoCambio, hi.observaciones, hi.fechaCambio, 
                       CONCAT(u.Nombres, ' ', u.ApellidoPaterno, ' ', COALESCE(u.ApellidoMaterno, '')) AS usuario
                FROM Historial_GInstrumento hi
                JOIN Usuario u ON hi.idUsuario = u.idUsuario
                ORDER BY hi.fechaCambio DESC
            """)
            historial_todos = cursor.fetchall()

        return {
            "estado_instrumentos": estado_instrumentos,
            "historial_instrumento": historial_instrumento,
            "historial_todos": historial_todos,
            "fecha_reporte": datetime.now().strftime("%d/%m/%Y %H:%M"),
        }
    except pymysql.Error as e:
        print(f"Error MySQL: {e}")
        return None
    finally:
        connection.close()

# Función para generar el PDF en memoria
def generar_pdf(id_instrumento: Optional[int] = None):
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    template = env.get_template("reporte.html")

    datos = obtener_datos(id_instrumento)
    if not datos:
        raise HTTPException(status_code=500, detail="No se obtuvieron datos de la base de datos")

    pdf_options = {
        "page-size": "A4",
        "margin-top": "15mm",
        "encoding": "UTF-8",
        "footer-right": "[page]/[topage]",
        "quiet": "",
    }

    pdf_bytes = pdfkit.from_string(template.render(datos), False, configuration=PDF_CONFIG, options=pdf_options)

    return io.BytesIO(pdf_bytes)

# Endpoint para obtener el PDF con historial opcional de un instrumento específico
@app.get("/getPdf")
async def descargar_pdf(id_instrumento: Optional[int] = None):
    pdf_file = generar_pdf(id_instrumento)
    return StreamingResponse(pdf_file, media_type="application/pdf",
                             headers={"Content-Disposition": "inline; filename=Reporte_Instrumentos.pdf"})




def verificar_disponibilidad(id: int, fecha: str):
    connection = utils.get_connection()
    try:
        with connection.cursor() as cursor:
            fecha_base = datetime.strptime(fecha, "%Y-%m-%d %H:%M")
            rango_inicio = fecha_base - timedelta(hours=6)
            rango_fin = fecha_base + timedelta(hours=6)

            # Verifica si el instrumento tuvo una esterilización en el rango de 6 horas
            consulta = """
                SELECT COUNT(*) AS existe FROM IInstrumento
                WHERE idInstrumentoIndividual= %s
                AND ultimaEsterilizacion BETWEEN %s AND %s
            """
            cursor.execute(consulta, (id, rango_inicio.strftime("%Y-%m-%d %H:%M"), rango_fin.strftime("%Y-%m-%d %H:%M")))
            resultado = cursor.fetchone()

            return resultado["existe"] == 0  # `True` si está disponible, `False` si hay traslape

    except pymysql.Error as e:
        print(f"Error en BD: {e}")
        return None
    finally:
        connection.close()

@app.get("/verificar-disponibilidad/{id}/{fecha}")
async def verificar(id: int, fecha: str):
    disponible = verificar_disponibilidad(id, fecha)

    if disponible is None:
        raise HTTPException(status_code=500, detail="Error en la consulta a la BD")

    return {"id": id, "fecha": fecha, "disponible": disponible}

@app.get("/login")
async def root(response: Response, login: login):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            hashed_password = sha256(login.Contrasena.encode()).hexdigest()
            cursor.execute("SELECT * FROM Usuario WHERE Correo = %s AND Contrasena = %s", (login.Correo, hashed_password))
            result = cursor.fetchall()
            if not result:
                response.status_code = status.HTTP_401_UNAUTHORIZED
                return {"message": "Usuario o contraseña incorrectos"}
            access_token = utils.create_access_token(
                data={"idUsuario": result[0][0], "correo": result[0][5]},
                expires_delta=timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
            )
            return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        error = "Error: " + str(e)
        return error
    finally:
        connection.close()

@app.get("/protectedAdmin")
async def root(response: Response, token: str = Depends(oauth2_scheme)):
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
async def root(response: Response, token: str = Depends(oauth2_scheme)):
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
async def root(response: Response, token: str = Depends(oauth2_scheme)):
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

@app.post("/postGInstrumento")
async def crear_ginstrumento(grupo: GInstrumento, response: Response, token: str = Depends(oauth2_scheme)):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            payload = utils.verify_token(token)
            if payload["rol"] != "Administrador":
                response.status_code = status.HTTP_403_FORBIDDEN
                return {"message": "No tienes permiso para acceder a esta ruta"}
            cursor.execute("SET @idUsuario = %s", (payload["idUsuario"]))

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



@app.put("/updateGInstrumento")
async def actualizar_ginstrumento(update: UpdateGInstrumento, response: Response, token: str = Depends(oauth2_scheme)):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            payload = utils.verify_token(token)
            if payload["rol"] != "Administrador":
                response.status_code = status.HTTP_403_FORBIDDEN
                return {"message": "No tienes permiso para acceder a esta ruta"}
            cursor.execute("SET @idUsuario = %s", (payload["idUsuario"]))

            cursor.execute("SELECT Cantidad FROM GInstrumento WHERE idInstrumento = %s", (update.idInstrumento,))
            grupo = cursor.fetchone()
            if not grupo:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "Grupo de instrumentos no encontrado"}
            
            cantidad_actual = grupo[0]
            diferencia = update.nuevaCantidad - cantidad_actual

            if diferencia > 0: 
                for _ in range(diferencia):
                    cursor.execute("""
                        INSERT INTO IInstrumento (idInstrumentoGrupo, Estado, Ubicacion, ultimaEsterilizacion)
                        VALUES (%s, %s, %s, NOW())
                    """, (update.idInstrumento, "Disponible", "Almacén"))
            
            elif diferencia < 0:  
                cantidad_a_eliminar = abs(diferencia)
                cursor.execute("""
                    SELECT idInstrumentoIndividual FROM IInstrumento 
                    WHERE idInstrumentoGrupo = %s AND Estado = 'Disponible' LIMIT %s
                """, (update.idInstrumento, cantidad_a_eliminar))
                
                instrumentos_disponibles = cursor.fetchall()
                if len(instrumentos_disponibles) < cantidad_a_eliminar:
                    response.status_code = status.HTTP_400_BAD_REQUEST
                    return {"message": "No hay suficientes instrumentos disponibles para eliminar"}
                
                for instrumento in instrumentos_disponibles:
                    cursor.execute("DELETE FROM IInstrumento WHERE idInstrumentoIndividual = %s", (instrumento[0],))
            
            cursor.execute("UPDATE GInstrumento SET Cantidad = %s WHERE idInstrumento = %s", (update.nuevaCantidad, update.idInstrumento))
            connection.commit()
            return {"message": "Grupo de instrumentos actualizado correctamente"}
    
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}
    
    finally:
        connection.close()

@app.post("/postEquipo")
async def crear_equipo(equipo: Equipo, response: Response, token: str = Depends(oauth2_scheme)):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            payload = utils.verify_token(token)
            if payload["rol"] != "Administrador":
                response.status_code = status.HTTP_403_FORBIDDEN
                return {"message": "No tienes permiso para acceder a esta ruta"}
            cursor.execute("SET @idUsuario = %s", (payload["idUsuario"]))
            cursor.execute("INSERT INTO Equipo (Nombre) VALUES (%s)", (equipo.Nombre,))
            connection.commit()
            return {"message": "Equipo registrado correctamente"}
    
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}
    
    finally:
        connection.close()

@app.put("/updateEquipo")
async def actualizar_equipo(equipo: Equipo, response: Response, token: str = Depends(oauth2_scheme)):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            payload = utils.verify_token(token)
            if payload["rol"] != "Administrador":
                response.status_code = status.HTTP_403_FORBIDDEN
                return {"message": "No tienes permiso para acceder a esta ruta"}
            cursor.execute("SET @idUsuario = %s", (payload["idUsuario"]))
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

@app.delete("/deleteEquipo")
async def eliminar_equipo(data: dict, response: Response, token: str = Depends(oauth2_scheme)):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            payload = utils.verify_token(token)
            if payload["rol"] != "Administrador":
                response.status_code = status.HTTP_403_FORBIDDEN
                return {"message": "No tienes permiso para acceder a esta ruta"}
            cursor.execute("SET @idUsuario = %s", (payload["idUsuario"]))

            idEquipo = data.get("idEquipo")

            if not idEquipo:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return {"message": "Falta el parámetro 'idEquipo' en el JSON"}

            cursor.execute("SELECT * FROM Equipo WHERE idEquipo = %s", (idEquipo,))
            existe = cursor.fetchone()

            if not existe:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "Equipo no encontrado"}

            # ✅ Primero eliminar todas las herramientas asociadas en `Equipo_Instrumento`
            cursor.execute("DELETE FROM Equipo_Instrumento WHERE idEquipo = %s", (idEquipo,))

            # ✅ Ahora eliminar el equipo en `Equipo`
            cursor.execute("DELETE FROM Equipo WHERE idEquipo = %s", (idEquipo,))

            connection.commit()
            return {"message": "Equipo y sus herramientas asociadas eliminados correctamente"}

    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}

    finally:
        connection.close()

@app.post("/postEquipoInstrumento")
async def agregar_herramientas_equipo(data: EquipoInstrumento, response: Response, token: str = Depends(oauth2_scheme)):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            payload = utils.verify_token(token)
            if payload["rol"] != "Administrador":
                response.status_code = status.HTTP_403_FORBIDDEN
                return {"message": "No tienes permiso para acceder a esta ruta"}

            cursor.execute("SET @idUsuario = %s", (payload["idUsuario"]))

            idEquipo = data.idEquipo

            cursor.execute("SELECT idEquipo FROM Equipo WHERE idEquipo = %s", (idEquipo,))
            equipo_existente = cursor.fetchone()
            if not equipo_existente:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": f"Equipo con id {idEquipo} no encontrado"}

            for herramienta in data.herramientas:
                idInstrumento = herramienta["idInstrumento"]
                cantidad = herramienta["cantidad"]

                cursor.execute("SELECT Cantidad FROM GInstrumento WHERE idInstrumento = %s", (idInstrumento,))
                instrumento_existente = cursor.fetchone()
                if not instrumento_existente:
                    response.status_code = status.HTTP_404_NOT_FOUND
                    return {"message": f"Instrumento con id {idInstrumento} no encontrado"}

                cantidad_disponible = instrumento_existente[0]
                cantidad_final = min(cantidad, cantidad_disponible)

                cursor.execute("SELECT cantidad FROM Equipo_Instrumento WHERE idEquipo = %s AND idInstrumento = %s", 
                               (idEquipo, idInstrumento))
                instrumento_equipo = cursor.fetchone()

                if instrumento_equipo:
                    nueva_cantidad = min(instrumento_equipo[0] + cantidad_final, cantidad_disponible)
                    cursor.execute("""
                        UPDATE Equipo_Instrumento SET cantidad = %s WHERE idEquipo = %s AND idInstrumento = %s
                    """, (nueva_cantidad, idEquipo, idInstrumento))
                else:
                    cursor.execute("""
                        INSERT INTO Equipo_Instrumento (idEquipo, idInstrumento, cantidad)
                        VALUES (%s, %s, %s)
                    """, (idEquipo, idInstrumento, cantidad_final))

            connection.commit()
            return {"message": "Herramientas agregadas correctamente al equipo"}

    except pymysql.err.IntegrityError as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": f"Error de clave foránea: {str(e)}"}

    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}

    finally:
        connection.close()

@app.put("/updateEquipoInstrumento")
async def actualizar_herramientas_equipo(data: EquipoInstrumento, response: Response, token: str = Depends(oauth2_scheme)):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:

            payload = utils.verify_token(token)
            if payload["rol"] != "Administrador":
                response.status_code = status.HTTP_403_FORBIDDEN
                return {"message": "No tienes permiso para acceder a esta ruta"}
            cursor.execute("SET @idUsuario = %s", (payload["idUsuario"]))
            idEquipo = data.idEquipo

            cursor.execute("SELECT idEquipo FROM Equipo WHERE idEquipo = %s", (idEquipo,))
            equipo_existente = cursor.fetchone()
            if not equipo_existente:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "Equipo no encontrado"}

            for herramienta in data.herramientas:
                idInstrumento = herramienta["idInstrumento"]
                cantidad = herramienta["cantidad"]

                cursor.execute("SELECT cantidad FROM Equipo_Instrumento WHERE idEquipo = %s AND idInstrumento = %s",
                               (idEquipo, idInstrumento))
                instrumento_equipo = cursor.fetchone()
                if not instrumento_equipo:
                    response.status_code = status.HTTP_404_NOT_FOUND
                    return {"message": f"Instrumento con id {idInstrumento} no está en el equipo"}

                cursor.execute("SELECT Cantidad FROM GInstrumento WHERE idInstrumento = %s", (idInstrumento,))
                instrumento_existente = cursor.fetchone()
                cantidad_disponible = instrumento_existente[0]

                cantidad_final = min(cantidad, cantidad_disponible)

                cursor.execute("""
                    UPDATE Equipo_Instrumento SET cantidad = %s WHERE idEquipo = %s AND idInstrumento = %s
                """, (cantidad_final, idEquipo, idInstrumento))

            connection.commit()
            return {"message": "Cantidad de herramientas modificada correctamente"}

    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}

    finally:
        connection.close()


@app.delete("/deleteEquipoInstrumento")
async def eliminar_herramientas_equipo(data: EquipoInstrumento, response: Response, token: str = Depends(oauth2_scheme)):
    try:
        connection = utils.get_connection()
        with connection.cursor() as cursor:
            payload = utils.verify_token(token)
            if payload["rol"] != "Administrador":
                response.status_code = status.HTTP_403_FORBIDDEN
                return {"message": "No tienes permiso para acceder a esta ruta"}
            cursor.execute("SET @idUsuario = %s", (payload["idUsuario"]))

            idEquipo = data.idEquipo

            cursor.execute("SELECT idEquipo FROM Equipo WHERE idEquipo = %s", (idEquipo,))
            equipo_existente = cursor.fetchone()
            if not equipo_existente:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "Equipo no encontrado"}

            for herramienta in data.herramientas:
                idInstrumento = herramienta["idInstrumento"]

                cursor.execute("SELECT cantidad FROM Equipo_Instrumento WHERE idEquipo = %s AND idInstrumento = %s",
                               (idEquipo, idInstrumento))
                instrumento_equipo = cursor.fetchone()
                if not instrumento_equipo:
                    response.status_code = status.HTTP_404_NOT_FOUND
                    return {"message": f"Instrumento con id {idInstrumento} no está en el equipo"}

                cursor.execute("""
                    DELETE FROM Equipo_Instrumento WHERE idEquipo = %s AND idInstrumento = %s
                """, (idEquipo, idInstrumento))

            connection.commit()
            return {"message": "Herramientas eliminadas del equipo correctamente"}

    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}

    finally:
        connection.close()

