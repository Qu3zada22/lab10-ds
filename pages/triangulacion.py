"""Página Triangulación: pregunta de gestión P3 (¿qué porcentaje de los visitantes en Petén compra boleto a Tikal?).

V4 (índice base 100 de las tres fuentes) y V5 (% de visitantes con boleto a Tikal) están enlazadas: al hacer
clic en un mes de V4, V5 resalta ese mes.
"""

import dash
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, State, callback, ctx, dcc, html

from src import tema
from src.componentes import aviso, figura_vacia, kpi, tarjeta_grafica
from src.datos import MESES, MESES_CORTOS, indice_base_100, triangulacion

dash.register_page(__name__, path="/triangulacion", name="Triangulación",
                   title="Triangulación · Observatorio Petén", order=2)

SEGMENTOS_V5 = {"Nacionales": ("boletos_nac", "telefonia_nac"), "Extranjeros": ("boletos_ext", "telefonia_ext")}


def _etiqueta(fecha: pd.Timestamp) -> str:
    return f"{MESES_CORTOS[fecha.month - 1]} {fecha.year}"


def _porcentajes() -> pd.DataFrame:
    """% de visitantes por telefonía que compró boleto a Tikal, por mes y segmento."""
    t = triangulacion()
    out = t[["fecha"]].copy()
    for segmento, (boletos, telefonia) in SEGMENTOS_V5.items():
        out[segmento] = t[boletos] / t[telefonia]
    return out


# ---------------------------------------------------------------- indicadores

def _indicadores() -> list:
    t, pct, indice = triangulacion(), _porcentajes(), indice_base_100()
    meses_comunes = int(indice["en_comun"].sum())
    nac_tel = t["telefonia_nac"].sum() / (t["telefonia_nac"].sum() + t["telefonia_ext"].sum())
    return [
        kpi("Meses con las tres fuentes", f"{meses_comunes}", "Solo estos meses se usan para el índice base 100"),
        kpi("Visitantes por telefonía que son guatemaltecos", f"{nac_tel:.0%}", "Sep 2025 a ago 2026, sin enero ni febrero"),
        kpi("Boleto a Tikal, extranjeros", f"{pct['Extranjeros'].mean():.0%}", "Promedio mensual de boletos ÷ visitantes extranjeros"),
        kpi("Boleto a Tikal, nacionales", f"{pct['Nacionales'].mean():.0%}", "Promedio mensual de boletos ÷ visitantes guatemaltecos"),
    ]


# ---------------------------------------------------------------- figuras

def figura_indice(seleccion: str | None) -> go.Figure:
    """V4: las tres fuentes como índice (100 = su promedio en los meses en común) para comparar la forma."""
    df = indice_base_100()
    fig = go.Figure()
    fig.add_hline(y=100, line=dict(color=tema.TEXTO_2, width=1, dash="dot"),
                  annotation_text="100: promedio de cada fuente", annotation_position="top left",
                  annotation_font=dict(size=11, color=tema.TEXTO_2))
    if seleccion:
        fecha = pd.Timestamp(seleccion)
        fig.add_vrect(x0=fecha - pd.Timedelta(days=15), x1=fecha + pd.Timedelta(days=15),
                      fillcolor=tema.PRIMARIO, opacity=0.12, line_width=0, layer="below")

    for fuente, color in tema.FUENTES.items():
        serie = df[["fecha", fuente]]
        elegido = [bool(seleccion) and str(f.date()) == seleccion for f in serie["fecha"]]
        fig.add_trace(
            go.Scatter(
                x=serie["fecha"], y=serie[fuente], name=fuente, mode="lines+markers", connectgaps=False,
                line=dict(color=color, width=2.5),
                marker=dict(size=[14 if e else 8 for e in elegido], color=[tema.TARJETA if e else color for e in elegido],
                            line=dict(width=2.5, color=color)),
                hovertemplate="<b>" + fuente + "</b> · %{x|%b %Y}<br>Índice: %{y:.0f}<extra></extra>",
            )
        )

    # Los meses sin dato en alguna fuente quedan como hueco en la línea; se marcan para que no parezcan 0
    faltantes = df[~df[list(tema.FUENTES)].notna().all(axis=1)]
    for _, fila in faltantes.iterrows():
        fig.add_vrect(x0=fila["fecha"] - pd.Timedelta(days=15), x1=fila["fecha"] + pd.Timedelta(days=15),
                      fillcolor=tema.REJILLA, opacity=0.35, line_width=0, layer="below")

    fig.update_layout(
        height=400, hovermode="x unified", uirevision="v4",
        xaxis=dict(tickformat="%b %Y", dtick="M1", tickangle=-45),
        yaxis=dict(title="Índice (100 = promedio en meses comunes)", rangemode="tozero"),
    )
    return fig


