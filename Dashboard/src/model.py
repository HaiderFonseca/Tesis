import numpy as np
import pandas as pd
import pickle
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import StandardScaler
from sksurv.ensemble import RandomSurvivalForest


# Codificación fija para variables categóricas
class_categories = ['MATE', 'IIND', 'ECON', 'DERE', 'CPOL', 'ISIS', 'FISI', 'ANTR', 'ADMI', 'BIOL', 'PSIC', 'LENG', 'CHNA', 'MBIO', 'QUIM', 'IMEC', 'IELE', 'FILO', 'ICYA', 'MEDI', 'PSCL', 'MUSI', 'CBIO', 'DDER', 'MLIT', 'IBIO', 'CIDE', 'HIST', 'ARTI', 'EGOB', 'LITE', 'MPER', 'MSIN', 'GEOC', 'SPUB', 'DECA', 'MBIT', 'EDUC', 'STRA', 'CISO', 'HDIG', 'MHAR', 'MPAZ', 'MART', 'MINE', 'ARTE', 'INTL', 'MFIN', 'EPID', 'MGPU', 'CBCC', 'CBCO', 'CBPC', 'CBCA', 'FARH', 'CPER', 'DEIN', 'EPAH', 'MECU', 'CONT', 'DISO', 'DADM', 'MGEO', 'IDOC', 'ARQT', 'MIIA', 'ESCR', 'PSIQ', 'PMED', 'ARQU', 'DGIT', 'EMAT', 'DLIT', 'MDER', 'MISW', 'GLOB', 'DGGJ', 'MECA', 'DPRO', 'MDIS', 'MPCU', 'IQYA', 'MMER', 'PSIG', 'BCOM', 'FCIE', 'SOCI', 'MIMC', 'HART', 'BIOE', 'EECO', 'EMBA', 'GEST', 'MCLA', 'MGAD', 'MMBA', 'MSCM', 'PATO', 'MGAP', 'DCOM', 'DEMP', 'DENI', 'DEPI', 'DEPR', 'DPUB', 'DPUC', 'EPEM', 'ETRI', 'GPUB', 'LEGI', 'MADM', 'MGIT', 'MGLO', 'MGPA', 'MGPD', 'MIAD', 'MIFI', 'MMUS', 'MTRI', 'PEDI', 'DCHO', 'MAIA', 'IING', 'MINT']  # Categorías predefinidas para 'course_class'
ptrmdesc_categories = ['CURSOS MEDICINA - 21 SEMANAS',
 'PERIODO 202420 - 16 SEMANAS',
 'PERIODO NO RETIRABLE',
 'PRIMER CICLO - 8 SEMANAS',
 'SEGUNDO CICLO - 8 SEMANAS']  # Categorías predefinidas para 'ptrmdesc'
day_categories = ["l", "m", "i", "j", "v", "s", "d"]  # Días de la semana (Lunes a Domingo)
time_categories = ['06:30-06:60', '07:00-07:30', '07:30-07:60', '08:00-08:30', '08:30-08:60', '09:00-09:30', '09:30-09:60', '10:00-10:30', '10:30-10:60', '11:00-11:30', '11:30-11:60', '12:00-12:30', '12:30-12:60', '13:00-13:30', '13:30-13:60', '14:00-14:30', '14:30-14:60', '15:00-15:30', '15:30-15:60', '16:00-16:30', '16:30-16:60', '17:00-17:30', '17:30-17:60', '18:00-18:30', '18:30-18:60', '19:00-19:30', '19:30-19:60', '20:00-20:30', '20:30-20:60', '21:00-21:30']
# Función principal para la predicción

#####-----------------------------------------------------------------------
# Definimos una clase Course para encapsular los datos de cada curso
class Course:
    def __init__(self, nrc, schedules, course_level, course_class, ptrmdesc, first_enrollment_time):

        ptrmdesc_mapper={ 
            '16 SEMANAS':'PERIODO 202420 - 16 SEMANAS'
        }

        self.nrc = nrc
        self.schedules = schedules
        self.course_level = course_level
        self.course_class = course_class
        self.ptrmdesc = ptrmdesc_mapper.get(ptrmdesc,ptrmdesc)
        self.first_enrollment_time = first_enrollment_time  # First enrollment time as a timestamp

# Función para crear intervalos de 30 minutos y asignar 1 o 0 en función de los horarios del curso
def create_time_bins(schedules):
    bins = np.zeros(48)  # 48 intervalos de 30 minutos en un día
    for schedule in schedules:
        if schedule['time_ini'] is None or schedule['time_fin'] is None:
            continue
        time_ini = int(schedule['time_ini'][:2]) * 60 + int(schedule['time_ini'][2:])
        time_fin = int(schedule['time_fin'][:2]) * 60 + int(schedule['time_fin'][2:])
        for i in range(48):  # Intervalos de 30 minutos
            interval_start = i * 30
            interval_end = (i + 1) * 30
            if not (time_fin <= interval_start or time_ini >= interval_end):
                bins[i] = 1
    return bins

