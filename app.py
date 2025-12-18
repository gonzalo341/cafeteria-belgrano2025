from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from db import obtener_conexion_bd, IntegrityError, MENSAJE_ERROR_UNIQUE, MENSAJE_ERROR_CONEXION

app = Flask(__name__)
# Permitimos CORS para que Live Server (puerto 5500) pueda hablar con Flask (5000)
CORS(app)

# --- RUTAS DE NAVEGACIÓN ---

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/order")
def order():
    return render_template("order.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    
    # --- LÓGICA DE REGISTRO (POST) ---
    try:
        # 1. Validación del "No soy un robot"
        if not request.form.get("not_robot"):
            return jsonify({"error": "Debe verificar que no es un robot."}), 400

        # 2. Obtener datos del formulario
        name = request.form.get("name")
        surname = request.form.get("surname")
        email = request.form.get("email")
        password = request.form.get("password")
        birth_date = request.form.get("birthDate") or None
        address = request.form.get("address")

        # 3. Validación de campos obligatorios
        if not all([name, surname, email, password]):
            return jsonify({"error": "Faltan campos obligatorios."}), 400

        # 4. Conexión e Inserción
        conn = obtener_conexion_bd()
        if not conn:
            return jsonify({"error": MENSAJE_ERROR_CONEXION}), 500

        cursor = conn.cursor()
        sql = """
            INSERT INTO users (name, surname, email, password, birth_date, address) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (name, surname, email, password, birth_date, address))
        
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "¡Usuario registrado con éxito!"}), 201

    except IntegrityError as e:
        # El error 1062 es por duplicado (email unique)
        if e.errno == 1062:
            return jsonify({"error": MENSAJE_ERROR_UNIQUE}), 400
        return jsonify({"error": f"Error de base de datos: {str(e)}"}), 500

    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

if __name__ == "__main__":
    # Corremos en localhost, puerto 5000
    app.run(host="127.0.0.1", port=5000, debug=True)