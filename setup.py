import mysql.connector, sys
from mysql.connector import errorcode

# --- CONFIGURACIÓN ---
SERVER_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",  # Cambiar si tienes contraseña en XAMPP/WAMP
    "port": 3306
}

DB_NAME = "cafeteria_bd"

TABLA_USERS = """
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    surname VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    birth_date DATE,
    address VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
"""

def inicializar_proyecto():
    """
    Crea la base de datos y las tablas necesarias con manejo de errores avanzado.
    """
    conexion = None
    try:
        # Intentar conectar al servidor MySQL
        print(f"Conectando al servidor MySQL en {SERVER_CONFIG['host']}...")
        conexion = mysql.connector.connect(**SERVER_CONFIG)
        cursor = conexion.cursor()

        # Intentar crear la base de datos
        try:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS {DB_NAME} DEFAULT CHARACTER SET 'utf8'"
            )
            print(f"✅ Base de datos '{DB_NAME}' lista.")
        except mysql.connector.Error as err:
            print(f"❌ Error al crear la base de datos: {err}")
            sys.exit(1)

        # Seleccionar la base de datos
        conexion.database = DB_NAME

        # Crear la tabla de usuarios
        try:
            cursor.execute(TABLA_USERS)
            print("✅ Tabla 'users' verificada/creada exitosamente.")
        except mysql.connector.Error as err:
            print(f"❌ Error al crear la tabla: {err}")
        
        cursor.close()
        print("\n✅ Inicialización completada con éxito.")
        return True

    except mysql.connector.Error as err:
        # Manejo de errores específicos de conexión
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("❌ Error: Usuario o contraseña de MySQL incorrectos.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("❌ Error: La base de datos no existe.")
        else:
            print(f"❌ Error crítico de conexión: {err}")
        return False
    
    finally:
        # Aseguramos que la conexión se cierre siempre
        if conexion and conexion.is_connected():
            conexion.close()

if __name__ == "__main__":
    inicializar_proyecto()