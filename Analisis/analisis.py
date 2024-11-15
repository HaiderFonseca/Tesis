
import pandas as pd

# Lee el archivo .parquet y carga los datos en un DataFrame
df = pd.read_parquet('Oferta_Academica_Cursos 1.parquet')

# Muestra los primeros 5 registros del DataFrame
print(df.head())

# Muestra la información general del DataFrame
print(df.info())

# Muestra un resumen estadístico de los datos
print(df.describe())

# Muestra los nombres de las columnas del DataFrame
print(df.columns)

# Accede a una columna específica del DataFrame
print(df['nombre_columna'])

# Filtra los datos según una condición
filtered_df = df[df['nombre_columna'] > 10]
print(filtered_df.head())


