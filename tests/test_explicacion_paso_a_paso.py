import re
from pathlib import Path

import pytest
import sympy as sp
from streamlit.testing.v1 import AppTest

from metodos.biseccion import biseccion
from metodos.muller import muller
from metodos.newton_raphson import newton_raphson
from metodos.punto_fijo import punto_fijo
from metodos.regla_falsa import regla_falsa
from metodos.secante import secante
from utilidades.explicacion_paso_a_paso import (
    GENERADORES,
    _formatear,
    _seccion_convergencia,
    _seccion_error,
    _seccion_formula_general,
    _seccion_iteraciones,
    _seccion_objetivo,
    _seccion_presentacion,
    _seccion_recta_tangente,
    _seccion_resultado_final,
    _valor_display,
    generar_explicacion,
    generar_explicacion_newton_raphson,
    validar_estado_explicacion,
)
from utilidades.graficas import crear_grafica_con_tangente
from utilidades.parser_funciones import (
    analizar_funcion,
    funcion_numerica,
    funcion_numerica_compleja,
)


def _resolver_newton(x0=0.5, error_permitido=1e-6, max_iteraciones=50, criterio="error"):
    expresion = analizar_funcion("exp(-x)-x")
    derivada = sp.diff(expresion, sp.Symbol("x", real=True))
    if criterio == "error":
        resultado = newton_raphson(
            funcion_numerica(expresion), funcion_numerica(derivada), x0,
            error_permitido=error_permitido, max_iteraciones=max_iteraciones, criterio="error",
        )
    else:
        resultado = newton_raphson(
            funcion_numerica(expresion), funcion_numerica(derivada), x0,
            error_permitido=None, max_iteraciones=None, criterio="fijo", iteraciones_fijas=max_iteraciones,
        )
    return expresion, derivada, resultado


def test_formatear_numero():
    assert _formatear(3.14159, 2) == "3.14"
    assert _formatear(2.0, 0) == "2"
    assert _formatear(complex(1, 2), 3) == "1.000 + 2.000i"
    assert _formatear(float("inf")) == "No disponible"


def test_objetivo_y_formula_general_contienen_elementos_clave():
    objetivo = _seccion_objetivo()
    assert "Newton-Raphson" in objetivo
    assert "cero" in objetivo
    assert "positiva, negativa o cero" in objetivo

    formula = _seccion_formula_general()
    assert r"x_{n+1} = x_n" in formula
    assert r"f(x_n)" in formula
    assert "Valor actual" in formula
    assert "Nueva aproximación" in formula


def test_presentacion_usa_valores_dinamicos():
    expresion, derivada, _ = _resolver_newton()
    parametros = {"x0": 0.5}
    seccion = _seccion_presentacion(expresion, derivada, parametros, "exp(-x)-x", 1e-6, 50, "error", 6)
    assert "0.500000" in seccion
    assert "0.000001" in seccion  # error permitido 1e-6 formateado
    assert "50" in seccion
    assert "6" in seccion


def test_iteraciones_muestran_valores_reales():
    expresion, derivada, resultado = _resolver_newton()
    seccion = _seccion_iteraciones(resultado.iteraciones, expresion, derivada, 6)
    primera = resultado.iteraciones[0]
    xi = primera["xi"]
    fxi = primera["f(xi)"]
    dfxi = primera["f'(xi)"]
    xn1 = primera["xi+1"]
    assert f"Iteración {primera['i']}" in seccion
    assert f"{xi:.6f}" in seccion
    assert f"{fxi:.6f}" in seccion
    assert f"{dfxi:.6f}" in seccion
    assert f"{xn1:.6f}" in seccion
    assert "<details>" in seccion


def _resolver_polinomio(func_text, x0, iteraciones_fijas):
    expresion = analizar_funcion(func_text)
    derivada = sp.diff(expresion, sp.Symbol("x", real=True))
    resultado = newton_raphson(
        funcion_numerica(expresion), funcion_numerica(derivada), x0,
        error_permitido=None, max_iteraciones=None, criterio="fijo", iteraciones_fijas=iteraciones_fijas,
    )
    return expresion, derivada, resultado


