import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html
import modules.LiveTracking as LiveTracking
import modules.NextPassage as NextPassage
import modules.FlightTrajectory as FlightTrajectory
import modules.ScientificAnalysis as ScientificAnalysis

app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="PariSat App",
    update_title=None
)

server = app.server

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#CFD8DC",
    "overflow": "hidden",
    "overflow-y": "scroll",
    "-ms-overflow-style": "none",
    "scrollbar-width": "none"
}

sidebar_style = {
    "::-webkit-scrollbar": {
        "display": "none"
    }
}

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "1.5rem",
    "height": "100vh",
    "overflow": "hidden",
    "margin-top": "0",
    "display": "flex",
    "justify-content": "center",
    "align-items": "center",
}

sidebar = html.Div(
    [
        html.Div(
            html.Img(src='/assets/PariSat-Logo.svg',
                     style={'width': '80%', 'height': 'auto', 'margin-bottom': '1rem'}),
            style={'text-align': 'center'}
        ),
        html.Hr(),
        html.P(
            "PariSat App", className="lead", style={"color": "#2C3E50", "font-family": "Roboto", "font-weight": "bold"}
        ),
        dbc.Nav(
            [
                dbc.NavLink("Live Tracking", href="/", active="exact",
                            style={"font-family": "Roboto"}),
                dbc.NavLink("Flight Trajectory", href="/flight-trajectory",
                            active="exact", style={"font-family": "Roboto"}),
                dbc.NavLink("Scientific Analysis", href="/scientific-analysis",
                            active="exact", style={"font-family": "Roboto"}),
                dbc.NavLink("About", href="/about", active="exact",
                            style={"font-family": "Roboto"}),
            ],
            vertical=True,
            pills=True,
        ),
        html.Div(id="live-tracking-input", style={"margin-top": "1rem"})
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)
fig, visibility_traces, _ = FlightTrajectory.ShowOrbit()

app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    content,
    dcc.Interval(id="interval-component", interval=2*1000, n_intervals=0)
], style={"background-color": "#ECEFF1", "min-height": "100vh"})


