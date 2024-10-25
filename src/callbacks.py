from dash import Input, Output, State, callback, html, dcc, MATCH, ALL
import dash_bootstrap_components as dbc
import random
import requests
import dash
import json
from plan import create_plan_page

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
    if pathname == "/":
        return html.H1("Página inicial")
    if pathname == "/resumen":
        return html.H1("Resumen de la Aplicación")
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
                    "schedules": schedules
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
            ], style={"display":"grid", "grid-template-columns": "1fr auto", "gap": "10px"} )
        )

    # Cambiar estilos para mostrar detalles y ocultar resultados de búsqueda
    search_detail_style["display"] = "block"
    search_results_style["display"] = "none"
    
    return section_rows, search_detail_style, search_results_style


@callback(
    [
        Output("events-container", "children"),
        Output("current-plan", "children"),
    ],
    Input({'type': 'storage', 'index': 'local'}, 'data'),
)
def update_events(events):

    if not events:
        return [], []
    
    summary_events = []
    displayed_events = []
    for section in events:
        for schedule in section['schedules']:
            # Asignamos el día, la hora de inicio y de fin
            # Tomamos todos los días
            for day in schedule['days'].split(','):
                start_time_min = int(schedule['time_ini'][:2]) * 60 + int(schedule['time_ini'][-2:])
                end_time_min = int(schedule['time_fin'][:2]) * 60 + int(schedule['time_fin'][-2:])
                duration_min = end_time_min - start_time_min

                # Calculamos la posición y tamaño del evento
                total_days = 6  # Número de días de la semana visibles
                calendar_height = 680  # Alto del contenedor del calendario
                time_span = 16 * 60  # Rango de horas visible (ejemplo: 6 AM - 10 PM)
                time_zero = 6 * 60  # Hora mínima visible (6 AM)

                top = (start_time_min - time_zero) * calendar_height / time_span
                left = (["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"].index(day)) / total_days * 100
                height = duration_min * calendar_height / time_span

                # Creamos un nuevo evento
                new_event = html.Div(
                    f"{section['nrc']} - {section['section']} - 90%",
                    className="event-box",
                    style={
                        "position": "absolute",
                        "top": f"{top}px",
                        "left": f"{left}%",
                        "height": f"{height}px",
                        "fontSize": "x-small"
                    }
                )
                displayed_events.append(new_event)

        # Creamos un resumen de los eventos
        summary_element = html.Div([
            html.Div(
                f"{section['title']} - {section['nrc']} - {section['section']}",
                className="event-summary"
            ),
            html.Div("X", id={'type': 'remove-section', 'index': section['nrc']}, style={"cursor": "pointer", "backgroundColor": "red", "color": "white", "borderRadius": "50%", "width": "20px", "height": "20px", "display": "flex", "justifyContent": "center", "alignItems": "center"})
        ], style={"display": "grid", "justifyContent": "space-between", "alignItems": "center", "width": "100%", "gridTemplateColumns": "1fr auto", "gap": "10px", "padding": "5px"})
        summary_events.append(summary_element)
            
    return displayed_events, summary_events


@callback(
    [
        Output("progress-panel", "children"),
    ],
    Input({'type': 'storage', 'index': 'local'}, 'data'),
    prevent_initial_call=True
)
def update_progress_bar(events):
    percentage = random.randint(0, 100)
    return [html.Div(
        className="progress",
        style={"height": "20px", "borderRadius": "15px"},
        children=[
            html.Div(
                f"{percentage}%",  # Este texto será mostrado dentro de la barra
                className="progress-bar progress-bar-striped progress-bar-animated",
                role="progressbar",
                style={"width": f"{percentage}%", "backgroundColor": "#F0A500", "color": "#FFF"},  # Color personalizado y ancho del progreso
                **{"aria-valuenow": f"{percentage}", "aria-valuemin": "0", "aria-valuemax": "100"}
            )
        ]
    )]



