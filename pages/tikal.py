"""Página Tikal: preguntas de gestión P1 (evolución y recuperación) y P2 (temporada alta).

V1 (evolución) y V2 (estacionalidad) están enlazadas: al hacer clic en un año en
cualquiera de las dos, ese año se resalta en ambas.
"""

import dash
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, State, callback, ctx, dcc, html

from src import tema
from src.componentes import aviso, figura_vacia, kpi, tarjeta_grafica
from src.datos import CIERRE_FIN, CIERRE_INICIO, MESES, MESES_CORTOS, tikal

dash.register_page(__name__, path="/", name="Tikal", title="Tikal · Observatorio Petén", order=1)

DETALLES = {"Año": "Y", "Trimestre": "Q", "Mes": "M"}
MESES_POR_PERIODO = {"Y": 12, "Q": 3, "M": 1}
SEGMENTOS = list(tema.SEGMENTOS)


# ---------------------------------------------------------------- indicadores

def _indicadores() -> list:
    """Tarjetas con el total de todos los segmentos para el último año completo."""
    df = tikal()
    meses_con_dato = df.dropna(subset=["visitantes"]).groupby("anio")["mes"].nunique()
    ultimo = int(meses_con_dato[meses_con_dato == 12].index.max())
    por_anio = df.groupby("anio")["visitantes"].sum()
    por_seg = df[df["anio"] == ultimo].groupby("segmento")["visitantes"].sum()

    recuperacion = por_anio[ultimo] / por_anio[2019] - 1
    extranjeros = por_seg["Extranjeros"] / por_seg.sum()

    recientes = df[df["anio"].between(ultimo - 3, ultimo)]
    mes_pico = recientes.groupby(["anio", "mes"])["visitantes"].sum().groupby("mes").mean().idxmax()

    return [
        kpi(f"Visitantes en {ultimo}", f"{por_anio[ultimo]:,.0f}", "Último año completo"),
        kpi("Frente a 2019", f"{recuperacion:+.1%}", "2019: último año antes de la pandemia"),
        kpi(f"Extranjeros en {ultimo}", f"{extranjeros:.1%}", "Del total de boletos"),
        kpi("Mes más visitado", MESES[mes_pico - 1], f"Promedio {ultimo - 3}–{ultimo}"),
    ]


# ---------------------------------------------------------------- figuras

def _filtrar(segmentos: list, rango: list) -> pd.DataFrame:
    df = tikal()
    return df[df["segmento"].isin(segmentos) & df["anio"].between(rango[0], rango[1])]


def _etiqueta_periodo(periodo: pd.Period, frecuencia: str) -> str:
    if frecuencia == "M":
        return f"{MESES[periodo.month - 1]} {periodo.year}"
    if frecuencia == "Q":
        return f"Trimestre {periodo.quarter} de {periodo.year}"
    return str(periodo.year)


