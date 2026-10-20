"""Métodos directos para sistemas lineales de la Unidad 2.

Los algoritmos desarrollan explícitamente las operaciones principales. NumPy
se usa para almacenar matrices y para verificaciones independientes, no como
sustituto del procedimiento de cada método.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


TOLERANCIA_RELATIVA = 1e-12


class ErrorSistemaLineal(ValueError):
    """Error de validación o imposibilidad numérica del sistema."""


class MatrizSingularError(ErrorSistemaLineal):
    """La matriz no permite obtener una solución única."""


@dataclass
class ResultadoSistemaLineal:
    metodo: str
    A: np.ndarray
    b: np.ndarray
    x: np.ndarray
    determinante: float
    tolerancia: float
    comprobacion: np.ndarray
    residuo: np.ndarray
    norma_residuo: float
    pasos: list[dict[str, Any]] = field(default_factory=list)
    inversa: np.ndarray | None = None
    columnas_inversa: list[dict[str, Any]] = field(default_factory=list)
    matrices_cramer: list[np.ndarray] = field(default_factory=list)
    determinantes_cramer: list[float] = field(default_factory=list)
    P: np.ndarray | None = None
    L: np.ndarray | None = None
    U: np.ndarray | None = None
    y: np.ndarray | None = None
    pasos_progresiva: list[dict[str, Any]] = field(default_factory=list)
    pasos_regresiva: list[dict[str, Any]] = field(default_factory=list)
    norma_factorizacion: float | None = None
    hubo_pivoteo: bool = False


def validar_sistema(A: Any, b: Any) -> tuple[np.ndarray, np.ndarray]:
    """Convierte y valida un sistema cuadrado finito ``Ax=b``."""

    try:
        matriz = np.asarray(A, dtype=float)
        vector = np.asarray(b, dtype=float).reshape(-1)
    except (TypeError, ValueError) as exc:
        raise ErrorSistemaLineal("Todos los coeficientes de A y b deben ser numéricos.") from exc

    if matriz.ndim != 2:
        raise ErrorSistemaLineal("A debe ser una matriz bidimensional.")
    filas, columnas = matriz.shape
    if filas != columnas:
        raise ErrorSistemaLineal("A debe ser cuadrada: el número de filas y columnas debe coincidir.")
    if filas < 2:
        raise ErrorSistemaLineal("El sistema debe tener al menos dos incógnitas.")
    if vector.shape != (filas,):
        raise ErrorSistemaLineal(f"b debe contener exactamente {filas} términos independientes.")
    if not np.isfinite(matriz).all() or not np.isfinite(vector).all():
        raise ErrorSistemaLineal("A y b solo pueden contener valores numéricos finitos.")
    return matriz.copy(), vector.copy()


def calcular_tolerancia(A: np.ndarray, tolerancia: float | None = None) -> float:
    """Tolerancia escalada para decidir si un pivote es numéricamente nulo."""

    escala = max(1.0, float(np.linalg.norm(A, ord=np.inf)))
    if tolerancia is None:
        return TOLERANCIA_RELATIVA * escala
    try:
        valor = float(tolerancia)
    except (TypeError, ValueError) as exc:
        raise ErrorSistemaLineal("La tolerancia debe ser numérica.") from exc
    if not np.isfinite(valor) or valor <= 0:
        raise ErrorSistemaLineal("La tolerancia debe ser positiva y finita.")
    return valor


def _mensaje_singularidad(A: np.ndarray, b: np.ndarray, tolerancia: float) -> str:
    rango_a = int(np.linalg.matrix_rank(A, tol=tolerancia))
    rango_ampliada = int(np.linalg.matrix_rank(np.column_stack((A, b)), tol=tolerancia))
    if rango_a < rango_ampliada:
        return "El sistema es incompatible: no tiene solución."
    return "La matriz es singular y el sistema no tiene una solución única."


def determinante_eliminacion(
    A: Any, tolerancia: float | None = None
) -> tuple[float, list[dict[str, Any]]]:
    """Calcula el determinante en O(n³) mediante eliminación con pivoteo."""

    matriz = np.asarray(A, dtype=float)
    if matriz.ndim != 2 or matriz.shape[0] != matriz.shape[1]:
        raise ErrorSistemaLineal("El determinante requiere una matriz cuadrada.")
    if not np.isfinite(matriz).all():
        raise ErrorSistemaLineal("La matriz debe contener valores finitos.")

    trabajo = matriz.copy()
    n = trabajo.shape[0]
    tol = calcular_tolerancia(trabajo, tolerancia)
    signo = 1.0
    pasos: list[dict[str, Any]] = []

    for k in range(n):
        fila_pivote = k + int(np.argmax(np.abs(trabajo[k:, k])))
        pivote = float(trabajo[fila_pivote, k])
        paso: dict[str, Any] = {
            "etapa": k + 1,
            "columna": k + 1,
            "fila_pivote": fila_pivote + 1,
            "pivote": pivote,
            "intercambio": None,
            "multiplicadores": [],
        }
        if abs(pivote) <= tol:
            paso["pivote_nulo"] = True
            pasos.append(paso)
            return 0.0, pasos
        if fila_pivote != k:
            trabajo[[k, fila_pivote], :] = trabajo[[fila_pivote, k], :]
            signo *= -1.0
            paso["intercambio"] = (k + 1, fila_pivote + 1)
        for i in range(k + 1, n):
            multiplicador = float(trabajo[i, k] / trabajo[k, k])
            trabajo[i, k:] -= multiplicador * trabajo[k, k:]
            trabajo[i, k] = 0.0
            paso["multiplicadores"].append((i + 1, multiplicador))
        paso["matriz_triangular"] = trabajo.copy()
        pasos.append(paso)

    return float(signo * np.prod(np.diag(trabajo))), pasos


def factorizar_doolittle(
    A: Any, tolerancia: float | None = None
) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[dict[str, Any]], float]:
    """Obtiene ``PA=LU`` con diagonal unitaria en L y pivoteo parcial."""

    matriz = np.asarray(A, dtype=float)
    if matriz.ndim != 2 or matriz.shape[0] != matriz.shape[1]:
        raise ErrorSistemaLineal("Doolittle requiere una matriz cuadrada.")
    if not np.isfinite(matriz).all():
        raise ErrorSistemaLineal("La matriz debe contener valores finitos.")

    n = matriz.shape[0]
    tol = calcular_tolerancia(matriz, tolerancia)
    U = matriz.copy()
    L = np.eye(n, dtype=float)
    P = np.eye(n, dtype=float)
    signo = 1.0
    pasos: list[dict[str, Any]] = []

    for k in range(n):
        fila_pivote = k + int(np.argmax(np.abs(U[k:, k])))
        pivote_candidato = float(U[fila_pivote, k])
        paso: dict[str, Any] = {
            "etapa": k + 1,
            "fila_pivote": fila_pivote + 1,
            "pivote": pivote_candidato,
            "intercambio": None,
            "entradas_L": [],
            "entradas_U": [(k + 1, j + 1, float(U[k, j])) for j in range(k, n)],
            "calculos_L": [],
            "operaciones_fila": [],
        }
        if abs(pivote_candidato) <= tol:
            raise MatrizSingularError("Se encontró un pivote nulo o demasiado pequeño durante Doolittle.")
        if fila_pivote != k:
            U[[k, fila_pivote], :] = U[[fila_pivote, k], :]
            P[[k, fila_pivote], :] = P[[fila_pivote, k], :]
            if k:
                L[[k, fila_pivote], :k] = L[[fila_pivote, k], :k]
            signo *= -1.0
            paso["intercambio"] = (k + 1, fila_pivote + 1)
            paso["pivote"] = float(U[k, k])
            paso["entradas_U"] = [(k + 1, j + 1, float(U[k, j])) for j in range(k, n)]

        for i in range(k + 1, n):
            numerador = float(U[i, k])
            pivote = float(U[k, k])
            fila_antes = U[i, k:].copy()
            multiplicador = float(numerador / pivote)
            L[i, k] = multiplicador
            U[i, k:] -= multiplicador * U[k, k:]
            U[i, k] = 0.0
            paso["entradas_L"].append((i + 1, k + 1, multiplicador))
            paso["calculos_L"].append(
                (i + 1, k + 1, numerador, pivote, multiplicador)
            )
            paso["operaciones_fila"].append(
                {
                    "fila": i + 1,
                    "fila_pivote": k + 1,
                    "multiplicador": multiplicador,
                    "antes": fila_antes,
                    "despues": U[i, k:].copy(),
                }
            )
        paso["L"] = L.copy()
        paso["U"] = U.copy()
        pasos.append(paso)

    determinante = float(signo * np.prod(np.diag(U)))
    return P, L, U, pasos, determinante


def factorizar_crout(
    A: Any, tolerancia: float | None = None
) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[dict[str, Any]], float]:
    """Obtiene ``PA=LU`` con diagonal unitaria en U y pivoteo parcial."""

    matriz = np.asarray(A, dtype=float)
    if matriz.ndim != 2 or matriz.shape[0] != matriz.shape[1]:
        raise ErrorSistemaLineal("Crout requiere una matriz cuadrada.")
    if not np.isfinite(matriz).all():
        raise ErrorSistemaLineal("La matriz debe contener valores finitos.")

    n = matriz.shape[0]
    tol = calcular_tolerancia(matriz, tolerancia)
    trabajo = matriz.copy()
    L = np.zeros((n, n), dtype=float)
    U = np.eye(n, dtype=float)
    P = np.eye(n, dtype=float)
    signo = 1.0
    pasos: list[dict[str, Any]] = []

    for k in range(n):
        candidatos = np.array(
            [trabajo[i, k] - np.dot(L[i, :k], U[:k, k]) for i in range(k, n)],
            dtype=float,
        )
        fila_pivote = k + int(np.argmax(np.abs(candidatos)))
        pivote_candidato = float(candidatos[fila_pivote - k])
        paso: dict[str, Any] = {
            "etapa": k + 1,
            "fila_pivote": fila_pivote + 1,
            "pivote": pivote_candidato,
            "intercambio": None,
            "entradas_L": [],
            "entradas_U": [],
            "calculos_L": [],
            "calculos_U": [],
        }
        if abs(pivote_candidato) <= tol:
            raise MatrizSingularError("Se encontró un pivote nulo o demasiado pequeño durante Crout.")
        if fila_pivote != k:
            trabajo[[k, fila_pivote], :] = trabajo[[fila_pivote, k], :]
            P[[k, fila_pivote], :] = P[[fila_pivote, k], :]
            if k:
                L[[k, fila_pivote], :k] = L[[fila_pivote, k], :k]
            signo *= -1.0
            paso["intercambio"] = (k + 1, fila_pivote + 1)

        for i in range(k, n):
            suma = float(np.dot(L[i, :k], U[:k, k]))
            elemento = float(trabajo[i, k])
            L[i, k] = elemento - suma
            paso["entradas_L"].append((i + 1, k + 1, float(L[i, k])))
            paso["calculos_L"].append(
                (i + 1, k + 1, elemento, suma, float(L[i, k]))
            )
        if abs(L[k, k]) <= tol:
            raise MatrizSingularError("Se encontró un pivote nulo o demasiado pequeño durante Crout.")
        for j in range(k + 1, n):
            suma = float(np.dot(L[k, :k], U[:k, j]))
            elemento = float(trabajo[k, j])
            U[k, j] = (elemento - suma) / L[k, k]
            paso["entradas_U"].append((k + 1, j + 1, float(U[k, j])))
            paso["calculos_U"].append(
                (k + 1, j + 1, elemento, suma, float(L[k, k]), float(U[k, j]))
            )
        paso["L"] = L.copy()
        paso["U"] = U.copy()
        pasos.append(paso)

    determinante = float(signo * np.prod(np.diag(L)))
    return P, L, U, pasos, determinante


def sustitucion_progresiva(
    L: Any, b: Any, tolerancia: float
) -> tuple[np.ndarray, list[dict[str, Any]]]:
    matriz = np.asarray(L, dtype=float)
    vector = np.asarray(b, dtype=float).reshape(-1)
    n = matriz.shape[0]
    y = np.zeros(n, dtype=float)
    pasos: list[dict[str, Any]] = []
    for i in range(n):
        suma = float(np.dot(matriz[i, :i], y[:i]))
        pivote = float(matriz[i, i])
        if abs(pivote) <= tolerancia:
            raise MatrizSingularError("La sustitución progresiva encontró un pivote nulo.")
        y[i] = (vector[i] - suma) / pivote
        pasos.append({"indice": i + 1, "termino": float(vector[i]), "suma": suma, "pivote": pivote, "valor": float(y[i])})
    return y, pasos


def sustitucion_regresiva(
    U: Any, y: Any, tolerancia: float
) -> tuple[np.ndarray, list[dict[str, Any]]]:
    matriz = np.asarray(U, dtype=float)
    vector = np.asarray(y, dtype=float).reshape(-1)
    n = matriz.shape[0]
    x = np.zeros(n, dtype=float)
    pasos: list[dict[str, Any]] = []
    for i in range(n - 1, -1, -1):
        suma = float(np.dot(matriz[i, i + 1 :], x[i + 1 :]))
        pivote = float(matriz[i, i])
        if abs(pivote) <= tolerancia:
            raise MatrizSingularError("La sustitución regresiva encontró un pivote nulo.")
        x[i] = (vector[i] - suma) / pivote
        pasos.append({"indice": i + 1, "termino": float(vector[i]), "suma": suma, "pivote": pivote, "valor": float(x[i])})
    return x, pasos


def _resultado_base(
    metodo: str,
    A: np.ndarray,
    b: np.ndarray,
    x: np.ndarray,
    determinante: float,
    tolerancia: float,
    **kwargs: Any,
) -> ResultadoSistemaLineal:
    comprobacion = A @ x
    residuo = comprobacion - b
    return ResultadoSistemaLineal(
        metodo=metodo,
        A=A,
        b=b,
        x=x,
        determinante=float(determinante),
        tolerancia=tolerancia,
        comprobacion=comprobacion,
        residuo=residuo,
        norma_residuo=float(np.linalg.norm(residuo, ord=np.inf)),
        **kwargs,
    )


def resolver_matriz_inversa(
    A: Any, b: Any, tolerancia: float | None = None
) -> ResultadoSistemaLineal:
    matriz, vector = validar_sistema(A, b)
    tol = calcular_tolerancia(matriz, tolerancia)
    try:
        P, L, U, pasos_lu, determinante = factorizar_doolittle(matriz, tol)
    except MatrizSingularError as exc:
        raise MatrizSingularError(_mensaje_singularidad(matriz, vector, tol)) from exc

    n = matriz.shape[0]
    inversa = np.zeros_like(matriz)
    columnas: list[dict[str, Any]] = []
    for j in range(n):
        e = np.zeros(n, dtype=float)
        e[j] = 1.0
        rhs = P @ e
        y, pasos_y = sustitucion_progresiva(L, rhs, tol)
        z, pasos_z = sustitucion_regresiva(U, y, tol)
        inversa[:, j] = z
        columnas.append({"columna": j + 1, "e": e, "Pb": rhs, "y": y, "z": z, "pasos_y": pasos_y, "pasos_z": pasos_z})

    x = inversa @ vector
    return _resultado_base(
        "Matriz inversa",
        matriz,
        vector,
        x,
        determinante,
        tol,
        pasos=pasos_lu,
        inversa=inversa,
        columnas_inversa=columnas,
        P=P,
        L=L,
        U=U,
        norma_factorizacion=float(np.linalg.norm(P @ matriz - L @ U, ord=np.inf)),
        hubo_pivoteo=not np.allclose(P, np.eye(n)),
    )


def resolver_cramer(
    A: Any, b: Any, tolerancia: float | None = None
) -> ResultadoSistemaLineal:
    matriz, vector = validar_sistema(A, b)
    tol = calcular_tolerancia(matriz, tolerancia)
    determinante, pasos = determinante_eliminacion(matriz, tol)
    if determinante == 0.0:
        raise MatrizSingularError(_mensaje_singularidad(matriz, vector, tol))

    matrices: list[np.ndarray] = []
    determinantes: list[float] = []
    x = np.zeros(matriz.shape[0], dtype=float)
    for i in range(matriz.shape[0]):
        Ai = matriz.copy()
        Ai[:, i] = vector
        det_ai, pasos_ai = determinante_eliminacion(Ai, tol)
        matrices.append(Ai)
        determinantes.append(det_ai)
        x[i] = det_ai / determinante
        pasos.append({"cramer": i + 1, "determinante": det_ai, "pasos_determinante": pasos_ai})

    return _resultado_base(
        "Regla de Cramer",
        matriz,
        vector,
        x,
        determinante,
        tol,
        pasos=pasos,
        matrices_cramer=matrices,
        determinantes_cramer=determinantes,
    )


def _resolver_lu(
    metodo: str, A: Any, b: Any, tolerancia: float | None = None
) -> ResultadoSistemaLineal:
    matriz, vector = validar_sistema(A, b)
    tol = calcular_tolerancia(matriz, tolerancia)
    factorizador = factorizar_doolittle if metodo == "Doolittle" else factorizar_crout
    try:
        P, L, U, pasos, determinante = factorizador(matriz, tol)
    except MatrizSingularError as exc:
        raise MatrizSingularError(_mensaje_singularidad(matriz, vector, tol)) from exc
    rhs = P @ vector
    y, pasos_y = sustitucion_progresiva(L, rhs, tol)
    x, pasos_x = sustitucion_regresiva(U, y, tol)
    n = matriz.shape[0]
    return _resultado_base(
        metodo,
        matriz,
        vector,
        x,
        determinante,
        tol,
        pasos=pasos,
        P=P,
        L=L,
        U=U,
        y=y,
        pasos_progresiva=pasos_y,
        pasos_regresiva=pasos_x,
        norma_factorizacion=float(np.linalg.norm(P @ matriz - L @ U, ord=np.inf)),
        hubo_pivoteo=not np.allclose(P, np.eye(n)),
    )


def resolver_doolittle(A: Any, b: Any, tolerancia: float | None = None) -> ResultadoSistemaLineal:
    return _resolver_lu("Doolittle", A, b, tolerancia)


def resolver_crout(A: Any, b: Any, tolerancia: float | None = None) -> ResultadoSistemaLineal:
    return _resolver_lu("Crout", A, b, tolerancia)


RESOLUTORES = {
    "Matriz inversa": resolver_matriz_inversa,
    "Regla de Cramer": resolver_cramer,
    "Doolittle": resolver_doolittle,
    "Crout": resolver_crout,
}


def resolver_sistema(
    metodo: str, A: Any, b: Any, tolerancia: float | None = None
) -> ResultadoSistemaLineal:
    try:
        resolver = RESOLUTORES[metodo]
    except KeyError as exc:
        raise ErrorSistemaLineal(f"El método {metodo!r} no está implementado en la Unidad 2.") from exc
    return resolver(A, b, tolerancia)

