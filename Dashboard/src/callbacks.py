from dash import Input, Output, State, callback, html, ALL
import dash_bootstrap_components as dbc
import random
import requests
import dash
import json
from plan import create_plan_page
from landing import landing
from summary import create_summary_page
import pandas as pd
from dash.exceptions import PreventUpdate
from model import predict_course_probability, Course, FIRST_ENROLLMENT_TIME
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from dotenv import load_dotenv
import os

load_dotenv()
API_URL = os.getenv("API_URL")

# Callback para controlar la apertura y cierre del menú lateral
@callback(
    Output("sidebar", "style"),
    Input("hamburger-icon", "n_clicks")
)
def toggle_sidebar(n_clicks):
    if n_clicks % 2 == 1:
        return {
            "left": "0", 
            "transition": "0.3s", 
            "position": "absolute", 
            "top": "0", 
            "height": "100%", 
            "width": "250px", 
            "backgroundColor": "#f0f2f5", 
            "paddingTop": "90px",
            "zIndex": 1,
            "boxShadow": "rgba(0, 0, 0, 0.3) 8px 10px 35px -2px",
            "color": "black"
        }
    else:
        return {
            "position": "absolute",
            "top": "0",
            "left": "-250px",  # Posición fuera de la pantalla
            "height": "100%",
            "width": "250px",
            "backgroundColor": "#f0f2f5",
            "paddingTop": "90px",
            "transition": "0.3s",
            "zIndex": 1,
            "color": "black"
        }

# Callback para mostrar el contenido dinámico en base al ítem del menú seleccionado
@callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    # Si la ruta comienza con "/api", permite que Flask maneje la solicitud
    if pathname.startswith("/api"):
        raise PreventUpdate  # Evita que Dash procese esta ruta


    if pathname == "/":
        return landing
    elif pathname.startswith("/resumen/"):
        nrc = pathname.split("/")[2]
        return create_summary_page(nrc)
    elif pathname.startswith("/plan-"):
        plan_num = pathname.split("-")[1]
        layout = create_plan_page(plan_num)
        return layout
    else:
        return html.H1("Página no encontrada")

# Callback para controlar la apertura y cierre del modal
@callback(
    Output("modal", "is_open"),  # Cambia el estado de "is_open" del modal
    [Input("add-event-fab", "n_clicks")],  # Escucha clicks en el botón de FAB y en el botón de cerrar del modal
    [State("modal", "is_open")],  # Obtiene el estado actual del modal
    prevent_initial_call=True
)
def toggle_modal(fab_clicks, is_open):
    # Si se hace clic en el FAB y el modal está cerrado, ábrelo
    if fab_clicks:
        return not is_open  # Alterna el estado del modal (True para abrir, False para cerrar)
    return is_open


# Callback para realizar la búsqueda de cursos y mostrar las secciones
@callback(
    [
        Output('search-results', 'children'),
        Output({'type': 'storage', 'index': 'memory'}, 'data'),
        Output("search-detail", "style"),
        Output("search-results", "style"),
    ],
    Input('search-btn-api', 'n_clicks'),
    [
        State('search-input', 'value'),
        State("search-detail", "style"),
        State("search-results", "style"),
    ],
    prevent_initial_call=True
)
def search_courses(n_clicks, search_value, search_detail_style, search_results_style):

    # Días de la semana con sus abreviaciones
    days_of_week = {"l": "Lunes", "m": "Martes", "i": "Miércoles", "j": "Jueves", "v": "Viernes", "s": "Sábado"}

    search_detail_style["display"] = "none"
    search_results_style["display"] = "flex"


    if n_clicks > 0 and search_value:
        # Realizar la petición a la API
        search_value = search_value.upper().strip()
        url = f'{API_URL}?nameInput={search_value}'
        response = requests.get(url)

        if response.status_code == 200:
            courses_data = response.json()
            
            # Agrupar los cursos por course_code
            courses_by_code = {}
            for course in courses_data:
                course_code = f"{course.get('class','')}{course.get('course', '')}"
                if course_code not in courses_by_code:
                    courses_by_code[course_code] = []
                
                schedules = []
                for schedule in course.get("schedules", []):
                    days = []
                    for day_key, day_name in days_of_week.items():
                        if schedule.get(day_key):
                            days.append(day_name)
                    schedules.append({
                        "days": ",".join(days),
                        "time_ini": schedule.get("time_ini", 0),
                        "time_fin": schedule.get("time_fin",0),
                        "classroom": schedule.get("classroom", "No disponible")
                    })

                course = {
                    "title": course.get("title", "No disponible"),
                    "section": course.get("section", "No disponible"),
                    "nrc": course.get("nrc", "No disponible"),
                    "credits": course.get("credits", "No disponible"),
                    "instructors": list(map(lambda i: i.get("name", ''), course.get("instructors", []))),
                    "schedules": schedules,
                    "course_level":int(course.get('course', '0')[0]),
                    "course_class":course.get('class',''),
                    "ptrmdesc":course.get('ptrmdesc','')
                }
                courses_by_code[course_code].append(course)


            # Crear una lista de filas con la información de los cursos
            course_rows = []
            for code, courses in courses_by_code.items():
                course_rows.append(
                    html.Div([
                        f"{code} - {courses[0].get('title', 'No disponible')}",
                        # Botón para más información
                        html.Button([
                            html.I(className="fas fa-chevron-right", style={"color": "#B6B6B6"}),
                        ], id={'type': 'show-sections', 'index': code}, n_clicks=0, style={"border": "none", "backgroundColor": "transparent", "cursor": "pointer"}),
                    ], style={"borderRadius": "22px", "padding": "10px", "boxShadow": "2px 2px 5px rgba(0, 0, 0, 0.1)", "display": "flex", "justifyContent": "space-between", "alignItems": "center", "backgroundColor": "#F1F1F1", "width": "100%"})
                )
            
            
            return (course_rows, courses_by_code, search_detail_style, search_results_style) if course_rows else (html.Div("No se encontraron resultados para la búsqueda."), "", search_detail_style, search_results_style)
        else:
            return html.Div("Error al obtener datos de la API."), "", search_detail_style, search_results_style
    return html.Div("Introduce un valor y presiona buscar."), "", search_detail_style, search_results_style