def figura_evolucion(df: pd.DataFrame, detalle: str, anio_sel: int | None) -> go.Figure:
    """V1: visitantes por segmento en el tiempo, con el nivel de detalle elegido."""
    frecuencia = DETALLES[detalle]
    esperado = MESES_POR_PERIODO[frecuencia]

    agregado = (
        df.assign(periodo=df["fecha"].dt.to_period(frecuencia))
        .groupby(["segmento", "periodo"])
        .agg(visitantes=("visitantes", lambda s: s.sum(min_count=1)), meses=("visitantes", "count"))
        .reset_index()
    )
    inicio = agregado["periodo"].dt.start_time
    # Cada punto se dibuja a la mitad de su periodo para que caiga dentro del año que representa
    agregado["x"] = inicio + (agregado["periodo"].dt.end_time - inicio) / 2

    fig = go.Figure()
    fig.add_vrect(
        x0=CIERRE_INICIO, x1=CIERRE_FIN + pd.offsets.MonthEnd(1), fillcolor=tema.REJILLA,
        opacity=0.7, line_width=0, layer="below",
        annotation_text="Parque cerrado", annotation_position="top left",
        annotation_font=dict(size=11, color=tema.TEXTO_2),
    )
    if anio_sel is not None:
        fig.add_vrect(
            x0=pd.Timestamp(year=anio_sel, month=1, day=1),
            x1=pd.Timestamp(year=anio_sel + 1, month=1, day=1),
            fillcolor=tema.PRIMARIO, opacity=0.12, line_width=0, layer="below",
        )

    for segmento in [s for s in SEGMENTOS if s in set(agregado["segmento"])]:
        datos = agregado[agregado["segmento"] == segmento]
        parcial = (datos["meses"] < esperado) & (datos["meses"] > 0)
        etiquetas = [
            _etiqueta_periodo(p, frecuencia) + (f" · parcial ({m} de {esperado} meses)" if es_parcial else "")
            for p, m, es_parcial in zip(datos["periodo"], datos["meses"], parcial)
        ]
        color = tema.SEGMENTOS[segmento]
        fig.add_trace(
            go.Scatter(
                x=datos["x"], y=datos["visitantes"], name=segmento,
                mode="lines" if frecuencia == "M" else "lines+markers",
                line=dict(color=color, width=2.5),
                marker=dict(
                    size=8, color=color, line=dict(width=2, color=color),
                    symbol=np.where(parcial, "circle-open", "circle"),
                ),
                customdata=etiquetas,
                hovertemplate="<b>%{customdata}</b><br>" + segmento + ": %{y:,.0f}<extra></extra>",
            )
        )

    fig.update_layout(
        height=380,
        hovermode="closest",
        uirevision=detalle,  # conserva el zoom del usuario mientras no cambie el nivel de detalle
        yaxis=dict(title=f"Visitantes por {detalle.lower()}", rangemode="tozero", tickformat=",.0f"),
        xaxis=dict(tickformat="%Y", dtick="M12"),
    )
    return fig


def figura_estacionalidad(df: pd.DataFrame, anio_sel: int | None) -> go.Figure:
    """V2: mapa de calor mes × año del total de los segmentos elegidos."""
    tabla = (
        df.groupby(["anio", "mes"])["visitantes"].sum(min_count=1)
        .unstack("mes").reindex(columns=range(1, 13))
    )
    estado = df.groupby(["anio", "mes"])["estado"].first().unstack("mes").reindex(columns=range(1, 13))
    anios = tabla.index.tolist()

    textos = []
    for anio in anios:
        fila = []
        for mes in range(1, 13):
            valor = tabla.at[anio, mes]
            detalle = "Sin dato" if pd.isna(valor) else f"{valor:,.0f} visitantes"
            if estado.at[anio, mes] == "cerrado":
                detalle += " · parque cerrado"
            fila.append(f"<b>{MESES[mes - 1]} {anio}</b><br>{detalle}")
        textos.append(fila)

    fig = go.Figure(
        go.Heatmap(
            z=tabla.values, x=list(range(1, 13)), y=anios, text=textos,
            hovertemplate="%{text}<extra></extra>",
            colorscale=tema.SECUENCIAL, xgap=2, ygap=2,
            colorbar=dict(title=dict(text="Visitantes", font=dict(size=12)), thickness=12, tickformat=",.0f"),
        )
    )

    if 2020 in anios:
        fig.add_annotation(
            x=6.5, y=2020, text="Parque cerrado (abr–sep)", showarrow=False,
            font=dict(size=11, color=tema.TEXTO), bgcolor="rgba(255,255,255,0.85)",
        )

    if anio_sel in anios:
        # Foco + contexto: se aclaran los demás años y se enmarca el elegido
        for anio in anios:
            if anio != anio_sel:
                fig.add_shape(
                    type="rect", x0=0.5, x1=12.5, y0=anio - 0.5, y1=anio + 0.5,
                    fillcolor="white", opacity=0.6, line_width=0,
                )
        fig.add_shape(
            type="rect", x0=0.5, x1=12.5, y0=anio_sel - 0.5, y1=anio_sel + 0.5,
            line=dict(color=tema.TEXTO, width=2),
        )

    fig.update_layout(
        height=max(220, 70 + 32 * len(anios)),
        margin=dict(l=56, r=16, t=8, b=40),
        xaxis=dict(tickvals=list(range(1, 13)), ticktext=MESES_CORTOS, ticks="", linecolor=tema.TARJETA),
        yaxis=dict(tickvals=anios, autorange="reversed", gridcolor=tema.TARJETA, ticks=""),
    )
    return fig


