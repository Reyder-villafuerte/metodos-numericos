"""Explicación paso a paso del método de Müller (soporta números complejos)."""

import cmath
import math

from ._comunes import (
    _seccion_convergencia,
    _seccion_error,
    _seccion_formula_general,
    _seccion_objetivo,
    _seccion_presentacion_generica,
    _seccion_resultado_final,
    _seccion_sin_iteraciones,
)
from ._formato import (
    TOLERANCIA_COMPLEJA,
    _diferencia_latex,
    _es_complejo_significativo,
    _latex_funcion,
    _latex_num,
    _parentizar,
    _paren,
    _resta,
    _texto_comparacion_error,
    _valor_display,
)


def _con_complejos(*valores):
    return any(_es_complejo_significativo(v) for v in valores)


def _producto_latex(*diferencias):
    return "".join(_parentizar(d) for d in diferencias)


def _iteraciones_muller(filas, expresion, decimales, criterio, error_permitido):
    bloques = ["### 4. Explicación completa de cada iteración\n"]
    if not filas:
        bloques.append("No se realizaron iteraciones.\n")
        return "\n".join(bloques)

    bloques.append(
        "Cada iteración construye una **parábola** por tres puntos y calcula su intersección con el eje "
        "$x$. El método puede trabajar con números complejos. Despliegue cada iteración para ver el "
        "detalle.\n"
    )

    expr_latex = _latex_funcion(expresion)

    for fila in filas:
        numero = fila["i"]
        x0 = fila["x0"]; x1 = fila["x1"]; x2 = fila["x2"]
        f0 = fila["f(x0)"]; f1 = fila["f(x1)"]; f2 = fila["f(x2)"]
        a = fila["a"]; b = fila["b"]; c = fila["c"]
        disc = fila["Discriminante"]
        x3 = fila["x3"]
        ea = fila["Ea (%)"]

        x0_txt = _latex_num(x0, decimales); x1_txt = _latex_num(x1, decimales); x2_txt = _latex_num(x2, decimales)
        f0_txt = _latex_num(f0, decimales); f1_txt = _latex_num(f1, decimales); f2_txt = _latex_num(f2, decimales)
        a_txt = _latex_num(a, decimales); b_txt = _latex_num(b, decimales); c_txt = _latex_num(c, decimales)
        disc_txt = _latex_num(disc, decimales); x3_txt = _latex_num(x3, decimales)

        complejo = _con_complejos(x0, x1, x2, f0, f1, f2, a, b, c, disc, x3)

        bloques.append(f"<details><summary><b>Iteración {numero}</b></summary>\n")
        bloques.append(f"#### Iteración {numero}\n")

        bloques.append("**1. Tres aproximaciones y sus imágenes:**\n")
        bloques.append(f"$$x_0 = {x0_txt}, \\qquad x_1 = {x1_txt}, \\qquad x_2 = {x2_txt}$$\n")
        bloques.append(f"$$f(x) = {expr_latex}$$\n")
        bloques.append(
            f"$$f(x_0) = {f0_txt}, \\qquad f(x_1) = {f1_txt}, \\qquad f(x_2) = {f2_txt}$$\n"
        )

        bloques.append("**2. Interpolación cuadrática:**\n")
        bloques.append("Se busca la parábola que pasa por los tres puntos, escrita como:\n")
        bloques.append("$$P(x) = a\\,(x - x_2)^2 + b\\,(x - x_2) + c, \\qquad c = f(x_2)$$\n")
        bloques.append(
            "Imponiendo que $P(x_0) = f(x_0)$ y $P(x_1) = f(x_1)$ se obtienen los coeficientes:\n"
        )
        bloques.append(
            "$$a = \\frac{(x_1 - x_2)(f_0 - f_2) - (x_0 - x_2)(f_1 - f_2)}"
            "{(x_0 - x_2)(x_1 - x_2)(x_0 - x_1)}$$\n"
        )
        bloques.append(
            "$$b = \\frac{(x_0 - x_2)^2 (f_1 - f_2) - (x_1 - x_2)^2 (f_0 - f_2)}"
            "{(x_0 - x_2)(x_1 - x_2)(x_0 - x_1)}$$\n"
        )

        bloques.append("**3. Cálculo de los coeficientes con los valores reales:**\n")
        d_x1x2 = x1 - x2
        d_f0f2 = f0 - f2
        d_x0x2 = x0 - x2
        d_f1f2 = f1 - f2
        d_x0x1 = x0 - x1
        denominador = d_x0x2 * d_x1x2 * d_x0x1

        bloques.append(
            f"$$a = \\frac{{{_parentizar(_diferencia_latex(x1, x2, decimales))}"
            f"{_parentizar(_diferencia_latex(f0, f2, decimales))} - "
            f"{_parentizar(_diferencia_latex(x0, x2, decimales))}"
            f"{_parentizar(_diferencia_latex(f1, f2, decimales))}}}"
            f"{{{_producto_latex(_diferencia_latex(x0, x2, decimales), _diferencia_latex(x1, x2, decimales), _diferencia_latex(x0, x1, decimales))}}}$$\n"
        )
        bloques.append(
            f"$$b = \\frac{{{_parentizar(_diferencia_latex(x0, x2, decimales))}^2"
            f"{_parentizar(_diferencia_latex(f1, f2, decimales))} - "
            f"{_parentizar(_diferencia_latex(x1, x2, decimales))}^2"
            f"{_parentizar(_diferencia_latex(f0, f2, decimales))}}}"
            f"{{{_producto_latex(_diferencia_latex(x0, x2, decimales), _diferencia_latex(x1, x2, decimales), _diferencia_latex(x0, x1, decimales))}}}$$\n"
        )

        if not complejo:
            bloques.append("Valores intermedios:\n")
            bloques.append(
                f"$$x_1 - x_2 = {_valor_display(d_x1x2, decimales)}, \\qquad "
                f"f_0 - f_2 = {_valor_display(d_f0f2, decimales)}$$\n"
            )
            bloques.append(
                f"$$x_0 - x_2 = {_valor_display(d_x0x2, decimales)}, \\qquad "
                f"f_1 - f_2 = {_valor_display(d_f1f2, decimales)}$$\n"
            )
            bloques.append(
                f"$$(x_0 - x_2)(x_1 - x_2)(x_0 - x_1) = {_valor_display(denominador, decimales)}$$\n"
            )
        else:
            bloques.append(
                "Los valores son **complejos**, por lo que las operaciones se realizan con aritmética "
                "compleja. El resultado de los coeficientes es el siguiente.\n"
            )

        bloques.append(f"$$a = {a_txt}$$\n")
        bloques.append(f"$$b = {b_txt}$$\n")
        bloques.append(f"$$c = f(x_2) = {c_txt}$$\n")

        bloques.append("**4. Discriminante de la parábola:**\n")
        bloques.append("$$D = b^2 - 4ac$$\n")
        bloques.append(
            f"$$D = {_parentizar(b_txt)}^2 - 4({a_txt})({c_txt})$$\n"
        )
        bloques.append(f"$$D = {disc_txt}$$\n")

        raiz_disc = cmath.sqrt(complex(disc)) if not _es_complejo_significativo(disc) else cmath.sqrt(disc)
        raiz_txt = _latex_num(raiz_disc, decimales)
        bloques.append("**5. Raíz cuadrada del discriminante:**\n")
        bloques.append(f"$$\\sqrt{{D}} = \\sqrt{{{disc_txt}}} = {raiz_txt}$$\n")

        bloques.append("**6. Selección del denominador (estabilidad numérica):**\n")
        denominador1 = b + raiz_disc
        denominador2 = b - raiz_disc
        bloques.append(
            f"$$b + \\sqrt{{D}} = {b_txt} + {_parentizar(raiz_txt)} = {_latex_num(denominador1, decimales)}$$\n"
        )
        bloques.append(
            f"$$b - \\sqrt{{D}} = {_diferencia_latex(b, raiz_disc, decimales)} = {_latex_num(denominador2, decimales)}$$\n"
        )
        bloques.append(
            f"$$\\left|b + \\sqrt{{D}}\\right| = {_valor_display(abs(denominador1), decimales)}, \\qquad "
            f"\\left|b - \\sqrt{{D}}\\right| = {_valor_display(abs(denominador2), decimales)}$$\n"
        )
        if abs(denominador1) >= abs(denominador2):
            elegido = denominador1
            signo_elegido = "+"
        else:
            elegido = denominador2
            signo_elegido = "-"
        bloques.append(
            f"El algoritmo elige el denominador con **mayor valor absoluto**, es decir "
            f"$b {signo_elegido} \\sqrt{{D}} = {_latex_num(elegido, decimales)}$. Así se evita dividir "
            "por un número muy pequeño y se reduce el error numérico.\n"
        )

        bloques.append("**7. Cálculo de la nueva aproximación $x_3$:**\n")
        bloques.append("$$x_3 = x_2 - \\frac{2c}{b \\pm \\sqrt{b^2 - 4ac}}$$\n")
        bloques.append(
            f"$$x_3 = {x2_txt} - \\frac{{2 \\cdot {_parentizar(c_txt)}}}"
            f"{{{_latex_num(elegido, decimales)}}}$$\n"
        )
        if abs(elegido) > TOLERANCIA_COMPLEJA:
            cociente = 2 * c / elegido
            if _es_complejo_significativo(cociente):
                paso_x3 = f"{x2_txt} - {_paren(cociente, decimales)}"
            else:
                paso_x3 = _resta(x2_txt, _latex_num(cociente, decimales))
            bloques.append(f"$$x_3 = {paso_x3}$$\n")
        bloques.append(f"$$x_3 = {x3_txt}$$\n")

        bloques.append("**8. Cálculo del error aproximado:**\n")
        if abs(complex(x3)) < TOLERANCIA_COMPLEJA:
            bloques.append(
                "Como la nueva aproximación es prácticamente cero, el método usa la **diferencia "
                "absoluta** para evitar dividir por cero:\n"
            )
            bloques.append("$$E_a = |x_3 - x_2|$$\n")
        else:
            bloques.append(
                "$$E_a = \\frac{|x_3 - x_2|}{|x_3|} \\times 100$$\n"
            )
        if isinstance(ea, (int, float)) and math.isfinite(ea):
            bloques.append(
                f"$$E_a = {_valor_display(ea, decimales)} \\%$$\n"
            )
            bloques.append(_texto_comparacion_error(ea, error_permitido, criterio, decimales) + "\n")
        else:
            bloques.append(f"$$E_a = {_valor_display(ea, decimales)}$$\n")

        bloques.append("</details>\n")
        bloques.append("")

    return "\n".join(bloques)


