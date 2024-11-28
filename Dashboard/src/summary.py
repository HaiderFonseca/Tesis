from dash import html, dcc, Input, Output,callback, State
import dash_bootstrap_components as dbc
import requests
import pandas as pd
import plotly.graph_objs as go
from dotenv import load_dotenv
import os
from model import predict_course_probability, Course, FIRST_ENROLLMENT_TIME

load_dotenv()
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL"))
API_URL = os.getenv("API_URL")

def create_summary_page(nrc):
    url = f'{API_URL}?nameInput={nrc}'
    response = requests.get(url)

    if response.status_code != 200 or len(response.json()) == 0:
        return html.Div(
            style={"textAlign": "center", "fontSize": "24px", "fontWeight": "bold", "margin": "20px"},
            children="Error al cargar la página"
        )
    
    course_data = response.json()[0]
    course_name = course_data.get('title', 'Curso no encontrado')

    course_code = course_data.get('class', '') + course_data.get('course', '')
    url = f'{API_URL}?nameInput={course_code}'
    response = requests.get(url)
    simmilar_courses = response.json()

    return html.Div(
        style={"backgroundColor": "#F7F7F7", "padding": "20px"},
        children=[

            # IDS no utilizados en esta página, previenen errores de id not found en callbacks
            html.Div(id="events-container", style={"display": "none"}),
            html.Div(id="progress-panel", style={"display": "none"}),

            dcc.Interval(
                id="interval-component",
                interval=UPDATE_INTERVAL*1000,  # Intervalo en milisegundos (5 segundos)
                n_intervals=0  # Número de intervalos transcurridos (se incrementa automáticamente)
            ),
            html.Div(
                style={"display": "none"},
                children=nrc,
                id="summary-nrc",
            ),
            # Encabezado con solo texto
            html.Div(
                style={
                    "textAlign": "center",
                    "fontSize": "24px",
                    "fontWeight": "bold",
                    "marginBottom": "20px",
                },
                children=f"{course_name} (Sección {course_data.get('section', 'desconocida')})"
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
                                    dcc.Graph(id="probability-gauge"),
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
                                    html.Div(style={"fontSize": "36px", "fontWeight": "bold"}, id="available-seats"),
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
                        id="suggestions-list"
                    )
                ],
            ),
        ]
    )



# Callback para actualizar la gráfica
@callback(
    Output("dynamic-graph", "figure"),
    Output("available-seats", "children"),
    Output("probability-gauge", "figure"),
    Output("suggestions-list", "children"),
    Input("interval-component", "n_intervals"),
    Input({'type': 'storage', 'index': 'position'}, 'data'),
    State("summary-nrc", "children"),
)
def update_graph(_, position, nrc):
    # Llamada al endpoint
    endpoint = f"http://127.0.0.1:8050/api/history/{nrc}"
    response = requests.get(endpoint)
    data = response.json()

    url = f'{API_URL}?nameInput={nrc}'
    response = requests.get(url)
    course_data = response.json()[0]

    # Transformar los datos en un DataFrame
    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["timestamp"] = df["timestamp"] - pd.Timedelta(hours=5)
    df = df.sort_values("timestamp")

    maxenrol = int(course_data.get('maxenrol', 0))

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

    # Añadir una línea horizontal para maxenrol
    figure.add_hline(
        y=maxenrol,
        line_dash="dash",  # Línea discontinua
        line_color="rgba(0,0,0,0.5)",  # Color rojo para resaltar
        annotation_text=f"Total de cupos: {maxenrol}",  # Etiqueta de la línea
        annotation_position="top right",  # Posición de la etiqueta
        annotation_font_size=12,  # Tamaño de la fuente
        annotation_font_color="rgba(0,0,0,0.5)"  # Color del texto
    )

    slots = max(maxenrol - int(course_data.get('enrolled', 0)), 0)

    # Calcular la probabilidad
    # Crear una instancia de Course para cada curso
    days_of_week = {"l": "Lunes", "m": "Martes", "i": "Miércoles", "j": "Jueves", "v": "Viernes", "s": "Sábado"}
    schedules = []
    for schedule in course_data.get("schedules", []):
        days = []
        for day_key, day_name in days_of_week.items():
            if schedule.get(day_key):
                days.append(day_name)
        schedules.append({
            "days": ",".join(days),
            "time_ini": schedule.get("time_ini", "0000"),
            "time_fin": schedule.get("time_fin", "0000"),
            "classroom": schedule.get("classroom", "Desconocido"),
        })
    
    course = Course(
        nrc=course_data.get('nrc', ''),
        schedules=schedules,
        course_level=int(course_data.get('course', '0')[0]),
        course_class=course_data.get('class', ''),
        ptrmdesc=course_data.get('ptrmdesc', ''),
        first_enrollment_time=FIRST_ENROLLMENT_TIME
    )
    
    # Fecha límite (un mes después del inicio de los cursos)
    enrollment_deadline = FIRST_ENROLLMENT_TIME + pd.Timedelta(days=30)
    position = pd.Timestamp(position)

    # Calcular la probabilidad de inscripción para el curso
    if position  > enrollment_deadline:
        # Si ha pasado más de un mes, la probabilidad es cero
        probability = 0
        expected_fill_time = None
    else:
        # Calcular la probabilidad normal si aún estamos dentro del plazo
        probability, expected_fill_time = predict_course_probability(course, position)

    gauge = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=probability * 100,  # Aquí 'probability' debe ser un valor entre 0 y 1
            number={
                "suffix": "%",  # Añadir sufijo de porcentaje
            },
            gauge={
                "axis": {"range": [0, 100]},  # Rango mínimo y máximo entre 0 y 1
                "bar": {"color": "blue"},
            },
            domain={"x": [0.2, 0.8], "y": [0.2, 0.8]},
        ),
        # Hacer la gráfica más pequeña
        layout=go.Layout(height=200, margin={"t": 0, "b": 0, "l": 0, "r": 0}, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    )

    course_code = course_data.get('class', '') + course_data.get('course', '')
    url = f'{API_URL}?nameInput={course_code}'
    response = requests.get(url)
    simmilar_courses = response.json()

    suggestions_list = [
        html.Div(
            style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "padding": "10px", "borderRadius": "15px", "backgroundColor": "#f7f7f7"},
            children=[
                html.Div(f"{course.get('class', '') + course.get('course', '')}: Sección {course.get('section', '')} ({course.get('credits', '')} créditos)", style={"fontWeight": "bold"}),
                html.Div(f"{max(int(course.get('maxenrol', '')) - int(course.get('enrolled', '')), 0)} Cupos", style={"marginLeft": "auto", "fontWeight": "bold"}),
                html.Div(f"Inscritos: {course.get('enrolled', '')} - Total {course.get('maxenrol', '')}", style={"marginLeft": "10px", "marginRight": "10px"}),
            ],
        )
        for course in sorted(simmilar_courses, key=lambda x: int(x.get('maxenrol', '')) - int(x.get('enrolled', '')), reverse=True)
    ]

    return figure, slots, gauge, suggestions_list