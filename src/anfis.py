"""
Sistema de inferencia neuro-difusa adaptativa (E5).

Implementación desde cero en PyTorch, capa por capa. Es la aportación relevante
del trabajo, por lo que no se emplea ninguna biblioteca de ANFIS.

Estructura del fichero:
  E5.1  Capa 1: funciones de pertenencia   
  E5.2  Capas 2-5: inferencia hacia delante
  E5.3  Inicialización por percentiles
  E5.4  Entrenamiento
"""

import numpy as np
import torch
import torch.nn as nn

ENTRADAS = ["log_rv_1", "log_rv_5", "log_rv_22"]
OBJETIVO = "log_y"
SEMILLA = 42


class CapaPertenencia(nn.Module):
    """Capa 1 de ANFIS: fuzzificación.

    Transforma cada entrada numérica en sus grados de pertenencia a los
    conjuntos difusos definidos sobre esa variable. Con 3 entradas y 3
    conjuntos por entrada, un vector de 3 números se convierte en una
    matriz 3x3 de grados en [0, 1].

    Se usa la campana generalizada de Jang (1993):

        mu(x) = 1 / (1 + |(x - c)/a|^(2b))


    Los tres parámetros son nn.Parameter, es decir, PyTorch los registra
    como entrenables y calcula sus gradientes automáticamente. Esta es la
    idea central de ANFIS: las funciones de pertenencia no se fijan a mano,
    se aprenden de los datos.
    """

    def __init__(self, n_entradas: int = 3, n_conjuntos: int = 3):
        super().__init__()
        self.n_entradas = n_entradas
        self.n_conjuntos = n_conjuntos

        # Cada parámetro es una matriz (n_entradas x n_conjuntos):
        # una fila por variable, una columna por conjunto difuso.
        # Se inicializan provisionalmente; E5.3 los fijará por percentiles.
        self.c = nn.Parameter(torch.zeros(n_entradas, n_conjuntos))
        self.a = nn.Parameter(torch.ones(n_entradas, n_conjuntos))

        # b se guarda en logaritmo para garantizar que b = exp(log_b) > 0
        # durante todo el entrenamiento. Si b pudiera hacerse negativo, la
        # campana se invertiría y perdería sentido. Es una reparametrización
        # habitual para imponer restricciones de positividad sin recurrir a
        # optimización con restricciones.
        self.log_b = nn.Parameter(torch.zeros(n_entradas, n_conjuntos))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """x de forma (N, n_entradas) -> grados (N, n_entradas, n_conjuntos).

        El truco es x.unsqueeze(-1), que añade una dimensión al final:
        (N, 3) pasa a (N, 3, 1). Al operar con c, que es (3, 3), PyTorch
        aplica broadcasting y expande automáticamente a (N, 3, 3), de modo
        que cada valor se compara con los 3 conjuntos de su variable sin
        escribir ningún bucle.
        """
        b = torch.exp(self.log_b)

        # Se suma un epsilon a |a| para evitar dividir por cero si la
        # anchura colapsa durante el entrenamiento.
        a_seguro = torch.abs(self.a) + 1e-6

        z = torch.abs((x.unsqueeze(-1) - self.c) / a_seguro)

        return 1.0 / (1.0 + z ** (2 * b))