# Callback para manejar la expansión y mostrar secciones de un curso específico
@callback(
    [
        Output("search-detail", "children"),
        Output("search-detail", "style", allow_duplicate=True),
        Output("search-results", "style", allow_duplicate=True),
    ],
    Input({'type': 'show-sections', 'index': ALL}, 'n_clicks'),
    [
        State({'type': 'storage', 'index': 'memory'}, 'data'),
        State("search-detail", "style"),
        State("search-results", "style"),
    ],
    prevent_initial_call=True
)
def show_course_sections(n_clicks, courses_by_code, search_detail_style, search_results_style):

    # Verificar si hubo algún clic
    if not any(n_clicks):
        return dash.no_update, search_detail_style, search_results_style

    # Obtener qué botón fue clicado usando callback_context
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, search_detail_style, search_results_style

    triggered_id = ctx.triggered[0]['prop_id'].replace(".n_clicks", "")
    course_code = json.loads(triggered_id)["index"]

    # Obtener las secciones del curso
    sections = courses_by_code.get(course_code, [])
    
    # Crear detalles de las secciones
    section_rows = []
    for section in sections:
        days = section.get('schedules', [])[0].get('days', '') if len(section.get('schedules', [])) else "No disponible"
        time_ini = section.get('schedules', [])[0].get('time_ini', '') if len(section.get('schedules', [])) else "No disponible"
        time_fin = section.get('schedules', [])[0].get('time_fin', '') if len(section.get('schedules', [])) else "No disponible"
        section_rows.append(
            html.Div([
                html.Div([
                    f"NRC {section.get('nrc','')}    Sección {section.get('section', '')}",
                    html.P(section.get('instructors', [])[0] if section.get('instructors', []) else "No disponible"),
                    html.P(f"{days}  {time_ini} - {time_fin}"),

                ], style={"borderRadius": "20px", "padding": "5px", "backgroundColor": "#f0f0f0", "margin": "10px 0", "display": "flex", "flexDirection":"column" , "justifyContent": "space-between", "alignItems": "center"}),
                html.Div([
                    # Botón de agregar
                    html.Button([
                        html.I(className="fas fa-plus", style={"color": "orange"}),
                    ], id={'type': 'add-section', 'index': section.get('nrc','')}, n_clicks=0, style={"border": "none", "backgroundColor": "transparent", "cursor": "pointer", "float": "right"}),
                ], style={"borderRadius": "20px", "padding": "10px", "backgroundColor": "#f0f0f0", "margin": "10px 0", "display": "flex", "flexDirection":"column" , "justifyContent": "center", "alignItems": "center"})
            ], style={"display":"grid", "gridTemplateColumns": "1fr auto", "gap": "10px"} )
        )

    # Cambiar estilos para mostrar detalles y ocultar resultados de búsqueda
    search_detail_style["display"] = "block"
    search_results_style["display"] = "none"
    
    return section_rows, search_detail_style, search_results_style