def test_iteracion1_usa_x0_y_calcula_x1():
    expresion, derivada, resultado = _resolver_polinomio("x**3+3*x+1", 0.0, 2)
    seccion = _seccion_iteraciones(resultado.iteraciones, expresion, derivada, 6, "fijo", None)
    iteracion_1 = seccion.split("Iteración 2")[0]

    assert r"x_{0} = 0" in iteracion_1
    assert r"Partimos del valor inicial $x_0$" in iteracion_1
    assert r"f(0) = (0)^3 + 3(0) + 1" in iteracion_1
    assert r"f(0) = 1" in iteracion_1
    assert r"f'(0) = 3(0)^2 + 3" in iteracion_1
    assert r"f'(0) = 3" in iteracion_1
    assert r"x_{1} = 0 - \frac{1}{3}" in iteracion_1
    assert r"x_{1} = 0 - 0.333333" in iteracion_1
    assert r"x_{1} = -0.333333" in iteracion_1
    assert r"x_{2}" not in iteracion_1


def test_iteracion2_usa_x1_y_calcula_x2():
    expresion, derivada, resultado = _resolver_polinomio("x**3+3*x+1", 0.0, 2)
    seccion = _seccion_iteraciones(resultado.iteraciones, expresion, derivada, 6, "fijo", None)
    iteracion_2 = seccion.split("Iteración 2", 1)[1]

    assert r"#### Iteración 2" in iteracion_2
    assert r"x_{1} = -0.333333" in iteracion_2
    assert r"x_{2}" in iteracion_2
    assert r"x_{3}" not in iteracion_2


def test_sustitucion_usa_la_funcion_actual():
    exp1, derivada1, resultado1 = _resolver_polinomio("x**3+3*x+1", 0.0, 2)
    seccion1 = _seccion_iteraciones(resultado1.iteraciones, exp1, derivada1, 6, "fijo", None)
    exp2, derivada2, resultado2 = _resolver_polinomio("x**2-4", 1.0, 2)
    seccion2 = _seccion_iteraciones(resultado2.iteraciones, exp2, derivada2, 6, "fijo", None)

    assert "(0)^3 + 3(0) + 1" in seccion1
    assert "(1)^2 - 4" in seccion2
    assert seccion1 != seccion2


def test_explicacion_sin_datos_obsoletos():
    exp1, derivada1, resultado1 = _resolver_polinomio("x**3+3*x+1", 0.0, 2)
    contenido1 = generar_explicacion_newton_raphson(
        exp1, derivada1, resultado1.iteraciones, resultado1,
        {"x0": 0.0}, "x**3+3*x+1", None, 2, "fijo", 6,
    )
    contenido_repetido = generar_explicacion_newton_raphson(
        exp1, derivada1, resultado1.iteraciones, resultado1,
        {"x0": 0.0}, "x**3+3*x+1", None, 2, "fijo", 6,
    )
    assert contenido1 == contenido_repetido
    exp2, derivada2, resultado2 = _resolver_polinomio("x**2-4", 1.0, 2)
    contenido2 = generar_explicacion_newton_raphson(
        exp2, derivada2, resultado2.iteraciones, resultado2,
        {"x0": 1.0}, "x**2-4", None, 2, "fijo", 6,
    )
    assert "(0)^3 + 3(0) + 1" in contenido1
    assert "(0)^3 + 3(0) + 1" not in contenido2


def test_fraciones_renderizan_con_frac_sin_pegar_numeros():
    expresion, derivada, resultado = _resolver_polinomio("x**3+3*x+1", 0.0, 2)
    seccion = _seccion_iteraciones(resultado.iteraciones, expresion, derivada, 6, "fijo", None)
    assert r"\frac{1}{3}" in seccion
    assert r"\frac{f(x_{0})}{f'(x_{0})}" in seccion
    assert "1.0000003.000000" not in seccion
    assert "3.0000000.333333" not in seccion


def test_formula_del_error_usa_valores_correctos():
    expresion, derivada, resultado = _resolver_polinomio("x**3+3*x+1", 0.0, 2)
    seccion = _seccion_iteraciones(resultado.iteraciones, expresion, derivada, 6, "fijo", None)
    assert r"Ea_{1} = \left| \frac{-0.333333 - 0}{-0.333333} \right| \times 100" in seccion
    assert r"Ea_{1} = 100 \%$" in seccion


