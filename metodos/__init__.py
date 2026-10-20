"""Compatibilidad — re-exporta la implementación de Unidad 1.

Las implementaciones canónicas viven en ``unidades.unidad_1.metodos``.
Este paquete se conserva únicamente para no romper imports públicos existentes.
"""

from unidades.unidad_1.metodos import *  # noqa: F401,F403
from unidades.unidad_1.metodos import (
    ResultadoMetodo,
    error_aproximado,
    validar_parametros,
    validar_parametros_fijo,
    valor_real,
    biseccion,
    regla_falsa,
    punto_fijo,
    newton_raphson,
    secante,
    muller,
)

__all__ = [
    "ResultadoMetodo",
    "error_aproximado",
    "validar_parametros",
    "validar_parametros_fijo",
    "valor_real",
    "biseccion",
    "regla_falsa",
    "punto_fijo",
    "newton_raphson",
    "secante",
    "muller",
]