# Callback unificado para guardar y cargar el turno de inscripción como timestamp
@callback(
    [
        Output({'type': 'storage', 'index': 'position'}, 'data'),  # Guardar en dcc.Store
        Output('input-day', 'value'),
        Output('input-month', 'value'),
        Output('input-year', 'value'),
        Output('input-hour', 'value'),
        Output('input-minute', 'value'),
        Output("url", "pathname"),
    ],
    [
        Input('position-set-button', 'n_clicks'),  # Botón para establecer el turno
        Input({'type': 'storage', 'index': 'position'}, 'data'),  # Al cargar los datos del local storage
        Input("url", "pathname"),
    ],
    [
        State('input-day', 'value'),
        State('input-month', 'value'),
        State('input-year', 'value'),
        State('input-hour', 'value'),
        State('input-minute', 'value')
    ],
    prevent_initial_call=False  # Evitar que se ejecute al inicio sin interacción
)
def handle_position(n_clicks, stored_position, url, day, month, year, hour, minute):
    ctx = dash.callback_context

    # Si se hace clic en el botón, guarda el turno como timestamp en local storage
    if ctx.triggered and ctx.triggered[0]['prop_id'] == 'position-set-button.n_clicks' and n_clicks:
        # Convertir los valores de día, mes, año, hora y minuto a timestamp
        position_timestamp = pd.Timestamp(year=int(year), month=int(month), day=int(day), hour=int(hour), minute=int(minute))
        return position_timestamp.isoformat(), day, month, year, hour, minute, "/plan-1" if url == "/" else dash.no_update

    # Si hay datos almacenados, cargarlos en los campos de entrada
    if stored_position:
        # Convertir el timestamp almacenado de vuelta a una fecha y hora
        stored_timestamp = pd.Timestamp(stored_position)
        return (
            dash.no_update,  # No actualizamos el store (no hay interacción del usuario)
            stored_timestamp.day,
            stored_timestamp.month,
            stored_timestamp.year,
            stored_timestamp.hour,
            stored_timestamp.minute,
            dash.no_update,
        )

    # Si no hay datos, devolvemos valores predeterminados
    day = FIRST_ENROLLMENT_TIME.day
    month = FIRST_ENROLLMENT_TIME.month
    year = FIRST_ENROLLMENT_TIME.year
    hour = FIRST_ENROLLMENT_TIME.hour
    minute = FIRST_ENROLLMENT_TIME.minute
    return FIRST_ENROLLMENT_TIME, day, month, year, hour, minute, dash.no_update


# Obtener el colormap "Blues"
cmap = plt.get_cmap("Blues")

# Función para mapear una probabilidad (0 a 1) a un color en la escala de "Blues" de matplotlib
def get_color_from_probability(probability):
    """
    Mapea una probabilidad (0 a 1) a un color hexadecimal usando el colormap 'Blues' de Matplotlib.

    Args:
        probability (float): Probabilidad entre 0 y 1.

    Returns:
        str: Color en formato hexadecimal (#RRGGBB).
    """
    # Asegurarse de que la probabilidad esté en el rango [0, 1]
    probability = max(0, min(probability, 1))

    # Mapear la probabilidad a un color
    rgba_color = cmap(probability)

    # Convertir el color RGBA a formato hexadecimal
    hex_color = mcolors.to_hex(rgba_color)

    return hex_color


