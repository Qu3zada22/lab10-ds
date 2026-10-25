"""Punto de entrada del tablero: Observatorio de Turismo Sostenible, Tikal y Flores (Petén).

Ejecutar con:  uv run python app.py   y abrir http://127.0.0.1:8050
"""

import dash
from dash import Dash, Input, Output, dcc, html

from src import tema  # noqa: F401  (registra la plantilla de Plotly)

app = Dash(
    __name__,
    use_pages=True,
    title="Observatorio · Tikal y Flores",
    suppress_callback_exceptions=True,
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
    ],
)

app.layout = html.Div(
    [
        dcc.Location(id="url"),
        html.Header(
            className="barra",
            children=[
                html.Div(
                    className="marca",
                    children=[
                        html.Span("Observatorio de Turismo Sostenible", className="marca-nombre"),
                        html.Span("Tikal y Flores · Petén", className="marca-destino"),
                    ],
                ),
                html.Nav(id="navegacion", className="navegacion", **{"aria-label": "Secciones"}),
            ],
        ),
        html.Main(dash.page_container, className="principal"),
        html.Footer(
            "Datos proporcionados por INGUAT para el Observatorio · Laboratorio 10 · CC3066 Data Science · "
            "UVG · Grupo 2",
            className="pie",
        ),
    ]
)


@app.callback(Output("navegacion", "children"), Input("url", "pathname"))
def marcar_pagina_activa(ruta):
    return [
        dcc.Link(
            pagina["name"], href=pagina["relative_path"],
            className="nav-enlace activo" if pagina["relative_path"] == ruta else "nav-enlace",
        )
        for pagina in sorted(dash.page_registry.values(), key=lambda p: p["order"])
    ]


if __name__ == "__main__":
    app.run(debug=True)
