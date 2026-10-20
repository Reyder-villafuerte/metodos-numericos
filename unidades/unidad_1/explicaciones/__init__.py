"""Explicaciones dinámicas paso a paso para todos los métodos numéricos.

La función principal :func:`generar_explicacion` actúa como dispatcher: recibe el
nombre del método y los datos reales de la ejecución (expresión, iteraciones,
resultado y parámetros) y delega en el generador correspondiente.

Todo el contenido se construye a partir de los datos reales; no hay resultados
precargados.
"""

from ._formato import (
    TOLERANCIA_COMPLEJA,
    _derivada_de,
    _desglose_polinomio,
    _es_complejo_significativo,
    _es_finito,
    _evaluar_expresion,
    _expresion_con_valor,
    _formatear,
    _formatear_error,
    _latex_funcion,
    _latex_num,
    _obtener_simbolo,
    _resta,
    _unir_con_signos,
    _valor_display,
)
from ._comunes import (
    _seccion_convergencia,
    _seccion_error,
    _seccion_formula_general,
    _seccion_objetivo,
    _seccion_presentacion_generica,
    _seccion_resultado_final,
    _seccion_sin_iteraciones,
    validar_estado_explicacion,
)
from ._newton import (
    _generar_newton_uniforme,
    _seccion_iteraciones,
    _seccion_presentacion,
    _seccion_recta_tangente,
    generar_explicacion_newton_raphson,
)
from ._intervalos import (
    generar_explicacion_biseccion,
    generar_explicacion_regla_falsa,
)
from ._punto_fijo import generar_explicacion_punto_fijo
from ._secante import generar_explicacion_secante
from ._muller import generar_explicacion_muller


GENERADORES = {
    "Bisección": generar_explicacion_biseccion,
    "Regla falsa": generar_explicacion_regla_falsa,
    "Punto fijo": generar_explicacion_punto_fijo,
    "Newton-Raphson": _generar_newton_uniforme,
    "Secante": generar_explicacion_secante,
    "Müller": generar_explicacion_muller,
}


def generar_explicacion(
    metodo,
    expresion,
    filas,
    resultado,
    parametros=None,
    funcion_texto=None,
    error_permitido=None,
    max_iteraciones=None,
    criterio="error",
    decimales=6,
):
    """Genera la explicación paso a paso del método indicado."""
    generador = GENERADORES.get(metodo)
    if generador is None:
        raise ValueError(f"No hay explicación disponible para el método {metodo!r}.")
    if resultado is None:
        raise ValueError("No hay resultado del método para explicar.")
    return generador(
        expresion,
        filas or [],
        resultado,
        parametros or {},
        funcion_texto,
        error_permitido,
        max_iteraciones,
        criterio,
        decimales,
    )


__all__ = [
    "GENERADORES",
    "TOLERANCIA_COMPLEJA",
    "_derivada_de",
    "_desglose_polinomio",
    "_es_complejo_significativo",
    "_es_finito",
    "_evaluar_expresion",
    "_expresion_con_valor",
    "_formatear",
    "_formatear_error",
    "_generar_newton_uniforme",
    "_latex_funcion",
    "_latex_num",
    "_obtener_simbolo",
    "_resta",
    "_seccion_convergencia",
    "_seccion_error",
    "_seccion_formula_general",
    "_seccion_iteraciones",
    "_seccion_objetivo",
    "_seccion_presentacion",
    "_seccion_presentacion_generica",
    "_seccion_recta_tangente",
    "_seccion_resultado_final",
    "_seccion_sin_iteraciones",
    "_unir_con_signos",
    "_valor_display",
    "generar_explicacion",
    "generar_explicacion_biseccion",
    "generar_explicacion_muller",
    "generar_explicacion_newton_raphson",
    "generar_explicacion_punto_fijo",
    "generar_explicacion_regla_falsa",
    "generar_explicacion_secante",
    "validar_estado_explicacion",
]