@app.callback(
    Output("page-content", "children"),
    Output("live-tracking-input", "children"),
    [Input("url", "pathname")]
)
def render_page_content(pathname):
    latitude = 48.8566
    longitude = 2.3522
    elevation = 0.0

    if pathname == "/":
        return (
            dcc.Graph(id='live-tracking-graph', figure=LiveTracking.ShowOrbit(latitude, longitude),
                      style={"height": "90vh", "width": "100%"}, config={'displayModeBar': False}),
            html.Div([
                html.Hr(),
                html.Div([
                    dbc.Row([
                        dbc.Col(html.P("Latitude:", style={
                                "color": "#2C3E50", "font-family": "Roboto", "margin-bottom": "0", "min-width": "5rem"}), width="auto"),
                        dbc.Col(dbc.Input(id="latitude-input", type="number", value=latitude, placeholder="Value", min=-90, max=90, style={
                                "color": "#2C3E50", "font-family": "Roboto", "width": "100%", "background-color": "transparent", "border": "none", "text-align": "right", "appearance": "textfield"}))
                    ], align="center"),
                ]),
                html.Div([
                    dbc.Row([
                        dbc.Col(html.P("Longitude:", style={
                                "color": "#2C3E50", "font-family": "Roboto", "margin-bottom": "0", "min-width": "5rem"}), width="auto"),
                        dbc.Col(dbc.Input(id="longitude-input", type="number", value=longitude, placeholder="Value", min=-180, max=180, style={
                                "color": "#2C3E50", "font-family": "Roboto", "width": "100%", "background-color": "transparent", "border": "none", "text-align": "right", "appearance": "textfield"}))
                    ], align="center"),
                ]),
                html.Div([
                    dbc.Row([
                        dbc.Col(html.P("Elevation:", style={
                                "color": "#2C3E50", "font-family": "Roboto", "margin-bottom": "0", "min-width": "5rem"}), width="auto"),
                        dbc.Col(dbc.Input(id="elevation-input", type="number", value=elevation, placeholder="Value", min=0, max=90, style={
                                "color": "#2C3E50", "font-family": "Roboto", "width": "100%", "background-color": "transparent", "border": "none", "text-align": "right", "appearance": "textfield"}))
                    ], align="center"),
                ]),
                html.Hr(),
                dbc.Button(
                    [
                        "Next Pass ",
                        html.Span("▶", id="triangle-icon", style={
                                  "display": "inline-block", "transition": "transform 0.3s ease"})
                    ],
                    id="collapse-button",
                    color="primary",
                    n_clicks=0,
                    style={"margin-bottom": "1rem", "background-color": "#2C3E50",
                           "border": "none", "color": "#ECEFF1", "font-family": "Roboto"}
                ),
                dbc.Collapse(
                    html.Div(id="next-pass-info",
                             children="Informations sur le prochain passage"),
                    id="collapse",
                    is_open=False
                )
            ])
        )
    elif pathname == "/flight-trajectory":
        return (
            html.Div([
                dcc.Graph(
                    id='flight-trajectory-graph',
                    figure=fig,
                    style={"height": "100%", "width": "100%"},
                    config={'displayModeBar': False},
                    clear_on_unhover=True
                ),
                html.Div(id='photo-image-container')
            ], style={"height": "90vh", "width": "100%"}), html.Div([
                html.Hr(),
                dbc.Row([
                    dbc.Col(html.P("Liftoff (T0):", style={
                            "color": "#2C3E50", "font-family": "Roboto"}), width="auto"),
                    dbc.Col(html.P([
                        "2024-07-09",
                        html.Br(),
                        "19:00:00 UTC"
                    ]), style={"text-align": "right", "color": "#2C3E50", "font-family": "Roboto"})
                ], align="center"),
                dbc.Row([
                    dbc.Col(html.P("Initialization:", style={
                            "color": "#2C3E50", "font-family": "Roboto"}), width="auto"),
                    dbc.Col(html.P([
                        "2024-07-09",
                        html.Br(),
                        "20:06:03 UTC"
                    ]), style={"text-align": "right", "color": "#2C3E50", "font-family": "Roboto"})
                ], align="center"),
            ])
        )
    elif pathname == "/scientific-analysis":
        return (
            dcc.Graph(
                id='scientific-analysis-graph',
                figure=ScientificAnalysis.ScientificPlot(),
                style={"height": "90vh", "width": "100%"},
                config={'displaylogo': False, 'scrollZoom': True},
            ), html.Div([
                html.Hr(),
                dbc.Row([
                    dbc.Col(html.P("Liftoff (T0):", style={
                            "color": "#2C3E50", "font-family": "Roboto"}), width="auto"),
                    dbc.Col(html.P([
                        "2024-07-09",
                        html.Br(),
                        "19:00:00 UTC"
                    ]), style={"text-align": "right", "color": "#2C3E50", "font-family": "Roboto"})
                ], align="center"),
                dbc.Row([
                    dbc.Col(html.P("Initialization:", style={
                            "color": "#2C3E50", "font-family": "Roboto"}), width="auto"),
                    dbc.Col(html.P([
                        "2024-07-09",
                        html.Br(),
                        "20:06:03 UTC"
                    ]), style={"text-align": "right", "color": "#2C3E50", "font-family": "Roboto"})
                ], align="center"),
            ])
        )
    elif pathname == "/about":
        return (
            html.Div([
                html.Div([
                    html.Img(
                        src='/assets/PariSat.png',
                        style={
                            "width": "100%",
                            "height": "auto"
                        }
                    )
                ], style={
                    "width": "50%",
                    "display": "inline-block",
                    "marginRight": "5%",
                }),
                html.Div([
                    dcc.Markdown(
                        open("assets/PariSatPresentation-EN.md",
                             encoding="utf-8").read(),
                        style={
                            "white-space": "pre-line",
                            "color": "#2C3E50",
                            "font-family": "Roboto"
                        }
                    )
                ], className="markdown-container", style={
                    "width": "50%",
                    "display": "inline-block",
                })
            ], style={
                "display": "flex",
                "alignItems": "center",
                "height": "100vh",
            }), html.Div([
                html.Hr(),
                dbc.Button(
                    [html.I(className="bi bi-file-earmark-arrow-down", style={
                            "margin-right": "0.5rem", "color": "#ECEFF1"}), "Experiment Report"],
                    id="download-report-button",
                    color="primary",
                    style={"background-color": "#2C3E50", "border": "none",
                           "color": "#ECEFF1", "font-family": "Roboto"},
                ),
                dcc.Download(id="download-report"),
            ])
        )

    return (
        html.Div(
            [
                html.H1("404: Not found", className="text-danger"),
                html.Hr(),
                html.P(f"The pathname {pathname} was not recognised..."),
            ],
            className="p-3",
            style={"background-color": "#CFD8DC", "border-radius": "1rem"},
        ),
        None
    )


