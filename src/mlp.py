"""
Perceptrón multicapa (E4).

Modelo no lineal pero NO difuso. Permite distinguir si
una eventual mejora de ANFIS proviene de la no linealidad o de la estructura
de reglas difusas.

Arquitectura deliberadamente pequeña (3 -> 8 -> 1, unos 41 parámetros) para
que sea comparable en capacidad con el ANFIS de 27 reglas.
"""

import numpy as np
import pandas as pd
import torch
import torch.nn as nn

ENTRADAS = ["log_rv_1", "log_rv_5", "log_rv_22"]
OBJETIVO = "log_y"
SEMILLA = 42


class MLP(nn.Module):
    """Red de una capa oculta con activación tanh.

    nn.Linear(a, b) es una aplicación afín: x -> Wx + b. La no linealidad la
    aporta tanh entre ambas capas; sin ella, componer dos aplicaciones afines
    daría otra aplicación afín y la red no sería más que un HAR con pasos
    intermedios.

    Se usa tanh y no ReLU porque la superficie a aprender es suave y la red
    es muy pequeña: con 8 neuronas, ReLU daría una función lineal a trozos
    con pocos tramos.
    """

    def __init__(self, n_entradas: int = 3, n_ocultas: int = 8):
        super().__init__()
        self.red = nn.Sequential(
            nn.Linear(n_entradas, n_ocultas),
            nn.Tanh(),
            nn.Linear(n_ocultas, 1),
        )

    def forward(self, x):
        # .squeeze(-1) quita la última dimensión: (n, 1) -> (n,)
        return self.red(x).squeeze(-1)


def _a_tensor(datos: pd.DataFrame):
    """DataFrame -> tensores de PyTorch en float32."""
    X = torch.tensor(datos[ENTRADAS].values, dtype=torch.float32)
    y = torch.tensor(datos[OBJETIVO].values, dtype=torch.float32)
    return X, y


def entrenar_mlp(train, val, n_ocultas=8, epocas=2000, lr=0.01, paciencia=100):
    """Entrena por descenso de gradiente con parada temprana.

    - MSELoss: error cuadrático medio, la función de pérdida.
    - Adam: variante del descenso de gradiente con paso adaptativo.
    - Parada temprana: se guarda el estado con menor error de VALIDACIÓN y
      se detiene si no mejora durante `paciencia` épocas. Sin esto la red
      acabaría memorizando el ruido del entrenamiento.

    El conjunto de prueba NO interviene en ningún momento.
    """
    torch.manual_seed(SEMILLA)   # reproducibilidad: fija la inicialización
    np.random.seed(SEMILLA)

    X_tr, y_tr = _a_tensor(train)
    X_val, y_val = _a_tensor(val)

    modelo = MLP(len(ENTRADAS), n_ocultas)
    perdida = nn.MSELoss()
    optimizador = torch.optim.Adam(modelo.parameters(), lr=lr)

    mejor_val, mejor_estado, sin_mejora = float("inf"), None, 0
    historial = []

    for epoca in range(epocas):
        # --- Paso de entrenamiento ---
        modelo.train()
        optimizador.zero_grad()          # borra los gradientes anteriores
        error = perdida(modelo(X_tr), y_tr)
        error.backward()                 # retropropagación
        optimizador.step()               # actualiza los pesos

        # --- Evaluación en validación (sin calcular gradientes) ---
        modelo.eval()
        with torch.no_grad():
            error_val = perdida(modelo(X_val), y_val).item()

        historial.append((error.item(), error_val))

        # --- Parada temprana ---
        if error_val < mejor_val:
            mejor_val = error_val
            mejor_estado = {k: v.clone() for k, v in modelo.state_dict().items()}
            sin_mejora = 0
        else:
            sin_mejora += 1
            if sin_mejora >= paciencia:
                print(f"[mlp] Parada temprana en la época {epoca}")
                break

    modelo.load_state_dict(mejor_estado)   # recuperamos el mejor estado
    n_par = sum(p.numel() for p in modelo.parameters())
    print(f"[mlp] MSE de validación: {mejor_val:.5f} | parámetros: {n_par}")

    return modelo, historial


def predecir_mlp(modelo, datos: pd.DataFrame) -> pd.Series:
    """Predice en ESCALA ORIGINAL (deshace el logaritmo con exp)."""
    X, _ = _a_tensor(datos)
    modelo.eval()
    with torch.no_grad():
        log_pred = modelo(X).numpy()
    return pd.Series(np.exp(log_pred), index=datos.index)