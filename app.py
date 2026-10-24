"""Punto de entrada del tablero: Observatorio de Turismo Sostenible, Tikal y Flores (Petén).

Ejecutar con:  uv run python app.py   y abrir http://127.0.0.1:8050
"""

import dash
from dash import Dash, Input, Output, dcc, html

from src import tema  # noqa: F401  (registra la plantilla de Plotly)
from src.componentes import en_construccion

app = Dash(
    __name__,
    use_pages=True,
    title="Observatorio · Tikal y Flores",
    suppress_callback_exceptions=True,
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
    ],
)

# Secciones planificadas en docs/documento_diseno.md que aún no se implementan.
# Cada integrante reemplaza su entrada por un archivo en pages/ cuando la construya.
PENDIENTES = [
    ("resumen", "Resumen", 0, "Panorama general del destino",
     "Tarjetas clave de las tres fuentes y guía de uso del tablero.", "Anggie Quezada"),
    ("triangulacion", "Triangulación", 2,
     "P3. ¿Qué porcentaje de los visitantes en Petén compra boleto a Tikal?",
     "V4 índice base 100 de las tres fuentes enlazado con V5 % de visitantes con boleto.", "Jonathan Díaz"),
    ("conectividad", "Conectividad", 3,
     "P4. ¿Cuánto pesa cada aerolínea en el AIMM y cómo se reconstruye 2023?",
     "V6 treemap año → aerolínea enlazado con V7 pasajeros y operaciones del operador.", "Iris Ayala"),
    ("hospedaje", "Hospedaje", 4,
     "P5. ¿La ocupación hotelera acompaña la temporada alta de Tikal?",
     "V8 ocupación mensual por año enlazada con V9 capacidad instalada frente a demanda.", "Iris Ayala"),
    ("fronteras", "Fronteras", 5,
     "P6. ¿Por qué fronteras entran los visitantes internacionales a Petén y de qué mercados vienen?",
     "V10 ingresos por frontera y año enlazado con V11 mercados de origen.", "Jonathan Díaz"),
    ("acerca", "Acerca de", 6, "Fuentes, glosario y limitaciones",
     "Descripción de cada fuente, glosario de términos y limitaciones de los datos.", "Anggie Quezada"),
]
for modulo, nombre, orden, pregunta, contenido, responsable in PENDIENTES:
    dash.register_page(
        modulo, path=f"/{modulo}", name=nombre, order=orden, title=f"{nombre} · Observatorio Petén",
        layout=en_construccion(nombre, pregunta, contenido, responsable),
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