@app.callback(
    Output("next-pass-info", "children"),
    [Input("latitude-input", "value"),
     Input("longitude-input", "value"),
     Input("elevation-input", "value")]
)
def update_next_pass(latitude, longitude, elevation):
    next_pass_info = NextPassage.NextPass(latitude, longitude, elevation)
    rise_time, culminate_time, set_time, culmination_azimuth, culmination_elevation, culmination_distance = next_pass_info
    if all([rise_time, culminate_time, set_time]):
        return html.Div([
            dbc.Row([
                dbc.Col(html.P("Rise:", style={
                        "color": "#2C3E50", "font-family": "Roboto"}), width="auto"),
                dbc.Col(html.P([
                    rise_time.strftime('%Y-%m-%d'),
                    html.Br(),
                    rise_time.strftime('%H:%M:%S %Z')
                ]), style={"text-align": "right", "color": "#2C3E50", "font-family": "Roboto"})
            ], align="center"),
            dbc.Row([
                dbc.Col(html.P("Culmination:", style={
                        "color": "#2C3E50", "font-family": "Roboto"}), width="auto"),
                dbc.Col(html.P([
                    culminate_time.strftime('%Y-%m-%d'),
                    html.Br(),
                    culminate_time.strftime('%H:%M:%S %Z')
                ]), style={"text-align": "right", "color": "#2C3E50", "font-family": "Roboto"})
            ], align="center"),
            dbc.Row([
                dbc.Col(html.P("Set:", style={
                        "color": "#2C3E50", "font-family": "Roboto"}), width="auto"),
                dbc.Col(html.P([
                    set_time.strftime('%Y-%m-%d'),
                    html.Br(),
                    set_time.strftime('%H:%M:%S %Z')
                ]), style={"text-align": "right", "color": "#2C3E50", "font-family": "Roboto"})
            ], align="center"),
            dbc.Row([
                dbc.Col(html.P("Azimuth:", style={
                        "color": "#2C3E50", "font-family": "Roboto"}), width="auto"),
                dbc.Col(html.P([f"{culmination_azimuth}°"], style={
                        "text-align": "right", "color": "#2C3E50", "font-family": "Roboto"}))
            ]),
            dbc.Row([
                dbc.Col(html.P("Elevation:", style={
                        "color": "#2C3E50", "font-family": "Roboto"}), width="auto"),
                dbc.Col(html.P(f"{culmination_elevation}°", style={
                        "text-align": "right", "color": "#2C3E50", "font-family": "Roboto"}))
            ]),
            dbc.Row([
                dbc.Col(html.P("Distance:", style={
                        "color": "#2C3E50", "font-family": "Roboto"}), width="auto"),
                dbc.Col(html.P(f"{culmination_distance} km", style={
                        "text-align": "right", "color": "#2C3E50", "font-family": "Roboto"}))
            ])
        ])
    else:
        return html.P("No pass in the next 72 hours")


