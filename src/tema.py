"""Paleta, tipografía y plantilla de Plotly del tablero.

Los valores vienen de docs/documento_diseno.md (sección 4.1). Cada color tiene un único
significado en toda la aplicación, así que las páginas deben tomarlos de aquí y no
escribir códigos de color sueltos.
"""

import plotly.graph_objects as go
import plotly.io as pio

# Interfaz
TEXTO = "#1F2933"
TEXTO_2 = "#52606D"
FONDO = "#F5F7F8"
TARJETA = "#FFFFFF"
REJILLA = "#E4E7EB"
PRIMARIO = "#0B5563"  # barra de navegación y "lo que el usuario seleccionó"
CONTEXTO = "#B8C0C8"  # elementos no seleccionados (foco + contexto)

# Segmento de visitante
SEGMENTOS = {
    "Nacionales": "#0072B2",
    "Extranjeros": "#C25400",
    "Otros": "#7B8794",
}

# Fuente de datos (triangulación)
FUENTES = {
    "Boletos Tikal": "#00826A",
    "AIMM": "#7B4FB0",
    "Telefonía": "#9A6700",
}

# Escala secuencial de un solo tono: claro = poco, oscuro = mucho
SECUENCIAL = [[0.0, "#E6F2F3"], [1.0, PRIMARIO]]

FUENTE = "Inter, system-ui, -apple-system, 'Segoe UI', sans-serif"

pio.templates["observatorio"] = go.layout.Template(
    layout=dict(
        font=dict(family=FUENTE, size=13, color=TEXTO),
        paper_bgcolor=TARJETA,
        plot_bgcolor=TARJETA,
        colorway=list(SEGMENTOS.values()),
        separators=".,",
        margin=dict(l=56, r=16, t=16, b=40),
        xaxis=dict(
            showgrid=False,
            linecolor=REJILLA,
            ticks="outside",
            tickcolor=REJILLA,
            tickfont=dict(size=12, color=TEXTO_2),
            title=dict(font=dict(size=12, color=TEXTO_2)),
        ),
        yaxis=dict(
            gridcolor=REJILLA,
            zeroline=False,
            tickfont=dict(size=12, color=TEXTO_2),
            title=dict(font=dict(size=12, color=TEXTO_2)),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            x=0,
            font=dict(size=12),
        ),
        hoverlabel=dict(font=dict(family=FUENTE, size=13), bgcolor=TARJETA),
    )
)
pio.templates.default = "observatorio"
