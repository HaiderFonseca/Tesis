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
    html.Div(
        style={
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center",  # Asegura que esté centrado en el navbar
            "width": "100%",
            "height": "70px",
            "backgroundColor": "#f0f2f5",
            "position": "relative",  # Para manejar la posición del ícono de hamburguesa
        },
        children=[
            # Ícono de hamburguesa alineado a la izquierda
            html.Button(
                html.I(className="fas fa-bars"),
                id="hamburger-icon",
                n_clicks=0,
                style={
                    "position": "absolute",
                    "left": "20px",
                    "background": "transparent",
                    "border": "none",
                    "color": "black",
                    "fontSize": "24px",
                    "cursor": "pointer",
                },
            ),
            
            # Logo y texto clicable que lleva a "/"
            dcc.Link(
                href="/",
                style={"textDecoration": "none"},  # Sin subrayado en el enlace
                children=html.Div(
                    style={"display": "flex", "alignItems": "center", "gap": "10px"},
                    children=[
                        html.Div(
                            style={"display": "flex", "alignItems": "center"},
                            children=[
                                html.Span(
                                    "Wizard ",
                                    style={
                                        "fontFamily": "'Irish Grover', cursive",
                                        "fontSize": "20px",
                                        "color": "black"
                                    }
                                ),
                                html.Span(
                                    "Séneca",
                                    style={
                                        "fontFamily": "'Irish Grover', cursive",
                                        "fontSize": "20px",
                                        "color": "#FFC107"
                                    }
                                )
                            ]
                        ),
                        html.Img(
                            src="/assets/Logo_Hadas.png",
                            style={"height": "50px"}
                        ),
                    ]
                )
            )
        ]
    ),
    color="#f0f2f5",
    dark=False,
    sticky="top",
    style={"padding": "0"},
)

# Layout principal que contiene el navbar y el sidebar
layout = html.Div([
    dcc.Location(id="url"),  # Monitorear la URL para detectar cambios
    dcc.Store(id={'type': 'storage', 'index': 'memory'}, storage_type='memory'), # Almacenar datos en memoria (temporal)
    dcc.Store(id={'type': 'storage', 'index': 'schedules'}, storage_type='local'),  # Almacenar datos localmente (horarios)
    dcc.Store(id={'type': 'storage', 'index': 'position'}, storage_type='local'),  # Almacenar datos localmente (turno de inscripción)
    modal,
    navbar,
    sidebar,
    html.Div(id="page-content")
])
