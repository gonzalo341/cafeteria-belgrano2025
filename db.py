import mysql.connector
from mysql.connector import Error, errorcode, IntegrityError
import setup as setup  # Importamos setup.py para autocompletar la BD si falta

# ----------------------------------------------
# Mensajes constantes para mantener el orden
# ----------------------------------------------
MENSAJE_ERROR_CONEXION = "Error: No se pudo conectar con la base de datos."
MENSAJE_ERROR_UNIQUE = "El correo electrónico ya se encuentra registrado."

def obtener_conexion_bd():                  # Intenta conectar a MySQL. Si falla porque la BD no existe, llama a setup.py para crearla.
    config = setup.SERVER_CONFIG.copy()     # Copiamos la config del servidor (user, password, host)
    config["database"] = setup.DB_NAME      # Agregamos el nombre de la BD a la config
    
    try:
        conn = mysql.connector.connect(**config)    # Intento normal de conexión
        return conn
        
    except Error as err:
        # Error 1049: la base de datos no existe. 
        # Si pasa esto, ejecutamos el script de instalación automática.
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            print(f"⚠️ La base de datos '{setup.DB_NAME}' no existe. Intentando crearla...")
            
            # Llamamos a la función de setup.py que crea la BD y las tablas
            if setup.inicializar_bd():
                try:
                    # Reintentamos conectar ahora que la BD existe
                    conn = mysql.connector.connect(**config)
                    print("✅ Conexión establecida tras la creación automática de la BD.")
                    return conn
                except Error as e:
                    print(f"❌ Error al reconectar: {e}")
            else:   # Otros errores (contraseña mal, servidor apagado, etc.)
                print("❌ Falló la autoinstalación.")
        
        return None

# Definimos qué puede importar app.py desde aquí
__all__ = ["obtener_conexion_bd", "IntegrityError", "MENSAJE_ERROR_CONEXION", "MENSAJE_ERROR_UNIQUE"]