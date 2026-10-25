"""Página Hospedaje: pregunta de gestión P5 (¿la ocupación hotelera presiona la capacidad instalada?).

V8 (ocupación mensual, una línea por año) y V9 (capacidad instalada frente a ocupación estimada) están
enlazadas: al hacer clic en un mes de V8, V9 traduce ese porcentaje a habitaciones.
"""

import dash
import plotly.graph_objects as go
from dash import Input, Output, State, callback, ctx, dcc, html

from src import tema
from src.componentes import aviso, figura_vacia, kpi, tarjeta_grafica
from src.datos import MESES, MESES_CORTOS, TIPOS_ALOJAMIENTO, ocupacion_peten, oferta_peten

dash.register_page(__name__, path="/hospedaje", name="Hospedaje",
                   title="Hospedaje · Observatorio Petén", order=4)

UMBRAL = 0.85  # por encima de este nivel se considera ocupación alta (posible saturación)

# Mismo azul petróleo en tres intensidades: más oscuro = año más reciente
COLORES_ANIO = {2023: "#4F9AA6", 2024: "#2A7482", 2025: tema.PRIMARIO}
# Tipos de alojamiento en grises etiquetados directamente, para no gastar colores con otro significado
COLORES_TIPO = {"Hotel": "#3E4C59", "Hospedaje": "#7B8794", "Pensión": "#CBD2D9"}
TEXTO_TIPO = {"Hotel": "#FFFFFF", "Hospedaje": "#FFFFFF", "Pensión": tema.TEXTO}


def _capacidad(anio: int) -> dict:
    """Habitaciones instaladas por tipo en el corte del 4.º trimestre del año."""
    df = oferta_peten()
    df = df[(df["anio"] == anio) & (df["trimestre"] == 4)].set_index("tipo")["habitaciones"]
    return {tipo: int(df[tipo]) for tipo in TIPOS_ALOJAMIENTO if tipo in df.index}


# ---------------------------------------------------------------- indicadores

def _indicadores() -> list:
    df = ocupacion_peten()
    ultimo = int(df["anio"].max())
    actual = df[df["anio"] == ultimo].set_index("mes")["ocupacion"]
    altos = [MESES_CORTOS[m - 1] for m in actual.index[actual >= UMBRAL]]
    return [
        kpi(f"Ocupación promedio {ultimo}", f"{actual.mean():.0%}", "Promedio de los 12 meses, todo Petén"),
        kpi(f"Meses con ocupación alta en {ultimo}", f"{len(altos)}", f"≥ {UMBRAL:.0%}: {', '.join(altos) or 'ninguno'}"),
        kpi("Mes de menor ocupación", MESES[actual.idxmin() - 1], f"{actual.min():.0%} en {ultimo}"),
        kpi(f"Habitaciones en {ultimo}", f"{sum(_capacidad(ultimo).values()):,}", "Hoteles, hospedajes y pensiones"),
    ]


# ---------------------------------------------------------------- figuras

def figura_ocupacion(seleccion: dict | None) -> go.Figure:
    """V8: ocupación mensual de Petén; cada año es una línea para comparar la temporada."""
    df = ocupacion_peten()
    fig = go.Figure()
    fig.add_hline(
        y=UMBRAL, line=dict(color=tema.TEXTO_2, width=1.5, dash="dot"),
        annotation_text=f"{UMBRAL:.0%}: ocupación alta", annotation_position="top left",
        annotation_font=dict(size=11, color=tema.TEXTO_2),
    )
    if seleccion:
        fig.add_vrect(
            x0=seleccion["mes"] - 0.5, x1=seleccion["mes"] + 0.5,
            fillcolor=tema.PRIMARIO, opacity=0.12, line_width=0, layer="below",
        )

    for anio, grupo in df.groupby("anio"):
        color = COLORES_ANIO.get(anio, tema.PRIMARIO)
        elegido = [bool(seleccion) and seleccion["anio"] == anio and m == seleccion["mes"] for m in grupo["mes"]]
        fig.add_trace(
            go.Scatter(
                x=grupo["mes"], y=grupo["ocupacion"], name=str(anio), mode="lines+markers",
                line=dict(color=color, width=2.5),
                marker=dict(
                    size=[14 if e else 8 for e in elegido], color=[tema.TARJETA if e else color for e in elegido],
                    line=dict(width=2.5, color=color),
                ),
                customdata=[anio] * len(grupo),
                hovertemplate="<b>%{text} " + str(anio) + "</b><br>Ocupación: %{y:.0%}<extra></extra>",
                text=[MESES[m - 1] for m in grupo["mes"]],
            )
        )

    fig.update_layout(
        height=400, hovermode="closest", uirevision="v8",
        xaxis=dict(tickvals=list(range(1, 13)), ticktext=MESES_CORTOS, range=[0.5, 12.5]),
        yaxis=dict(title="Ocupación hotelera", tickformat=".0%", range=[0, 1.05]),
        legend=dict(title=dict(text="Año  ")),
    )
    return fig