def _seccion_interpretacion_muller(filas, decimales):
    bloques = ["### 6. Interpretación geométrica y raíces complejas\n"]
    bloques.append(
        "Müller ajusta una **parábola** a los tres puntos más recientes y usa su corte con el eje $x$ "
        "como nueva aproximación. Al ser cuadrática, la parábola puede no cortar el eje real: en ese caso "
        "las raíces son **complejas** y el método las aproxima sin problema.\n"
    )
    bloques.append(
        "La fórmula $x_3 = x_2 - \\dfrac{2c}{b \\pm \\sqrt{b^2 - 4ac}}$ proviene de resolver "
        "$a(x-x_2)^2 + b(x-x_2) + c = 0$. La elección del signo con mayor denominador evita la "
        "cancelación catastrófica que ocurriría al restar cantidades casi iguales.\n"
    )
    hay_complejos = any(_con_complejos(f["x3"], f["Discriminante"]) for f in filas)
    if hay_complejos:
        bloques.append(
            "En esta ejecución aparecieron **valores complejos**; se representan en la forma $a + bi$.\n"
        )
    bloques.append("")
    return "\n".join(bloques)


def generar_explicacion_muller(expresion, filas, resultado, parametros, funcion_texto,
                               error_permitido, max_iteraciones, criterio, decimales):
    secciones = []
    secciones.append(_seccion_presentacion_generica("Müller", expresion, parametros, funcion_texto,
                                                    error_permitido, max_iteraciones, criterio, decimales))
    secciones.append(_seccion_objetivo("Müller"))
    secciones.append(_seccion_formula_general("Müller"))
    if filas:
        secciones.append(_iteraciones_muller(filas, expresion, decimales, criterio, error_permitido))
        secciones.append(_seccion_error(filas, error_permitido, criterio, decimales,
                                        clave="x3", clave_funcion="f(x2)", etiqueta="$x_3$"))
        secciones.append(_seccion_interpretacion_muller(filas, decimales))
        secciones.append(_seccion_convergencia(resultado, filas, error_permitido, criterio, decimales, "Müller"))
    else:
        secciones.append(_seccion_sin_iteraciones("Müller", expresion, resultado, parametros, decimales))
    secciones.append(_seccion_resultado_final(resultado, expresion, decimales, "Müller", criterio, parametros, len(filas)))
    return "\n".join(secciones)