def test_explicacion_funciona_con_polinomio_2x3():
    expresion, derivada, resultado = _resolver_polinomio("2*x**3-6*x**2+3*x+1", 3.0, 2)
    assert len(resultado.iteraciones) == 2
    seccion = _seccion_iteraciones(resultado.iteraciones, expresion, derivada, 6, "fijo", None)
    assert "2(3)^3 - 6(3)^2 + 3(3) + 1" in seccion
    assert "54 - 54 + 9 + 1" in seccion
    assert "6(3)^2 - 12(3) + 3" in seccion
    assert "54 - 36 + 3" in seccion


def test_resta_no_muestra_doble_signo_menos():
    expresion, derivada, resultado = _resolver_polinomio("x**3+3*x+1", 0.0, 2)
    seccion = _seccion_iteraciones(resultado.iteraciones, expresion, derivada, 6, "fijo", None)
    assert " - -" not in seccion
    assert "-0.333333 + 0.011111" in seccion
    assert "+ 0.333333" in seccion


def test_seccion_error_usa_errores_reales():
    _, _, resultado = _resolver_newton()
    seccion = _seccion_error(resultado.iteraciones, 1e-6, "error", 6)
    errores = [fila["Ea (%)"] for fila in resultado.iteraciones]
    for error_valor in errores:
        assert f"{error_valor:.6f}" in seccion
    assert r"E_a" in seccion
    assert "menor" in seccion


def test_seccion_recta_tangente_muestra_ecuacion_por_iteracion():
    expresion, derivada, resultado = _resolver_newton()
    seccion = _seccion_recta_tangente(resultado.iteraciones, expresion, derivada, 6)
    primera = resultado.iteraciones[0]
    fxi = primera["f(xi)"]
    dfxi = primera["f'(xi)"]
    assert f"{fxi:.6f}" in seccion
    assert f"{dfxi:.6f}" in seccion
    assert "Recta tangente" in seccion


def test_seccion_convergencia_usa_estado_real():
    _, _, resultado = _resolver_newton()
    seccion = _seccion_convergencia(resultado, resultado.iteraciones, 1e-6, "error", 6)
    assert "onvergi" in seccion
    assert len(resultado.iteraciones) >= 2


def test_seccion_resultado_final_evalua_la_raiz():
    expresion, _, resultado = _resolver_newton()
    seccion = _seccion_resultado_final(resultado, expresion, 6)
    assert "Raíz aproximada" in seccion
    assert f"{resultado.raiz:.6f}" in seccion
    assert "válida" in seccion or "válido" in seccion


def test_no_convergencia_se_explica_claramente():
    expresion = analizar_funcion("exp(x)")
    derivada = sp.diff(expresion, sp.Symbol("x", real=True))
    resultado = newton_raphson(
        funcion_numerica(expresion), funcion_numerica(derivada), 0.0,
        error_permitido=1e-2, max_iteraciones=4, criterio="error",
    )
    assert resultado.convergio is False
    seccion = _seccion_convergencia(resultado, resultado.iteraciones, 1e-2, "error", 6)
    assert "no convergió" in seccion.lower()
    assert "máximo de iteraciones" in seccion.lower()


def test_iteraciones_fijas_explica_que_no_afirma_convergencia():
    _, _, resultado = _resolver_newton(max_iteraciones=4, criterio="fijo")
    assert resultado.convergio is None
    seccion = _seccion_convergencia(resultado, resultado.iteraciones, None, "fijo", 6)
    assert "completaron" in seccion or "completó" in seccion


def test_explicacion_completa_es_dinamica():
    expresion, derivada, resultado = _resolver_newton()
    contenido = generar_explicacion_newton_raphson(
        expresion, derivada, resultado.iteraciones, resultado,
        {"x0": 0.5}, "exp(-x)-x", 1e-6, 50, "error", 6,
    )
    assert "1. Presentación del ejercicio" in contenido
    assert "2. ¿Qué busca" in contenido
    assert "3. Fórmula general" in contenido
    assert "4. Explicación de cada iteración" in contenido
    assert "5. Cálculo del error" in contenido
    assert "6. La recta tangente" in contenido
    assert "7. Análisis de convergencia" in contenido
    assert "8. Resultado final" in contenido
    assert f"{resultado.raiz:.6f}" in contenido


