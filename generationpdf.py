from jinja2 import Environment, FileSystemLoader
import pdfkit
import pymysql
import credentials

# Conectar a la base de datos
def obtener_datos():
    connection = credentials.get_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Estado actual de los instrumentos
            cursor.execute("SELECT idInstrumento as id, Estado as estado, idCharola as Ubicacion FROM instrumento")
            instrumentos = cursor.fetchall()

            # Historial de instrumentos
            cursor.execute("""
                SELECT i.idInstrumento as id, i.Estado as estado, c.idCharola as Ubicacion
                FROM instrumento i
                JOIN instrumento_has_charola ic ON i.idInstrumento = ic.Instrumento_idInstrumento
                JOIN charola c ON ic.charola_idCharola = c.idCharola
            """)
            historial_instrumentos = cursor.fetchall()

        return {"instrumentos": instrumentos, "historial_instrumentos": historial_instrumentos}
    finally:
        connection.close()

# Generar el PDF
def generar_pdf():
    datos = obtener_datos()
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("reporte.html")
    html_renderizado = template.render(datos)

    # Convertir HTML en PDF
    pdfkit.from_string(html_renderizado, "reporte.pdf")

# Ejecutar la generación de PDF
if __name__ == "__main__":
    generar_pdf()
    print("¡PDF generado correctamente!")