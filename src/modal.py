from dash import html, dcc
import dash_bootstrap_components as dbc

# Modal de búsuqueda de cursos
modal = html.Div(
    dbc.Modal(
        [
            dbc.ModalBody(
              html.Div([
                html.Div([
                    html.H3("Buscar cursos", style={"marginBottom": "20px"}),
                    html.Div(id="search-section", children=[
                        # Barra de búsqueda
                        dcc.Input(id="search-input", type="text", placeholder="IIND1000, NRC o Nombre", className="search-form-control"),
                        
                        # Botón para buscar
                        html.Button([
                            html.I(className="fas fa-search", style={"color": "#B6B6B6"}),
                        ], id="search-btn-api", n_clicks=0, style={"border": "none", "backgroundColor": "transparent", "cursor": "pointer"}),
                    ], className="search-box"),
                    html.Div(id="search-detail", style={"display": "none", "height": "360px", "padding": "20px 0", "textAlign": "center", "display": "flex", "alignItems": "center", "color": "#AAAAAA", "flexDirection": "column", "overflowY": "scroll", "gap": "10px", "margin": "10px 0", "width": "100%"}),
                    html.Div([
                      "Aquí puedes buscar cursos para añadir a tu plan.",
                    ], id="search-results", style={"height": "360px", "padding": "20px 0", "textAlign": "center", "display": "flex", "alignItems": "center", "color": "#AAAAAA", "flexDirection": "column", "overflowY": "scroll", "gap": "10px", "margin": "10px 0", "width": "100%"}),
                ], style={"width": "50%", "display": "flex", "flexDirection": "column", "justifyContent": "start", "alignItems": "center", "marginTop": "20px"}),
                html.Div("", style={"height": "100%", "width": "1px", "backgroundColor": "#B6B6B6", "margin": "0 10px"}),
                html.Div([
                    html.H3("Plan Actual", style={"marginBottom": "20px"}),
                    html.Div([
                        "Aquí puedes ver tus cursos añadidos.",
                        ], id="current-plan", style={"height": "400px", "padding": "20px 0", "textAlign": "center", "display": "flex", "alignItems": "center", "color": "#AAAAAA", "flexDirection": "column", "overflowY": "scroll", "gap": "10px", "margin": "10px 0", "width": "100%"}),
                ], style={"width": "50%", "display": "flex", "flexDirection": "column", "justifyContent": "start", "alignItems": "center", "marginTop": "20px"}),
              ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "start", "height": "500px", "overflow": "hidden"}),
            ),
        ],
        id="modal",
        is_open=False,  # Inicialmente oculto
        centered=True,
        size="xl",  # Tamaño grande
    )
)