# Unificación de los callbacks
@callback(
    [
        Output("events-container", "children"),
        Output("current-plan", "children"),
        Output("progress-panel", "children"),
    ],
    [
        Input({'type': 'storage', 'index': 'schedules'}, 'data'),
        Input({'type': 'storage', 'index': 'position'}, 'data'),
        Input("url", "pathname"),
    ],
    
)
def update_dashboard(schedules_data, position, url):
    plan_id = url.split("-")[-1] if url.startswith("/plan-") else None
    if not schedules_data or not position or not plan_id in schedules_data:
        return [], dash.no_update, []
    
    schedules_data = schedules_data[plan_id]

    
    summary_events = []
    displayed_events = []
    total_probability = 1  # Probabilidad combinada de inscribir todos los cursos
    position = pd.Timestamp(position)

    # Fecha límite (un mes después del inicio de los cursos)
    enrollment_deadline = FIRST_ENROLLMENT_TIME + pd.Timedelta(days=50)

    # Procesar cada curso en schedules
    for section in schedules_data:
        # Crear una instancia de Course para cada curso
        course = Course(
            nrc=section.get('nrc', ''),
            schedules=section.get('schedules', []),
            course_level=section.get('course_level', 0),
            course_class=section.get('course_class', ''),
            ptrmdesc=section.get('ptrmdesc', ''),
            first_enrollment_time=FIRST_ENROLLMENT_TIME
        )
       

        # Calcular la probabilidad de inscripción para el curso
        if position  > enrollment_deadline:
            # Si ha pasado más de un mes, la probabilidad es cero
            probability = 0
            expected_fill_time = None
        else:
            # Calcular la probabilidad normal si aún estamos dentro del plazo
            probability, expected_fill_time = predict_course_probability(course, position)

        print(f"Probabilidad de inscripción para el curso {course.nrc}: {probability}")
        print(f"Tiempo esperado de llenado del curso {course.nrc}: {expected_fill_time}")

        # Multiplicar la probabilidad al total
        total_probability *= probability

        # Crear eventos y resumen de eventos
        for schedule in section.get('schedules', []):
            for day in schedule.get('days', '').split(','):
                start_time_min = int(schedule.get('time_ini', '00')[:2]) * 60 + int(schedule.get('time_ini', '00')[-2:])
                end_time_min = int(schedule.get('time_fin', '00')[:2]) * 60 + int(schedule.get('time_fin', '00')[-2:])
                duration_min = end_time_min - start_time_min

                # Calcular posición y tamaño del evento
                total_days = 6
                calendar_height = 680
                time_span = 16 * 60
                time_zero = 6 * 60

                top = (start_time_min - time_zero) * calendar_height / time_span
                left = (["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"].index(day)) / total_days * 100
                height = duration_min * calendar_height / time_span

                # Obtener el color de fondo según la probabilidad
                if probability == 0:
                    background_color = "#0B3D91"  # Azul oscuro para probabilidad 0
                else:
                    background_color = get_color_from_probability(1 - probability)
                profesors = ", ".join(section.get('instructors', []))
                alert_emoji = "⚠ " if probability < 0.5 else ""
                
                # Crear nuevo evento con animación de flip card
                new_event = html.Div(
                    html.Div(
                        [
                            # Lado frontal de la tarjeta
                            html.Div(
                                f"{alert_emoji}{section.get('title', '')} - sección: {section.get('section', '')} - Probabilidad de inscripción: {int(probability * 100)}%",
                                className="flip-front",
                                style={"backgroundColor": background_color, "color": "black"}
                            ),
                            # Lado trasero de la tarjeta
                            html.Div(
                                [
                                    html.Div(
                                        f"Esperado: {expected_fill_time.strftime('%Y-%m-%d %H:%M') if expected_fill_time else 'No disponible'} \n Profesor: {profesors}",
                                        style={"marginBottom": "10px"}
                                    ),
                                    # Sección del botón y texto "HISTÓRICO"
                                    html.Div(
                                        [
                                            html.A(
                                                html.I(className="fas fa-chart-line", style={"color": "#007BFF"}),  # Ícono de gráfica
                                                style={
                                                    "border": "2px solid #007BFF",  # Borde azul
                                                    "borderRadius": "5px",
                                                    "cursor": "pointer",
                                                    "color": "#007BFF",  # Texto azul
                                                    "fontWeight": "bold",
                                                    "marginLeft": "8px",
                                                    "textDecoration": "none",
                                                    "display": "block",
                                                    "padding": "4px",
                                                },
                                                href=f"/resumen/{section.get('nrc', '')}",  # Enlace a la página de historial
                                            )
                                        ],
                                        style={"display": "flex", "alignItems": "center", "justifyContent": "space-between"}
                                    )
                                ],                          
                                className="flip-back",
                                style={"backgroundColor": background_color, "color": "black", "padding": "10px"}
                            ),
                        ],
                        className="flip-inner"
                    ),
                    className="event-box",
                    style={
                        "top": f"{top}px",
                        "left": f"{left}%",
                        "height": f"{height}px",
                        "fontSize": "x-small",
                        "backgroundColor": background_color,  # Mantengo el color de fondo original
                    }
                )
                displayed_events.append(new_event)

        # Crear resumen de los eventos
        summary_element = html.Div([
            html.Div(
                f"{section.get('title', '')} - {section.get('nrc', '')} - {section.get('section', '')}",
                className="event-summary"
            ),
            html.Div(
                html.I(className="fas fa-trash-alt"),
                id={'type': 'remove-section', 'index': section.get('nrc', '')}, 
                style={
                    "cursor": "pointer", "color": "red", "borderRadius": "50%", "width": "20px",
                    "height": "20px", "display": "flex", "justifyContent": "center", "alignItems": "center"
                }
            )
        ], style={"display": "grid", "justifyContent": "space-between", "alignItems": "center", "width": "100%", "gridTemplateColumns": "1fr auto", "gap": "10px", "padding": "5px"})
        
        summary_events.append(summary_element)

    # Convertir total_probability a porcentaje
    combined_probability = int(total_probability * 100)

    # Actualizar barra de progreso
    progress_bar = html.Div(
        className="progress",
        style={"height": "20px", "borderRadius": "15px"},
        children=[
            html.Div(
                f"{combined_probability}%",  # Mostrar el porcentaje en la barra
                className="progress-bar progress-bar-striped progress-bar-animated",
                role="progressbar",
                style={"width": f"{combined_probability}%", "backgroundColor": "#F0A500", "color": "#FFF"},
                **{"aria-valuenow": f"{combined_probability}", "aria-valuemin": "0", "aria-valuemax": "100"}
            )
        ]
    )
    
    return displayed_events, summary_events, [progress_bar]


