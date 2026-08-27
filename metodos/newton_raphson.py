from . import ResultadoMetodo, error_aproximado, validar_parametros, valor_real


def newton_raphson(funcion, derivada, x0: float, error_permitido: float = 0.01, max_iteraciones: int = 100) -> ResultadoMetodo:
    validar_parametros(error_permitido, max_iteraciones)
    x = valor_real(x0, "El valor inicial")
    filas = []
    for indice in range(1, max_iteraciones + 1):
        fx, dfx = valor_real(funcion(x), "f(xi)"), valor_real(derivada(x), "f'(xi)")
        if abs(dfx) < 1e-14:
            raise ValueError("La derivada es cero o demasiado cercana a cero; no se puede dividir.")
        nuevo = valor_real(x - fx / dfx, "xi+1")
        error = error_aproximado(nuevo, x)
        filas.append({"i": indice, "xi": x, "f(xi)": fx, "f'(xi)": dfx, "xi+1": nuevo, "Ea (%)": error})
        if fx == 0 or error < error_permitido:
            return ResultadoMetodo(nuevo, error, filas, True, "Se alcanzó el error permitido.")
        x = nuevo
    return ResultadoMetodo(x, filas[-1]["Ea (%)"], filas, False, "Se alcanzó el máximo de iteraciones.")
