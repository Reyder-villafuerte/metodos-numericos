"""Explicación paso a paso del método de Newton-Raphson."""

import math

from ._comunes import (
    _seccion_convergencia,
    _seccion_error,
    _seccion_formula_general,
    _seccion_objetivo,
    _seccion_resultado_final,
    _seccion_sin_iteraciones,
)
from ._formato import (
    _derivada_de,
    _desglose_polinomio,
    _expresion_con_valor,
    _formatear,
    _latex_funcion,
    _resta,
    _valor_display,
)


def generar_explicacion_newton_raphson(
    expresion,
    derivada,
    filas,
    resultado,
    parametros,
    funcion_texto,
    error_permitido,
    max_iteraciones,
    criterio,
    decimales,
):
    secciones = []
    secciones.append(_seccion_presentacion(expresion, derivada, parametros, funcion_texto, error_permitido, max_iteraciones, criterio, decimales))
    secciones.append(_seccion_objetivo("Newton-Raphson"))
    secciones.append(_seccion_formula_general("Newton-Raphson"))
    if filas:
        secciones.append(_seccion_iteraciones(filas, expresion, derivada, decimales, criterio, error_permitido))
        secciones.append(_seccion_error(filas, error_permitido, criterio, decimales))
        secciones.append(_seccion_recta_tangente(filas, expresion, derivada, decimales))
        secciones.append(_seccion_convergencia(resultado, filas, error_permitido, criterio, decimales, "Newton-Raphson"))
    else:
        secciones.append(_seccion_sin_iteraciones("Newton-Raphson", expresion, resultado, parametros, decimales))
    secciones.append(_seccion_resultado_final(resultado, expresion, decimales, "Newton-Raphson", criterio, parametros, len(filas)))
    return "\n".join(secciones)


def _seccion_presentacion(expresion, derivada, parametros, funcion_texto, error_permitido, max_iteraciones, criterio, decimales):
    parametros = parametros or {}
    x0 = parametros.get("x0", "?")
    expr_latex = _latex_funcion(expresion)
    deriv_latex = _latex_funcion(derivada)

    bloques = []
    bloques.append("### 1. Presentación del ejercicio\n")
    bloques.append("**Función ingresada:**\n")
    bloques.append(f"$$f(x) = {expr_latex}$$\n")
    bloques.append("**Derivada calculada con SymPy:**\n")
    bloques.append(f"$$f'(x) = {deriv_latex}$$\n")
    bloques.append(f"- **Valor inicial** $x_0$ = {_formatear(x0, decimales)}")
    if criterio == "error":
        error_txt = _formatear(error_permitido, decimales) if error_permitido is not None else "N/A"
        bloques.append(f"- **Error permitido** = {error_txt} %")
        bloques.append(f"- **Máximo de iteraciones (seguridad)** = {max_iteraciones}")
    else:
        bloques.append(f"- **Iteraciones solicitadas** = {max_iteraciones}")
    bloques.append(f"- **Decimales para visualizar** = {decimales}")
    bloques.append("")
    return "\n".join(bloques)


