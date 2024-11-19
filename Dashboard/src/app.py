import dash
import dash_bootstrap_components as dbc

from layout import layout
import callbacks

import warnings
warnings.filterwarnings("ignore")

# Inicializar la aplicación
app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP, "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css"],
    suppress_callback_exceptions=True,
)

app.title = "PredictMyCourses: Dashboard de Horario"
app.layout = layout

if __name__ == '__main__':
    app.run_server(debug=True)
    