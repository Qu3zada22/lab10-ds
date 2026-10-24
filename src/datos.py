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