def figura_capacidad(seleccion: dict | None) -> go.Figure:
    """V9: habitaciones instaladas por tipo frente a la ocupación estimada del mes elegido."""
    if not seleccion:
        return figura_vacia("Haz clic en un mes de la gráfica de ocupación para ver cuántas habitaciones "
                            "representa ese porcentaje.", 420)

    anio, mes = seleccion["anio"], seleccion["mes"]
    capacidad = _capacidad(anio)
    if not capacidad:
        return figura_vacia(f"No hay datos de capacidad instalada para {anio}.", 420)

    total = sum(capacidad.values())
    ocupacion = ocupacion_peten().query("anio == @anio and mes == @mes")["ocupacion"].iloc[0]
    ocupadas = round(total * ocupacion)

    fig = go.Figure()
    for tipo, habitaciones in capacidad.items():
        fig.add_trace(
            go.Bar(
                x=["Capacidad instalada"], y=[habitaciones], name=tipo, width=0.45,
                marker=dict(color=COLORES_TIPO[tipo], line=dict(width=2, color=tema.TARJETA)),
                text=f"{tipo}<br>{habitaciones:,}", textposition="inside", insidetextanchor="middle",
                textfont=dict(color=TEXTO_TIPO[tipo], size=12),
                hovertemplate=f"<b>{tipo}</b><br>{habitaciones:,} habitaciones<extra></extra>",
            )
        )
    etiqueta = "Estimación"
    fig.add_trace(
        go.Bar(
            x=[f"{MESES[mes - 1]} {anio}"], y=[ocupadas], name=f"Ocupadas ({etiqueta.lower()})", width=0.45,
            marker=dict(color=tema.PRIMARIO, line=dict(width=2, color=tema.TARJETA), pattern=dict(shape="/", fgcolor="#FFFFFF", size=6)),
            text=f"Ocupadas<br>≈ {ocupadas:,}", textposition="inside", textfont=dict(color="#FFFFFF", size=12),
            hovertemplate=f"<b>Habitaciones ocupadas ({etiqueta.lower()})</b><br>≈ {ocupadas:,} de {total:,}<br>"
                          f"Ocupación del mes: {ocupacion:.0%}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            x=[f"{MESES[mes - 1]} {anio}"], y=[total - ocupadas], name=f"Libres ({etiqueta.lower()})", width=0.45,
            marker=dict(color=tema.REJILLA, line=dict(width=2, color=tema.TARJETA), pattern=dict(shape="/", fgcolor="#FFFFFF", size=6)),
            text=f"Libres<br>≈ {total - ocupadas:,}", textposition="inside", textfont=dict(color=tema.TEXTO, size=12),
            hovertemplate=f"<b>Habitaciones libres ({etiqueta.lower()})</b><br>≈ {total - ocupadas:,} de {total:,}<extra></extra>",
        )
    )
    fig.add_annotation(
        x=f"{MESES[mes - 1]} {anio}", y=total, yshift=18, showarrow=False,
        text=f"<b>{ocupacion:.0%}</b> de ocupación", font=dict(size=13, color=tema.TEXTO),
    )
    fig.update_layout(
        height=420, barmode="stack", showlegend=False, margin=dict(l=64, r=16, t=48, b=40),
        yaxis=dict(title="Habitaciones", tickformat=",.0f", range=[0, total * 1.12]),
        xaxis=dict(categoryorder="array", categoryarray=["Capacidad instalada", f"{MESES[mes - 1]} {anio}"]),
    )
    return fig


