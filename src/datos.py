"""Carga y limpieza de las fuentes del tablero.

Las fuentes originales van en la carpeta `datos/` (no se versionan, ver README).
Cada función se cachea para que la app lea el Excel una sola vez.
"""

from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "datos"

MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]
MESES_CORTOS = [m[:3] for m in MESES]

ARCHIVO_TIKAL = DATOS / "Visitantes_Tikal_2017-2026.xlsx"

# Abril a septiembre de 2020 el parque estuvo cerrado: el 0 es real.
CIERRE_INICIO = pd.Timestamp("2020-04-01")
CIERRE_FIN = pd.Timestamp("2020-09-01")
# Enero de 2017 viene en 0, pero el resto del año no, así que se trata como sin dato.
MESES_SIN_DATO = [pd.Timestamp("2017-01-01")]


@lru_cache
def tikal() -> pd.DataFrame:
    """Boletos al Parque Nacional Tikal en formato largo.

    Columnas: fecha, anio, mes, segmento, visitantes, estado.
    `estado` es "normal", "cerrado" (pandemia) o "sin dato".
    """
    df = pd.read_excel(ARCHIVO_TIKAL, sheet_name="Datos")
    # La columna "otros" viene con un espacio al final en el Excel original
    df.columns = df.columns.str.strip()

    df["mes"] = df["mes"].str.strip().str.capitalize().map(
        {nombre: i + 1 for i, nombre in enumerate(MESES)}
    )
    df["fecha"] = pd.to_datetime(dict(year=df["año"], month=df["mes"], day=1))

    largo = df.melt(
        id_vars=["fecha"],
        value_vars=["nacionales", "extranjeros", "otros"],
        var_name="segmento",
        value_name="visitantes",
    )
    largo["segmento"] = largo["segmento"].str.capitalize()
    largo["visitantes"] = largo["visitantes"].astype(float)
    largo["anio"] = largo["fecha"].dt.year
    largo["mes"] = largo["fecha"].dt.month

    cerrado = largo["fecha"].between(CIERRE_INICIO, CIERRE_FIN)
    sin_dato = largo["fecha"].isin(MESES_SIN_DATO)
    largo["estado"] = np.select([cerrado, sin_dato], ["cerrado", "sin dato"], "normal")
    largo.loc[sin_dato, "visitantes"] = np.nan

    return largo.sort_values(["fecha", "segmento"]).reset_index(drop=True)


# ---------------------------------------------------------------- AIMM (conectividad aérea)

ARCHIVO_AIMM_AEROLINEAS = DATOS / "AIMM_Aerolineas_2023-2026.xlsx"
ARCHIVO_AIMM_SEGMENTOS = DATOS / "AIMM_Consolidado_2022-2025.xlsx"
ARCHIVO_AIMM_OPERACIONES = DATOS / "AIMM_Operaciones_Aeronauticas_2022-2026.xlsx"

# Los archivos nombran distinto al mismo operador (AERORUTA / AERO RUTA MAYA), así que se unifican.
OPERADORES = {
    "AERORUTA": "Aero Ruta Maya",
    "AERO RUTA MAYA": "Aero Ruta Maya",
    "AVIATECA": "Aviateca",
    "T.A.G.": "T.A.G.",
    "TROPIC AIR": "Tropic Air",
    "PRIVADOS": "Privados",
    "VUELOS PRIV. CONTROLADOS POR FBO": "Privados controlados (FBO)",
    "OTROS": "Otros",
    "ARMSA / AEROMAR": "ARMSA / Aeromar",
    "CHARTER PRIVADOS": "Charter privados",
    "VUELOS MILITARES EN AIMM": "Vuelos militares",
}


def _con_fecha(df: pd.DataFrame, anio: str, mes: str) -> pd.DataFrame:
    df = df.copy()
    df["anio"] = df[anio].astype(int)
    df["mes"] = df[mes].astype(int)
    df["fecha"] = pd.to_datetime(dict(year=df["anio"], month=df["mes"], day=1))
    return df


@lru_cache
def aimm_aerolineas() -> pd.DataFrame:
    """Pasajeros del AIMM por aerolínea y sentido, ene 2023 a abr 2026.

    Columnas: fecha, anio, mes, operador, flujo, pasajeros. Si una aerolínea no tiene fila en un mes
    (por ejemplo Tropic Air en 2026) ese mes queda sin dato, no en 0.
    """
    df = _con_fecha(pd.read_excel(ARCHIVO_AIMM_AEROLINEAS, sheet_name="Base de Datos"), "Año", "mes_numero")
    df["operador"] = df["Aerolínea"].map(OPERADORES)
    return df.rename(columns={"Tipo de Flujo": "flujo", "Pasajeros": "pasajeros"})[
        ["fecha", "anio", "mes", "operador", "flujo", "pasajeros"]
    ]


