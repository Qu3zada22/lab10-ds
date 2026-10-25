"""Página Conectividad: pregunta de gestión P4 (peso de cada aerolínea y dependencia de pocos operadores).

V6 (bloques año → aerolínea) y V7 (pasajeros y operaciones mensuales) están enlazadas: al hacer clic en
una aerolínea en V6, V7 muestra solo ese operador. Pasajeros y operaciones van en paneles separados
porque son unidades distintas y nunca comparten eje.
"""

import dash
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, State, callback, ctx, dcc, html
from plotly.subplots import make_subplots

from src import tema
from src.componentes import aviso, kpi, tarjeta_grafica
from src.datos import aimm_aerolineas, aimm_operaciones, aimm_pasajeros_total

dash.register_page(__name__, path="/conectividad", name="Conectividad",
                   title="Conectividad · Observatorio Petén", order=3)

COLOR = tema.FUENTES["AIMM"]
COLOR_ANIO = "#D9CFEA"  # tono claro del violeta AIMM, para los bloques de año
TODO = "todo el aeropuerto"
MESES_ABREV = ["", "ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


def _etiqueta_anio(anio: int, meses: int) -> str:
    return str(anio) if meses == 12 else f"{anio} (ene–{MESES_ABREV[meses]})"


# ---------------------------------------------------------------- indicadores

def _indicadores() -> list:
    total = aimm_pasajeros_total()
    completos = total.groupby("anio")["mes"].nunique()
    ultimo = int(completos[completos == 12].index.max())
    por_anio = total.groupby("anio")["pasajeros"].sum()
    variacion = por_anio[ultimo] / por_anio[ultimo - 1] - 1

    aero = aimm_aerolineas()
    aero = aero[aero["anio"] == ultimo].groupby("operador")["pasajeros"].sum().sort_values(ascending=False)
    top2 = aero.head(2)

    ops = aimm_operaciones()
    ops_ultimo = ops[ops["anio"] == ultimo]["operaciones"].sum()
    return [
        kpi(f"Pasajeros en {ultimo}", f"{por_anio[ultimo]:,.0f}", "Entradas + salidas, último año completo"),
        kpi(f"Frente a {ultimo - 1}", f"{variacion:+.1%}", "Cambio en pasajeros del aeropuerto"),
        kpi("Peso de las 2 mayores", f"{top2.sum() / aero.sum():.1%}", f"{' y '.join(top2.index)} en {ultimo}"),
        kpi(f"Operaciones en {ultimo}", f"{ops_ultimo:,.0f}", "Aterrizajes + despegues (vuelos, no personas)"),
    ]


# ---------------------------------------------------------------- figuras

def figura_treemap() -> go.Figure:
    """V6: pasajeros por año y aerolínea. Clic en un año para entrar; la barra superior regresa."""
    base = aimm_aerolineas()
    df = base.groupby(["anio", "operador"])["pasajeros"].sum().reset_index()
    df = df[df["pasajeros"] > 0]
    meses = base.groupby("anio")["mes"].nunique()

    ids, etiquetas, padres, valores, colores, textos = [], [], [], [], [], []
    for anio, grupo in df.groupby("anio"):
        ids.append(str(anio))
        etiquetas.append(_etiqueta_anio(anio, meses[anio]))
        padres.append("")
        valores.append(grupo["pasajeros"].sum())
        colores.append(COLOR_ANIO)
        textos.append(tema.TEXTO)
        for fila in grupo.itertuples():
            ids.append(f"{anio}|{fila.operador}")
            etiquetas.append(fila.operador)
            padres.append(str(anio))
            valores.append(fila.pasajeros)
            colores.append(COLOR)
            textos.append("#FFFFFF")

    fig = go.Figure(
        go.Treemap(
            ids=ids, labels=etiquetas, parents=padres, values=valores, branchvalues="total",
            marker=dict(colors=colores, line=dict(width=2, color=tema.TARJETA)),
            textfont=dict(color=textos, size=13),
            texttemplate="<b>%{label}</b><br>%{value:,.0f} pasajeros<br>%{percentParent:.1%} del año",
            hovertemplate="<b>%{label}</b><br>%{value:,.0f} pasajeros<br>%{percentParent:.1%} del total del año<extra></extra>",
            pathbar=dict(visible=True, textfont=dict(size=12)),
            tiling=dict(pad=3),
        )
    )
    fig.update_layout(height=430, margin=dict(l=8, r=8, t=8, b=8), uirevision="v6")
    return fig


def _serie(df: pd.DataFrame, columna: str, fechas: pd.DatetimeIndex) -> pd.Series:
    """Serie mensual completa: los meses sin registro quedan vacíos (hueco), nunca en 0."""
    return df.groupby("fecha")[columna].sum(min_count=1).reindex(fechas)


def figura_pasajeros_operaciones(operador: str | None) -> go.Figure:
    """V7: pasajeros (arriba) y operaciones (abajo) por mes, de un operador o de todo el aeropuerto."""
    ops = aimm_operaciones()
    fechas = pd.date_range(ops["fecha"].min(), ops["fecha"].max(), freq="MS")

    if operador is None:
        pasajeros = aimm_pasajeros_total().set_index("fecha")["pasajeros"].reindex(fechas)
        operaciones = _serie(ops, "operaciones", fechas)
    else:
        aero = aimm_aerolineas()
        pasajeros = _serie(aero[aero["operador"] == operador], "pasajeros", fechas)
        operaciones = _serie(ops[ops["operador"] == operador], "operaciones", fechas)

    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.14,
        subplot_titles=("Pasajeros por mes (entradas + salidas)", "Operaciones por mes (aterrizajes + despegues)"),
    )
    for fila, serie, nombre, unidad in ((1, pasajeros, "Pasajeros", "pasajeros"), (2, operaciones, "Operaciones", "operaciones")):
        fig.add_trace(
            go.Scatter(
                x=serie.index, y=serie.values, name=nombre, mode="lines+markers",
                line=dict(color=COLOR, width=2.5), marker=dict(size=5, color=COLOR),
                connectgaps=False, showlegend=False,
                hovertemplate="<b>%{x|%B %Y}</b><br>%{y:,.0f} " + unidad + "<extra></extra>",
            ),
            row=fila, col=1,
        )

    # Contexto de la fuente, para que los huecos y la reconstrucción se entiendan
    if operador is None:
        nota, x0, x1 = "2023 reconstruido con la base por aerolínea", "2023-01-01", "2023-12-31"
    else:
        nota, x0, x1 = "Sin pasajeros por aerolínea en 2022", "2022-01-01", "2022-12-31"
    fig.add_vrect(
        x0=x0, x1=x1, fillcolor=tema.REJILLA, opacity=0.6, line_width=0, layer="below",
        annotation_text=nota, annotation_position="top left",
        annotation_font=dict(size=11, color=tema.TEXTO_2), row=1, col=1,
    )

    fig.update_layout(height=520, margin=dict(l=64, r=16, t=40, b=40), hovermode="closest", uirevision="v7")
    fig.update_annotations(font=dict(size=13, color=tema.TEXTO), selector=dict(xref="paper"))
    fig.update_yaxes(rangemode="tozero", tickformat=",.0f")
    fig.update_xaxes(tickformat="%Y", dtick="M12", showgrid=False)
    return fig


