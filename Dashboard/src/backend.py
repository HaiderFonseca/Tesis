from flask import Flask, jsonify, request, Blueprint
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import requests
import threading
import time
from datetime import datetime
from collections import Counter

print("Loading backend...")

# Cargar variables de entorno
load_dotenv()
API_URL = os.getenv("API_URL")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL"))
POLLING_ENABLED = os.getenv("POLLING_ENABLED", "true").lower() in ["true", "1", "yes"]

# Configuración de Flask y SQLite
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///enrollment.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Crear un Blueprint para el API
api_blueprint = Blueprint("api", __name__, url_prefix="/api")

# Modelo para el historial completo de cambios
class CourseEnrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Clave primaria
    nrc = db.Column(db.String(20), nullable=False)
    enrolled = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Tabla materializada para el último valor por nrc
class LatestEnrollment(db.Model):
    nrc = db.Column(db.String(20), primary_key=True)  # Clave única por nrc
    enrolled = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

# Crear las tablas
with app.app_context():
    db.create_all()

# Función para consultar la API periódicamente
def poll_api():
    while True:
        try:
            response = requests.get(API_URL)
            if response.status_code == 200:
                courses = response.json()

                # Usar contexto de aplicación para trabajar con la base de datos
                with app.app_context():
                    save_to_db_if_changed(courses)

            time.sleep(POLL_INTERVAL)
        except Exception as e:
            print(f"Error polling API: {e}")

# Guardar los datos solo si han cambiado
def save_to_db_if_changed(current_courses):
    # Obtener los últimos registros desde la tabla materializada
    latest_records = get_latest_records()

    # Eliminar valores duplicados en current_courses
    # Primero contar y luego eliminar TODOS los que tengan más de 1
    counter = Counter([course['nrc'] for course in current_courses])
    duplicates = [nrc for nrc, count in counter.items() if count > 1]
    current_courses = [course for course in current_courses if course['nrc'] not in duplicates]

    # Comparar los datos actuales con los registros más recientes
    changes = []
    for course in current_courses:
        nrc = course['nrc']
        enrolled = int(course['enrolled'])

        # Verificar si hay cambios
        if nrc not in latest_records or latest_records[nrc]['enrolled'] != enrolled:
            changes.append(CourseEnrollment(nrc=nrc, enrolled=enrolled))

    # Guardar los nuevos registros en el historial
    if changes:
        db.session.add_all(changes)
        db.session.commit()

        # Actualizar la tabla materializada
        update_latest_enrollment(changes)
        print(f"Saved {len(changes)} changes at {datetime.utcnow()}")
    else:
        print("No changes detected at", datetime.utcnow())

# Actualizar la tabla materializada
def update_latest_enrollment(new_courses):
    for course in new_courses:
        # Buscar si el curso ya existe en la tabla materializada
        existing = LatestEnrollment.query.filter_by(nrc=course.nrc).first()

        if not existing:
            # Si no existe, añadir un nuevo registro
            new_entry = LatestEnrollment(
                nrc=course.nrc,
                enrolled=course.enrolled,
                timestamp=course.timestamp
            )
            db.session.add(new_entry)
        elif existing.timestamp < course.timestamp:
            # Si existe pero el timestamp es más antiguo, actualizar
            existing.enrolled = course.enrolled
            existing.timestamp = course.timestamp

    # Confirmar los cambios
    db.session.commit()

# Obtener los últimos registros desde la tabla materializada
def get_latest_records():
    latest_records = LatestEnrollment.query.all()
    # Convertir a un diccionario {nrc: {enrolled, timestamp}}
    return {record.nrc: {'enrolled': record.enrolled, 'timestamp': record.timestamp} for record in latest_records}

@api_blueprint.route('/history/<nrc>', methods=['GET'])
def get_course_history(nrc):
    # Obtener el historial completo de un curso
    courses = CourseEnrollment.query.filter_by(nrc=nrc).order_by(CourseEnrollment.timestamp).all()
    if not courses:
        return jsonify({"message": "No history found"}), 404
    history = [{"timestamp": c.timestamp, "enrolled": c.enrolled} for c in courses]
    return jsonify(history)

@api_blueprint.route('/latest/<nrc>', methods=['GET'])
def get_latest_course(nrc):
    # Obtener el último registro desde la tabla materializada
    latest = LatestEnrollment.query.filter_by(nrc=nrc).first()
    if not latest:
        return jsonify({"message": "Course not found"}), 404
    return jsonify({
        "nrc": latest.nrc,
        "enrolled": latest.enrolled,
        "timestamp": latest.timestamp
    })

# Registrar el Blueprint del API
app.register_blueprint(api_blueprint)

# Crear un evento para controlar si el hilo ya está en ejecución
if POLLING_ENABLED:
    polling_started = threading.Event()

    # Iniciar el hilo del polling solo si no está en ejecución
    if not polling_started.is_set():
        polling_thread = threading.Thread(target=poll_api, daemon=True)
        polling_thread.start()
        polling_started.set()

