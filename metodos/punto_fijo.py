from . import ResultadoMetodo, error_aproximado, validar_parametros, valor_real


def punto_fijo(funcion, despeje, x0: float, error_permitido: float = 0.01, max_iteraciones: int = 100) -> ResultadoMetodo:
    validar_parametros(error_permitido, max_iteraciones)
    x = valor_real(x0, "El valor inicial")
    filas = []
    for indice in range(1, max_iteraciones + 1):
        nuevo = valor_real(despeje(x), "g(x)")
        error = error_aproximado(nuevo, x)
        filas.append({"i": indice, "xi": x, "g(xi)": nuevo, "Ea (%)": error})
        if error < error_permitido:
            return ResultadoMetodo(nuevo, error, filas, True, "Se alcanzó el error permitido.")
        x = nuevo
    return ResultadoMetodo(x, filas[-1]["Ea (%)"], filas, False, "Se alcanzó el máximo de iteraciones.")
