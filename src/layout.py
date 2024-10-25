from dash import html, dcc
import dash_bootstrap_components as dbc
from modal import modal

# Define el menú lateral que aparecerá al hacer clic en el icono de hamburguesa
sidebar = html.Div(
    id="sidebar",
    children=[
        # Resumen con ícono de casa
        html.A([
            html.I(className="fas fa-home", style={"marginRight": "10px"}),  # Ícono de casa
            "Resumen"
        ], href="/resumen", style={"padding": "8px 8px 8px 32px", "textDecoration": "none", "display": "block", "color": "inherit"}),

        # Contenedor para la lista de planes
        html.Div(id="plan-list", children=[]),

        # Crear nuevo plan con ícono de más
        html.A([
            html.I(className="fas fa-plus", style={"marginRight": "10px"}),  # Ícono de más
            "Crear nuevo plan"
        ], id="add-plan", href="#", style={"padding": "8px 8px 8px 32px", "textDecoration": "none", "display": "block", "color": "inherit"}),
    ]
)

# Define el navbar con el ícono de hamburguesa y el nombre de la app
navbar = dbc.Navbar(
    html.Div([
        html.Div(
            html.Button(
                html.I(className="fas fa-bars"), id="hamburger-icon", n_clicks=0, style={
                "background": "transparent", "border": "none", "color": "black", "fontSize": "24px", "cursor": "pointer"
                }),
            style={"position": "absolute", "left": "20px"}
        ),
        html.H2("Hadas", style={"textAlign": "center", "color": "black", "margin": "0"})
    ], style={"display": "flex", "justifyContent": "center", "width": "100%", "alignItems": "center", "height": "70px"}),
    color="#f0f2f5",
    dark=False,
    sticky="top",
    style={"padding": "0"}
)

# Layout principal que contiene el navbar y el sidebar
layout = html.Div([
    dcc.Location(id="url"),  # Monitorear la URL para detectar cambios
    dcc.Store(id={'type': 'storage', 'index': 'memory'}, storage_type='memory'), # Almacenar datos en memoria
    dcc.Store(id={'type': 'storage', 'index': 'local'}, storage_type='local'),  # Almacenar datos localmente
    modal,
    navbar,
    sidebar,
    html.Div(id="page-content")
])
