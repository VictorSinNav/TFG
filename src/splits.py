"""
Partición temporal del dataset (E0.6).

Divide el dataset por fechas (nunca al azar) y aplica un embargo en las
fronteras para evitar solapamiento del objetivo.

Uso:  python -m src.splits from src.splits import particionar, normalizar
"""

import pandas as pd

from src.features import construir_dataset

# ---------------------------------------------------------------- CONFIG
FIN_TRAIN = "2015-12-31"
FIN_VAL = "2019-12-31"
INICIO_ESTRES = "2020-02-15"
FIN_ESTRES = "2020-04-30"

HORIZONTE = 5          # el objetivo mira 5 días adelante
EMBARGO = HORIZONTE    # filas a descartar al final de train y val

ENTRADAS = ["log_rv_1", "log_rv_5", "log_rv_22"]
OBJETIVO = "log_y"


def particionar(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Divide el dataset en train / val / test, con embargo en las fronteras.

    El embargo elimina las últimas EMBARGO filas de train y de val.
    """
    train = df.loc[:FIN_TRAIN]
    val = df.loc[pd.Timestamp(FIN_TRAIN) + pd.Timedelta(days=1):FIN_VAL]
    test = df.loc[pd.Timestamp(FIN_VAL) + pd.Timedelta(days=1):]

    # .iloc[:-EMBARGO] descarta las últimas filas. Solo en train y val:
    # test es el final de la serie y no invade nada.
    train = train.iloc[:-EMBARGO]
    val = val.iloc[:-EMBARGO]

    estres = test.loc[INICIO_ESTRES:FIN_ESTRES]

    for nombre, parte in [("train", train), ("val", val),
                          ("test", test), ("estres", estres)]:
        print(f"[splits] {nombre:7s}: {len(parte):5d} filas  "
              f"({parte.index[0].date()} → {parte.index[-1].date()})")

    return {"train": train, "val": val, "test": test, "estres": estres}


def normalizar(partes: dict[str, pd.DataFrame]) -> tuple[dict, dict]:
    """Estandariza las entradas: (x - media) / desviación.
    """
    media = partes["train"][ENTRADAS].mean()
    desv = partes["train"][ENTRADAS].std()

    normalizadas = {}
    for nombre, parte in partes.items():
        copia = parte.copy()
        copia[ENTRADAS] = (copia[ENTRADAS] - media) / desv
        normalizadas[nombre] = copia

    estadisticos = {"media": media, "desv": desv}
    return normalizadas, estadisticos


def verificar_sin_fuga(partes: dict[str, pd.DataFrame]) -> None:
    """Comprueba que la partición no solapa. Lanza error si algo falla."""
    train, val, test = partes["train"], partes["val"], partes["test"]

    # 1) Orden estricto entre bloques
    if not train.index.max() < val.index.min():
        raise ValueError("train y val se solapan")
    if not val.index.max() < test.index.min():
        raise ValueError("val y test se solapan")

    # 2) Ninguna fecha aparece en dos conjuntos
    if len(set(train.index) & set(val.index)) > 0:
        raise ValueError("fechas compartidas entre train y val")
    if len(set(val.index) & set(test.index)) > 0:
        raise ValueError("fechas compartidas entre val y test")

    # 3) El embargo cubre el horizonte del objetivo
    hueco_tv = (val.index.min() - train.index.max()).days
    hueco_vt = (test.index.min() - val.index.max()).days
    if hueco_tv < HORIZONTE or hueco_vt < HORIZONTE:
        raise ValueError(f"embargo insuficiente: {hueco_tv}, {hueco_vt} días")

    print(f"[splits] Sin fuga. Huecos de {hueco_tv} y {hueco_vt} días "
          f"naturales en las fronteras.")


if __name__ == "__main__":
    df = construir_dataset(guardar=False)
    partes = particionar(df)
    verificar_sin_fuga(partes)
    partes_norm, est = normalizar(partes)

    print("\nEstadísticos de normalización (calculados solo con train):")
    print(pd.DataFrame({"media": est["media"], "desv": est["desv"]}).round(4))