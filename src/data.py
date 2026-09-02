"""
Descarga y caché de precios diarios del S&P 500 (^GSPC).

Es nuestra única vía de entrada de datos externos al proyecto. No hace ningun
preprocesamiento ni transofrmación de los datos.

Uso:  python -m src.data from src.data import cargar_precios
"""

from pathlib import Path

import pandas as pd
import yfinance as yf

# ---------------------------------------------------------------- CONFIG
TICKER = "^GSPC"                # S&P 500 en Yahoo Finance
FECHA_INICIO = "2000-01-01"     # INCLUSIVA
FECHA_FIN = "2026-09-01"        # EXCLUSIVA -> último dato: 31-08-2026
COLUMNAS_ESPERADAS = {"Open", "High", "Low", "Close", "Volume"}
MINIMO_FILAS = 6_000            # ~26,6 años x ~252 sesiones ≈ 6.700

# ---------------------------------------------------------------- RUTAS
# __file__ es la ruta de este archivo. 
# parents[1] sube de src/ a la raíz del proyecto y así el módulo 
# funciona igual se llame desde donde se llame;
RAIZ = Path(__file__).resolve().parents[1]
DIR_RAW = RAIZ / "data" / "raw"
RUTA_CSV = DIR_RAW / f"{TICKER.replace('^', '')}_{FECHA_INICIO}_{FECHA_FIN}.csv"


def _descargar() -> pd.DataFrame:
    """Petición a Yahoo Finance."""
    print(f"[data] Descargando {TICKER} ({FECHA_INICIO} → {FECHA_FIN})...")
    datos = yf.download(
        tickers=TICKER,
        start=FECHA_INICIO,
        end=FECHA_FIN,
        interval="1d",
        auto_adjust=True,   # explícito, aunque ya sea el valor por defecto
        actions=False,      # sin columnas de dividendos/splits
        progress=False,
        threads=False,
        timeout=30,
    )
    # yf.download NO lanza excepción al fallar: devuelve None o vacío.
    if datos is None or datos.empty:
        raise RuntimeError(
            "Descarga vacía. Revisa conexión/ticker. Si Yahoo limita "
            "peticiones (YFRateLimitError), espera unos minutos."
        )
    return datos


def _aplanar(datos: pd.DataFrame) -> pd.DataFrame:
    """Deja columnas de un solo nivel: Open, High, Low, Close, Volume.
    yfinance sirmpre devuelve columnas MultiIndex (magnitud, ticker) 
    icluso en este caso que hay solo un activo
    """
    datos = datos.copy()
    if isinstance(datos.columns, pd.MultiIndex):
        # Localizamos el nivel que contiene el ticker (su orden depende de
        # group_by, por eso no se elimina el nivel 1 a ciegas).
        niveles = [n for n in range(datos.columns.nlevels)
                   if set(datos.columns.get_level_values(n)) == {TICKER}]
        datos.columns = datos.columns.droplevel(niveles[0] if niveles else -1)
    datos.columns = [str(c) for c in datos.columns]
    datos.index.name = "Date"
    return datos


def _validar(datos: pd.DataFrame) -> None:
    """Comprueba lo que todo lo posterior da por supuesto.
    Se usa raise y no assert: los assert se desactivan con python -O.
    """
    faltan = COLUMNAS_ESPERADAS - set(datos.columns)
    if faltan:
        raise ValueError(f"Faltan columnas: {sorted(faltan)}")
    if not isinstance(datos.index, pd.DatetimeIndex):
        raise TypeError("El índice no es DatetimeIndex (¿falta parse_dates?)")
    if not datos.index.is_monotonic_increasing:
        raise ValueError("Fechas no ordenadas de forma creciente")
    if datos.index.has_duplicates:
        raise ValueError("Hay fechas duplicadas")
    if datos["Close"].isna().any():
        raise ValueError(f"{int(datos['Close'].isna().sum())} NaN en Close")
    if (datos["Close"] <= 0).any():
        raise ValueError("Precios no positivos: log() no estaría definido")
    if len(datos) < MINIMO_FILAS:
        raise ValueError(f"Solo {len(datos)} filas, esperadas ≥ {MINIMO_FILAS}")


def cargar_precios(forzar_descarga: bool = False) -> pd.DataFrame:
    """Precios diarios del S&P 500. Descarga solo si no hay caché.
    Devuelve un DataFrame con DatetimeIndex
    """
    if RUTA_CSV.exists() and not forzar_descarga:
        print(f"[data] Caché local: {RUTA_CSV.name}")
        precios = pd.read_csv(RUTA_CSV, index_col=0, parse_dates=True)
        precios.index.name = "Date"
    else:
        precios = _aplanar(_descargar())
        DIR_RAW.mkdir(parents=True, exist_ok=True)
        precios.to_csv(RUTA_CSV)
        print(f"[data] Guardado en {RUTA_CSV}")

    # Se valida siempre, venga de la red o del disco.
    _validar(precios)
    return precios


# Este bloque solo se ejecuta con `python -m src.data`
if __name__ == "__main__":
    precios = cargar_precios()
    print(precios.head(), "\n")
    print(precios.tail(), "\n")
    print(f"Filas: {len(precios)}")
    print(f"Rango: {precios.index[0].date()} → {precios.index[-1].date()}")
    print(f"Columnas: {list(precios.columns)}")