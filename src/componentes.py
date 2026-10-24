"""Piezas de interfaz reutilizables por todas las páginas del tablero."""

import plotly.graph_objects as go
from dash import dcc, html

from src import tema


def kpi(titulo: str, valor: str, nota: str) -> html.Div:
    """Tarjeta de un solo valor (complementaria, no cuenta como visualización)."""
    return html.Div(
        className="kpi",
        children=[
            html.Div(titulo, className="kpi-titulo"),
            html.Div(valor, className="kpi-valor"),
            html.Div(nota, className="kpi-nota"),
        ],
    )


def tarjeta_grafica(titulo: str, subtitulo: str, id_grafica: str, ayuda: str | None = None,
                    extra: list | None = None) -> html.Section:
    """Contenedor estándar de una visualización: título, qué muestra y para qué sirve."""
    return html.Section(
        className="tarjeta",
        children=[
            html.H2(titulo, className="tarjeta-titulo"),
            html.P(subtitulo, className="tarjeta-subtitulo"),
            *(extra or []),
            dcc.Graph(
                id=id_grafica,
                config={"displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d"]},
            ),
            html.P(ayuda, className="tarjeta-ayuda") if ayuda else None,
        ],
    )


def aviso(*contenido) -> html.Div:
    """Mensaje de limitación de los datos."""
    return html.Div(className="aviso", role="note", children=[html.Span("⚠", className="aviso-icono"), html.Div(contenido)])


def figura_vacia(mensaje: str, alto: int = 320) -> go.Figure:
    """Figura que explica por qué no hay datos en lugar de mostrar ejes vacíos."""
    fig = go.Figure()
    fig.add_annotation(
        text=mensaje, x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False,
        font=dict(size=14, color=tema.TEXTO_2),
    )
    fig.update_layout(height=alto, xaxis=dict(visible=False), yaxis=dict(visible=False))
    return fig


def en_construccion(titulo: str, pregunta: str, contenido: str, responsable: str) -> html.Div:
    """Página provisional para las secciones que aún no se implementan."""
    return html.Div(
        className="pagina",
        children=[
            html.H1(titulo, className="pagina-titulo"),
            html.P(pregunta, className="pagina-pregunta"),
            html.Section(
                className="tarjeta construccion",
                children=[
                    html.H2("Sección en construcción", className="tarjeta-titulo"),
                    html.P(contenido, className="tarjeta-subtitulo"),
                    html.P(f"Responsable: {responsable}", className="tarjeta-ayuda"),
                ],
            ),
        ],
    )