def test_explicacion_cambia_con_la_funcion():
    def _contenido(func_text, x0):
        expresion = analizar_funcion(func_text)
        derivada = sp.diff(expresion, sp.Symbol("x", real=True))
        resultado = newton_raphson(
            funcion_numerica(expresion), funcion_numerica(derivada), x0,
            error_permitido=1e-6, max_iteraciones=50, criterio="error",
        )
        return generar_explicacion_newton_raphson(
            expresion, derivada, resultado.iteraciones, resultado,
            {"x0": x0}, func_text, 1e-6, 50, "error", 6,
        )

    contenido_cos = _contenido("cos(x)-x", 0.5)
    contenido_cuadrado = _contenido("x**2-4", 1.0)
    assert contenido_cos != contenido_cuadrado
    assert r"\cos" in contenido_cos
    assert "0.500000" in contenido_cos
    assert "1.000000" in contenido_cuadrado


def test_validar_estado_detecta_faltantes():
    problemas = validar_estado_explicacion(None, None, [], None, None)
    assert len(problemas) >= 3


def test_grafica_con_tangente_construye_figura():
    expresion, _, resultado = _resolver_newton()
    fila = resultado.iteraciones[0]
    figura = crear_grafica_con_tangente(expresion, fila, (-1, 1), [0.5])
    trazas = [t.name for t in figura.data]
    anotaciones = [a.text for a in figura.layout.annotations if getattr(a, "text", None)]
    assert "f(x)" in trazas
    assert any("Recta tangente" in t for t in trazas)
    assert any("punto actual" in t for t in trazas)
    assert any("cruce con eje x" in t for t in trazas)
    assert "x_0" in anotaciones
    assert "x_1" in anotaciones


def test_grafica_con_tangente_derivada_cero_es_informativa():
    import sympy as sp
    from utilidades.graficas import crear_grafica_con_tangente

    simbolo = sp.Symbol("x", real=True)
    expresion = simbolo
    fila = {"i": 1, "xi": 0.5, "f(xi)": 0.25, "f'(xi)": 0.0, "xi+1": 9.0}
    figura = crear_grafica_con_tangente(expresion, fila, (0, 2), [0.5])
    anotaciones = [a.text for a in figura.layout.annotations if getattr(a, "text", None)]
    assert any("Derivada cercana a cero" in a for a in anotaciones)


def test_grafica_con_tangente_rechaza_valores_no_finitos():
    import sympy as sp
    from utilidades.graficas import crear_grafica_con_tangente

    simbolo = sp.Symbol("x", real=True)
    expresion = simbolo
    fila = {"i": 1, "xi": float("inf"), "f(xi)": 1.0, "f'(xi)": 2.0, "xi+1": 3.0}
    with pytest.raises(ValueError):
        crear_grafica_con_tangente(expresion, fila, (0, 2))


APP = Path(__file__).resolve().parents[1] / "app.py"


def test_app_muestra_pestana_explicacion_newton():
    app = AppTest.from_file(APP, default_timeout=30).run()
    app.selectbox(key="metodo_selector").select("Newton-Raphson").run()
    next(boton for boton in app.button if "Cargar ejemplo" in boton.label).click().run()
    resolver = next(boton for boton in app.button if boton.label == "Resolver")
    resolver.click().run()
    assert not app.exception
    assert len(app.tabs) == 5
    nombres_tabs = [tab.label for tab in app.tabs]
    assert any("Iteraciones" in n for n in nombres_tabs)
    assert any("Explicación paso a paso" in n for n in nombres_tabs)
    assert any("Gráfica" in n for n in nombres_tabs)
    indice_iter = next(i for i, n in enumerate(nombres_tabs) if "Iteraciones" in n)
    indice_exp = next(i for i, n in enumerate(nombres_tabs) if "Explicación paso a paso" in n)
    indice_graf = next(i for i, n in enumerate(nombres_tabs) if "Gráfica" in n)
    assert indice_iter < indice_exp < indice_graf


