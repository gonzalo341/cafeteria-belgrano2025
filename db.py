import mysql.connector
from mysql.connector import Error, errorcode, IntegrityError
import setup as setup  # Importamos tu nuevo setup para usar sus funciones

# Mensajes de error centralizados para usar en app.py
MENSAJE_ERROR_CONEXION = "Error: No se pudo conectar con la base de datos."
MENSAJE_ERROR_UNIQUE = "El correo electrónico ya se encuentra registrado."

def obtener_conexion_bd():
    """
    Intenta establecer conexión con la base de datos.
    Si la base de datos no existe, ejecuta el setup automáticamente.
    """
    config = setup.SERVER_CONFIG.copy()
    config["database"] = setup.DB_NAME
    
    try:
        # Intentar la conexión normal
        conn = mysql.connector.connect(**config)
        return conn
        
    except Error as err:
        # Si el error es que la base de datos no existe (Error 1049)
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            print(f"⚠️ La base de datos '{setup.DB_NAME}' no existe. Intentando crearla...")
            
            # Llamamos a la función de tu script de setup
            if setup.inicializar_proyecto():
                try:
                    # Reintentar la conexión después de crear la BD
                    conn = mysql.connector.connect(**config)
                    print("✅ Conexión establecida tras la creación automática de la BD.")
                    return conn
                except Error as e:
                    print(f"❌ Error al reconectar después del setup: {e}")
            else:
                print("❌ No se pudo inicializar la base de datos automáticamente.")
        
        else:
            # Otros errores (contraseña mal, servidor apagado, etc.)
            print(f"❌ Error de base de datos: {err}")
            
        return None

# Definimos qué puede importar app.py desde aquí
__all__ = ["obtener_conexion_bd", "IntegrityError", "MENSAJE_ERROR_CONEXION", "MENSAJE_ERROR_UNIQUE"]