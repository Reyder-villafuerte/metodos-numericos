from . import ResultadoMetodo, error_aproximado, validar_parametros, valor_real


def secante(funcion, x0: float, x1: float, error_permitido: float = 0.01, max_iteraciones: int = 100) -> ResultadoMetodo:
    validar_parametros(error_permitido, max_iteraciones)
    anterior, actual = valor_real(x0, "x0"), valor_real(x1, "x1")
    filas = []
    for indice in range(1, max_iteraciones + 1):
        f_anterior, f_actual = valor_real(funcion(anterior), "f(xi-1)"), valor_real(funcion(actual), "f(xi)")
        denominador = f_actual - f_anterior
        if abs(denominador) < 1e-14:
            raise ValueError("El denominador de la secante es cero o demasiado cercano a cero.")
        nuevo = valor_real(actual - f_actual * (actual - anterior) / denominador, "xi+1")
        error = error_aproximado(nuevo, actual)
        filas.append({"i": indice, "xi-1": anterior, "xi": actual, "f(xi-1)": f_anterior, "f(xi)": f_actual, "xi+1": nuevo, "Ea (%)": error})
        if f_actual == 0 or error < error_permitido:
            return ResultadoMetodo(nuevo, error, filas, True, "Se alcanzó el error permitido.")
        anterior, actual = actual, nuevo
    return ResultadoMetodo(actual, filas[-1]["Ea (%)"], filas, False, "Se alcanzó el máximo de iteraciones.")
