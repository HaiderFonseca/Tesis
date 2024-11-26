from dash import Input, Output, State, callback, html, dcc, MATCH, ALL
import dash_bootstrap_components as dbc
import random
import requests
import dash
import json
from plan import create_plan_page
from landing import landing
from summary import create_summary_page
from model import predict_course_probability, Course, FIRST_ENROLLMENT_TIME
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from dash.exceptions import PreventUpdate


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


# Callback para agregar un nuevo plan al hacer clic en "Crear nuevo plan"
@callback(
    Output("plan-list", "children"),
    Input("add-plan", "n_clicks"),
    State("plan-list", "children"),
    prevent_initial_call=True
)
def add_new_plan(n_clicks, current_plans):
    # Contar el número de planes actuales para nombrar el siguiente
    plan_count = len(current_plans) + 1

    # Crear el nuevo plan con su ícono de calendario
    new_plan = html.A([
        html.I(className="fas fa-calendar-alt", style={"marginRight": "10px"}),  # Ícono de calendario
        f"Plan {plan_count}"
    ], href=f"/plan-{plan_count}", style={"color": "inherit", "padding": "8px 8px 8px 32px", "textDecoration": "none", "display": "block"})

    # Agregar el nuevo plan a la lista actual
    return current_plans + [new_plan]


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
        url = f'https://ofertadecursos.uniandes.edu.co/api/courses?nameInput={search_value}'
        response = requests.get(url)

        if response.status_code == 200:
            courses_data = response.json()
            
            # Agrupar los cursos por course_code
            courses_by_code = {}
            for course in courses_data:
                course_code = f"{course['class']}{course['course']}"
                if course_code not in courses_by_code:
                    courses_by_code[course_code] = []
                
                schedules = []
                for schedule in course["schedules"]:
                    days = []
                    for day_key, day_name in days_of_week.items():
                        if schedule.get(day_key):
                            days.append(day_name)
                    schedules.append({
                        "days": ",".join(days),
                        "time_ini": schedule["time_ini"],
                        "time_fin": schedule["time_fin"],
                        "classroom": schedule["classroom"]
                    })

                course = {
                    "title": course["title"],
                    "section": course["section"],
                    "nrc": course["nrc"],
                    "credits": course["credits"],
                    "instructors": list(map(lambda i: i["name"], course["instructors"])),
                    "schedules": schedules,
                    "course_level":int(course['course'][0]),
                    "course_class":course['class'],
                    "ptrmdesc":course['ptrmdesc']
                }
                courses_by_code[course_code].append(course)


            # Crear una lista de filas con la información de los cursos
            course_rows = []
            for code, courses in courses_by_code.items():
                course_rows.append(
                    html.Div([
                        f"{code} - {courses[0]['title']}",
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
    sections = courses_by_code[course_code]
    
    # Crear detalles de las secciones
    section_rows = []
    for section in sections:
        section_rows.append(
            html.Div([
                html.Div([
                    f"NRC {section['nrc']}    Sección {section['section']}",
                    html.P(section['instructors'][0]),
                    html.P(f"{section['schedules'][0]['days']}  {section['schedules'][0]['time_ini']} - {section['schedules'][0]['time_fin']}"),

                ], style={"borderRadius": "20px", "padding": "5px", "backgroundColor": "#f0f0f0", "margin": "10px 0", "display": "flex", "flexDirection":"column" , "justifyContent": "space-between", "alignItems": "center"}),
                html.Div([
                    # Botón de agregar
                    html.Button([
                        html.I(className="fas fa-plus", style={"color": "orange"}),
                    ], id={'type': 'add-section', 'index': section['nrc']}, n_clicks=0, style={"border": "none", "backgroundColor": "transparent", "cursor": "pointer", "float": "right"}),
                ], style={"borderRadius": "20px", "padding": "10px", "backgroundColor": "#f0f0f0", "margin": "10px 0", "display": "flex", "flexDirection":"column" , "justifyContent": "center", "alignItems": "center"})
            ], style={"display":"grid", "gridTemplateColumns": "1fr auto", "gap": "10px"} )
        )

    # Cambiar estilos para mostrar detalles y ocultar resultados de búsqueda
    search_detail_style["display"] = "block"
    search_results_style["display"] = "none"
    
    return section_rows, search_detail_style, search_results_style



# Unificación de los callbacks
@callback(
    [
        Output("events-container", "children"),
        Output("current-plan", "children"),
        Output("progress-panel", "children"),
    ],
    [
        Input({'type': 'storage', 'index': 'schedules'}, 'data'),
        Input({'type': 'storage', 'index': 'position'}, 'data')
    ],
    
)
def update_dashboard(schedules_data, position):
    if not schedules_data or not position:
        return [], dash.no_update, []
    

    
    summary_events = []
    displayed_events = []
    total_probability = 1  # Probabilidad combinada de inscribir todos los cursos
    position = pd.Timestamp(position)


    # Procesar cada curso en schedules
    for section in schedules_data:
        # Crear una instancia de Course para cada curso
        course = Course(
            nrc=section['nrc'],
            schedules=section['schedules'],
            course_level=section['course_level'],
            course_class=section['course_class'],
            ptrmdesc=section['ptrmdesc'],
            first_enrollment_time=FIRST_ENROLLMENT_TIME
        )
       

        # Calcular la probabilidad de inscripción para el curso y el tiempo esperado de llenado
        probability, expected_fill_time = predict_course_probability(course, position)
        print(f"Probabilidad de inscripción para el curso {course.nrc}: {probability}")
        print(f"Tiempo esperado de llenado del curso {course.nrc}: {expected_fill_time}")

        # Multiplicar la probabilidad al total
        total_probability *= probability

        print(section.keys())

        # Crear eventos y resumen de eventos
        for schedule in section['schedules']:
            for day in schedule['days'].split(','):
                start_time_min = int(schedule['time_ini'][:2]) * 60 + int(schedule['time_ini'][-2:])
                end_time_min = int(schedule['time_fin'][:2]) * 60 + int(schedule['time_fin'][-2:])
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
                background_color = get_color_from_probability(1 - probability)
                profesors = ", ".join(section['instructors'])
                alert_emoji = "⚠ " if probability < 0.5 else ""
                
                # Crear nuevo evento con animación de flip card
                new_event = html.Div(
                    html.Div(
                        [
                            # Lado frontal de la tarjeta
                            html.Div(
                                f"{alert_emoji}{section['title']} - sección: {section['section']} - Probabilidad: {int(probability * 100)}%",
                                className="flip-front",
                                style={"backgroundColor": background_color, "color": "black"}
                            ),
                            # Lado trasero de la tarjeta
                            html.Div(
                                f"Esperado: {expected_fill_time.strftime('%Y-%m-%d %H:%M') if expected_fill_time else 'No disponible'} \n Profesor: {profesors}",
                                className="flip-back",
                                style={"backgroundColor": background_color, "color": "black"}
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
                f"{section['title']} - {section['nrc']} - {section['section']}",
                className="event-summary"
            ),
            html.Div(
                html.I(className="fas fa-trash-alt"),
                id={'type': 'remove-section', 'index': section['nrc']}, 
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
    Output({'type': 'storage', 'index': 'schedules'}, 'data'),
    [
        Input({'type': 'add-section', 'index': ALL}, 'n_clicks'),
        Input({'type': 'remove-section', 'index': ALL}, 'n_clicks')
    ],
    [
        State({'type': 'storage', 'index': 'memory'}, 'data'),
        State({'type': 'storage', 'index': 'schedules'}, 'data')
    ],
    prevent_initial_call=True
)
def modify_section_in_calendar(add_clicks, remove_clicks, courses_by_code, current_events):

    # Inicializa la lista de eventos si está vacía
    if current_events is None:
        current_events = []

    # Detecta qué botón fue clicado (agregar o eliminar)
    ctx = dash.callback_context
    if not ctx.triggered:
        return current_events

    triggered_id = json.loads(ctx.triggered[0]['prop_id'].replace(".n_clicks", ""))
    action_type = triggered_id["type"]
    section_nrc = triggered_id["index"]

    # Acción de agregar sección
    found = False
    if action_type == "add-section":

        if not any(add_clicks):
            return current_events

        for course_code, sections in courses_by_code.items():
            if found:
                break
            for section in sections:
                if found:
                    break
                if section["nrc"] == section_nrc:
                    current_events.append(section)
                    found = True


    # Acción de eliminar sección
    elif action_type == "remove-section":

        if not any(remove_clicks):
            return current_events

        current_events = [
            event for event in current_events if event['nrc'] != section_nrc
        ]

    return current_events



# Callback unificado para guardar y cargar el turno de inscripción como timestamp
@callback(
    [
        Output({'type': 'storage', 'index': 'position'}, 'data'),  # Guardar en dcc.Store
        Output('input-day', 'value'),
        Output('input-month', 'value'),
        Output('input-year', 'value'),
        Output('input-hour', 'value'),
        Output('input-minute', 'value')
    ],
    [
        Input('position-set-button', 'n_clicks'),  # Botón para establecer el turno
        Input({'type': 'storage', 'index': 'position'}, 'data')  # Al cargar los datos del local storage
    ],
    [
        State('input-day', 'value'),
        State('input-month', 'value'),
        State('input-year', 'value'),
        State('input-hour', 'value'),
        State('input-minute', 'value')
    ],
    prevent_initial_call=True  # Evitar que se ejecute al inicio sin interacción
)
def handle_position(n_clicks=None, stored_position=None, day=1, month=1, year=2024, hour=0, minute=0):
    ctx = dash.callback_context

    # Si se hace clic en el botón, guarda el turno como timestamp en local storage
    if ctx.triggered and ctx.triggered[0]['prop_id'] == 'position-set-button.n_clicks' and n_clicks:
        # Convertir los valores de día, mes, año, hora y minuto a timestamp
        position_timestamp = pd.Timestamp(year=int(year), month=int(month), day=int(day), hour=int(hour), minute=int(minute))
        return position_timestamp.isoformat(), day, month, year, hour, minute

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
            stored_timestamp.minute
        )

    # Si no hay datos, devolvemos valores vacíos
    return dash.no_update, '', '', '', '', ''