"""
Modelos de referencia sin parámetros (E1).

No se entrenan: predicen copiando la volatilidad pasada. Se aplican
directamente al conjunto de prueba.
"""

import pandas as pd


def predecir_ingenuo(datos: pd.DataFrame, columna: str = "rv_5") -> pd.Series:
    """ŷ_t = valor de `columna` en el día t."""
    return datos[columna].copy()