def test_app_selector_tangente_en_grafica():
    app = AppTest.from_file(APP, default_timeout=30).run()
    app.selectbox(key="metodo_selector").select("Newton-Raphson").run()
    next(boton for boton in app.button if "Cargar ejemplo" in boton.label).click().run()
    next(boton for boton in app.button if boton.label == "Resolver").click().run()
    assert not app.exception
    etiquetas = [s.label for s in app.selectbox]
    assert any("tangente" in e.lower() or "iteración" in e.lower() for e in etiquetas)


# ---------------------------------------------------------------------------
# Explicaciones paso a paso para TODOS los métodos (datos reales)
# ---------------------------------------------------------------------------

METODOS_TODOS = ["Bisección", "Regla falsa", "Punto fijo", "Newton-Raphson", "Secante", "Müller"]


def _sin_artefactos(contenido):
    assert not re.search(r"\bnan\b", contenido.lower()), "aparece 'nan' como valor"
    assert not re.search(r"\binf\b", contenido.lower()), "aparece 'inf' como valor"
    assert "complex(" not in contenido, "aparece representación complex() de Python"
    assert " - -" not in contenido, "aparece doble signo menos"
    assert "+-" not in contenido, "aparece signos pegados '+-'"
    assert not re.search(r"\dj\b", contenido), "aparece número complejo con sufijo j"


def _resolver_biseccion(criterio="error", error_permitido=1.0, iteraciones_fijas=6):
    expresion = analizar_funcion("exp(-x)-x")
    if criterio == "error":
        resultado = biseccion(funcion_numerica(expresion), 0.0, 1.0,
                              error_permitido=error_permitido, max_iteraciones=100, criterio="error")
    else:
        resultado = biseccion(funcion_numerica(expresion), 0.0, 1.0,
                              error_permitido=None, max_iteraciones=None, criterio="fijo",
                              iteraciones_fijas=iteraciones_fijas)
    return expresion, resultado


def _resolver_regla_falsa(criterio="error", error_permitido=1.0, iteraciones_fijas=6):
    expresion = analizar_funcion("x*sin(x)-1")
    if criterio == "error":
        resultado = regla_falsa(funcion_numerica(expresion), 2.0, 3.0,
                                error_permitido=error_permitido, max_iteraciones=100, criterio="error")
    else:
        resultado = regla_falsa(funcion_numerica(expresion), 2.0, 3.0,
                                error_permitido=None, max_iteraciones=None, criterio="fijo",
                                iteraciones_fijas=iteraciones_fijas)
    return expresion, resultado


def _resolver_punto_fijo(criterio="error", error_permitido=1e-4, iteraciones_fijas=5):
    expresion = analizar_funcion("x^3+2*x^2+10*x-20")
    despeje = analizar_funcion("20/(x^2+2*x+10)")
    if criterio == "error":
        resultado = punto_fijo(funcion_numerica(expresion), funcion_numerica(despeje), 1.5,
                               error_permitido=error_permitido, max_iteraciones=100, criterio="error")
    else:
        resultado = punto_fijo(funcion_numerica(expresion), funcion_numerica(despeje), 1.5,
                               error_permitido=None, max_iteraciones=None, criterio="fijo",
                               iteraciones_fijas=iteraciones_fijas)
    return expresion, despeje, resultado


def _resolver_secante(criterio="error", error_permitido=1e-6, iteraciones_fijas=5):
    expresion = analizar_funcion("exp(-x)-x")
    if criterio == "error":
        resultado = secante(funcion_numerica(expresion), 0.0, 1.0,
                            error_permitido=error_permitido, max_iteraciones=50, criterio="error")
    else:
        resultado = secante(funcion_numerica(expresion), 0.0, 1.0,
                            error_permitido=None, max_iteraciones=None, criterio="fijo",
                            iteraciones_fijas=iteraciones_fijas)
    return expresion, resultado


