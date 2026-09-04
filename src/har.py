"""
Modelo HAR (Corsi, 2009). Etapa E3.

Regresión lineal sobre log RV(1), log RV(5) y log RV(22). Se estima por
mínimos cuadrados ordinarios, con solución cerrada.

HAR es el caso particular de ANFIS con una sola regla. Esto lo convierte en
el baseline más importante del trabajo: usa exactamente las mismas entradas,
de modo que cualquier diferencia es atribuible a la estructura del modelo.
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm

ENTRADAS = ["log_rv_1", "log_rv_5", "log_rv_22"]
OBJETIVO = "log_y"


def entrenar_har(train: pd.DataFrame):
    """Ajusta HAR por MCO sobre el conjunto de entrenamiento.

    sm.add_constant añade una columna de unos para el término independiente
    beta_0. Sin ella la recta pasaría forzosamente por el origen.
    """
    X = sm.add_constant(train[ENTRADAS])
    y = train[OBJETIVO]
    return sm.OLS(y, X).fit()


def predecir_har(modelo, datos: pd.DataFrame) -> pd.Series:
    """Predice en ESCALA ORIGINAL.

    El modelo se ajustó sobre log_y, así que devuelve logaritmos. Aplicamos
    la exponencial para volver a unidades de volatilidad, que es donde se
    calculan todas las métricas (notas/05: sesgo de Jensen).

    Ventaja colateral: exp() es siempre positiva, así que nunca se predicen
    volatilidades negativas.
    """
    X = sm.add_constant(datos[ENTRADAS], has_constant="add")
    return pd.Series(np.exp(modelo.predict(X)), index=datos.index)