from . import ResultadoMetodo, error_aproximado, validar_parametros, validar_parametros_fijo, valor_real


def secante(funcion, x0: float, x1: float, error_permitido: float = None, max_iteraciones: int = 100,
            criterio: str = "error", iteraciones_fijas: int = None) -> ResultadoMetodo:
    """
    Método de la secante.
    
    Criterios de parada:
    - "error": detener cuando error < error_permitido o se alcance max_iteraciones
    - "fijo": ejecutar exactamente iteraciones_fijas nuevas aproximaciones (después de x0 y x1)
    """
    if criterio == "error":
        validar_parametros(error_permitido, max_iteraciones)
        max_iter = max_iteraciones
    else:
        validar_parametros_fijo(iteraciones_fijas, max_iteraciones)
        max_iter = iteraciones_fijas
    
    anterior, actual = valor_real(x0, "x0"), valor_real(x1, "x1")
    f_anterior = valor_real(funcion(anterior), "f(x0)")
    if f_anterior == 0:
        return ResultadoMetodo(anterior, 0.0, [], True, "El primer valor inicial es una raíz.")

    f_actual = valor_real(funcion(actual), "f(x1)")
    if f_actual == 0:
        return ResultadoMetodo(actual, 0.0, [], True, "El segundo valor inicial es una raíz.")

    filas = []
    for indice in range(1, max_iter + 1):
        f_anterior, f_actual = valor_real(funcion(anterior), "f(xi-1)"), valor_real(funcion(actual), "f(xi)")
        denominador = f_actual - f_anterior
        if abs(denominador) < 1e-14:
            raise ValueError("El denominador de la secante es cero o demasiado cercano a cero.")
        nuevo = valor_real(actual - f_actual * (actual - anterior) / denominador, "xi+1")
        error = error_aproximado(nuevo, actual)
        filas.append({"i": indice, "xi-1": anterior, "xi": actual, "f(xi-1)": f_anterior, "f(xi)": f_actual, "xi+1": nuevo, "Ea (%)": error})
        
        if criterio == "error":
            if f_actual == 0 or error < error_permitido:
                return ResultadoMetodo(nuevo, error, filas, True, "Se alcanzó el error permitido.")
        
        anterior, actual = actual, nuevo
    
    if criterio == "error":
        return ResultadoMetodo(actual, filas[-1]["Ea (%)"], filas, False, "Se alcanzó el máximo de iteraciones.")
    else:
        return ResultadoMetodo(actual, filas[-1]["Ea (%)"], filas, None, f"Se completaron las {iteraciones_fijas} iteraciones solicitadas.")
