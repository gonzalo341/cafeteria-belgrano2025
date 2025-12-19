from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from db import obtener_conexion_bd, IntegrityError, MENSAJE_ERROR_UNIQUE, MENSAJE_ERROR_CONEXION

app = Flask(__name__)
CORS(app)           # CORS permite que el navegador (puerto 5500 o Live Server) se comunique con Flask (puerto 5000)

# ----------------------------------------------
#              Rutas de navegación
# ----------------------------------------------
@app.route("/")
def index(): return render_template("index.html")

@app.route("/about")
def about(): return render_template("about.html")

@app.route("/order")
def order(): return render_template("order.html")

# ----------------------------------------------
#           Ruta de API para registro
# ----------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    
    try:
        # ----------------------------------------------
        #       Validación del "No soy un robot"
        # ----------------------------------------------
        if not request.form.get("not_robot"):
            return jsonify({"error": "Debe verificar que no es un robot."}), 400

        # ----------------------------------------------
        #       Obtención de datos del formulario
        # ----------------------------------------------
        name = request.form.get("name")
        surname = request.form.get("surname")
        email = request.form.get("email")
        password = request.form.get("password")
        birth_date = request.form.get("birthDate") or None
        address = request.form.get("address")

        # ----------------------------------------------
        #       Validación de campos obligatorios
        # ----------------------------------------------
        if not all([name, surname, email, password]):
            return jsonify({"error": "Faltan campos obligatorios."}), 400

        # ----------------------------------------------
        #           Conexión a la Base de Datos
        # ----------------------------------------------
        conn = obtener_conexion_bd()        # Función importada de db.py
        if not conn:
            return jsonify({"error": MENSAJE_ERROR_CONEXION}), 500

        cursor = conn.cursor()              # Creamos un "cursor": es como un puntero que nos permite ejecutar comandos SQL
        sql = """INSERT INTO users (name, surname, email, password, birth_date, address) 
                VALUES (%s, %s, %s, %s, %s, %s)"""
        # Ejecutamos la orden enviando las variables
        cursor.execute(sql, (name, surname, email, password, birth_date, address))
        
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "¡Usuario registrado con éxito!"}), 201

    except IntegrityError as e:
        if e.errno == 1062:                 # El error 1062 en MySQL significa "Entrada duplicada" (el email ya existe)
            return jsonify({"error": MENSAJE_ERROR_UNIQUE}), 400
        return jsonify({"error": f"Error de base de datos: {str(e)}"}), 500
    
    except Exception as e:                  # Captura cualquier otro error inesperado
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)