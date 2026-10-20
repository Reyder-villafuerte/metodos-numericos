"""Método iterativo de Gauss-Seidel con historial educativo completo.

Este módulo no depende de Streamlit. Calcula realmente cada iteración y
conserva, para cada incógnita, los términos usados en la fórmula

    x_i^(k+1) = (b_i - sum_{j<i} a_ij x_j^(k+1) - sum_{j>i} a_ij x_j^(k)) / a_ii

de modo que la interfaz pueda explicar el procedimiento con los datos reales
de la ejecución. La característica que lo distingue de Jacobi es que cada
componente nueva se usa inmediatamente dentro de la misma iteración.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import permutations
from typing import Any

import numpy as np

from .sistemas_lineales import ErrorSistemaLineal


CRITERIOS_GAUSS_SEIDEL = {
    "absoluto": "Error absoluto ‖X⁽ᵏ⁺¹⁾ − X⁽ᵏ⁾‖∞",
    "relativo": "Error relativo ‖X⁽ᵏ⁺¹⁾ − X⁽ᵏ⁾‖∞ / ‖X⁽ᵏ⁺¹⁾‖∞",
    "residuo": "Residuo ‖AX⁽ᵏ⁺¹⁾ − b‖∞",
}

REORDENACIONES = {
    "si_hay_ceros": "Solo si hay ceros en la diagonal",
    "dominante": "Buscar un orden diagonalmente dominante",
    "nunca": "No reordenar las ecuaciones",
}

_EPS_DIAGONAL = np.finfo(float).eps
_LIMITE_DIVERGENCIA = 1e150
_MAX_N_PERMUTACIONES = 8


class ErrorGaussSeidel(ErrorSistemaLineal):
    """Error de validación del método de Gauss-Seidel."""


@dataclass
class TerminoGS:
    """Un producto a_ij·x_j usado al calcular x_i."""

    j: int  # índice base 0
    coeficiente: float
    valor: float
    nuevo: bool  # True si x_j pertenece a la iteración k+1

    @property
    def producto(self) -> float:
        return self.coeficiente * self.valor


@dataclass
class PasoVariableGS:
    i: int  # índice base 0
    b_i: float
    a_ii: float
    terminos: list[TerminoGS]
    suma_nuevos: float
    suma_anteriores: float
    numerador: float
    valor: float
    valor_anterior: float
    error_absoluto: float
    error_relativo: float | None


@dataclass
class IteracionGS:
    k: int
    x_anterior: np.ndarray
    x: np.ndarray
    pasos: list[PasoVariableGS]
    errores_absolutos: np.ndarray
    errores_relativos: list[float | None]
    norma_cambio: float
    error_relativo: float | None
    residuo_vector: np.ndarray
    residuo: float
    error: float | None  # valor del criterio seleccionado


@dataclass
class ResultadoGaussSeidel:
    metodo: str
    A: np.ndarray
    b: np.ndarray
    x0: np.ndarray
    x: np.ndarray
    tolerancia: float
    max_iter: int
    criterio: str
    iteraciones: int
    convergio: bool
    error: float | None
    motivo: str
    historial_detallado: list[IteracionGS]
    residuo_inicial: float
    A_original: np.ndarray
    b_original: np.ndarray
    permutacion: list[int] | None = None
    D: np.ndarray | None = None
    L: np.ndarray | None = None
    U: np.ndarray | None = None
    matriz_iteracion: np.ndarray | None = None
    vector_constante: np.ndarray | None = None
    valores_propios: np.ndarray | None = None
    radio_espectral: float | None = None
    dominancia: list[dict[str, Any]] = field(default_factory=list)
    estrictamente_dominante: bool = False

    # Compatibilidad con ResultadoIterativo -------------------------------
    @property
    def historial(self) -> list[dict[str, Any]]:
        return [
            {"iteracion": it.k, "x": it.x.copy(), "error": it.norma_cambio, "residuo": it.residuo}
            for it in self.historial_detallado
        ]

    @property
    def comprobacion(self) -> np.ndarray:
        return self.A @ self.x

    @property
    def residuo_vector(self) -> np.ndarray:
        return self.A @ self.x - self.b

    @property
    def norma_residuo(self) -> float:
        return float(np.linalg.norm(self.residuo_vector, ord=np.inf))

    @property
    def hubo_reordenacion(self) -> bool:
        return self.permutacion is not None and self.permutacion != list(range(len(self.b)))


# ---------------------------------------------------------------------------
# Validación
# ---------------------------------------------------------------------------

def _a_vector(valores: Any, nombre: str) -> np.ndarray:
    try:
        vector = np.asarray(valores, dtype=float).reshape(-1)
    except (TypeError, ValueError) as exc:
        raise ErrorGaussSeidel(f"Todos los valores de {nombre} deben ser numéricos.") from exc
    return vector


def validar_entrada_gauss_seidel(
    A: Any,
    b: Any,
    x0: Any | None,
    tolerancia: Any,
    max_iter: Any,
    criterio: str = "absoluto",
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float, int]:
    """Valida tipos, dimensiones y parámetros. No revisa la diagonal."""

    try:
        matriz = np.asarray(A, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ErrorGaussSeidel("Todos los coeficientes de la matriz A deben ser numéricos.") from exc
    if matriz.ndim != 2:
        raise ErrorGaussSeidel("A debe ser una matriz bidimensional.")
    filas, columnas = matriz.shape
    if filas != columnas:
        raise ErrorGaussSeidel(
            f"A debe ser cuadrada: tiene {filas} filas y {columnas} columnas."
        )
    if filas < 2:
        raise ErrorGaussSeidel("El sistema debe tener al menos dos incógnitas.")
    if not np.isfinite(matriz).all():
        raise ErrorGaussSeidel("Complete la matriz A con valores numéricos finitos (hay celdas vacías o inválidas).")

    vector = _a_vector(b, "b")
    if vector.shape != (filas,):
        raise ErrorGaussSeidel(
            f"El vector b debe tener {filas} componentes (tiene {vector.size})."
        )
    if not np.isfinite(vector).all():
        raise ErrorGaussSeidel("Complete el vector b con valores numéricos finitos.")

    inicial = np.zeros(filas) if x0 is None else _a_vector(x0, "X⁽⁰⁾")
    if inicial.shape != (filas,):
        raise ErrorGaussSeidel(
            f"El vector inicial X⁽⁰⁾ debe tener {filas} componentes (tiene {inicial.size})."
        )
    if not np.isfinite(inicial).all():
        raise ErrorGaussSeidel("Complete el vector inicial X⁽⁰⁾ con valores numéricos finitos.")

    try:
        tol = float(tolerancia)
    except (TypeError, ValueError) as exc:
        raise ErrorGaussSeidel("La tolerancia debe ser un número, por ejemplo 0.001.") from exc
    if not np.isfinite(tol) or tol <= 0:
        raise ErrorGaussSeidel("La tolerancia debe ser un número positivo y finito.")

    try:
        maximo_float = float(max_iter)
    except (TypeError, ValueError) as exc:
        raise ErrorGaussSeidel("El máximo de iteraciones debe ser un entero positivo.") from exc
    if not np.isfinite(maximo_float) or maximo_float < 1 or maximo_float != int(maximo_float):
        raise ErrorGaussSeidel("El máximo de iteraciones debe ser un entero positivo.")

    if criterio not in CRITERIOS_GAUSS_SEIDEL:
        raise ErrorGaussSeidel(f"Criterio de parada desconocido: {criterio}.")

    return matriz.copy(), vector.copy(), inicial.copy(), tol, int(maximo_float)


def diagonal_nula(A: np.ndarray) -> list[int]:
    """Índices (base 0) de los elementos diagonales numéricamente nulos."""

    escala = max(1.0, float(np.max(np.abs(A))))
    return [i for i in range(A.shape[0]) if abs(A[i, i]) <= _EPS_DIAGONAL * escala]


# ---------------------------------------------------------------------------
# Dominancia diagonal y reordenación
# ---------------------------------------------------------------------------

def analizar_dominancia(A: Any) -> tuple[list[dict[str, Any]], bool]:
    matriz = np.asarray(A, dtype=float)
    filas = []
    for i, fila in enumerate(matriz):
        diagonal = abs(float(fila[i]))
        resto = float(np.sum(np.abs(fila)) - diagonal)
        filas.append(
            {
                "fila": i + 1,
                "diagonal": diagonal,
                "suma_resto": resto,
                "estricta": diagonal > resto,
            }
        )
    return filas, all(f["estricta"] for f in filas)


def _puntaje_orden(A: np.ndarray, orden: tuple[int, ...]) -> tuple[int, int, float] | None:
    diag = np.array([abs(A[orden[i], i]) for i in range(len(orden))])
    escala = max(1.0, float(np.max(np.abs(A))))
    if np.any(diag <= _EPS_DIAGONAL * escala):
        return None
    resto = np.array([np.sum(np.abs(A[orden[i]])) - diag[i] for i in range(len(orden))])
    dominantes = int(np.sum(diag > resto))
    estricta = int(dominantes == len(orden))
    # Mayor margen relativo mínimo (|a_ii| / Σ|a_ij|) como desempate.
    margen = float(np.min(diag / (diag + resto)))
    return estricta, dominantes, margen


def buscar_reordenacion(A: Any, preferir_dominante: bool = True) -> list[int] | None:
    """Busca un orden de filas con diagonal no nula.

    Devuelve ``orden`` tal que la nueva fila i es la ecuación original
    ``orden[i]``. Con ``preferir_dominante`` se elige, entre los órdenes
    válidos, el que maximiza la dominancia diagonal. Para n > 8 se usa una
    asignación voraz por columnas.
    """

    matriz = np.asarray(A, dtype=float)
    n = matriz.shape[0]
    identidad = tuple(range(n))
    if n <= _MAX_N_PERMUTACIONES:
        mejor, mejor_puntaje = None, None
        for orden in permutations(range(n)):
            puntaje = _puntaje_orden(matriz, orden)
            if puntaje is None:
                continue
            if not preferir_dominante:
                # El primer orden válido más cercano al original.
                return list(orden) if orden != identidad else list(identidad)
            # En empate se conserva el orden encontrado primero (más cercano al original).
            if mejor_puntaje is None or puntaje > mejor_puntaje:
                mejor, mejor_puntaje = orden, puntaje
        return None if mejor is None else list(mejor)

    disponibles = set(range(n))
    orden = []
    for columna in range(n):
        candidato = max(disponibles, key=lambda f: abs(matriz[f, columna]), default=None)
        if candidato is None or abs(matriz[candidato, columna]) <= _EPS_DIAGONAL:
            return None
        orden.append(candidato)
        disponibles.remove(candidato)
    return orden


# ---------------------------------------------------------------------------
# Análisis matricial: A = L + D + U
# ---------------------------------------------------------------------------

def descomposicion_ldu(A: Any) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Devuelve (D, L, U) con A = L + D + U.

    L es estrictamente triangular inferior y U estrictamente triangular
    superior (convención aditiva, sin signo negativo).
    """

    matriz = np.asarray(A, dtype=float)
    D = np.diag(np.diag(matriz))
    L = np.tril(matriz, k=-1)
    U = np.triu(matriz, k=1)
    return D, L, U