class ANFIS(nn.Module):
    """Sistema de inferencia neuro-difusa de tipo Takagi-Sugeno de orden 1.

    Cinco capas:
      1. Fuzzificación: entradas -> grados de pertenencia (CapaPertenencia)
      2. Activación de reglas: producto de pertenencias (t-norma)
      3. Normalización: los pesos pasan a sumar 1
      4. Consecuentes: una función lineal por regla
      5. Salida: media ponderada de los consecuentes

    Con 3 entradas y 3 conjuntos: 27 reglas, 27 parámetros de premisa
    (a, b, c) y 108 de consecuente (4 por regla). Total 135.

    Caso límite: con una sola regla el peso normalizado vale 1 para todo x
    y la salida se reduce a una función lineal, es decir, al modelo HAR.
    """

    def __init__(self, n_entradas: int = 3, n_conjuntos: int = 3):
        super().__init__()
        self.n_entradas = n_entradas
        self.n_conjuntos = n_conjuntos
        self.n_reglas = n_conjuntos ** n_entradas      # 27

        self.pertenencia = CapaPertenencia(n_entradas, n_conjuntos)

        # --- Índices de las reglas ---
        # Cada regla es una combinación: qué conjunto toma de cada variable.
        # register_buffer lo guarda en el modelo SIN hacerlo entrenable:
        # es una constante estructural, no un parámetro.
        indices = torch.cartesian_prod(
            *[torch.arange(n_conjuntos) for _ in range(n_entradas)]
        )                                              # (27, 3)
        self.register_buffer("indices_reglas", indices)

        # --- Consecuentes ---
        self.p = nn.Parameter(torch.zeros(self.n_reglas, n_entradas))
        self.q = nn.Parameter(torch.zeros(self.n_reglas))

    def pesos_reglas(self, x: torch.Tensor) -> torch.Tensor:
        """Capas 2 y 3: activación y normalización. Devuelve (N, 27).

        Se expone como método propio porque en E7 necesitaremos consultar
        qué reglas se activan cada día.
        """
        mu = self.pertenencia(x)                       # (N, 3, 3)

        # Para cada regla, seleccionamos el conjunto que le toca de cada
        # variable. Resultado (N, 27, 3).
        idx = self.indices_reglas.unsqueeze(0).expand(x.shape[0], -1, -1)
        mu_exp = mu.unsqueeze(1).expand(-1, self.n_reglas, -1, -1)
        seleccion = torch.gather(mu_exp, 3, idx.unsqueeze(-1)).squeeze(-1)

        # Capa 2: t-norma producto ("Y" difuso). Si una pertenencia es
        # baja, la regla entera se apaga.
        w = seleccion.prod(dim=2)                      # (N, 27)

        # Capa 3: normalización. El epsilon evita dividir por cero.
        return w / (w.sum(dim=1, keepdim=True) + 1e-12)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Capas 4 y 5: consecuentes y media ponderada. Devuelve (N,)."""
        w_norm = self.pesos_reglas(x)                  # (N, 27)

        # Capa 4: f_i(x) = p_i · x + q_i para las 27 reglas a la vez.
        f = x @ self.p.t() + self.q                    # (N, 27)

        # Capa 5: localmente lineal, globalmente no lineal.
        return (w_norm * f).sum(dim=1)                 # (N,)



def inicializar_por_percentiles(modelo: "ANFIS", train, coef_har=None) -> None:
    """Coloca premisas y consecuentes en valores sensatos antes de entrenar.


    Estrategia:
      - Centros en los percentiles de cada variable, para que cada conjunto
        caiga en una zona poblada.
      - Anchuras iguales a la mitad de la separación entre centros
        consecutivos, de modo que las campanas se solapen.
      - b = 1 (campana estándar).
      - Consecuentes iguales a los coeficientes de HAR: como HAR es ANFIS
        con una sola regla, esto equivale a partir de la solución de HAR y
        garantiza que el entrenamiento solo pueda mejorar desde ahí.

    """
    n_conj = modelo.n_conjuntos
    X = train[ENTRADAS].values

    # Percentiles equiespaciados: con 3 conjuntos -> 10, 50, 90.
    ps = np.linspace(10, 90, n_conj)
    centros = np.array([np.percentile(X[:, k], ps)
                        for k in range(modelo.n_entradas)])   # (3, 3)

    # Anchura: mitad de la separación media entre centros consecutivos.
    # Con este valor, en el punto medio entre dos centros ambas campanas
    # valen aproximadamente 0.5, lo que asegura solapamiento.
    separaciones = np.diff(centros, axis=1).mean(axis=1, keepdims=True)
    anchuras = np.repeat(separaciones / 2, n_conj, axis=1)     # (3, 3)

    with torch.no_grad():   # modificamos parámetros sin registrar gradientes
        modelo.pertenencia.c.copy_(torch.tensor(centros, dtype=torch.float32))
        modelo.pertenencia.a.copy_(torch.tensor(anchuras, dtype=torch.float32))
        modelo.pertenencia.log_b.fill_(0.0)                    # b = 1

        if coef_har is not None:
            # coef_har = [beta_0, beta_1, beta_2, beta_3].
            # Todas las reglas arrancan con la misma recta: la de HAR.
            modelo.q.fill_(float(coef_har[0]))
            modelo.p.copy_(torch.tensor(coef_har[1:], dtype=torch.float32)
                           .repeat(modelo.n_reglas, 1))
        else:
            modelo.p.zero_()
            modelo.q.zero_()

    print(f"[anfis] Centros por variable:\n{centros.round(3)}")
    print(f"[anfis] Anchuras: {anchuras[:, 0].round(3)}")


def entrenar_anfis(modelo, train, val, epocas=3000, lr_consec=0.01,
                   lr_premisa=0.001, paciencia=200):
    """Entrena ANFIS por descenso de gradiente con parada temprana.

    Mínimos cuadrados para los consecuentes y gradiente para las premisas. Aquí usamos gradiente sobre
    todos los parámetros, porque la inicialización ya parte de la solución
    de HAR, que es lo que los mínimos cuadrados darían en el primer paso.

    Tasas de aprendizaje distintas por grupo: mover un centro reorganiza qué
    reglas se activan y tiene un efecto mucho más brusco que ajustar un
    coeficiente de una recta. Un paso diez veces menor en las premisas evita
    que la estructura difusa se destruya en las primeras épocas.
    """
    torch.manual_seed(SEMILLA)

    X_tr = torch.tensor(train[ENTRADAS].values, dtype=torch.float32)
    y_tr = torch.tensor(train[OBJETIVO].values, dtype=torch.float32)
    X_val = torch.tensor(val[ENTRADAS].values, dtype=torch.float32)
    y_val = torch.tensor(val[OBJETIVO].values, dtype=torch.float32)

    perdida = nn.MSELoss()

    # Adam admite grupos de parámetros con hiperparámetros propios.
    optimizador = torch.optim.Adam([
        {"params": modelo.pertenencia.parameters(), "lr": lr_premisa},
        {"params": [modelo.p, modelo.q], "lr": lr_consec},
    ])

    mejor_val, mejor_estado, sin_mejora = float("inf"), None, 0
    historial = []

    for epoca in range(epocas):
        modelo.train()
        optimizador.zero_grad()
        error = perdida(modelo(X_tr), y_tr)
        error.backward()
        optimizador.step()

        modelo.eval()
        with torch.no_grad():
            error_val = perdida(modelo(X_val), y_val).item()
        historial.append((error.item(), error_val))

        if error_val < mejor_val - 1e-7:      # tolerancia: evita paradas por ruido
            mejor_val, sin_mejora = error_val, 0
            mejor_estado = {k: v.clone() for k, v in modelo.state_dict().items()}
        else:
            sin_mejora += 1
            if sin_mejora >= paciencia:
                print(f"[anfis] Parada temprana en la época {epoca}")
                break

    modelo.load_state_dict(mejor_estado)
    print(f"[anfis] MSE de validación: {mejor_val:.5f}")

    # Diagnóstico: si las anchuras se han disparado, las campanas se aplanan,
    # todas las reglas pesan igual y ANFIS degenera en HAR.
    with torch.no_grad():
        a_med = modelo.pertenencia.a.abs().mean().item()
    print(f"[anfis] Anchura media final: {a_med:.3f}")

    return modelo, historial


def predecir_anfis(modelo, datos) -> "pd.Series":
    """Predice en ESCALA ORIGINAL (deshace el logaritmo con exp)."""
    import pandas as pd
    X = torch.tensor(datos[ENTRADAS].values, dtype=torch.float32)
    modelo.eval()
    with torch.no_grad():
        log_pred = modelo(X).numpy()
    return pd.Series(np.exp(log_pred), index=datos.index)