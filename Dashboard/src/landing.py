from dash import html, dcc

landing = html.Div(
    style={
        "display": "flex",
        "flexDirection": "column",
        "alignItems": "center",
        "justifyContent": "center",
        "height": "100vh",
        "backgroundColor": "#f5f5f5",
        "padding": "20px",
        "gap": "10px",
    },
    children=[
      
        # IDS no utilizados en esta página, previenen errores de id not found en callbacks
        html.Div(id="events-container", style={"display": "none"}),
        html.Div(id="progress-panel", style={"display": "none"}),

        # Imagen de la mascota
        html.Img(
            src="assets/Logo_Hadas.png",  # Asegúrate de tener la imagen en la carpeta 'assets'
            style={"width": "150px", "marginBottom": "10px"},
        ),

        # Encabezado y bienvenida
        html.H1("¡Bienvenid@ a Wizard Séneca!", style={"textAlign": "center", "color": "#333", "fontSize": "36px"}),

        # Descripción del sistema
        html.P(
            "Aquí tendrás la oportunidad de planear tu horario académico ideal y conocer de antemano si "
            "con tu turno de inscripción lograrás inscribirlo o no. Wizard Séneca es tu herramienta personalizada "
            "para optimizar el proceso de inscripción de materias.",
            style={"textAlign": "center", "color": "#555", "maxWidth": "600px"},
        ),
        html.P(
            "Podrás explorar diferentes combinaciones de horarios, recibir recomendaciones basadas en tus "
            "preferencias y asegurarte de que tu plan se ajuste a tus necesidades. Olvídate del estrés de no "
            "saber si alcanzarás un cupo en tu clase preferida; con Wizard Séneca, estarás un paso adelante y podrás "
            "tomar decisiones informadas para aprovechar al máximo tu experiencia académica.",
            style={"textAlign": "center", "color": "#555", "maxWidth": "600px"},
        ),

        # Sección para ingresar el turno
        html.Div(
            style={
                "textAlign": "center",
                "color": "#333",
                "marginTop": "10px",
                "fontSize": "24px",
            },
            children="Ingresa tu turno",
        ),

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
                dcc.Input(
                    type="number", id="input-day", placeholder="DD", min=1, max=31, 
                    style={
                        "width": "50px", "textAlign": "center", 
                        "borderRadius": "10px", "backgroundColor": "#F5F5F5", "fontSize": "14px"
                    }
                ),
                # Mes
                dcc.Input(
                    type="number", id="input-month", placeholder="MM", min=1, max=12,
                    style={
                        "width": "50px", "textAlign": "center",
                        "borderRadius": "10px", "backgroundColor": "#F5F5F5", "fontSize": "14px"
                    }
                ),
                # Año
                dcc.Input(
                    type="number", id="input-year", placeholder="AAAA", min=1900, max=2100,
                    style={
                        "width": "60px", "textAlign": "center",
                        "borderRadius": "10px", "backgroundColor": "#F5F5F5", "fontSize": "14px"
                    }
                ),
                # Hora
                html.Div(
                    children=[
                        dcc.Input(
                            type="number", id="input-hour", placeholder="HH", min=0, max=23,
                            style={
                                "width": "45px", "textAlign": "center",
                                "borderRadius": "10px", "backgroundColor": "#F5F5F5", "fontSize": "12px"
                            }
                        ),
                        html.Span(":", style={"margin": "0 5px"}),
                        dcc.Input(
                            type="number", id="input-minute", placeholder="MM", min=0, max=59,
                            style={
                                "width": "45px", "textAlign": "center",
                                "borderRadius": "10px", "backgroundColor": "#F5F5F5", "fontSize": "12px"
                            }
                        )
                    ],
                    style={"display": "flex", "alignItems": "center"}
                ),
            ]
        ),

        # Botón de guardar
        html.A(
            "Ingresar",  # Texto del botón
            style={
                "backgroundColor": "#F0A500",
                "color": "#fff",
                "border": "none",
                "borderRadius": "20px",
                "padding": "10px 20px",
                "fontSize": "16px",
                "cursor": "pointer",
                "textDecoration": "none",
                "display": "block",
            },
            id="position-set-button",  # ID del botón para el callback
            href="#"  # Redirige a la página de planificación
        )
    ]
)