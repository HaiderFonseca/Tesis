from dash import html, dcc, Input, Output,callback
import dash_bootstrap_components as dbc
import requests
import pandas as pd
import plotly.graph_objs as go

# ID del NRC predeterminado
NRC = 58409

summary = html.Div(
    style={"backgroundColor": "#F7F7F7", "padding": "20px"},
    children=[
        # Encabezado con solo texto
        html.Div(
            style={
                "textAlign": "center",
                "fontSize": "24px",
                "fontWeight": "bold",
                "marginBottom": "20px",
            },
            children=NRC,
        ),

        # Contenido Principal
        html.Div(
            style={"display": "grid", "gridTemplateColumns": "2fr 1fr", "gap": "20px", "marginTop": "20px"},
            children=[
                # Gráfico (Placeholder)
                html.Div(
                    style={
                        "borderRadius": "20px",
                        "backgroundColor": "#F0F2F5",
                        "padding": "20px",
                        "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)",
                    },
                    children=dcc.Graph(id="dynamic-graph"),
                ),

                # Panel de Probabilidad, Cupos y Turno
                html.Div(
                    style={"display": "flex", "flexDirection": "column", "gap": "20px"},
                    children=[
                        # Turno en contenedor estilizado con color de fondo
                        html.Div(
                            style={
                                "borderRadius": "20px",
                                "backgroundColor": "#FFF",
                                "padding": "20px",
                                "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)",
                                "textAlign": "center",
                            },
                            children=[
                                html.H4("Turno", style={"marginBottom": "10px"}),

                                # Rectángulo con color para el turno
                                html.Div(
                                    style={
                                        "backgroundColor": "#FFF8E8",
                                        "borderRadius": "20px",
                                        "padding": "10px",
                                        "display": "inline-flex",
                                        "gap": "10px",
                                        "alignItems": "center",
                                        "justifyContent": "center",
                                    },
                                    children=[
                                        # Día
                                        dcc.Input(
                                            type="number", id="input-day", placeholder="DD", min=1, max=31,
                                            style={
                                                "width": "50px", "textAlign": "center",
                                                "borderRadius": "10px",
                                                "backgroundColor": "#FFFFFF",
                                                "fontSize": "14px",
                                                "border": "1px solid #ccc",
                                            }
                                        ),
                                        # Mes
                                        dcc.Input(
                                            type="number", id="input-month", placeholder="MM", min=1, max=12,
                                            style={
                                                "width": "50px", "textAlign": "center",
                                                "borderRadius": "10px",
                                                "backgroundColor": "#FFFFFF",
                                                "fontSize": "14px",
                                                "border": "1px solid #ccc",
                                            }
                                        ),
                                        # Año
                                        dcc.Input(
                                            type="number", id="input-year", placeholder="AAAA", min=1900, max=2100,
                                            style={
                                                "width": "60px", "textAlign": "center",
                                                "borderRadius": "10px",
                                                "backgroundColor": "#FFFFFF",
                                                "fontSize": "14px",
                                                "border": "1px solid #ccc",
                                            }
                                        ),
                                        # Hora
                                        html.Div(
                                            children=[
                                                dcc.Input(
                                                    type="number", id="input-hour", placeholder="HH", min=0, max=23,
                                                    style={
                                                        "width": "50px", "textAlign": "center",
                                                        "borderRadius": "10px",
                                                        "backgroundColor": "#FFFFFF",
                                                        "fontSize": "14px",
                                                        "border": "1px solid #ccc",
                                                    }
                                                ),
                                                html.Span(":", style={"margin": "0 5px", "fontSize": "18px"}),
                                                dcc.Input(
                                                    type="number", id="input-minute", placeholder="MM", min=0, max=59,
                                                    style={
                                                        "width": "50px", "textAlign": "center",
                                                        "borderRadius": "10px",
                                                        "backgroundColor": "#FFFFFF",
                                                        "fontSize": "14px",
                                                        "border": "1px solid #ccc",
                                                    }
                                                ),
                                            ],
                                            style={"display": "flex", "alignItems": "center"},
                                        ),
                                        # Botón guardar con emoji
                                        html.Button(
                                            html.I(className="fas fa-save", style={"color": "#F0A500"}),
                                            style={
                                                "border": "none", "backgroundColor": "transparent",
                                                "cursor": "pointer"
                                            },
                                            id="position-set-button"  # ID del botón para el callback
                                        ),
                                    ],
                                ),
                            ],
                        ),

                        # Probabilidad
                        html.Div(
                            style={
                                "borderRadius": "20px",
                                "backgroundColor": "#FFF",
                                "padding": "20px",
                                "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)",
                                "textAlign": "center",
                            },
                            children=[
                                html.H4("Probabilidad", style={"marginBottom": "10px"}),
                                html.Div("28%", style={"fontSize": "36px", "fontWeight": "bold"}),
                            ]
                        ),

                        # Cupos disponibles
                        html.Div(
                            style={
                                "borderRadius": "20px",
                                "backgroundColor": "#FFF",
                                "padding": "20px",
                                "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)",
                                "textAlign": "center",
                            },
                            children=[
                                html.H4("Cupos disponibles en este momento", style={"marginBottom": "10px"}),
                                html.Div("15", style={"fontSize": "36px", "fontWeight": "bold"}),
                            ]
                        ),
                    ]
                ),
            ],
        ),

        # Sección de Sugerencias
        html.Div(
            style={
                "marginTop": "30px",
                "padding": "20px",
                "borderRadius": "20px",
                "backgroundColor": "#FFF",
                "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)",
            },
            children=[
                html.H4("Sugerencias", style={"marginBottom": "20px"}),
                html.Div(
                    style={"display": "grid", "gap": "10px"},
                    children=[
                        html.Div(
                            style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "padding": "10px", "borderRadius": "15px", "backgroundColor": "#f7f7f7"},
                            children=[
                                html.Div("Sección 1", style={"fontWeight": "bold"}),
                                html.Div("Cupos: 40", style={"marginLeft": "auto", "marginRight": "10px"}),
                                html.Button(html.I(className="fas fa-plus", style={"color": "orange"}), style={"border": "none", "backgroundColor": "transparent", "cursor": "pointer"}),
                            ],
                        ),
                        html.Div(
                            style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "padding": "10px", "borderRadius": "15px", "backgroundColor": "#f7f7f7"},
                            children=[
                                html.Div("Sección 8", style={"fontWeight": "bold"}),
                                html.Div("Cupos: 10", style={"marginLeft": "auto", "marginRight": "10px"}),
                                html.Button(html.I(className="fas fa-exclamation-triangle", style={"color": "orange"}), style={"border": "none", "backgroundColor": "transparent", "cursor": "pointer"}),
                            ],
                        ),
                    ]
                )
            ],
        ),
    ]
)



# Callback para actualizar la gráfica
@callback(
    Output("dynamic-graph", "figure"),
    Input("dynamic-graph", "id")  # Este input es solo un trigger, no se usa
)
def update_graph(_):
    # Llamada al endpoint
    endpoint = f"http://127.0.0.1:8050/api/history/{NRC}"
    response = requests.get(endpoint)
    data = response.json()

    # Transformar los datos en un DataFrame
    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")

    # Crear la figura
    figure = go.Figure(
        data=go.Scatter(x=df["timestamp"], y=df["enrolled"], mode="lines+markers"),
        layout=go.Layout(
            title="Historial de Inscripciones",
            xaxis={"title": "Tiempo"},
            yaxis={"title": "Inscritos"},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
    )
    return figure