def _resolver_muller(func_text="x^3-13*x-12", x0=4.5, x1=5.5, x2=5.0,
                     criterio="error", error_permitido=0.5, iteraciones_fijas=3):
    expresion = analizar_funcion(func_text)
    if criterio == "error":
        resultado = muller(funcion_numerica_compleja(expresion), x0, x1, x2,
                           error_permitido=error_permitido, max_iteraciones=100, criterio="error")
    else:
        resultado = muller(funcion_numerica_compleja(expresion), x0, x1, x2,
                           error_permitido=None, max_iteraciones=None, criterio="fijo",
                           iteraciones_fijas=iteraciones_fijas)
    return expresion, resultado


def _contenido_por_metodo(metodo):
    if metodo == "Bisección":
        expresion, resultado = _resolver_biseccion()
        contenido = generar_explicacion(metodo, expresion, resultado.iteraciones, resultado,
                                        {"a": 0.0, "b": 1.0}, "exp(-x)-x", 1.0, 100, "error", 6)
    elif metodo == "Regla falsa":
        expresion, resultado = _resolver_regla_falsa()
        contenido = generar_explicacion(metodo, expresion, resultado.iteraciones, resultado,
                                        {"a": 2.0, "b": 3.0}, "x*sin(x)-1", 1.0, 100, "error", 6)
    elif metodo == "Punto fijo":
        expresion, despeje, resultado = _resolver_punto_fijo()
        contenido = generar_explicacion(metodo, expresion, resultado.iteraciones, resultado,
                                        {"x0": 1.5, "despeje": despeje}, "x^3+2*x^2+10*x-20",
                                        1e-4, 100, "error", 6)
    elif metodo == "Newton-Raphson":
        expresion, derivada, resultado = _resolver_newton()
        contenido = generar_explicacion(metodo, expresion, resultado.iteraciones, resultado,
                                        {"x0": 0.5, "derivada": derivada}, "exp(-x)-x", 1e-6, 50, "error", 6)
    elif metodo == "Secante":
        expresion, resultado = _resolver_secante()
        contenido = generar_explicacion(metodo, expresion, resultado.iteraciones, resultado,
                                        {"x0": 0.0, "x1": 1.0}, "exp(-x)-x", 1e-6, 50, "error", 6)
    elif metodo == "Müller":
        expresion, resultado = _resolver_muller()
        contenido = generar_explicacion(metodo, expresion, resultado.iteraciones, resultado,
                                        {"x0": 4.5, "x1": 5.5, "x2": 5.0}, "x^3-13*x-12", 0.5, 100, "error", 6)
    else:
        raise ValueError(metodo)
    return contenido, resultado


def test_generadores_incluyen_todos_los_metodos():
    assert set(METODOS_TODOS).issubset(set(GENERADORES.keys()))


def test_dispatcher_rechaza_metodo_desconocido():
    expresion = analizar_funcion("x-1")
    with pytest.raises(ValueError):
        generar_explicacion("Método inexistente", expresion, [], None, {})


def test_dispatcher_rechaza_resultado_nulo():
    expresion = analizar_funcion("x-1")
    with pytest.raises(ValueError):
        generar_explicacion("Bisección", expresion, [], None, {})


@pytest.mark.parametrize("metodo", METODOS_TODOS)
def test_explicaciones_tienen_todas_las_secciones_y_sin_artefactos(metodo):
    contenido, _ = _contenido_por_metodo(metodo)
    for titulo in [
        "1. Presentación del ejercicio",
        "2. ¿Qué busca",
        "3. Fórmula general",
        "4. Explicación",
        "5. Cálculo del error",
        "7. Análisis de convergencia",
        "8. Resultado final",
    ]:
        assert titulo in contenido, f"falta la sección {titulo!r} en {metodo}"
    _sin_artefactos(contenido)


@pytest.mark.parametrize("metodo", METODOS_TODOS)
def test_objetivo_y_formula_general_por_metodo(metodo):
    objetivo = _seccion_objetivo(metodo)
    formula = _seccion_formula_general(metodo)
    assert metodo in objetivo
    assert metodo in formula
    assert "Significado de cada elemento" in formula