# ---------------------------------------------------------------- layout

layout = html.Div(
    className="pagina",
    children=[
        html.H1("Hospedaje en Petén", className="pagina-titulo"),
        html.P(
            "¿Cuándo hay presión sobre la capacidad de hospedaje y en qué meses sobra? "
            "Índice de ocupación mensual 2023 a 2025 y capacidad instalada de todo el departamento de Petén.",
            className="pagina-pregunta",
        ),
        html.Div(_indicadores(), className="fila-kpi"),
        dcc.Store(id="hospedaje-mes"),
        html.Div(
            className="estado-seleccion", role="status",
            children=[
                html.Span(id="hospedaje-estado"),
                html.Button("Quitar selección", id="hospedaje-quitar", className="boton-enlace", n_clicks=0),
            ],
        ),
        tarjeta_grafica(
            "¿En qué meses se llena la oferta de hospedaje?",
            "Ocupación hotelera de cada mes, una línea por año. Sirve para ver si la temporada alta se repite "
            "y en qué meses la ocupación pasa de 85 %, señal de posible saturación, o queda mucha capacidad libre.",
            "hospedaje-v8",
            ayuda="Haz clic en un mes para ver cuántas habitaciones representa. Haz clic en un año de la leyenda "
                  "para ocultarlo o mostrarlo; doble clic para ver solo ese año.",
        ),
        tarjeta_grafica(
            "¿Cuántas habitaciones hay y cuántas se ocupan?",
            "Habitaciones instaladas por tipo de alojamiento frente a las habitaciones ocupadas del mes elegido. "
            "Sirve para traducir un porcentaje a una cantidad que se pueda planificar.",
            "hospedaje-v9",
            ayuda="Las habitaciones ocupadas y libres son una estimación: la ocupación del mes multiplicada por la "
                  "capacidad del cierre del año. Las barras con rayas son estimaciones.",
        ),
        aviso(
            html.B("Sobre los datos. "),
            "La ocupación es un índice del departamento completo de Petén, no solo de Flores o Tikal, y llega hasta "
            "diciembre de 2025. La capacidad instalada es un corte del cuarto trimestre de cada año, no una serie "
            "mensual, y se usa para todos los meses de ese año. Por eso las habitaciones ocupadas son aproximadas. "
            "Los datos de 2026 se omiten: son parciales y cerca de la mitad repite el valor del año previo. "
            "Los cambios que se ven son observaciones; los datos no permiten atribuirles una causa.",
        ),
    ],
)


# ---------------------------------------------------------------- interacción

@callback(
    Output("hospedaje-mes", "data"),
    Input("hospedaje-v8", "clickData"),
    Input("hospedaje-quitar", "n_clicks"),
    State("hospedaje-mes", "data"),
    prevent_initial_call=True,
)
def seleccionar_mes(clic, _quitar, actual):
    """Enlace V8 → V9: guarda el año y mes elegidos. Un segundo clic en el mismo punto lo quita."""
    if ctx.triggered_id != "hospedaje-v8" or not clic:
        return None
    punto = clic["points"][0]
    anio = punto["customdata"]
    anio = int(anio[0] if isinstance(anio, list) else anio)
    elegido = {"anio": anio, "mes": int(punto["x"])}
    return None if elegido == actual else elegido


@callback(
    Output("hospedaje-estado", "children"),
    Output("hospedaje-quitar", "hidden"),
    Input("hospedaje-mes", "data"),
)
def mostrar_seleccion(seleccion):
    if not seleccion:
        return "Consejo: haz clic en un mes de la gráfica de ocupación para ver el detalle en habitaciones.", True
    return ["Mostrando: ", html.B(f"{MESES[seleccion['mes'] - 1]} {seleccion['anio']}"),
            " · clic de nuevo en el mismo punto para quitar"], False


@callback(Output("hospedaje-v8", "figure"), Input("hospedaje-mes", "data"))
def actualizar_v8(seleccion):
    return figura_ocupacion(seleccion)


@callback(Output("hospedaje-v9", "figure"), Input("hospedaje-mes", "data"))
def actualizar_v9(seleccion):
    return figura_capacidad(seleccion)
