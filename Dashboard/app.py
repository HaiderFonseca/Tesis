import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import random

# Inicializar la aplicación
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Lista de horas (6 AM - 10 PM)
hours = [f'{i}:00 AM' if i < 12 else f'{i-12}:00 PM' if i > 12 else '12:00 PM' for i in range(6, 23)]

# Datos inventados para el gráfico de porcentajes a lo largo de los días de septiembre
dias = list(range(1, 31))  # Días del 1 al 30 de septiembre
porcentajes = [random.randint(10, 100) for _ in dias]

# Layout del dashboard
app.layout = html.Div([
    # Fondo gris claro para el contenedor principal
    html.Div(className="main-container", children=[

        # Panel lateral
        html.Div(className="sidebar", children=[
            html.Div("Menu", className="sidebar-title"),
            html.Div(className="sidebar-icon", children="📅 1 "),
            html.Div(className="sidebar-icon", children="📅 2 "),
            html.Div(className="sidebar-icon", children="⚙️"),
        ]),

        # Contenedor del horario
        html.Div(className="schedule-container", children=[
            # Barra de progreso en la parte superior
            html.Div(className="progress-panel", children=[
                dbc.Progress("90%", value=90, striped=False, style={"height": "20px", "border-radius": "15px", "background-color": "#F0A500", "color": "#FFF"}, className="progress-bar")
            ], style={"margin-bottom": "20px"}),  # Ajustes de la barra de progreso

            # Caja que contiene el calendario
            html.Div(className="calendar-box", children=[
                html.Div(className="calendar-container", children=[
                    # Columna de horas
                    html.Div(className="hour-column", children=[
                        html.Div(hour, className="hour-box") for hour in hours
                    ]),

                    # Contenedor de los días con los encabezados centrados
                    html.Div(className="schedule-grid", children=[
                        # Lunes
                        html.Div(className="day-column", children=[
                            html.Div(className="day-header-container", children=[
                                html.Div("Lunes", className="day-header"),
                            ]),
                            # Eventos de lunes con el efecto flip y gráfico de área de porcentajes
                            html.Div(className="flip-card event-box event-lunes-2-3", children=[
                                html.Div(className="flip-card-inner", children=[
                                    html.Div(className="flip-card-front", children=[
                                        html.P("Evento Lunes 2-3 PM")
                                    ]),
                                    html.Div(className="flip-card-back", children=[
                                        # Contenedor para la gráfica
                                        html.Div(className="graph-container", children=[
                                            # Gráfico de área con estilo moderno
                                            dcc.Graph(
                                                id='area-chart',
                                                config={'displayModeBar': False},  # Ocultar barra de herramientas del gráfico
                                                figure={
                                                    'data': [
                                                        go.Scatter(
                                                            x=dias,
                                                            y=porcentajes,
                                                            fill='tozeroy',  # Estilo de área
                                                            mode='lines',
                                                            line=dict(color='#3b5998'),  # Color moderno
                                                        )
                                                    ],
                                                    'layout': go.Layout(
                                                        title='Historial',
                                                        xaxis={'title': 'Día del mes'},
                                                        yaxis={'title': 'Porcentaje'},
                                                        paper_bgcolor='rgba(0,0,0,0)',
                                                        plot_bgcolor='rgba(0,0,0,0)',
                                                        margin=dict(l=40, r=20, t=30, b=30),  # Márgenes ajustados
                                                        height=300  # Altura del gráfico
                                                    )
                                                }
                                            )
                                        ], style={"padding": "10px", "border": "1px solid #ddd", "border-radius": "10px", "background-color": "#f7f7f7"})
                                    ]),
                                ])
                            ]),
                        ]),

                        # Martes
                        html.Div(className="day-column", children=[
                            html.Div(className="day-header-container", children=[
                                html.Div("Martes", className="day-header"),
                            ]),
                        ]),

                        # Miércoles
                        html.Div(className="day-column", children=[
                            html.Div(className="day-header-container", children=[
                                html.Div("Miércoles", className="day-header"),
                            ]),
                        ]),

                        # Jueves
                        html.Div(className="day-column", children=[
                            html.Div(className="day-header-container", children=[
                                html.Div("Jueves", className="day-header"),
                            ]),
                        ]),

                        # Viernes
                        html.Div(className="day-column", children=[
                            html.Div(className="day-header-container", children=[
                                html.Div("Viernes", className="day-header"),
                            ]),
                        ]),

                        # Sábado
                        html.Div(className="day-column", children=[
                            html.Div(className="day-header-container", children=[
                                html.Div("Sábado", className="day-header"),
                            ]),
                        ]),
                    ])
                ])
            ])
        ])
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)