def figura_porcentaje(seleccion: str | None) -> go.Figure:
    """V5: de cada 100 visitantes detectados por telefonía, cuántos compraron boleto a Tikal."""
    pct = _porcentajes()
    if pct[list(SEGMENTOS_V5)].isna().all().all():
        return figura_vacia("No hay meses con boletos y telefonía a la vez.", 420)

    etiquetas = [_etiqueta(f) for f in pct["fecha"]]
    fig = go.Figure()
    fig.add_hline(y=1, line=dict(color=tema.TEXTO_2, width=1, dash="dot"),
                  annotation_text="100 %", annotation_position="top left",
                  annotation_font=dict(size=11, color=tema.TEXTO_2))
    for segmento, color in ((s, tema.SEGMENTOS[s]) for s in SEGMENTOS_V5):
        opacidad = [1.0 if not seleccion or str(f.date()) == seleccion else 0.35 for f in pct["fecha"]]
        fig.add_trace(
            go.Bar(
                x=etiquetas, y=pct[segmento], name=segmento, marker=dict(color=color, opacity=opacidad),
                text=[f"{v:.0%}" if pd.notna(v) else "" for v in pct[segmento]], textposition="outside",
                textfont=dict(size=11, color=tema.TEXTO_2), cliponaxis=False,
                hovertemplate="<b>" + segmento + "</b> · %{x}<br>Compró boleto: %{y:.1%}<extra></extra>",
            )
        )

    sin_dato = [_etiqueta(f) for f, v in zip(pct["fecha"], pct[list(SEGMENTOS_V5)].isna().all(axis=1)) if v]
    for etiqueta in sin_dato:
        fig.add_annotation(x=etiqueta, y=0, yshift=18, text="Sin dato de<br>telefonía", showarrow=False,
                           font=dict(size=11, color=tema.TEXTO_2))
    tope = float(pct[list(SEGMENTOS_V5)].max().max())
    fig.update_layout(
        height=420, barmode="group", uirevision="v5", margin=dict(l=64, r=16, t=48, b=60),
        xaxis=dict(categoryorder="array", categoryarray=etiquetas, tickangle=-45),
        yaxis=dict(title="% con boleto a Tikal", tickformat=".0%", range=[0, max(1.1, tope * 1.15)]),
    )
    return fig


# ---------------------------------------------------------------- layout

