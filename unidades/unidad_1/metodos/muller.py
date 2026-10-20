import cmath
import math

from . import ResultadoMetodo, validar_parametros, validar_parametros_fijo


TOLERANCIA = 1e-14


def _valor_complejo(valor, nombre):
    """Convierte y valida un valor numérico real o complejo."""
    try:
        numero = complex(valor)
    except (TypeError, ValueError):
        raise ValueError(f"{nombre} no es numérico.") from None
    if not (math.isfinite(numero.real) and math.isfinite(numero.imag)):
        raise ValueError(f"{nombre} produjo un valor no finito.")
    return numero


def _evaluar(funcion, valor, nombre):
    try:
        return _valor_complejo(funcion(valor), nombre)
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(f"La función no puede evaluarse en {nombre}.") from exc


def _error_aproximado(nuevo, anterior):
    diferencia = abs(nuevo - anterior)
    if abs(nuevo) < TOLERANCIA:
        return diferencia
    return diferencia / abs(nuevo) * 100


def _normalizar_salida(valor):
    """Devuelve float cuando la parte imaginaria es ruido numérico."""
    if isinstance(valor, complex) and abs(valor.imag) < TOLERANCIA:
        return float(valor.real)
    return valor


def muller(funcion, x0, x1, x2, error_permitido=None, max_iteraciones=100,
           criterio="error", iteraciones_fijas=None) -> ResultadoMetodo:
    """Aproxima una raíz real o compleja mediante el método de Müller."""
    if criterio == "error":
        validar_parametros(error_permitido, max_iteraciones)
        max_iter = max_iteraciones
    elif criterio == "fijo":
        validar_parametros_fijo(iteraciones_fijas, max_iteraciones)
        max_iter = iteraciones_fijas
    else:
        raise ValueError("El criterio de detención no es válido.")

    x0 = _valor_complejo(x0, "x0")
    x1 = _valor_complejo(x1, "x1")
    x2 = _valor_complejo(x2, "x2")
    if abs(x0 - x1) < TOLERANCIA or abs(x0 - x2) < TOLERANCIA or abs(x1 - x2) < TOLERANCIA:
        raise ValueError("Los tres valores iniciales x0, x1 y x2 deben ser distintos.")

    filas = []
    for indice in range(1, max_iter + 1):
        f0 = _evaluar(funcion, x0, "x0")
        f1 = _evaluar(funcion, x1, "x1")
        f2 = _evaluar(funcion, x2, "x2")
        if abs(f2) < TOLERANCIA:
            return ResultadoMetodo(_normalizar_salida(x2), 0.0, filas, True, "Se encontró una raíz exacta.")

        denominador_coeficientes = (x0 - x2) * (x1 - x2) * (x0 - x1)
        if abs(denominador_coeficientes) < TOLERANCIA:
            raise ValueError("El denominador para calcular a y b es cero o demasiado cercano a cero.")

        a = ((x1 - x2) * (f0 - f2) - (x0 - x2) * (f1 - f2)) / denominador_coeficientes
        b = (((x0 - x2) ** 2) * (f1 - f2) - ((x1 - x2) ** 2) * (f0 - f2)) / denominador_coeficientes
        c = f2
        discriminante = b ** 2 - 4 * a * c
        raiz_discriminante = cmath.sqrt(discriminante)
        denominador1 = b + raiz_discriminante
        denominador2 = b - raiz_discriminante
        denominador = denominador1 if abs(denominador1) >= abs(denominador2) else denominador2
        if abs(denominador) < TOLERANCIA:
            raise ValueError("Los dos posibles denominadores de la fórmula de Müller son cero.")

        x3 = _valor_complejo(x2 - (2 * c / denominador), "La nueva aproximación")
        error = _error_aproximado(x3, x2)
        filas.append({
            "i": indice, "x0": _normalizar_salida(x0), "x1": _normalizar_salida(x1),
            "x2": _normalizar_salida(x2), "f(x0)": _normalizar_salida(f0),
            "f(x1)": _normalizar_salida(f1), "f(x2)": _normalizar_salida(f2),
            "a": _normalizar_salida(a), "b": _normalizar_salida(b), "c": _normalizar_salida(c),
            "Discriminante": _normalizar_salida(discriminante),
            "x3": _normalizar_salida(x3), "Ea (%)": error,
        })

        if criterio == "error" and error < error_permitido:
            return ResultadoMetodo(_normalizar_salida(x3), error, filas, True, "Se alcanzó el error permitido.")
        x0, x1, x2 = x1, x2, x3

    raiz = _normalizar_salida(x2)
    error_final = filas[-1]["Ea (%)"]
    if criterio == "error":
        return ResultadoMetodo(raiz, error_final, filas, False, "No se alcanzó el criterio dentro del máximo de iteraciones.")
    return ResultadoMetodo(raiz, error_final, filas, None, f"Se completaron las {iteraciones_fijas} iteraciones solicitadas.")
