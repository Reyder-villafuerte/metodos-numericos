from dataclasses import dataclass
from typing import Any


@dataclass
class ResultadoMetodo:
    raiz: float | complex
    error_final: float
    iteraciones: list[dict[str, Any]]
    convergio: bool | None
    motivo: str


def error_aproximado(nuevo: float, anterior: float) -> float:
    if nuevo == 0:
        return 0.0 if anterior == 0 else float("inf")
    return abs((nuevo - anterior) / nuevo) * 100


def validar_parametros(error_permitido: float, max_iteraciones: int) -> None:
    """Valida parámetros para criterio de error porcentual."""
    if error_permitido <= 0:
        raise ValueError("El error permitido debe ser mayor que cero.")
    if max_iteraciones <= 0:
        raise ValueError("El máximo de iteraciones debe ser un entero positivo.")


def validar_parametros_fijo(iteraciones_fijas: int, max_iteraciones: int) -> None:
    """Valida parámetros para criterio de iteraciones fijas."""
    if iteraciones_fijas <= 0:
        raise ValueError("El número de iteraciones debe ser un entero positivo.")
    if max_iteraciones is not None and max_iteraciones <= 0:
        raise ValueError("El máximo de iteraciones debe ser un entero positivo.")


def valor_real(valor: Any, nombre: str = "El valor") -> float:
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        raise ValueError(f"{nombre} no es numérico.") from None
    if numero != numero or numero in (float("inf"), float("-inf")):
        raise ValueError(f"{nombre} debe ser finito.")
    return numero
