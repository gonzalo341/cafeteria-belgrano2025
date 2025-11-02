import os
import logging
from datetime import datetime
from pathlib import Path
import base64

import mysql.connector
from mysql.connector import Error
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "127.0.0.1"),
    "port": int(os.environ.get("DB_PORT", 3306)),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "cafeteria_bd"),
}

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
PRODUCTION = os.environ.get("PRODUCTION", "False").lower() in ("1", "true", "yes")
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder=str(BASE_DIR / "static"), template_folder=str(BASE_DIR / "templates"))
CORS(app, resources={r"/*": {"origins": ["http://127.0.0.1:5500", "http://localhost:5500"]}})

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            autocommit=False,
        )
        return conn
    except Error as e:
        logger.error("DB connection error: %s", e)
        raise

def allowed_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS

def save_file_storage(file_storage):
    if not file_storage or file_storage.filename == "":
        return None
    filename = secure_filename(file_storage.filename)
    if not allowed_file(filename):
        return None
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    name, ext = os.path.splitext(filename)
    new_name = f"{name}_{timestamp}{ext}"
    save_path = UPLOAD_FOLDER / new_name
    file_storage.save(str(save_path))
    return f"/static/uploads/{new_name}"

def save_profile_picture_from_base64(obj):
    if not obj:
        return None
    filename = secure_filename(obj.get("filename", "upload.jpg"))
    if not allowed_file(filename):
        return None
    b64 = obj.get("data")
    if not b64:
        return None
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    name, ext = os.path.splitext(filename)
    if not ext:
        ext = ".jpg"
    new_name = f"{name}_{timestamp}{ext}"
    save_path = UPLOAD_FOLDER / new_name
    with open(save_path, "wb") as f:
        f.write(base64.b64decode(b64))
    return f"/static/uploads/{new_name}"

@app.route("/", methods=["GET"])
def index():
    return render_template("register.html")

@app.route("/register", methods=["GET"])
def register_form():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register():
    try:
        if request.content_type and request.content_type.startswith("application/json"):
            data = request.get_json(force=True)
            if data is None:
                return jsonify({"error": "JSON inválido"}), 400
            name = data.get("name")
            surname = data.get("surname")
            email = data.get("email")
            birth_date = data.get("birthDate") or None
            password = data.get("password")
            address = data.get("address")
            profile_picture_obj = data.get("profilePicture")
            profile_picture_path = save_profile_picture_from_base64(profile_picture_obj) if profile_picture_obj else None
        else:
            form = request.form
            name = form.get("name")
            surname = form.get("surname")
            email = form.get("email")
            birth_date = form.get("birthDate") or None
            password = form.get("password")
            address = form.get("address")
            file = request.files.get("profilePicture") or None
            profile_picture_path = save_file_storage(file) if file else None

        if not name or not surname or not email or not password:
            return jsonify({"error": "Campos obligatorios faltantes (name, surname, email, password)."}), 400

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()
        insert_sql = """
            INSERT INTO users
            (name, surname, email, birth_date, profile_picture, password, address, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        created_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        params = (name, surname, email, birth_date, profile_picture_path, hashed_password, address, created_at)
        cursor.execute(insert_sql, params)
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Usuario insertado: %s %s (%s)", name, surname, email)
        return jsonify({"message": "Usuario registrado exitosamente."}), 201

    except mysql.connector.IntegrityError as ie:
        logger.exception("IntegrityError en /register")
        return jsonify({"error": "Error de integridad en la base de datos.", "details": str(ie)}), 400

    except Exception as e:
        logger.exception("Error en /register")
        return jsonify({"error": "Error interno al procesar la solicitud.", "details": str(e)}), 500

@app.route("/static/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(str(UPLOAD_FOLDER), filename)

if __name__ == "__main__":
    try:
        conn_test = get_db_connection()
        conn_test.close()
        logger.info("Conexión a DB OK")
    except Exception as e:
        logger.error("No se pudo conectar a la DB: %s", e)
    if PRODUCTION:
        from waitress import serve
        serve(app, host="0.0.0.0", port=5050)
    else:
        app.run(host="127.0.0.1", port=5050, debug=True)