def _seccion_iteraciones(filas, expresion, derivada, decimales, criterio="error", error_permitido=None):
    bloques = []
    bloques.append("### 4. Explicación de cada iteración\n")

    if not filas:
        bloques.append("No se realizaron iteraciones porque el método encontró una raíz en los datos iniciales.\n")
        return "\n".join(bloques)

    bloques.append("Cada paso del método se detalla a continuación. Puede desplegar cada iteración para ver los cálculos completos.\n")

    texto_expr = str(expresion)
    texto_derivada = str(derivada)
    expr_latex = _latex_funcion(expresion)
    deriv_latex = _latex_funcion(derivada)

    for i, fila in enumerate(filas):
        numero = fila["i"]
        xn = fila["xi"]
        fxn = fila["f(xi)"]
        dfxn = fila["f'(xi)"]
        xn1 = fila["xi+1"]
        ea = fila["Ea (%)"]

        ind = numero - 1
        ind1 = numero
        xn_txt = _valor_display(xn, decimales)
        fxn_txt = _valor_display(fxn, decimales)
        dfxn_txt = _valor_display(dfxn, decimales)
        xn1_txt = _valor_display(xn1, decimales)
        ea_txt = _valor_display(ea, decimales)

        bloques.append(f"<details><summary><b>Iteración {numero}</b></summary>\n")
        bloques.append(f"#### Iteración {numero}\n")

        bloques.append("**1. Valor actual:**\n")
        bloques.append(f"$$x_{{{ind}}} = {xn_txt}$$\n")
        if i == 0:
            bloques.append("Partimos del valor inicial $x_0$.\n")
        else:
            bloques.append("Utilizamos la aproximación obtenida en la iteración anterior.\n")
        bloques.append("Este es el valor que utilizaremos para calcular la siguiente aproximación.\n")

        bloques.append("**2. Evaluación completa de la función:**\n")
        bloques.append(f"$$f(x) = {expr_latex}$$\n")
        bloques.append(f"$$f(x_{{{ind}}}) = f({xn_txt})$$\n")
        fxn_sust = _expresion_con_valor(texto_expr, xn, decimales)
        bloques.append(f"$$f({xn_txt}) = {fxn_sust}$$\n")
        desglose = _desglose_polinomio(expresion, xn, decimales)
        if desglose is not None:
            terminos, valores, total = desglose
            bloques.append(f"$$f({xn_txt}) = {terminos} = {valores} = {total}$$\n")
        bloques.append(f"$$f({xn_txt}) = {fxn_txt}$$\n")

        bloques.append("**3. Evaluación completa de la derivada:**\n")
        bloques.append(f"$$f'(x) = {deriv_latex}$$\n")
        dfxn_sust = _expresion_con_valor(texto_derivada, xn, decimales)
        bloques.append(f"$$f'({xn_txt}) = {dfxn_sust}$$\n")
        desglose_deriv = _desglose_polinomio(derivada, xn, decimales)
        if desglose_deriv is not None:
            terminos, valores, total = desglose_deriv
            bloques.append(f"$$f'({xn_txt}) = {terminos} = {valores} = {total}$$\n")
        bloques.append(f"$$f'({xn_txt}) = {dfxn_txt}$$\n")
        bloques.append(f"**Variables del programa:** $fx_{{{ind}}} = {fxn_txt}$ y $dfx_{{{ind}}} = {dfxn_txt}$.\n")

        bloques.append("**4. Sustitución completa en Newton-Raphson:**\n")
        bloques.append(f"$$x_{{{ind1}}} = x_{{{ind}}} - \\frac{{f(x_{{{ind}}})}}{{f'(x_{{{ind}}})}}$$\n")
        bloques.append(
            f"**Valores disponibles:** $x_{{{ind}}} = {xn_txt}$, $f(x_{{{ind}}}) = {fxn_txt}$, "
            f"$f'(x_{{{ind}}}) = {dfxn_txt}$.\n"
        )
        if dfxn == 0 or abs(dfxn) < 1e-14:
            bloques.append("**¡Atención!** La derivada es cero o muy cercana a cero en este punto. Esto puede causar problemas numéricos.\n")
        else:
            cociente = fxn / dfxn
            cociente_txt = _valor_display(cociente, decimales)
            bloques.append(f"$$x_{{{ind1}}} = {xn_txt} - \\frac{{{fxn_txt}}}{{{dfxn_txt}}}$$\n")
            bloques.append(f"$$x_{{{ind1}}} = {_resta(xn_txt, cociente_txt)}$$\n")
        bloques.append(f"$$x_{{{ind1}}} = {xn1_txt}$$\n")
        bloques.append(f"> $x_{{{ind}}} = {xn_txt}$ → $x_{{{ind1}}} = {xn1_txt}$\n")

        bloques.append("**5. Cálculo completo del error:**\n")
        bloques.append(f"$$Ea_{{{ind1}}} = \\left| \\frac{{x_{{{ind1}}} - x_{{{ind}}}}}{{x_{{{ind1}}}}} \\right| \\times 100$$\n")
        if isinstance(ea, (int, float)) and math.isfinite(ea):
            bloques.append(f"$$Ea_{{{ind1}}} = \\left| \\frac{{{_resta(xn1_txt, xn_txt)}}}{{{xn1_txt}}} \\right| \\times 100$$\n")
            if criterio == "error" and error_permitido is not None:
                if ea > error_permitido:
                    mensaje_error = (
                        f"El error ({ea_txt} %) todavía es mayor que el permitido "
                        f"({_valor_display(error_permitido, decimales)} %), por eso continuamos."
                    )
                else:
                    mensaje_error = (
                        f"El error ({ea_txt} %) ya es menor o igual que el permitido "
                        f"({_valor_display(error_permitido, decimales)} %), por eso terminamos."
                    )
            else:
                mensaje_error = f"El error aproximado de esta iteración es {ea_txt} %."
            bloques.append(f"$$Ea_{{{ind1}}} = {ea_txt} \\%$$\n")
            bloques.append(mensaje_error + "\n")
        else:
            bloques.append(f"$$Ea_{{{ind1}}} = {ea_txt} \\%$$\n")

        bloques.append("</details>\n")
        bloques.append("")

    return "\n".join(bloques)


