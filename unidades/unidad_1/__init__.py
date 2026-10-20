"""Unidad 1 — Raíces de ecuaciones.

Reúne los seis métodos numéricos y sus explicaciones paso a paso.
"""

from .explicaciones import (
    generar_explicacion,
    generar_explicacion_biseccion,
    generar_explicacion_regla_falsa,
    generar_explicacion_punto_fijo,
    generar_explicacion_secante,
    generar_explicacion_muller,
    _generar_newton_uniforme,
    generar_explicacion_newton_raphson,
)
from .metodos import (
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