layout = html.Div(
    className="pagina",
    children=[
        html.H1("Triangulación de fuentes", className="pagina-titulo"),
        html.P(
            "¿Las tres fuentes cuentan la misma historia y qué porcentaje de los visitantes en Petén compra boleto a "
            "Tikal? Se comparan los boletos de Tikal, los pasajeros del aeropuerto Mundo Maya y los visitantes "
            "estimados por telefonía, de septiembre de 2025 a agosto de 2026.",
            className="pagina-pregunta",
        ),
        html.Div(_indicadores(), className="fila-kpi"),
        dcc.Store(id="triangulacion-mes"),
        html.Div(
            className="estado-seleccion", role="status",
            children=[
                html.Span(id="triangulacion-estado"),
                html.Button("Quitar selección", id="triangulacion-quitar", className="boton-enlace", n_clicks=0),
            ],
        ),
        tarjeta_grafica(
            "¿Suben y bajan al mismo tiempo las tres fuentes?",
            "Cada fuente se muestra como índice: 100 es su promedio en los meses en que las tres tienen dato. "
            "Sirve para comparar la forma de la curva, no las cantidades, porque las fuentes miden cosas distintas.",
            "triangulacion-v4",
            ayuda="Haz clic en un mes para resaltarlo en la gráfica de abajo. Las franjas grises son meses en que "
                  "alguna fuente no tiene dato. Haz clic en una fuente de la leyenda para ocultarla o mostrarla.",
        ),
        tarjeta_grafica(
            "¿Qué porcentaje de los visitantes compra boleto a Tikal?",
            "Boletos de Tikal entre visitantes detectados por telefonía en Petén, separado en nacionales y extranjeros. "
            "Sirve para ver qué tanto de la visita al departamento llega a Tikal.",
            "triangulacion-v5",
            ayuda="El mes elegido en la gráfica de arriba aparece resaltado. Un valor cercano o mayor a 100 % no "
                  "significa que todos compraron boleto: ver la nota sobre los datos.",
        ),
        aviso(
            html.B("Sobre los datos. "),
            "Telefonía solo cubre 10 meses y le faltan enero y febrero de 2026; el AIMM llega hasta abril de 2026. "
            "Por eso el índice usa solo los 6 meses en que las tres fuentes tienen dato y el resto aparece en gris. "
            "El 93 % de los visitantes por telefonía son guatemaltecos, por lo que el total está dominado por turismo "
            "interno. Las cifras de telefonía son estimaciones y suman tres polígonos (aeropuerto, Isla de Flores y "
            "El Remate): una misma persona puede contarse más de una vez. Un boleto no equivale a una persona, porque "
            "alguien puede entrar a Tikal dos veces, y por eso el porcentaje de extranjeros puede pasar de 100 %. "
            "Los pasajeros del AIMM incluyen residentes y personal. Las fuentes se comparan por tendencia. "
            "Los cambios que se ven son observaciones; los datos no permiten atribuirles una causa.",
        ),
    ],
)


# ---------------------------------------------------------------- interacción

@callback(
    Output("triangulacion-mes", "data"),
    Input("triangulacion-v4", "clickData"),
    Input("triangulacion-quitar", "n_clicks"),
    State("triangulacion-mes", "data"),
    prevent_initial_call=True,
)
def seleccionar_mes(clic, _quitar, actual):
    """Enlace V4 → V5: guarda el mes elegido. Un segundo clic en el mismo mes lo quita."""
    if ctx.triggered_id != "triangulacion-v4" or not clic:
        return None
    elegido = str(pd.Timestamp(clic["points"][0]["x"]).date())
    return None if elegido == actual else elegido


@callback(
    Output("triangulacion-estado", "children"),
    Output("triangulacion-quitar", "hidden"),
    Input("triangulacion-mes", "data"),
)
def mostrar_seleccion(seleccion):
    if not seleccion:
        return "Consejo: haz clic en un mes de la primera gráfica para resaltarlo en la segunda.", True
    fecha = pd.Timestamp(seleccion)
    return ["Mostrando: ", html.B(f"{MESES[fecha.month - 1]} {fecha.year}"),
            " · clic de nuevo en el mismo mes para quitar"], False


@callback(Output("triangulacion-v4", "figure"), Input("triangulacion-mes", "data"))
def actualizar_v4(seleccion):
    return figura_indice(seleccion)


@callback(Output("triangulacion-v5", "figure"), Input("triangulacion-mes", "data"))
def actualizar_v5(seleccion):
    return figura_porcentaje(seleccion)