def _seccion_recta_tangente(filas, expresion, derivada, decimales):
    bloques = []
    bloques.append("### 6. La recta tangente y Newton-Raphson\n")
    bloques.append(
        "Newton-Raphson funciona construyendo una **recta tangente** sobre la función "
        "en el punto actual $x_n$. La ecuación de esa recta es:\n"
    )
    bloques.append("$$y = f(x_n) + f'(x_n) \\cdot (x - x_n)$$\n")
    bloques.append(
        "El punto donde esta recta corta el eje $x$ (es decir, donde $y = 0$) "
        "se convierte en la nueva aproximación $x_{n+1}$. Esto se obtiene despejando $x$:\n"
    )
    bloques.append("$$0 = f(x_n) + f'(x_n) \\cdot (x - x_n)$$\n")
    bloques.append("$$x = x_n - \\frac{f(x_n)}{f'(x_n)} = x_{n+1}$$\n")
    bloques.append(
        "Es decir, la fórmula de Newton-Raphson no es más que el resultado de encontrar "
        "dónde la recta tangente cruza el eje horizontal.\n"
    )

    if filas:
        bloques.append("**Recta tangente en cada iteración:**\n")
        for fila in filas:
            numero = fila["i"]
            ind = numero - 1
            ind1 = numero
            xn = fila["xi"]
            fxn = fila["f(xi)"]
            dfxn = fila["f'(xi)"]
            xn1 = fila["xi+1"]

            xn_fmt = _formatear(xn, decimales)
            fxn_fmt = _formatear(fxn, decimales)
            dfxn_fmt = _formatear(dfxn, decimales)
            xn1_fmt = _formatear(xn1, decimales)

            if abs(dfxn) > 1e-14:
                interseccion_info = (
                    f"Esta recta corta el eje $x$ en $x_{{{ind1}}} = {xn1_fmt}$, "
                    f"que se convierte en la nueva aproximación."
                )
            else:
                interseccion_info = (
                    "La derivada es cero o muy cercana a cero; la recta tangente es casi "
                    "horizontal y no produce una buena nueva aproximación."
                )

            bloques.append(f"<details><summary><b>Iteración {numero} — Recta tangente</b></summary>\n")
            bloques.append(f"**Iteración {numero} (usa $x_{{{ind}}}$ y calcula $x_{{{ind1}}}$):**\n")
            bloques.append(
                f"$$y = {fxn_fmt} + {dfxn_fmt} \\cdot (x - {xn_fmt})$$\n"
            )
            bloques.append(interseccion_info + "\n")
            bloques.append("</details>\n")
            bloques.append("")

    return "\n".join(bloques)


def _generar_newton_uniforme(expresion, filas, resultado, parametros, funcion_texto,
                             error_permitido, max_iteraciones, criterio, decimales):
    derivada = _derivada_de(expresion, parametros)
    return generar_explicacion_newton_raphson(
        expresion, derivada, filas, resultado, parametros or {}, funcion_texto,
        error_permitido, max_iteraciones, criterio, decimales,
    )