@lru_cache
def aimm_segmentos() -> pd.DataFrame:
    """Pasajeros del AIMM por segmento (doméstico, internacional, privado). Años 2022, 2024 y 2025.

    Columnas: fecha, anio, mes, segmento, flujo, pasajeros. El archivo no trae 2023.
    """
    df = pd.read_excel(ARCHIVO_AIMM_SEGMENTOS, sheet_name="Base Consolidada", header=2)
    df = _con_fecha(df, "Año", "N° Mes")
    return df.rename(columns={"Tipo de Pasajero": "segmento", "Tipo de Flujo": "flujo", "Pasajeros": "pasajeros"})[
        ["fecha", "anio", "mes", "segmento", "flujo", "pasajeros"]
    ]


@lru_cache
def aimm_operaciones() -> pd.DataFrame:
    """Operaciones aéreas (aterrizajes y despegues) por operador, ene 2022 a abr 2026.

    Columnas: fecha, anio, mes, operador, tipo, operaciones. Son vuelos, no personas.
    """
    df = pd.read_excel(ARCHIVO_AIMM_OPERACIONES, sheet_name="Base de Operaciones", header=2)
    df = _con_fecha(df, "Año", "N° Mes")
    df["operador"] = df["Operador"].map(OPERADORES)
    return df.rename(columns={"Tipo de Operación": "tipo", "Operaciones": "operaciones"})[
        ["fecha", "anio", "mes", "operador", "tipo", "operaciones"]
    ]


@lru_cache
def aimm_pasajeros_total() -> pd.DataFrame:
    """Pasajeros totales del AIMM por mes (entradas + salidas), ene 2022 a abr 2026.

    2022, 2024 y 2025 salen de la base por segmento. 2023 no existe ahí, así que se reconstruye con
    la base por aerolínea, igual que 2026. Los totales de 2024 y 2025 coinciden en ambas bases.
    Columnas: fecha, anio, mes, pasajeros, fuente.
    """
    seg = aimm_segmentos().groupby("fecha")["pasajeros"].sum().reset_index().assign(fuente="segmento")
    aero = aimm_aerolineas()
    aero = aero[~aero["anio"].isin(seg["fecha"].dt.year.unique())]
    aero = aero.groupby("fecha")["pasajeros"].sum().reset_index().assign(fuente="aerolinea")
    total = pd.concat([seg, aero]).sort_values("fecha").reset_index(drop=True)
    total["anio"], total["mes"] = total["fecha"].dt.year, total["fecha"].dt.month
    return total


# ---------------------------------------------------------------- Hospedaje

ARCHIVO_OCUPACION = DATOS / "indice_ocupacion_mensual_2023_2025_1.csv"
ARCHIVO_OFERTA = DATOS / "oferta_hotelera_2022_2026.csv"
TIPOS_ALOJAMIENTO = ["Hotel", "Hospedaje", "Pensión"]


@lru_cache
def ocupacion_peten() -> pd.DataFrame:
    """Índice de ocupación hotelera de todo el departamento de Petén, ene 2023 a dic 2025.

    Columnas: fecha, anio, mes, ocupacion (de 0 a 1). No hay datos de 2026.
    """
    df = pd.read_csv(ARCHIVO_OCUPACION)
    df = df[df["departamento"].str.startswith("Pet")]
    df["fecha"] = pd.to_datetime(dict(year=df["anio"], month=df["mes"], day=1))
    return df.rename(columns={"indice_ocupacion": "ocupacion"})[["fecha", "anio", "mes", "ocupacion"]].reset_index(drop=True)


@lru_cache
def oferta_peten() -> pd.DataFrame:
    """Capacidad instalada de Petén por tipo de alojamiento. Cortes: 4.º trim. 2022 a 2025 y 1.er trim. 2026.

    Columnas: anio, trimestre, tipo, establecimientos, habitaciones, plazas_cama. No es una serie mensual.
    """
    df = pd.read_csv(ARCHIVO_OFERTA)
    df = df[df["departamento"].str.startswith("Pet")]
    return df.rename(columns={"tipo_alojamiento": "tipo"}).drop(columns="departamento").reset_index(drop=True)