# ---------------------------------------------------------------- layout

layout = html.Div(
    className="pagina",
    children=[
        html.H1("Conectividad aérea: Aeropuerto Mundo Maya", className="pagina-titulo"),
        html.P(
            "¿Cuánto pesa cada aerolínea en los pasajeros del aeropuerto y qué tan dependiente es Petén de "
            "pocos operadores? Datos de la DGAC, enero 2022 a abril 2026.",
            className="pagina-pregunta",
        ),
        html.Div(_indicadores(), className="fila-kpi"),
        dcc.Store(id="conectividad-operador"),
        html.Div(
            className="estado-seleccion", role="status",
            children=[
                html.Span(id="conectividad-estado"),
                html.Button("Quitar selección", id="conectividad-quitar", className="boton-enlace", n_clicks=0),
            ],
        ),
        tarjeta_grafica(
            "¿Qué aerolíneas concentran los pasajeros?",
            "Pasajeros por año y aerolínea; mientras más grande el bloque, más pasajeros. Sirve para medir "
            "la dependencia de pocos operadores y el riesgo si uno reduce su servicio.",
            "conectividad-v6",
            ayuda="Haz clic en un año para ver sus aerolíneas y en la barra superior para regresar. "
                  "Haz clic en una aerolínea para ver su detalle mes a mes abajo.",
        ),
        tarjeta_grafica(
            "¿Cómo se mueven los pasajeros y los vuelos mes a mes?",
            "Arriba, personas; abajo, vuelos. Cada medida tiene su propia escala porque no se pueden "
            "comparar entre sí. Sirve para ver si más vuelos significan más pasajeros y detectar caídas de servicio.",
            "conectividad-v7",
            ayuda="Sin selección se muestra todo el aeropuerto. Los meses sin registro quedan en blanco: "
                  "no significan cero. Arrastra para acercar; doble clic para volver.",
        ),
        aviso(
            html.B("Sobre los datos. "),
            "El 2023 no existe en la base de pasajeros por segmento; aquí se reconstruye con la base por "
            "aerolínea (en 2024 y 2025 ambas bases dan el mismo total). El desglose por aerolínea empieza en 2023 "
            "y 2026 llega hasta abril. Un pasajero no es un turista: incluye residentes y personal. "
            "Las operaciones incluyen operadores que no transportan pasajeros comerciales (por ejemplo, vuelos "
            "militares) y la categoría Otros puede agrupar operadores distintos en cada base. "
            "Los cambios que se ven son observaciones; los datos no permiten atribuirles una causa.",
        ),
    ],
)


# ---------------------------------------------------------------- interacción

@callback(Output("conectividad-v6", "figure"), Input("conectividad-v6", "id"))
def dibujar_treemap(_):
    return figura_treemap()


@callback(
    Output("conectividad-operador", "data"),
    Input("conectividad-v6", "clickData"),
    Input("conectividad-quitar", "n_clicks"),
    State("conectividad-operador", "data"),
    prevent_initial_call=True,
)
def seleccionar_operador(clic, _quitar, actual):
    """Enlace V6 → V7: guarda la aerolínea elegida. Un segundo clic en la misma la quita."""
    if ctx.triggered_id != "conectividad-v6" or not clic:
        return None
    identificador = clic["points"][0].get("id", "")
    if "|" not in identificador:  # clic en un año: solo baja de nivel, no elige aerolínea
        return dash.no_update
    operador = identificador.split("|", 1)[1]
    return None if operador == actual else operador


@callback(
    Output("conectividad-estado", "children"),
    Output("conectividad-quitar", "hidden"),
    Input("conectividad-operador", "data"),
)
def mostrar_seleccion(operador):
    if operador is None:
        return f"Mostrando: {TODO}. Haz clic en una aerolínea del gráfico de bloques para ver solo esa.", True
    return ["Mostrando: ", html.B(operador), " · clic de nuevo en ella para quitar"], False


@callback(Output("conectividad-v7", "figure"), Input("conectividad-operador", "data"))
def actualizar_v7(operador):
    return figura_pasajeros_operaciones(operador)