@app.callback(
    Output("collapse", "is_open"),
    Output("triangle-icon", "style"),
    Input("collapse-button", "n_clicks"),
    Input("collapse", "is_open")
)
def toggle_collapse(n_clicks, is_open):
    if n_clicks:
        new_state = not is_open
        rotation_style = {
            "display": "inline-block",
            "transition": "transform 0.3s ease",
            "transform": "rotate(90deg)" if new_state else "rotate(0deg)"
        }
        return new_state, rotation_style
    return is_open, {"display": "inline-block", "transition": "transform 0.3s ease"}


@app.callback(
    Output("live-tracking-graph", "figure"),
    [Input("latitude-input", "value"),
     Input("longitude-input", "value"),
     Input("interval-component", "n_intervals")]
)
def update_orbit(latitude, longitude, n_intervals):
    latitude = latitude if latitude is not None else 48.8566
    longitude = longitude if longitude is not None else 2.3522
    return LiveTracking.ShowOrbit(latitude, longitude)


@app.callback(
    [Output('flight-trajectory-graph', 'figure'),
     Output('photo-image-container', 'children'),
     Output('photo-image-container', 'style')],
    [Input('flight-trajectory-graph', 'hoverData')]
)
def display_hover_data(hoverData):
    for idx in visibility_traces:
        fig.data[idx].visible = False
    image_content = None
    image_style = {'display': 'none'}
    if hoverData:
        for point in hoverData.get('points', []):
            if 'customdata' in point:
                x = point['bbox']['x1']
                y = point['bbox']['y1']
                transform = ''
                if "Photo n°" in point['customdata']:
                    photo_number = int(point['customdata'].split("n°")[-1])
                    visibility_idx = visibility_traces[photo_number - 1]
                    fig.data[visibility_idx].visible = True
                    image_path = f"assets/photos/photo_{photo_number}.jpg"
                    image_time = [4166, 4297, 4565, 4925,
                                  4963, 5006, 5758, 6118, 6522, 6560]
                    image_content = html.Div([
                        html.P(f"Photo n°{photo_number} • T0+{image_time[photo_number-1]}s", style={
                               'color': '#2C3E50', 'font-family': 'Roboto', 'margin': '0'}),
                        html.Img(src=image_path, style={
                                 'width': '20rem', 'height': 'auto', 'margin-top': '0.5rem'})
                    ], style={'background-color': 'rgba(207, 216, 220, 0.5)', 'padding': '0.5rem', 'border-radius': '0.5rem'})
                    if photo_number in {1, 2}:
                        x = point['bbox']['x0']
                        y = point['bbox']['y0']
                        transform = 'translate(-100%, -100%)'
                    elif photo_number in {3, 4, 5, 6}:
                        y = point['bbox']['y0']
                        transform = 'translateY(-100%)'
                else:
                    image_path = f"assets/photos/{point['customdata'][0]}.jpg"
                    image_content = html.Div([
                        html.P(f"{point['customdata'][1]}", style={
                               'color': '#2C3E50', 'font-family': 'Roboto', 'margin': '0'}),
                        html.Img(src=image_path, style={
                                 'width': '20rem', 'height': 'auto', 'margin-top': '0.5rem'})
                    ], style={'background-color': 'rgba(207, 216, 220, 0.5)', 'padding': '0.5rem', 'border-radius': '0.5rem'})
                image_style = {'position': 'absolute',
                               'zIndex': 100, 'pointerEvents': 'none'}
                image_style['left'] = f"{x}px"
                image_style['top'] = f"{y}px"
                image_style['transform'] = transform
    return fig, image_content, image_style


@app.callback(
    Output("download-report", "data"),
    Input("download-report-button", "n_clicks"),
    prevent_initial_call=True
)
def download_report(n_clicks):
    if n_clicks:
        return dcc.send_file("assets/GD2143A002-1.5 Rapport d'expérience PariSat.pdf")


if __name__ == "__main__":
    app.run_server(debug=True)
