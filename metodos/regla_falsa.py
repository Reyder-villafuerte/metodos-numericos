from . import ResultadoMetodo, error_aproximado, validar_parametros, valor_real


def regla_falsa(funcion, a: float, b: float, error_permitido: float = 0.01, max_iteraciones: int = 100) -> ResultadoMetodo:
    validar_parametros(error_permitido, max_iteraciones)
    a, b = valor_real(a, "El extremo inferior"), valor_real(b, "El extremo superior")
    if a >= b:
        raise ValueError("El extremo inferior debe ser menor que el superior.")
    fa, fb = valor_real(funcion(a), "f(a)"), valor_real(funcion(b), "f(b)")
    if fa == 0:
        return ResultadoMetodo(a, 0.0, [], True, "El extremo inferior es una raíz.")
    if fb == 0:
        return ResultadoMetodo(b, 0.0, [], True, "El extremo superior es una raíz.")
    if fa * fb > 0:
        raise ValueError("El intervalo no presenta cambio de signo: f(a) y f(b) deben tener signos opuestos.")
    filas, anterior = [], None
    for indice in range(1, max_iteraciones + 1):
        denominador = fb - fa
        if denominador == 0:
            raise ValueError("No se puede continuar: el denominador de la regla falsa es cero.")
        m = b - fb * (b - a) / denominador
        fm = valor_real(funcion(m), "f(m)")
        error = float("inf") if anterior is None else error_aproximado(m, anterior)
        filas.append({"i": indice, "ai": a, "bi": b, "mi": m, "f(ai)": fa, "f(mi)": fm, "f(bi)": fb, "Ea (%)": error})
        if fm == 0 or error < error_permitido:
            return ResultadoMetodo(m, error, filas, True, "Se alcanzó el error permitido.")
        if fa * fm < 0:
            b, fb = m, fm
        else:
            a, fa = m, fm
        anterior = m
    return ResultadoMetodo(filas[-1]["mi"], filas[-1]["Ea (%)"], filas, False, "Se alcanzó el máximo de iteraciones.")