@pytest.mark.parametrize("metodo", METODOS_TODOS)
def test_explicaciones_son_deterministas(metodo):
    primera, _ = _contenido_por_metodo(metodo)
    segunda, _ = _contenido_por_metodo(metodo)
    assert primera == segunda


def test_explicacion_biseccion_usa_datos_reales():
    expresion, resultado = _resolver_biseccion()
    contenido = generar_explicacion("Bisección", expresion, resultado.iteraciones, resultado,
                                    {"a": 0.0, "b": 1.0}, "exp(-x)-x", 1.0, 100, "error", 6)
    primera = resultado.iteraciones[0]
    assert "Bisección" in contenido
    assert f"{primera['mi']:.6f}" in contenido
    assert f"{primera['f(mi)']:.6f}" in contenido
    assert "<details>" in contenido
    _sin_artefactos(contenido)


def test_explicacion_regla_falsa_usa_datos_reales():
    expresion, resultado = _resolver_regla_falsa()
    contenido = generar_explicacion("Regla falsa", expresion, resultado.iteraciones, resultado,
                                    {"a": 2.0, "b": 3.0}, "x*sin(x)-1", 1.0, 100, "error", 6)
    primera = resultado.iteraciones[0]
    assert f"{primera['mi']:.6f}" in contenido
    assert f"{primera['f(mi)']:.6f}" in contenido
    assert r"x_r" in contenido
    _sin_artefactos(contenido)


def test_explicacion_punto_fijo_usa_g_y_despeje():
    expresion, despeje, resultado = _resolver_punto_fijo()
    contenido = generar_explicacion("Punto fijo", expresion, resultado.iteraciones, resultado,
                                    {"x0": 1.5, "despeje": despeje}, "x^3+2*x^2+10*x-20",
                                    1e-4, 100, "error", 6)
    primera = resultado.iteraciones[0]
    assert "Despeje ingresado" in contenido
    assert "g(x" in contenido
    assert f"{primera['g(xi)']:.6f}" in contenido
    _sin_artefactos(contenido)


def test_explicacion_secante_muestra_dos_puntos_y_sin_derivada():
    expresion, resultado = _resolver_secante()
    contenido = generar_explicacion("Secante", expresion, resultado.iteraciones, resultado,
                                    {"x0": 0.0, "x1": 1.0}, "exp(-x)-x", 1e-6, 50, "error", 6)
    primera = resultado.iteraciones[0]
    assert f"{primera['xi']:.6f}" in contenido
    assert f"{primera['f(xi)']:.6f}" in contenido
    assert r"x_{n+1}" in contenido
    assert "secante" in contenido.lower()
    _sin_artefactos(contenido)


def test_explicacion_muller_coeficientes_y_discriminante():
    expresion, resultado = _resolver_muller()
    contenido = generar_explicacion("Müller", expresion, resultado.iteraciones, resultado,
                                    {"x0": 4.5, "x1": 5.5, "x2": 5.0}, "x^3-13*x-12", 0.5, 100, "error", 6)
    primera = resultado.iteraciones[0]
    assert "Discriminante" in contenido
    assert _valor_display(primera["a"], 6) in contenido
    assert _valor_display(primera["b"], 6) in contenido
    assert _valor_display(primera["Discriminante"], 6) in contenido
    assert r"\sqrt{D}" in contenido
    _sin_artefactos(contenido)


def test_explicacion_muller_soporta_raices_complejas():
    expresion = analizar_funcion("x^2+1")
    resultado = muller(funcion_numerica_compleja(expresion), 0.0, 1.0, 2.0,
                       error_permitido=0.01, max_iteraciones=20, criterio="error")
    contenido = generar_explicacion("Müller", expresion, resultado.iteraciones, resultado,
                                    {"x0": 0.0, "x1": 1.0, "x2": 2.0}, "x^2+1", 0.01, 20, "error", 6)
    assert "i" in contenido
    assert isinstance(resultado.raiz, complex)
    assert abs(abs(resultado.raiz) - 1.0) < 1e-2
    _sin_artefactos(contenido)