# ---------------------------------------------------------------- layout

ANIO_MIN, ANIO_MAX = int(tikal()["anio"].min()), int(tikal()["anio"].max())
FILTROS_INICIALES = dict(segmentos=SEGMENTOS, rango=[ANIO_MIN, ANIO_MAX], detalle="Mes")


def _opcion_segmento(segmento: str) -> dict:
    return {
        "label": html.Span([html.Span(className="muestra", style={"background": tema.SEGMENTOS[segmento]}), segmento]),
        "value": segmento,
    }


filtros = html.Aside(
    className="filtros",
    children=[
        html.H2("Filtros", className="filtros-titulo"),
        html.Label("Segmento de visitante", htmlFor="tikal-segmentos", className="filtro-etiqueta"),
        dcc.Checklist(
            id="tikal-segmentos", options=[_opcion_segmento(s) for s in SEGMENTOS],
            value=FILTROS_INICIALES["segmentos"], className="filtro-opciones",
        ),
        html.P("Otros = boletos exonerados.", className="filtro-nota"),
        html.Label("Periodo", htmlFor="tikal-rango", className="filtro-etiqueta"),
        dcc.RangeSlider(
            id="tikal-rango", min=ANIO_MIN, max=ANIO_MAX, step=1, value=FILTROS_INICIALES["rango"],
            marks={a: str(a) for a in range(ANIO_MIN, ANIO_MAX + 1, 3)},
            tooltip={"placement": "bottom", "always_visible": True}, allow_direct_input=False,
        ),
        html.Label("Nivel de detalle", htmlFor="tikal-detalle", className="filtro-etiqueta"),
        dcc.RadioItems(
            id="tikal-detalle", options=list(DETALLES), value=FILTROS_INICIALES["detalle"],
            className="filtro-opciones",
        ),
        html.P("Año = vista general · Mes = máximo detalle.", className="filtro-nota"),
        html.Button("Restablecer", id="tikal-restablecer", className="boton-secundario", n_clicks=0),
    ],
)

