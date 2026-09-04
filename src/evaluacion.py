"""
 Métricas comunes a todos los modelos (E1).

REGLA: siempre en escala original, nunca sobre logaritmos.py
"""

import numpy as np
import pandas as pd


def rmse(y, y_hat) -> float:
    """Raíz del error cuadrático medio."""
    return float(np.sqrt(np.mean((np.asarray(y) - np.asarray(y_hat)) ** 2)))


def mae(y, y_hat) -> float:
    """Error absoluto medio. Menos sensible a los picos extremos."""
    return float(np.mean(np.abs(np.asarray(y) - np.asarray(y_hat))))


def qlike(y, y_hat) -> float:
    """QLIKE = (y/ŷ) - log(y/ŷ) - 1.

    Asimétrica: penaliza más infraestimar que sobreestimar. Vale 0 solo
    si ŷ = y. Exige predicciones estrictamente positivas.
    """
    y, y_hat = np.asarray(y), np.asarray(y_hat)
    if np.any(y_hat <= 0):
        raise ValueError("QLIKE exige predicciones positivas")
    ratio = y / y_hat
    return float(np.mean(ratio - np.log(ratio) - 1))


def evaluar(y, y_hat, idx_estres, nombre: str) -> dict:
    """Las tres métricas, desglosadas en total / tranquilo / estrés."""
    y = pd.Series(y)
    y_hat = pd.Series(np.asarray(y_hat), index=y.index)
    m = y.index.isin(idx_estres)          # máscara: True en días de estrés

    fila = {"modelo": nombre}
    for suf, (a, b) in {"": (y, y_hat),
                        "_tranq": (y[~m], y_hat[~m]),
                        "_estres": (y[m], y_hat[m])}.items():
        fila[f"RMSE{suf}"] = rmse(a, b)
        fila[f"MAE{suf}"] = mae(a, b)
        fila[f"QLIKE{suf}"] = qlike(a, b)
    return fila


def tabla_resultados(filas: list[dict]) -> pd.DataFrame:
    """Lista de evaluaciones -> tabla ordenada por QLIKE."""
    return pd.DataFrame(filas).set_index("modelo").round(4).sort_values("QLIKE")