# Callback combinado para añadir o eliminar eventos en el contenedor
@callback(
    [
        Output({'type': 'storage', 'index': 'schedules'}, 'data'),
        Output("plan-list", "children"),
    ],
    [
        Input({'type': 'add-section', 'index': ALL}, 'n_clicks'),
        Input({'type': 'remove-section', 'index': ALL}, 'n_clicks'),
        Input("add-plan", "n_clicks"),
        Input("url", "pathname"),
    ],
    [
        State({'type': 'storage', 'index': 'memory'}, 'data'),
        State({'type': 'storage', 'index': 'schedules'}, 'data'),
    ],
    prevent_initial_call=False
)
def modify_section_in_calendar(add_clicks, remove_clicks, add_plan_clicks, url, courses_by_code, current_events_all_plans):

    # Detecta qué botón fue clicado (agregar o eliminar)
    ctx = dash.callback_context
    add_plan_clicks_updated = any(trigg['prop_id'] == 'add-plan.n_clicks' for trigg in ctx.triggered)
    plan_id = url.split("-")[-1] if url.startswith("/plan-") else None

    #########################
    # CREAR NUEVO PLAN
    #########################

    # Contar el número de planes actuales para nombrar el siguiente
    current_events_all_plans = current_events_all_plans or {}
    if plan_id and plan_id not in current_events_all_plans:
        current_events_all_plans[plan_id] = []

    plan_count = len(current_events_all_plans)

    # Incrementar el contador si se hizo clic en "Crear nuevo plan"
    if add_plan_clicks_updated:
        current_events_all_plans[plan_count + 1] = []

    # Crear los elementos de la lista de planes
    plan_list = [
        html.A([
            html.I(className="fas fa-calendar-alt", style={"marginRight": "10px"}),  # Ícono de calendario
            f"Plan {plan_id_iter}"
        ], href=f"/plan-{plan_id_iter}", style={"color": "inherit", "padding": "8px 8px 8px 32px", "textDecoration": "none", "display": "block"})
        for plan_id_iter in current_events_all_plans.keys()
    ]

    if add_plan_clicks_updated or not ctx.triggered:
        return current_events_all_plans, plan_list

    #########################
    # EDITAR PLAN EXISTENTE
    #########################

    # Obtiene los current events del plan actual, Inicializa la lista de eventos si está vacía
    try:
        current_events = current_events_all_plans.get(plan_id, [])
        triggered_id = json.loads(ctx.triggered[0]['prop_id'].replace(".n_clicks", ""))
        action_type = triggered_id["type"]
        section_nrc = triggered_id["index"]
    except:
        return current_events_all_plans, plan_list

    # Acción de agregar sección
    found = False
    if action_type == "add-section":

        if not any(add_clicks):
            return current_events_all_plans, plan_list

        for course_code, sections in courses_by_code.items():
            if found:
                break
            for section in sections:
                if found:
                    break
                if section.get("nrc", '') == section_nrc:
                    current_events.append(section)
                    found = True


    # Acción de eliminar sección
    elif action_type == "remove-section":

        if not any(remove_clicks):
            return current_events_all_plans, plan_list

        current_events = [
            event for event in current_events if event.get('nrc', '') != section_nrc
        ]

    # Actualizar los eventos del plan actual
    current_events_all_plans[plan_id] = current_events

    return current_events_all_plans, plan_list