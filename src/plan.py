from dash import html, dcc
import dash_bootstrap_components as dbc

def create_plan_page(plan_id):

    # Lista de horas (6 AM - 10 PM)
    hours = [f'{i}:00 AM' if i < 12 else f'{i-12}:00 PM' if i > 12 else '12:00 PM' for i in range(6, 23)]
    days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]

    return html.Div([

        # Fondo gris claro para el contenedor principal
        html.Div(className="schedule-container", children=[

            # Floating Action Button para agregar un nuevo evento
            html.Button([
                html.I(className="fas fa-plus"),
            ], id="add-event-fab", className="add-event-button"),

            # Barra de progreso en la parte superior y turno
            html.Div(className="progress-up", children=[

                # Barra del turno
                html.Div(
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "borderRadius": "20px",
                        "backgroundColor": "#f7f9fc",
                        "padding": "5px 15px",
                        "boxShadow": "0 2px 5px rgba(0, 0, 0, 0.1)",
                        "gap": "8px",
                        "height": "50px"       
                    },
                    children=[
                        # Día
                        html.Div(
                            children=[
                                dcc.Input(
                                    type="number", placeholder="DD", min=1, max=31, 
                                    style={
                                        "width": "50px", "textAlign": "center", 
                                        "borderRadius": "10px", "backgroundColor": "#F5F5F5", "fontSize": "14px"
                                    }
                                )
                            ]
                        ),
                        # Mes
                        html.Div(
                            children=[
                                dcc.Input(
                                    type="number", placeholder="MM", min=1, max=12,
                                    style={
                                        "width": "50px", "textAlign": "center",
                                        "borderRadius": "10px", "backgroundColor": "#F5F5F5", "fontSize": "14px"
                                    }
                                )
                            ]
                        ),
                        # Año
                        html.Div(
                            children=[
                                dcc.Input(
                                    type="number", placeholder="AAAA", min=1900, max=2100,
                                    style={
                                        "width": "60px", "textAlign": "center",
                                        "borderRadius": "10px", "backgroundColor": "#F5F5F5", "fontSize": "14px"
                                    }
                                )
                            ]
                        ),
                        # Hora
                        html.Div(
                            children=[
                                dcc.Input(
                                    type="number", placeholder="HH", min=0, max=23,
                                    style={
                                        "width": "45px", "textAlign": "center",
                                        "borderRadius": "10px", "backgroundColor": "#F5F5F5", "fontSize": "12px"
                                    }
                                ),
                                html.Span(":", style={"margin": "0 5px"}),
                                dcc.Input(
                                    type="number", placeholder="MM", min=0, max=59,
                                    style={
                                        "width": "45px", "textAlign": "center",
                                        "borderRadius": "10px", "backgroundColor": "#F5F5F5", "fontSize": "12px"
                                    }
                                )
                            ],
                            style={"display": "flex", "alignItems": "center"}
                        ),
                        # Botón de envío
                        html.Button(
                            html.I(className="fas fa-paper-plane", style={"color": "blue"}),
                            style={
                                "border": "none", "backgroundColor": "transparent",
                                "cursor": "pointer"
                            },
                            id="submit-button"
                        )
                    ]
                ),

                # Barra de progreso

                html.Div(className="progress-panel", children=[
                    html.Div(
                        className="progress",
                        style={"height": "20px", "borderRadius": "15px"},
                        children=[
                            html.Div(
                                "",
                                className="progress-bar progress-bar-striped progress-bar-animated",
                                role="progressbar",
                                style={"width": "0%", "backgroundColor": "#F0A500", "color": "#FFF"},  # Color personalizado y ancho del progreso
                                **{"aria-valuenow": "0", "aria-valuemin": "0", "aria-valuemax": "100"}
                            )
                        ]
                    )
                ], style={"marginBottom": "20px", "padding": "0 20px"}, id="progress-panel")
     
            ], style={"display": "grid", "gridTemplateColumns": "auto 1fr", "gap": "20px"}),

            # Caja que contiene el calendario
            html.Div(className="calendar-box", children=[
                    html.Div(className="calendar-container", id="calendar-events", children=[
                        # Columna de horas
                        html.Div(className="hour-column", children=[
                            html.Div("", style={"height": "50px"}),  # Espacio en blanco para centrar las horas
                            *[html.Div(html.Span(hour, className="hour-text"), className="hour-box") for hour in hours]
                        ]),

                        html.Div(className="schedule-grid", children=[

                            # Contenedor de los días con los encabezados centrados
                            html.Div(className="day-columns", children=[
                                html.Div(className="day-header-container", children=[
                                    html.Div(day, className="day-header"),
                                ])
                                for day in days
                            ]),

                            # Contenedor de los eventos
                            html.Div(id="events-container", children=[]),
                        ])
                    ])
                ])
        ])
    ])