# Callback combinado para añadir o eliminar eventos en el contenedor
@callback(
    Output({'type': 'storage', 'index': 'local'}, 'data'),
    [
        Input({'type': 'add-section', 'index': ALL}, 'n_clicks'),
        Input({'type': 'remove-section', 'index': ALL}, 'n_clicks')
    ],
    [
        State({'type': 'storage', 'index': 'memory'}, 'data'),
        State({'type': 'storage', 'index': 'local'}, 'data')
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


# # Callback para añadir eventos al contenedor cuando se hace clic en el botón "+"
# @callback(
#     [Output({'type': 'storage', 'index': 'local'}, 'data')],
#     [Input({'type': 'add-section', 'index': ALL}, 'n_clicks')],
#     [
#         State({'type': 'storage', 'index': 'memory'}, 'data'),
#         State({'type': 'storage', 'index': 'local'}, 'data'),
#     ],
#     prevent_initial_call=True
# )
# def add_section_to_calendar(n_clicks, courses_by_code, current_events):

#     # Inicializamos `current_events` como lista si es None o no es una lista
#     if current_events is None:
#         current_events = []

#     if not any(n_clicks):
#         return [current_events] if current_events else [[]]

#     # Obtenemos el contexto de qué botón fue clicado
#     ctx = dash.callback_context
#     triggered_id = ctx.triggered[0]['prop_id'].replace(".n_clicks", "")
#     section_nrc = json.loads(triggered_id)["index"]

#     # Busca la sección correspondiente en el almacenamiento
#     for course_code, sections in courses_by_code.items():
#         for section in sections:
#             if section["nrc"] == section_nrc:
#                 # Añadimos el nuevo evento al contenedor
#                 current_events.append(section)

#                 return [current_events] if current_events else [[]]

#     return [current_events] if current_events else [[]]


# # Callback para realizar la búsqueda y agregar eventos con base en el horario de 'schedules'
# @callback(
#     Output('calendar-events', 'children'),
#     Input({'type': 'add-event', 'index': ALL}, 'n_clicks'),
#     State('calendar-events', 'children'),
#     State('search-input', 'value')
# )
# def add_scheduled_event(n_clicks, current_events, search_value):
#     if any(n_clicks) and search_value:
#         # Hacer la petición a la API de búsqueda de cursos
#         search_value = search_value.upper().strip()
#         url = f'https://ofertadecursos.uniandes.edu.co/api/courses?nameInput={search_value}'
#         response = requests.get(url)
        
#         if response.status_code == 200:
#             courses_data = response.json()
            
#             # Tomamos el primer curso (puedes cambiar esto para manejar más cursos)
#             course = courses_data[0]
            
#             # Extraer el título y el horario del curso
#             course_title = course["title"]
#             schedules = course["schedules"]

#             # Agregar eventos basados en el horario de 'schedules'
#             for schedule in schedules:
#                 time_ini = int(schedule["time_ini"][:2]) - 6  # Restamos 6 para ajustar el rango a las 6 AM
#                 time_fin = int(schedule["time_fin"][:2]) - 6
#                 classroom = schedule["classroom"]
                
#                 # Crear eventos para los días de la semana donde esté el curso
#                 for day_key, day_name in days_of_week.items():
#                     if schedule.get(day_key):  # Verifica si el curso está en ese día ('l', 'm', 'i', 'j', 'v', 's')
#                         # Calcular la posición y altura del evento
#                         top_position = (time_ini - 6) * 45  # Ajustamos el cálculo para que empiece desde 6 AM
#                         event_height = (time_fin - time_ini) * 45  # Altura basada en la duración del evento
                        
#                         # Ajustar el evento al día correcto en términos de columna
#                         day_position = list(days_of_week.keys()).index(day_key) * (100 / len(days_of_week))  # Porcentaje del ancho de la columna

#                         # Crear el evento para ese día y agregarlo al calendario
#                         new_event = html.Div(
#                             f"{course_title} ({classroom})", 
#                             className="event-box",
#                             style={
#                                 "top": f"{top_position}px", 
#                                 "height": f"{event_height}px",
#                                 "position": "absolute",
#                                 "left": f"{day_position}%",  # Posición en la columna del día
#                                 "width": f"{100 / len(days_of_week) - 2}%",  # Ajuste del ancho del evento con margen
#                                 "background-color": "#FFDDC1",
#                                 "border-radius": "8px",
#                                 "padding": "5px",
#                                 "text-align": "center",
#                                 "box-sizing": "border-box",  # Incluir padding y border en el ancho y alto
#                                 "margin-left": "1%",  # Margen izquierdo para separar eventos
#                                 "margin-right": "1%"  # Margen derecho para separar eventos
#                             }
#                         )
#                         current_events.append(new_event)
        
#         return current_events

#     return current_events