def matriz_iteracion_gauss_seidel(A: Any, b: Any):
    """T = −(D+L)⁻¹U y c = (D+L)⁻¹b, de modo que X⁽ᵏ⁺¹⁾ = T X⁽ᵏ⁾ + c."""

    D, L, U = descomposicion_ldu(A)
    DL = D + L
    try:
        T = -np.linalg.solve(DL, U)
        c = np.linalg.solve(DL, np.asarray(b, dtype=float))
    except np.linalg.LinAlgError:
        return None, None, None, None
    if not (np.isfinite(T).all() and np.isfinite(c).all()):
        return None, None, None, None
    valores = np.linalg.eigvals(T)
    radio = float(np.max(np.abs(valores)))
    return T, c, valores, radio


# ---------------------------------------------------------------------------
# Algoritmo
# ---------------------------------------------------------------------------

def _norma_inf(v: np.ndarray) -> float:
    return float(np.linalg.norm(v, ord=np.inf))


def _iteracion(A: np.ndarray, b: np.ndarray, anterior: np.ndarray, k: int, criterio: str) -> IteracionGS:
    n = len(b)
    actual = anterior.copy()
    pasos: list[PasoVariableGS] = []
    for i in range(n):
        terminos: list[TerminoGS] = []
        suma_nuevos = 0.0
        suma_anteriores = 0.0
        for j in range(n):
            if j == i:
                continue
            nuevo = j < i
            # Para j < i, actual[j] ya contiene x_j^(k+1): ésta es la diferencia con Jacobi.
            valor = float(actual[j]) if nuevo else float(anterior[j])
            termino = TerminoGS(j, float(A[i, j]), valor, nuevo)
            terminos.append(termino)
            if nuevo:
                suma_nuevos += termino.producto
            else:
                suma_anteriores += termino.producto
        numerador = float(b[i]) - suma_nuevos - suma_anteriores
        valor_i = numerador / float(A[i, i])
        actual[i] = valor_i
        error_abs = abs(valor_i - float(anterior[i]))
        error_rel = error_abs / abs(valor_i) if valor_i != 0 else None
        pasos.append(
            PasoVariableGS(
                i=i,
                b_i=float(b[i]),
                a_ii=float(A[i, i]),
                terminos=terminos,
                suma_nuevos=suma_nuevos,
                suma_anteriores=suma_anteriores,
                numerador=numerador,
                valor=valor_i,
                valor_anterior=float(anterior[i]),
                error_absoluto=error_abs,
                error_relativo=error_rel,
            )
        )

    cambio = actual - anterior
    norma_cambio = _norma_inf(cambio)
    norma_actual = _norma_inf(actual)
    error_relativo = norma_cambio / norma_actual if norma_actual > 0 else None
    residuo_vector = A @ actual - b
    residuo = _norma_inf(residuo_vector)
    if criterio == "absoluto":
        error = norma_cambio
    elif criterio == "relativo":
        error = error_relativo
    else:
        error = residuo
    return IteracionGS(
        k=k,
        x_anterior=anterior.copy(),
        x=actual.copy(),
        pasos=pasos,
        errores_absolutos=np.abs(cambio),
        errores_relativos=[p.error_relativo for p in pasos],
        norma_cambio=norma_cambio,
        error_relativo=error_relativo,
        residuo_vector=residuo_vector,
        residuo=residuo,
        error=error,
    )


