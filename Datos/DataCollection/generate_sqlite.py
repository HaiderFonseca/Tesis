import os
import json
import pandas as pd
import sqlite3
from datetime import datetime

def create_database(data_dir):
    # Directorio de datos
    json_file = os.path.join(data_dir, "initial_state.json")
    csv_file = os.path.join(data_dir, "transactions.csv")
    
    # Archivo de base de datos SQLite
    db_file = "enrollment.db"
    if os.path.exists(db_file):
        os.remove(db_file)  # Si existe, elimina el archivo previo
    
    # Conexión a la base de datos
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Crear tablas
    cursor.execute("""
        CREATE TABLE course_enrollment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nrc TEXT NOT NULL,
            enrolled INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE latest_enrollment (
            nrc TEXT PRIMARY KEY,
            enrolled INTEGER NOT NULL,
            timestamp DATETIME NOT NULL
        )
    """)
    
    initial_df = pd.read_json(json_file)
    initial_df = initial_df[~initial_df.duplicated(subset='nrc', keep=False)]

    # Preparar los valores iniciales por NRC
    initial_enrollment = {course["nrc"]: int(course["enrolled"]) for course in initial_df.to_dict(orient='records')}
    
    # Cargar datos de transacciones desde el CSV
    transactions = pd.read_csv(csv_file, parse_dates=['previous_time', 'current_time'], date_format='%Y-%m-%d %H.%M.%S')
    transactions['current_time'] = transactions['current_time'] - pd.Timedelta(hours=5)  # Ajustar a UTC-5

    # Identificar NRCs en transactions_df que no están en initial_df
    nrcs_initial = initial_df['nrc'].unique()
    nrcs_transactions = transactions['nrc'].unique()
    missing_nrcs = set(nrcs_transactions) - set(nrcs_initial)
    # Filtrar transactions_df para eliminar los NRCs que no están en initial_df
    transactions = transactions[~transactions['nrc'].isin(missing_nrcs)]
    # Filtrar initial_df para conservar solo los NRCs que también están en transactions_df
    initial_df = initial_df[initial_df['nrc'].isin(nrcs_transactions)]

    
    # Obtener el timestamp más antiguo del archivo de transacciones
    earliest_timestamp = transactions['current_time'].min()
    
    # Insertar datos iniciales en CourseEnrollment con el timestamp más antiguo
    for nrc, enrolled in initial_enrollment.items():
        # Validar y convertir datos
        enrolled = int(enrolled)  # Asegurarse de que sea un entero
        earliest_timestamp_str = earliest_timestamp.strftime("%Y-%m-%d %H:%M:%S")  # Convertir a cadena

        # Insertar en la tabla
        cursor.execute("""
            INSERT INTO course_enrollment (nrc, enrolled, timestamp)
            VALUES (?, ?, ?)
        """, (nrc, enrolled, earliest_timestamp_str))
    
    # Calcular el acumulado de inscritos
    transactions.sort_values(by=['nrc', 'current_time'], inplace=True)
    transactions['cumulative_enrolled'] = transactions.groupby('nrc')['delta_enrolled'].cumsum()
    
    # Agregar el valor inicial de enrolled para cada NRC
    transactions['initial_enrolled'] = transactions['nrc'].map(initial_enrollment)
    transactions['enrolled'] = transactions['cumulative_enrolled'] + transactions['initial_enrolled']
    
    # Insertar datos en CourseEnrollment
    for _, row in transactions.iterrows():
        # Validar y convertir datos
        nrc = str(row['nrc'])  # Asegurarse de que sea una cadena
        enrolled = int(row['enrolled'])  # Asegurarse de que sea un entero
        timestamp = row['current_time'].strftime("%Y-%m-%d %H:%M:%S")  # Convertir a cadena de texto

        # Insertar en la tabla
        cursor.execute("""
            INSERT INTO course_enrollment (nrc, enrolled, timestamp)
            VALUES (?, ?, ?)
        """, (nrc, enrolled, timestamp))

    # Insertar el último valor en LatestEnrollment
    latest_enrollments = transactions.sort_values(by='current_time').groupby('nrc').last().reset_index()
    for _, row in latest_enrollments.iterrows():
        # Validar y convertir datos
        nrc = str(row['nrc'])  # Asegurarse de que sea una cadena
        cumulative_enrolled = int(row['cumulative_enrolled'])  # Asegurarse de que sea un entero
        timestamp = row['current_time'].strftime("%Y-%m-%d %H:%M:%S")  # Convertir a cadena de texto

        # Insertar en la tabla
        cursor.execute("""
            INSERT INTO latest_enrollment (nrc, enrolled, timestamp)
            VALUES (?, ?, ?)
        """, (nrc, cumulative_enrolled, timestamp))

    
    # Confirmar cambios y cerrar la conexión
    conn.commit()
    conn.close()
    print(f"Base de datos creada exitosamente en {db_file}")

# Uso del script
if __name__ == "__main__":
    dataset_name = "../2024-20"  # Cambia esto al nombre de tu dataset
    create_database(dataset_name)
