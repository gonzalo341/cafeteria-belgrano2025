import os, json, base64, logging, mysql.connector
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

# ===== Config =====
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "cafeteria_bd"
}

UPLOAD_FOLDER = os.path.join("static", "uploads")
JSON_FOLDER = os.path.join("static", "json")
REQUEST_JSON_PATH = os.path.join(JSON_FOLDER, "request.json")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(JSON_FOLDER, exist_ok=True)

# ===== Logging =====
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ===== App =====
app = Flask(__name__)

# CORS: permitir el origen del Live Server (127.0.0.1:5500 y localhost:5500)
CORS(app, resources={r"/*": {"origins": ["http://127.0.0.1:5500", "http://localhost:5500"]}})

# ===== Helpers =====
def get_db_connection():
    return mysql.connector.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"],
        autocommit=False
    )

def save_request_json(data):
    try:
        with open(REQUEST_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Wrote request JSON to {REQUEST_JSON_PATH}")
    except Exception as e:
        logger.error(f"Failed to write request JSON: {e}")

def save_profile_picture(pic_obj):
    """
    pic_obj expected: { "filename": "name.jpg", "data": "<base64string>" }
    Returns the public path to saved file (e.g. '/static/uploads/uuid-name.jpg') or None
    """
    if not pic_obj:
        return None
    fname = secure_filename(pic_obj.get("filename", "upload"))
    b64 = pic_obj.get("data")
    if not b64:
        return None
    # crear nombre único
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    name, ext = os.path.splitext(fname)
    if ext == "":
        ext = ".jpg"
    new_fname = f"{name}_{timestamp}{ext}"
    save_path = os.path.join(UPLOAD_FOLDER, new_fname)
    try:
        with open(save_path, "wb") as f:
            f.write(base64.b64decode(b64))
        public_path = f"/static/uploads/{new_fname}"
        logger.info(f"Saved image to {save_path}")
        return public_path
    except Exception as e:
        logger.error(f"Error saving image file: {e}")
        return None

# ===== Request logging =====
@app.before_request
def log_request_info():
    try:
        logger.info(f"{request.remote_addr} - {request.method} {request.path}")
    except Exception:
        pass

# ===== Routes =====
@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json(force=True)
        if data is None:
            return jsonify({"error": "No JSON recibido"}), 400

        # Guardar copia del request JSON
        save_request_json(data)

        name = data.get("name")
        surname = data.get("surname")
        email = data.get("email")
        birthDate = data.get("birthDate")  # puede ser None o ""
        password = data.get("password")
        address = data.get("address")
        profilePictureObj = data.get("profilePicture")

        # Guardar la imagen (si se sube)
        profile_picture_path = save_profile_picture(profilePictureObj) if profilePictureObj else None

        # Insertar en DB
        conn = get_db_connection()
        cursor = conn.cursor()
        insert_sql = """
            INSERT INTO users
            (name, surname, email, birth_date, profile_picture, password, address)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_sql, (
            name,
            surname,
            email,
            birthDate if birthDate else None,
            profile_picture_path,
            password,
            address
        ))
        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"Usuario insertado: {email} - {name} {surname}")
        return jsonify({"message": "Usuario registrado exitosamente"}), 201

    except Exception as e:
        logger.exception("Error en /register")
        return jsonify({"error": "Error al procesar la solicitud", "details": str(e)}), 500

@app.route("/users", methods=["GET"])
def list_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, surname, email, birth_date, profile_picture, address FROM users")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"users": rows}), 200
    except Exception as e:
        logger.exception("Error en /users")
        return jsonify({"error": str(e)}), 500

# Ruta opcional para servir archivos subidos
@app.route("/static/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# ===== Probar conexión al iniciar =====
def test_db_connection():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        _ = cursor.fetchone()
        cursor.close()
        conn.close()
        logger.info("✅ Conexión exitosa a la base de datos")
    except Exception as e:
        logger.error(f"❌ Error de conexión a DB: {e}")

if __name__ == "__main__":
    test_db_connection()
    logger.info("Iniciando servidor en modo debug (sin Waitress) en http://127.0.0.1:5050")
    # En desarrollo usar app.run para facilitar debug; en producción podés volver a waitress
    app.run(host="127.0.0.1", port=5050, debug=True)

