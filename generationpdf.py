import os
import pdfkit
import pymysql
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import credentials

# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
OUTPUT_DIR = os.path.join(BASE_DIR, 'generated_pdfs')

# Configuración de pdfkit
try:
    PDF_CONFIG = pdfkit.configuration()
except Exception as e:
    raise RuntimeError(
        "Requisito faltante: wkhtmltopdf no está instalado.\n"
        "Instalar con: sudo apt install wkhtmltopdf"
    ) from e

# Función para obtener datos de la base de datos
def obtener_datos():
    try:
        connection = credentials.get_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Consulta usuarios actuales
            cursor.execute("""
                SELECT 
                    idUsuario AS id, 
                    Nombre AS nombre,
                    Rol AS rol, 
                    Correo AS correo 
                FROM usuario
            """)
            usuarios = cursor.fetchall()

        return {
            'usuarios': usuarios,
            'fecha_reporte': datetime.now().strftime('%d/%m/%Y %H:%M')
        }
    except pymysql.Error as e:
        print(f"Error MySQL: {e}")
        return None
    finally:
        if connection and connection.open:
            connection.close()

# Función para generar el PDF
def generar_pdf():
    # Verificar plantilla primero
    template_path = os.path.join(TEMPLATES_DIR, 'reporte.html')
    if not os.path.exists(template_path):
        raise FileNotFoundError(
            f"Plantilla no encontrada en: {template_path}\n"
            "Estructura requerida:\n"
            f"{BASE_DIR}/\n"
            "├── templates/\n"
            "│   └── reporte.html\n"
            "└── generated_pdfs/"
        )

    # Obtener datos
    datos = obtener_datos()
    if not datos:
        raise ValueError("No se obtuvieron datos de la base de datos")

    # Generar PDF
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
        template = env.get_template("reporte.html")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(OUTPUT_DIR, f"reporte_usuarios_{timestamp}.pdf")

        options = {
            'page-size': 'A4',
            'margin-top': '15mm',
            'encoding': 'UTF-8',
            'footer-right': '[page]/[topage]',
            'quiet': ''
        }

        pdfkit.from_string(
            template.render(datos),
            output_path,
            configuration=PDF_CONFIG,
            options=options
        )

        print(f"✓ PDF generado exitosamente:\n{output_path}")
        return output_path

    except Exception as e:
        print(f"✗ Error en generación: {str(e)}")
        return None

if __name__ == "__main__":
    generar_pdf()