# Cargar el scaler y el modelo desde archivos pickle
def load_scaler_model():
    with open("scaler.pkl", "rb") as scaler_file:
        scaler = pickle.load(scaler_file)
    with open("model.pkl", "rb") as model_file:
        model = pickle.load(model_file)
    return scaler, model

# Calcular la duración en minutos, dentro del horario activo de 8:00 am a 5:00 pm
def calcular_duration_en_horas_activas(first_enroll_time, fill_time):
    start_hour, end_hour = 8, 17
    if fill_time < first_enroll_time:
        return 0
    
    def calcular_horas_dia(dia_inicio, dia_fin):
        inicio_efectivo = max(dia_inicio.hour + dia_inicio.minute / 60, start_hour)
        fin_efectivo = min(dia_fin.hour + dia_fin.minute / 60, end_hour)
        return max(0, fin_efectivo - inicio_efectivo)

    total_minutes = 0
    if first_enroll_time.date() == fill_time.date():
        total_minutes += calcular_horas_dia(first_enroll_time, fill_time) * 60
    else:
        first_day_end = pd.Timestamp(first_enroll_time.year, first_enroll_time.month, first_enroll_time.day, end_hour, 0, 0)
        total_minutes += calcular_horas_dia(first_enroll_time, first_day_end) * 60
        next_day = first_enroll_time + pd.Timedelta(days=1)
        while next_day.date() < fill_time.date():
            if next_day.weekday() < 5:
                total_minutes += (end_hour - start_hour) * 60
            next_day += pd.Timedelta(days=1)
        fill_day_start = pd.Timestamp(fill_time.year, fill_time.month, fill_time.day, start_hour, 0, 0)
        total_minutes += calcular_horas_dia(fill_day_start, fill_time) * 60

    return total_minutes

# Calcular la hora de llenado en horas activas
def calcular_fill_time(first_enroll_time, fill_duration_minutes):
    current_time = first_enroll_time
    remaining_minutes = fill_duration_minutes
    start_hour, end_hour = 8, 17

    while remaining_minutes > 0:
        if current_time.hour < start_hour:
            current_time = current_time.replace(hour=start_hour, minute=0)
        elif current_time.hour >= end_hour:
            current_time += pd.Timedelta(days=1)
            current_time = current_time.replace(hour=start_hour, minute=0)
            while current_time.weekday() >= 5:
                current_time += pd.Timedelta(days=1)
        else:
            end_of_day = current_time.replace(hour=end_hour, minute=0)
            available_minutes = (end_of_day - current_time).total_seconds() / 60
            if remaining_minutes <= available_minutes:
                return current_time + pd.Timedelta(minutes=remaining_minutes)
            remaining_minutes -= available_minutes
            current_time = end_of_day + pd.Timedelta(minutes=1)

# Función principal de predicción
def predict_course_probability(course, enrollment_time):
    interval_labels = [f'{i//2:02}:{(i%2)*30:02}-{(i//2):02}:{((i%2)+1)*30:02}' for i in range(48)]
    time_bins = create_time_bins(course.schedules).reshape(1, -1)
    time_bins_expanded = pd.DataFrame(time_bins, columns=interval_labels)
    time_bins_expanded = time_bins_expanded[time_categories]
    time_bins = time_bins_expanded.values.reshape(1, -1)
    days_of_week = set(day for data in course.schedules for day in day_categories if data.get(day))
    days_one_hot = pd.DataFrame([{day: 1 if day in days_of_week else 0 for day in day_categories}]).values.reshape(1, -1)

    encoder_class = OneHotEncoder(categories=[class_categories], sparse_output=False)
    class_encoded = encoder_class.fit_transform([[course.course_class]]).reshape(1, -1)
    encoder_ptrmdesc = OneHotEncoder(categories=[ptrmdesc_categories], sparse_output=False)
    ptrmdesc_encoded = encoder_ptrmdesc.fit_transform([[course.ptrmdesc]]).reshape(1, -1)
    course_level = np.array([[course.course_level]])

    X = np.hstack([time_bins, days_one_hot, class_encoded, ptrmdesc_encoded, course_level])
    scaler, model = load_scaler_model()
    X_scaled = scaler.transform(X)

    if enrollment_time < course.first_enrollment_time:
        return 1.0, calcular_fill_time(course.first_enrollment_time, 0)
    
    survival_fn = model.predict_survival_function(X_scaled)
    max_duration_allowed = survival_fn[0].domain[1]
    duration_minutes = calcular_duration_en_horas_activas(course.first_enrollment_time, enrollment_time)
    duration_minutes = min(duration_minutes, max_duration_allowed)
    survival_prob = survival_fn[0](duration_minutes)

    print(course.first_enrollment_time, enrollment_time,duration_minutes)

    fill_duration = next((t for t in survival_fn[0].x if survival_fn[0](t) < 0.5), None)
    if fill_duration is not None:
        fill_time = calcular_fill_time(course.first_enrollment_time, fill_duration)
    else:
        fill_time = None

    return survival_prob, fill_time


