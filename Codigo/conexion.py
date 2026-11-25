import mysql.connector

conexion = None
cursor = None

try:
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="eclipse_ordenes"
    )
    # Con autocommit cada consulta ve los datos más recientes
    # (sin él, los SELECT se quedan con una "foto" vieja de la base de datos)
    conexion.autocommit = True
    cursor = conexion.cursor(buffered=True)
except Exception as e:
    print(f"Error de conexión: {e}")


def deshacer():
    # Deshace la transacción actual sin tronar si la conexión ya no existe
    try:
        conexion.rollback()
    except Exception:
        pass
