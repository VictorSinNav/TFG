"""

Construcción del dataset de modelado (E0.5).

Convierte la tabla de precios de src/data.py en la tabla final:
una fila por día con las entradas RV(1), RV(5), RV(22) y el objetivo y
a 5 días vista.

Uso:  python -m src.features from src.features import construir_dataset
"""

from pathlib import Path

import numpy as np
import pandas as pd

from src.data import cargar_precios

# ---------------------------------------------------------------- CONFIG
DIAS_ANIO = 252          # sesiones bursátiles al año (factor de anualización)
VENTANAS = (1, 5, 22)    # día, semana y mes bursátiles
HORIZONTE = 5            # días hacia delante que predecimos

RAIZ = Path(__file__).resolve().parents[1]
DIR_PROC = RAIZ / "data" / "processed"
RUTA_CSV = DIR_PROC / "dataset.csv"


def calcular_rendimientos(precios: pd.DataFrame) -> pd.Series:
    """r_t = log(P_t) - log(P_{t-1}).
    .diff() resta a cada fila la anterior. La primera queda NaN porque no
    existe P_{t-1}; se elimina al final del proceso.
    """
    return np.log(precios["Close"]).diff()


def volatilidad_pasada(r: pd.Series, w: int) -> pd.Series:
    """RV_t^(w) = sqrt( (252/w) * suma de r^2 sobre los ÚLTIMOS w días ).
    
    rolling(w) define una ventana móvil que TERMINA en la fila actual: para
    la fila t usa las filas t-w+1 ... t. Solo mira hacia atrás, así que no
    puede haber fuga de información.

    Incluir el propio día t es correcto: al cierre de t su rendimiento ya
    es conocido.
    """
    return np.sqrt(DIAS_ANIO / w * (r ** 2).rolling(window=w).sum())


def volatilidad_futura(r: pd.Series, h: int = HORIZONTE) -> pd.Series:
    """y_t = sqrt( (252/h) * suma de r^2 sobre los h días SIGUIENTES ).

    Como rolling solo mira atrás, calculamos la ventana que termina en t+h
    y la desplazamos con shift(-h) para colocarla en la fila t.

    shift(-h) trae valores del futuro. Es la ÚNICA operación del proyecto
    que lo hace, y solo es legítima aquí, en el objetivo. Si apareciese en
    una variable de entrada, habría fuga de información.
    """
    rv_ventana = np.sqrt(DIAS_ANIO / h * (r ** 2).rolling(window=h).sum())
    return rv_ventana.shift(-h)


def construir_dataset(guardar: bool = True) -> pd.DataFrame:
    """Devuelve la tabla de modelado, limpia y sin NaN."""
    precios = cargar_precios()
    r = calcular_rendimientos(precios)

    df = pd.DataFrame(index=precios.index)
    df["close"] = precios["Close"]
    df["r"] = r

    # --- Entradas: volatilidad realizada a 1, 5 y 22 días ---
    for w in VENTANAS:
        df[f"rv_{w}"] = volatilidad_pasada(r, w)

    # --- Variable en reserva: rendimiento acumulado con signo (E6) ---
    df["ret_5"] = r.rolling(window=5).sum()

    # --- Objetivo ---
    df["y"] = volatilidad_futura(r, HORIZONTE)

    # --- Escala logarítmica ---
    # Se entrena en log (mejor convergencia, predicciones positivas al
    # deshacerlo) pero se evalúa en escala original. Guardamos ambas.
    for col in [f"rv_{w}" for w in VENTANAS] + ["y"]:
        df[f"log_{col}"] = np.log(df[col])

    # --- Limpieza ---
    # Primeras 22 filas: ventana incompleta. Últimas 5: no hay futuro.
    n_antes = len(df)
    df = df.dropna()
    print(f"[features] {n_antes} filas -> {len(df)} tras eliminar NaN")

    if guardar:
        DIR_PROC.mkdir(parents=True, exist_ok=True)
        df.to_csv(RUTA_CSV)
        print(f"[features] Guardado en {RUTA_CSV}")

    return df


if __name__ == "__main__":
    df = construir_dataset()
    print(df.head(), "\n")
    print(df[["rv_1", "rv_5", "rv_22", "y"]].describe().round(4), "\n")
    print(f"Rango: {df.index[0].date()} → {df.index[-1].date()}")