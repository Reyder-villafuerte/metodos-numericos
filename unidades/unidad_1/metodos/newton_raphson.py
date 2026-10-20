from . import ResultadoMetodo, error_aproximado, validar_parametros, validar_parametros_fijo, valor_real


def newton_raphson(funcion, derivada, x0: float, error_permitido: float = None, max_iteraciones: int = 100,
                   criterio: str = "error", iteraciones_fijas: int = None) -> ResultadoMetodo:
    """
    Método de Newton-Raphson.
    
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
        fx, dfx = valor_real(funcion(x), "f(xi)"), valor_real(derivada(x), "f'(xi)")
        if abs(dfx) < 1e-14:
            raise ValueError("La derivada es cero o demasiado cercana a cero; no se puede dividir.")
        nuevo = valor_real(x - fx / dfx, "xi+1")
        error = error_aproximado(nuevo, x)
        filas.append({"i": indice, "xi": x, "f(xi)": fx, "f'(xi)": dfx, "xi+1": nuevo, "Ea (%)": error})
        
        if criterio == "error":
            if fx == 0:
                filas[-1]["Ea (%)"] = 0.0
                return ResultadoMetodo(nuevo, 0.0, filas, True, "Se encontró una raíz exacta.")
            if error < error_permitido:
                return ResultadoMetodo(nuevo, error, filas, True, "Se alcanzó el error permitido.")
        
        x = nuevo
    
    if criterio == "error":
        return ResultadoMetodo(x, filas[-1]["Ea (%)"], filas, False, "Se alcanzó el máximo de iteraciones.")
    else:
        return ResultadoMetodo(x, filas[-1]["Ea (%)"], filas, None, f"Se completaron las {iteraciones_fijas} iteraciones solicitadas.")
