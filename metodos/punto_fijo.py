from . import ResultadoMetodo, error_aproximado, validar_parametros, validar_parametros_fijo, valor_real


def punto_fijo(funcion, despeje, x0: float, error_permitido: float = None, max_iteraciones: int = 100,
               criterio: str = "error", iteraciones_fijas: int = None) -> ResultadoMetodo:
    """
    Método de punto fijo.
    
    Criterios de parada:
    - "error": detener cuando error < error_permitido o se alcance max_iteraciones
    - "fijo": ejecutar exactamente iteraciones_fijas actualizaciones
    """
    if criterio == "error":
        validar_parametros(error_permitido, max_iteraciones)
        max_iter = max_iteraciones
    else:
        validar_parametros_fijo(iteraciones_fijas, max_iteraciones)
        max_iter = iteraciones_fijas
    
    x = valor_real(x0, "El valor inicial")
    filas = []
    for indice in range(1, max_iter + 1):
        nuevo = valor_real(despeje(x), "g(x)")
        error = error_aproximado(nuevo, x)
        filas.append({"i": indice, "xi": x, "g(xi)": nuevo, "Ea (%)": error})
        
        if criterio == "error":
            if error < error_permitido:
                return ResultadoMetodo(nuevo, error, filas, True, "Se alcanzó el error permitido.")
        
        x = nuevo
    
    if criterio == "error":
        return ResultadoMetodo(x, filas[-1]["Ea (%)"], filas, False, "Se alcanzó el máximo de iteraciones.")
    else:
        return ResultadoMetodo(x, filas[-1]["Ea (%)"], filas, True, f"Se completaron las {iteraciones_fijas} iteraciones solicitadas.")