def resolver_gauss_seidel_detallado(
    A: Any,
    b: Any,
    x0: Any | None = None,
    tolerancia: Any = 1e-3,
    max_iter: Any = 100,
    criterio: str = "absoluto",
    reordenar: str = "si_hay_ceros",
) -> ResultadoGaussSeidel:
    """Resuelve Ax=b con Gauss-Seidel y conserva todo el procedimiento.

    Parameters
    ----------
    criterio:
        ``"absoluto"`` (‖ΔX‖∞), ``"relativo"`` (‖ΔX‖∞/‖X‖∞) o ``"residuo"``
        (‖AX−b‖∞). El método se detiene cuando el criterio es ≤ tolerancia.
    reordenar:
        ``"si_hay_ceros"``, ``"dominante"`` o ``"nunca"``.
    """

    if reordenar not in REORDENACIONES:
        raise ErrorGaussSeidel(f"Opción de reordenación desconocida: {reordenar}.")
    A0, b0, x_inicial, tol, maximo = validar_entrada_gauss_seidel(
        A, b, x0, tolerancia, max_iter, criterio
    )
    n = len(b0)

    permutacion: list[int] | None = None
    ceros = diagonal_nula(A0)
    if reordenar == "dominante":
        _, ya_dominante = analizar_dominancia(A0)
        if ceros or not ya_dominante:
            permutacion = buscar_reordenacion(A0, preferir_dominante=True)
            if permutacion is None and ceros:
                raise ErrorGaussSeidel(_mensaje_diagonal(ceros, sin_solucion=True))
    elif ceros:
        if reordenar == "nunca":
            raise ErrorGaussSeidel(_mensaje_diagonal(ceros))
        permutacion = buscar_reordenacion(A0, preferir_dominante=True)
        if permutacion is None:
            raise ErrorGaussSeidel(_mensaje_diagonal(ceros, sin_solucion=True))

    if permutacion is not None and permutacion != list(range(n)):
        matriz = A0[permutacion].copy()
        vector = b0[permutacion].copy()
    else:
        permutacion = None
        matriz, vector = A0.copy(), b0.copy()

    D, L, U = descomposicion_ldu(matriz)
    T, c, valores, radio = matriz_iteracion_gauss_seidel(matriz, vector)
    dominancia, estricta = analizar_dominancia(matriz)

    historial: list[IteracionGS] = []
    anterior = x_inicial.copy()
    residuo_inicial = _norma_inf(matriz @ anterior - vector)
    convergio = False
    motivo = ""
    with np.errstate(over="ignore", invalid="ignore"):
        for k in range(1, maximo + 1):
            it = _iteracion(matriz, vector, anterior, k, criterio)
            historial.append(it)
            if not np.isfinite(it.x).all() or _norma_inf(it.x) > _LIMITE_DIVERGENCIA:
                motivo = (
                    f"Las aproximaciones crecieron sin control en la iteración {k}; "
                    "el método diverge para este sistema y este orden de ecuaciones."
                )
                break
            if it.error is not None and it.error <= tol:
                convergio = True
                motivo = (
                    f"El criterio de parada ({CRITERIOS_GAUSS_SEIDEL[criterio]}) "
                    f"alcanzó {it.error:.6e} ≤ {tol:g} en la iteración {k}."
                )
                break
            anterior = it.x
        else:
            motivo = (
                f"Se realizaron las {maximo} iteraciones permitidas sin que el criterio "
                f"de parada fuera menor o igual que {tol:g}."
            )

    ultima = historial[-1]
    return ResultadoGaussSeidel(
        metodo="Gauss-Seidel",
        A=matriz,
        b=vector,
        x0=x_inicial,
        x=ultima.x.copy(),
        tolerancia=tol,
        max_iter=maximo,
        criterio=criterio,
        iteraciones=len(historial),
        convergio=convergio,
        error=ultima.error,
        motivo=motivo,
        historial_detallado=historial,
        residuo_inicial=residuo_inicial,
        A_original=A0,
        b_original=b0,
        permutacion=permutacion,
        D=D,
        L=L,
        U=U,
        matriz_iteracion=T,
        vector_constante=c,
        valores_propios=valores,
        radio_espectral=radio,
        dominancia=dominancia,
        estrictamente_dominante=estricta,
    )


def _mensaje_diagonal(ceros: list[int], sin_solucion: bool = False) -> str:
    posiciones = ", ".join(f"a{i + 1}{i + 1}" for i in ceros)
    base = (
        f"Gauss-Seidel divide entre los elementos diagonales y {posiciones} "
        f"{'es' if len(ceros) == 1 else 'son'} cero."
    )
    if sin_solucion:
        return base + " No existe un reordenamiento de las ecuaciones que deje toda la diagonal distinta de cero."
    return base + " Active la reordenación de ecuaciones o intercambie filas manualmente."


__all__ = [
    "CRITERIOS_GAUSS_SEIDEL",
    "REORDENACIONES",
    "ErrorGaussSeidel",
    "IteracionGS",
    "PasoVariableGS",
    "ResultadoGaussSeidel",
    "TerminoGS",
    "analizar_dominancia",
    "buscar_reordenacion",
    "descomposicion_ldu",
    "diagonal_nula",
    "matriz_iteracion_gauss_seidel",
    "resolver_gauss_seidel_detallado",
    "validar_entrada_gauss_seidel",
]