def test_explicacion_biseccion_raiz_en_extremo_sin_iteraciones():
    expresion = analizar_funcion("x")
    resultado = biseccion(funcion_numerica(expresion), 0.0, 1.0)
    assert resultado.iteraciones == []
    contenido = generar_explicacion("Bisección", expresion, resultado.iteraciones, resultado,
                                    {"a": 0.0, "b": 1.0}, "x", 1e-6, 100, "error", 6)
    assert "raíz" in contenido.lower()
    assert "### 8. Resultado final" in contenido
    _sin_artefactos(contenido)


def test_explicacion_muller_raiz_en_punto_inicial_sin_iteraciones():
    expresion = analizar_funcion("x")
    resultado = muller(funcion_numerica_compleja(expresion), -1.0, -2.0, 0.0,
                       error_permitido=1e-6, max_iteraciones=20, criterio="error")
    assert resultado.iteraciones == []
    contenido = generar_explicacion("Müller", expresion, resultado.iteraciones, resultado,
                                    {"x0": -1.0, "x1": -2.0, "x2": 0.0}, "x", 1e-6, 20, "error", 6)
    assert "### 8. Resultado final" in contenido
    _sin_artefactos(contenido)


def test_explicacion_distingue_criterio_error_y_fijo():
    expresion, despeje, resultado_error = _resolver_punto_fijo(criterio="error", error_permitido=1e-4)
    contenido_error = generar_explicacion("Punto fijo", expresion, resultado_error.iteraciones,
                                          resultado_error, {"x0": 1.5, "despeje": despeje},
                                          "x^3+2*x^2+10*x-20", 1e-4, 100, "error", 6)
    assert "error porcentual permitido" in contenido_error.lower()

    expresion, despeje, resultado_fijo = _resolver_punto_fijo(criterio="fijo", iteraciones_fijas=5)
    contenido_fijo = generar_explicacion("Punto fijo", expresion, resultado_fijo.iteraciones,
                                         resultado_fijo, {"x0": 1.5, "despeje": despeje},
                                         "x^3+2*x^2+10*x-20", None, 5, "fijo", 6)
    assert "número fijo de iteraciones" in contenido_fijo.lower()
    assert len(resultado_fijo.iteraciones) == 5
    assert contenido_error != contenido_fijo


def test_explicacion_no_convergencia_lo_indica():
    expresion = analizar_funcion("exp(x)-3")
    resultado = biseccion(funcion_numerica(expresion), 0.0, 2.0,
                          error_permitido=1e-12, max_iteraciones=3, criterio="error")
    assert resultado.convergio is False
    contenido = generar_explicacion("Bisección", expresion, resultado.iteraciones, resultado,
                                    {"a": 0.0, "b": 2.0}, "exp(x)-3", 1e-12, 3, "error", 6)
    assert "no convergió" in contenido.lower()
    _sin_artefactos(contenido)


def test_explicacion_cambia_con_la_funcion_y_los_parametros():
    e1 = analizar_funcion("exp(-x)-x")
    r1 = biseccion(funcion_numerica(e1), 0.0, 1.0, error_permitido=1.0, max_iteraciones=100, criterio="error")
    c1 = generar_explicacion("Bisección", e1, r1.iteraciones, r1, {"a": 0.0, "b": 1.0},
                             "exp(-x)-x", 1.0, 100, "error", 6)

    e2 = analizar_funcion("x**2-2")
    r2 = biseccion(funcion_numerica(e2), 0.0, 2.0, error_permitido=1.0, max_iteraciones=100, criterio="error")
    c2 = generar_explicacion("Bisección", e2, r2.iteraciones, r2, {"a": 0.0, "b": 2.0},
                             "x**2-2", 1.0, 100, "error", 6)

    assert c1 != c2
    assert "x^{2} - 2" in c2 or "x**2" in c2


def test_app_explicacion_funciona_para_biseccion():
    app = AppTest.from_file(APP, default_timeout=30).run()
    app.selectbox(key="metodo_selector").select("Bisección").run()
    next(boton for boton in app.button if "Cargar ejemplo" in boton.label).click().run()
    next(boton for boton in app.button if boton.label == "Resolver").click().run()
    assert not app.exception
    textos = [m.value for m in app.markdown]
    assert any("Bisección" in t for t in textos)