layout = html.Div(
    className="pagina con-filtros",
    children=[
        filtros,
        html.Div(
            className="contenido",
            children=[
                html.H1("Visitantes al Parque Nacional Tikal", className="pagina-titulo"),
                html.P(
                    "¿Cuántos visitantes recibe Tikal, cómo se ha recuperado frente a 2019 y en qué meses "
                    "se concentra la visita? Datos de boletos de ingreso al parque, enero 2017 a agosto 2026.",
                    className="pagina-pregunta",
                ),
                html.Div(_indicadores(), className="fila-kpi"),
                dcc.Store(id="tikal-anio"),
                html.Div(
                    className="estado-seleccion", role="status",
                    children=[
                        html.Span(id="tikal-estado-seleccion"),
                        html.Button("Quitar selección", id="tikal-quitar", className="boton-enlace", n_clicks=0),
                    ],
                ),
                tarjeta_grafica(
                    "¿Cómo ha evolucionado la visita a Tikal?",
                    "Boletos vendidos por segmento. Sirve para medir la recuperación tras la pandemia "
                    "y para comparar la tendencia de nacionales y extranjeros.",
                    "tikal-v1",
                    ayuda="Haz clic en un punto para resaltar ese año en el mapa de calor. Los círculos vacíos "
                          "son periodos incompletos (por ejemplo, 2026 llega hasta agosto). "
                          "Arrastra sobre la gráfica para acercar; doble clic para volver.",
                ),
                tarjeta_grafica(
                    "¿En qué meses se concentra la visita?",
                    "Total de boletos de los segmentos elegidos por mes y año. Más oscuro = más visitantes. "
                    "Sirve para planificar personal y servicios en temporada alta y cuidar la capacidad del parque.",
                    "tikal-v2",
                    ayuda="Haz clic en una fila para resaltar ese año también en la gráfica de evolución.",
                ),
                aviso(
                    html.B("Sobre los datos. "),
                    "Abril a septiembre de 2020 el parque estuvo cerrado por la pandemia: el 0 es real. "
                    "Enero de 2017 no tiene dato. 2026 llega hasta agosto. Un boleto no equivale a una persona "
                    "única: alguien que entra dos veces cuenta dos veces. Los cambios que se ven son "
                    "observaciones; los datos no permiten atribuirles una causa.",
                ),
            ],
        ),
    ],
)


# ---------------------------------------------------------------- interacción

@callback(
    Output("tikal-segmentos", "value"),
    Output("tikal-rango", "value"),
    Output("tikal-detalle", "value"),
    Input("tikal-restablecer", "n_clicks"),
    prevent_initial_call=True,
)
def restablecer_filtros(_):
    return FILTROS_INICIALES["segmentos"], FILTROS_INICIALES["rango"], FILTROS_INICIALES["detalle"]


@callback(
    Output("tikal-anio", "data"),
    Input("tikal-v1", "clickData"),
    Input("tikal-v2", "clickData"),
    Input("tikal-restablecer", "n_clicks"),
    Input("tikal-quitar", "n_clicks"),
    State("tikal-anio", "data"),
    prevent_initial_call=True,
)
def seleccionar_anio(clic_v1, clic_v2, _restablecer, _quitar, actual):
    """Enlace V1 ↔ V2: guarda el año elegido. Un segundo clic en el mismo año lo quita."""
    if ctx.triggered_id == "tikal-v1" and clic_v1:
        anio = pd.Timestamp(clic_v1["points"][0]["x"]).year
    elif ctx.triggered_id == "tikal-v2" and clic_v2:
        anio = int(clic_v2["points"][0]["y"])
    else:
        return None
    return None if anio == actual else anio


@callback(
    Output("tikal-estado-seleccion", "children"),
    Output("tikal-quitar", "hidden"),
    Input("tikal-anio", "data"),
)
def mostrar_seleccion(anio):
    if anio is None:
        return "Consejo: haz clic en un año en cualquiera de las dos gráficas para verlo en detalle.", True
    return ["Mostrando: ", html.B(str(anio)), " · resaltado en ambas gráficas"], False


@callback(
    Output("tikal-v1", "figure"),
    Input("tikal-segmentos", "value"),
    Input("tikal-rango", "value"),
    Input("tikal-detalle", "value"),
    Input("tikal-anio", "data"),
)
def actualizar_v1(segmentos, rango, detalle, anio):
    if not segmentos:
        return figura_vacia("Selecciona al menos un segmento de visitante en el panel de filtros.", 380)
    return figura_evolucion(_filtrar(segmentos, rango), detalle, anio)


@callback(
    Output("tikal-v2", "figure"),
    Input("tikal-segmentos", "value"),
    Input("tikal-rango", "value"),
    Input("tikal-anio", "data"),
)
def actualizar_v2(segmentos, rango, anio):
    if not segmentos:
        return figura_vacia("Selecciona al menos un segmento de visitante en el panel de filtros.")
    return figura_estacionalidad(_filtrar(segmentos, rango), anio)
