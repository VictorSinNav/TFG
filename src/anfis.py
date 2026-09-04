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