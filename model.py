import pandas as pd
import json
import pandas as pd
import numpy as np
from sksurv.preprocessing import OneHotEncoder
from sksurv.linear_model import CoxPHSurvivalAnalysis, CoxnetSurvivalAnalysis, IPCRidge
from sksurv.ensemble import RandomSurvivalForest, ExtraSurvivalTrees, GradientBoostingSurvivalAnalysis
from sksurv.metrics import concordance_index_censored
from sklearn.preprocessing import StandardScaler
from sksurv.svm import FastSurvivalSVM
import matplotlib.pyplot as plt

# Función para crear intervalos de 30 minutos y asignar 1 o 0 en función de todos los horarios del curso
def create_time_bins(schedules):
    bins = np.zeros(48)  # 48 intervalos de 30 minutos en un día (24 horas * 2)
    
    # Iterar sobre todas las entradas en la lista de horarios
    for schedule in schedules:
        if schedule['time_ini'] is None or schedule['time_fin'] is None:
            # Si no hay tiempo de inicio o fin, ignorar esta entrada
            continue

        # Convertir time_ini y time_fin a minutos
        time_ini = int(schedule['time_ini'][:2]) * 60 + int(schedule['time_ini'][2:])  # Convertir a minutos
        time_fin = int(schedule['time_fin'][:2]) * 60 + int(schedule['time_fin'][2:])  # Convertir a minutos
        
        # Marcar los intervalos de 30 minutos correspondientes
        for i in range(48):  # Cada intervalo representa 30 minutos
            interval_start = i * 30
            interval_end = (i + 1) * 30
            # Comprobar si el curso se solapa con el bin en cualquier punto
            if not (time_fin <= interval_start or time_ini >= interval_end):
                bins[i] = 1
    return bins

    
#ESTO ESTÁ EN EL DASHBOARD
# # Extraer datos adicionales desde initial_df
# schedules = initial_df.loc[initial_df['nrc'] == nrc, 'schedules'].values[0]
# course = initial_df.loc[initial_df['nrc'] == nrc, 'course'].values[0]
# course_level = int(str(course)[0])  # Tomar el primer número como el nivel del curso
# course_class = initial_df.loc[initial_df['nrc'] == nrc, 'class'].values[0]
# ptrmdesc = initial_df.loc[initial_df['nrc'] == nrc, 'ptrmdesc'].values[0]

# Crear los time_bins para la hora
time_bins = create_time_bins(schedules)

# Extraer los días de la semana
days_of_week = set(day for data in schedules for day in ['l', 'm', 'i', 'j', 'v', 's', 'd'] if data.get(day))

#-----------------------------

# Codificar los días de la semana como variables categóricas
days_expanded = result_df['days_of_week'].apply(lambda x: list(x)).explode()
days_one_hot = pd.get_dummies(days_expanded).groupby(level=0).sum()

# Crear etiquetas descriptivas para los intervalos de tiempo (30 minutos cada uno)
interval_labels = [f'{i//2:02}:{(i%2)*30:02}-{(i//2):02}:{((i%2)+1)*30:02}' for i in range(48)]

# Expandir los time_bins y crear un DataFrame con las etiquetas de tiempo
time_bins_expanded = pd.DataFrame(result_df['time_bins'].tolist(), columns=interval_labels)

# Eliminar las columnas que contienen solo ceros
time_bins_expanded = time_bins_expanded.loc[:, (time_bins_expanded != 0).any(axis=0)]

# Añadir las columnas codificadas al DataFrame original
result_df = result_df.join(days_one_hot)
result_df = result_df.join(time_bins_expanded)


# Codificar las variables categóricas ('class', 'ptrmdesc')
encoder_class = OneHotEncoder()  # Cambiado 'sparse_output' por 'sparse'
class_encoded = encoder_class.fit_transform(result_df[['course_class']])

encoder_ptrmdesc = OneHotEncoder()  # Cambiado 'sparse_output' por 'sparse'
ptrmdesc_encoded = encoder_ptrmdesc.fit_transform(result_df[['ptrmdesc']])

# Crear la matriz de características (X) uniendo todas las variables: 
# horas, días de la semana, clase, ciclo, y nivel
X = np.hstack([
    time_bins_expanded.values,       # Hora (intervalos de 30 minutos)
    days_one_hot.values,             # Días de la semana
    class_encoded,                   # Clase (codificada)
    ptrmdesc_encoded,                # Ciclo (codificado)
    result_df[['course_level']].values  # Nivel del curso
])
# El scaler se lee de un archivo
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)


model=RandomSurvivalForest()
#Se asume que se carga el modelo de un archivo
model.predict(X_scaled)