import pymysql
import os
from dotenv import load_dotenv
import psutil
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
from fastapi import HTTPException, status
from typing import Optional, Union

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 10

class TokenData(BaseModel):
    idUsuario: Optional[int] = None
    correo: Optional[str] = None

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# Obtiene las variables de entorno
__host=os.getenv('DB_HOST')
__port=int(os.getenv('DB_PORT',3306))
__user=os.getenv('DB_USER')
__password=os.getenv('DB_PASSWORD')
__db=os.getenv('DB_DB')
__SECRET_KEY=os.getenv('SECRET_KEY')

def create_access_token(data: dict):
    payload = {
        "idUsuario": data.get("idUsuario"),
        "correo": data.get("correo"),
        "rol": data.get("rol"),
        "exp": datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    }
    token = jwt.encode(payload, __SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_token(token: str):
    try:
        payload = jwt.decode(token, __SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("idUsuario")
        correo: str = payload.get("correo")
        if user_id is None or correo is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # Consultar la base de datos para obtener el rol
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT Rol FROM Usuario WHERE idUsuario=%s AND Correo=%s",
                    (user_id, correo)
                )
                result = cursor.fetchone()
                if not result:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Usuario no encontrado",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                rol = result[0]
        finally:
            conn.close()
        return {"idUsuario": user_id, "correo": correo, "rol": rol}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_connection():
    return pymysql.connect(
        host=__host,
        port=__port,
        user=__user,
        password=__password,
        db=__db
    )

def tokenize(rows, description):
    columns = [column[0] for column in description]
    return [dict(zip(columns, row)) for row in rows]

def get_memory_usage():
    """
    Obtiene el uso de memoria del sistema en MB.
    """
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    return memory_info.rss / (1024 * 1024)  # Convertir a MB

def get_memory_usage():
    """
    Obtiene el uso de memoria del sistema en MB.
    """
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    return memory_info.rss / (1024 * 1024)  # Convertir a MB