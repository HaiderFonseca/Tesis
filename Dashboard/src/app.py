import dash
import dash_bootstrap_components as dbc

from layout import layout
import callbacks

from backend import app, POLLING_ENABLED
#from flask import Flask; app = Flask(__name__); POLLING_ENABLED = False

import warnings
warnings.filterwarnings("ignore")


# Inicializar la aplicación
app_dash = dash.Dash(
    __name__, 
    server=app,
    external_stylesheets=[dbc.themes.BOOTSTRAP, "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css"],
    suppress_callback_exceptions=True,
    url_base_pathname="/",
)

app_dash.title = "Hadas: Dashboard de Horario"
app_dash.layout = layout

if __name__ == '__main__':
    app_dash.run_server(debug=True, use_reloader=not POLLING_ENABLED)  # poner reloader en True solo si no me conecto al simulador
    