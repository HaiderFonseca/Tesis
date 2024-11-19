import os
import glob
import pandas as pd

def combine_csv_files(input_folder, output_csv):
    # Obtener la lista de archivos CSV en la carpeta 'results'
    csv_files = glob.glob(os.path.join(input_folder, '*.csv'))

    # Ordenar la lista de archivos CSV por nombre (fecha y hora)
    csv_files.sort()
    
    # Listas para almacenar datos y tiempos
    data_rows = []
    all_times = []

    # Recorrer todos los archivos CSV, excepto 'courses_202410.json'
    for csv_file in csv_files:
        # Leer el archivo CSV y agregar los datos a la lista
        df = pd.read_csv(csv_file, names=['nrc', 'delta_enrolled'])
        
        # Obtener la 'current_time' del nombre del archivo
        current_time = os.path.splitext(os.path.basename(csv_file))[0]
        
        # Obtener la 'previous_time' del nombre del archivo anterior
        previous_time = all_times[-1] if len(all_times) else None
        
        # Añadir la 'current_time' a la lista de tiempos
        all_times.append(current_time)
        
        # Añadir cada fila a la lista de datos
        for _, row in df.iterrows():
            data_rows.append([previous_time, current_time, row['nrc'], row['delta_enrolled']])

    # Crear DataFrame a partir de la lista de datos
    combined_df = pd.DataFrame(data_rows, columns=['previous_time', 'current_time', 'nrc', 'delta_enrolled'])
    
    # Guardar el DataFrame combinado en un nuevo archivo CSV
    combined_df.to_csv(output_csv, index=False)

    # Crear un archivo CSV adicional con una única columna 'times'
    times_df = pd.DataFrame({'times': all_times})
    times_df.to_csv('all_times.csv', index=False)

if __name__ == "__main__":
    combine_csv_files("results", "output.csv")
