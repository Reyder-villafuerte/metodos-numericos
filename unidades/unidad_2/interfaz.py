"""Interfaz Streamlit de sistemas lineales para la Unidad 2."""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st
import sympy as sp

from .explicaciones import generar_explicacion, latex_matriz, latex_numero
from .metodos import (
    ErrorSistemaLineal,
    ErrorSistemaNoLineal,
    resolver_sistema,
    resolver_jacobi,
    resolver_gauss_seidel,
    resolver_jacobi_no_lineal,
    resolver_gauss_seidel_no_lineal,
    resolver_newton_raphson,
    evaluar_newton,
    diferencias_divididas,
    regresion_polinomial,
    regresion_lineal_multiple,
)
from .componentes_resultados import (
    mostrar_comprobacion_detallada,
    mostrar_graficas,
    mostrar_graficas_newton_sistema,
    mostrar_matriz,
    mostrar_resultados_completos,
    mostrar_resumen,
    mostrar_vector,
)
from .presentacion import dataframe_matriz
from .gauss_seidel_interfaz import mostrar_gauss_seidel


METODOS_UNIDAD_2 = {
    "Matriz inversa": {
        "icono": "A⁻¹",
        "tipo": "Método directo",
        "descripcion": "Construye numéricamente la matriz inversa y calcula x = A⁻¹b.",
        "formula": r"x=A^{-1}b",
    },
    "Regla de Cramer": {
        "icono": "Δ",
        "tipo": "Método directo",
        "descripcion": "Sustituye cada columna por b y usa cocientes de determinantes.",
        "formula": r"x_i=\frac{\det(A_i)}{\det(A)}",
    },
    "Doolittle": {
        "icono": "LU",
        "tipo": "Descomposición LU",
        "descripcion": "Factoriza PA = LU con diagonal unitaria en L y resuelve dos sistemas triangulares.",
        "formula": r"PA=LU,\quad l_{ii}=1",
    },
    "Crout": {
        "icono": "LU",
        "tipo": "Descomposición LU",
        "descripcion": "Factoriza PA = LU con diagonal unitaria en U y resuelve dos sistemas triangulares.",
        "formula": r"PA=LU,\quad u_{ii}=1",
    },
    "Jacobi": {
        "icono": "J", "tipo": "Iterativo lineal",
        "descripcion": "Actualiza todas las componentes usando exclusivamente la iteración anterior.",
        "formula": r"x_i^{(k+1)}=\frac{b_i-\sum_{j\ne i}a_{ij}x_j^{(k)}}{a_{ii}}",
    },
    "Gauss-Seidel": {
        "icono": "GS", "tipo": "Iterativo lineal",
        "descripcion": "Usa inmediatamente cada componente nueva para acelerar la convergencia.",
        "formula": r"x_i^{(k+1)}=\frac{b_i-\sum_{j<i}a_{ij}x_j^{(k+1)}-\sum_{j>i}a_{ij}x_j^{(k)}}{a_{ii}}",
    },
    "Jacobi no lineal": {
        "icono": "J", "tipo": "Sistema no lineal",
        "descripcion": "Iteración de punto fijo simultánea para x_i=g_i(x).",
        "formula": r"x_i^{(k+1)}=g_i(x^{(k)})",
    },
    "Gauss-Seidel no lineal": {
        "icono": "GS", "tipo": "Sistema no lineal",
        "descripcion": "Iteración de punto fijo no lineal con actualización inmediata.",
        "formula": r"x_i^{(k+1)}=g_i(x_1^{(k+1)},\ldots,x_{i-1}^{(k+1)},x_i^{(k)},\ldots)",
    },
    "Newton-Raphson para sistemas": {
        "icono": "N", "tipo": "Sistema no lineal",
        "descripcion": "Resuelve F(x)=0 mediante el Jacobiano analítico o diferencias finitas.",
        "formula": r"J_F(x^{(k)})\Delta x=-F(x^{(k)}),\quad x^{(k+1)}=x^{(k)}+\Delta x",
    },
    "Interpolación de Newton": {
        "icono": "P", "tipo": "Interpolación",
        "descripcion": "Construye el polinomio con diferencias divididas y nodos no equiespaciados.",
        "formula": r"P(x)=\sum_{i=0}^{n}c_i\prod_{j<i}(x-x_j)",
    },
    "Regresión polinomial": {
        "icono": "LS", "tipo": "Mínimos cuadrados",
        "descripcion": "Ajusta un polinomio minimizando la suma de cuadrados de los residuos.",
        "formula": r"\min_c\|Xc-y\|_2",
    },
    "Regresión lineal múltiple": {
        "icono": "LS", "tipo": "Mínimos cuadrados",
        "descripcion": "Ajusta una variable respuesta a varias variables explicativas.",
        "formula": r"y=\beta_0+\beta_1x_1+\cdots+\beta_px_p",
    },
}


EJEMPLOS = {
    "Matriz inversa": {
        "A": [[4.0, 7.0], [2.0, 6.0]],
        "b": [1.0, 0.0],
        "origen": "Ejemplo 2×2 de matriz invertible.",
    },
    "Regla de Cramer": {
        "A": [[0.3, 0.52, 1.0], [0.5, 1.0, 1.9], [0.1, 0.3, 0.5]],
        "b": [-0.01, 0.67, -0.44],
        "origen": "Ejemplo de Regla de Cramer presentado en la Sesión 6.",
    },
    "Doolittle": {
        "A": [[-1.0, 2.0, -3.0], [3.0, -3.0, -1.0], [1.0, 1.0, 0.0]],
        "b": [-2.0, -4.0, 3.0],
        "origen": "Primer sistema LU presentado en la Sesión 6.",
    },
    "Crout": {
        "A": [[8.0, 4.0, -1.0], [-2.0, 5.0, 1.0], [2.0, -1.0, 6.0]],
        "b": [11.0, 4.0, 7.0],
        "origen": "Segundo sistema LU presentado en la Sesión 6.",
    },
}


def limpiar_resultado_unidad_2() -> None:
    for clave in (
        "u2_resultado",
        "u2_iter_resultado",
        "u2_nl_resultado",
        "u2_interp_resultado",
        "u2_reg_resultado",
        "u2_error",
        "gs_resultado",
        "gs_error",
        "gs_iter_sel",
    ):
        st.session_state.pop(clave, None)


def _dataframes_sistema(A: np.ndarray, b: np.ndarray) -> tuple[pd.DataFrame, pd.DataFrame]:
    n = A.shape[0]
    indice = [f"Ecuación {i}" for i in range(1, n + 1)]
    columnas = [f"x{i}" for i in range(1, n + 1)]
    return (
        pd.DataFrame(A, index=indice, columns=columnas),
        pd.DataFrame({"b": b}, index=indice),
    )


def _establecer_sistema(A: np.ndarray, b: np.ndarray, origen: str = "") -> None:
    A = np.asarray(A, dtype=float)
    b = np.asarray(b, dtype=float).reshape(-1)
    st.session_state.u2_dimension = int(A.shape[0])
    st.session_state.u2_A_base, st.session_state.u2_b_base = _dataframes_sistema(A, b)
    st.session_state.u2_editor_version = st.session_state.get("u2_editor_version", 0) + 1
    st.session_state.u2_origen_ejemplo = origen
    limpiar_resultado_unidad_2()


def _nuevo_sistema() -> None:
    n = int(st.session_state.get("u2_dimension", 3))
    _establecer_sistema(np.eye(n), np.zeros(n), "Sistema nuevo con A inicializada como identidad.")


def _cargar_ejemplo(metodo: str) -> None:
    ejemplo = EJEMPLOS[metodo]
    _establecer_sistema(np.asarray(ejemplo["A"]), np.asarray(ejemplo["b"]), ejemplo["origen"])


def _cambiar_dimension() -> None:
    _nuevo_sistema()


def _inicializar_estado() -> None:
    st.session_state.setdefault("u2_dimension", 3)
    st.session_state.setdefault("u2_editor_version", 0)
    n = int(st.session_state.u2_dimension)
    if "u2_A_base" not in st.session_state or st.session_state.u2_A_base.shape != (n, n):
        A, b = _dataframes_sistema(np.eye(n), np.zeros(n))
        st.session_state.u2_A_base = A
        st.session_state.u2_b_base = b
        st.session_state.u2_origen_ejemplo = "Sistema nuevo con A inicializada como identidad."


def _mostrar_tarjeta_metodo(metodo: str) -> None:
    info = METODOS_UNIDAD_2[metodo]
    st.markdown(
        f'<div class="method-card"><h3>{info["icono"]} &nbsp;{metodo} '
        f'<span style="float:right;color:#2563eb;font-size:.78rem">{info["tipo"]}</span>'
        f'</h3><p>{info["descripcion"]}</p></div>',
        unsafe_allow_html=True,
    )
    st.latex(info["formula"])


def _mostrar_sistema(A: np.ndarray, b: np.ndarray, decimales: int) -> None:
    n = A.shape[0]
    variables = r"\begin{bmatrix}" + r" \\ ".join(f"x_{{{i}}}" for i in range(1, n + 1)) + r"\end{bmatrix}"
    st.latex(f"{latex_matriz(A, decimales)}{variables}={latex_matriz(b, decimales)}")


def _mostrar_resultado_iterativo(resultado) -> None:
    st.subheader(f"Resultado: {resultado.metodo}")
    st.metric("Iteraciones", resultado.iteraciones)
    st.metric("Error final", f"{resultado.error:.6e}")
    st.success("Convergió" if resultado.convergio else "No convergió dentro del máximo indicado.")
    st.dataframe(
        pd.DataFrame(
            {
                f"x{i + 1}": [fila["x"][i] for fila in resultado.historial]
                for i in range(len(resultado.x))
            }
            | {
                "Error": [fila["error"] for fila in resultado.historial],
                "Residuo": [fila["residuo"] for fila in resultado.historial],
            }
        ),
        width="stretch",
    )
    st.latex(f"x={latex_matriz(resultado.x, 8)}")


def _mostrar_metodo_iterativo_lineal(metodo: str) -> None:
    st.markdown("#### Sistema Ax=b")
    n = st.number_input("Número de incógnitas", min_value=2, max_value=8, value=3, step=1, key="u2_iter_n")
    A = st.data_editor(
        pd.DataFrame(np.eye(int(n))),
        key=f"u2_iter_A_{metodo}",
        num_rows="fixed",
        width="stretch",
    ).to_numpy(dtype=float)
    b = st.data_editor(
        pd.DataFrame({"b": np.zeros(int(n))}),
        key=f"u2_iter_b_{metodo}",
        num_rows="fixed",
        width="stretch",
    )["b"].to_numpy(dtype=float)
    cols = st.columns(3)
    tolerancia = cols[0].number_input("Tolerancia", min_value=1e-14, value=1e-8, format="%.2e", key=f"u2_tol_{metodo}")
    max_iter = cols[1].number_input("Máximo de iteraciones", min_value=1, value=100, step=1, key=f"u2_max_{metodo}")
    x0_texto = cols[2].text_input("x0 (opcional)", value="", key=f"u2_x0_{metodo}", help="Ejemplo: 0, 0, 0")
    if st.button("Resolver sistema", type="primary", key=f"u2_resolver_{metodo}"):
        try:
            x0 = None if not x0_texto.strip() else [float(v.strip()) for v in x0_texto.split(",")]
            resolver = resolver_jacobi if metodo == "Jacobi" else resolver_gauss_seidel
            st.session_state.u2_iter_resultado = resolver(A, b, x0, tolerancia, int(max_iter))
            st.session_state.pop("u2_error", None)
        except (ValueError, ErrorSistemaLineal) as exc:
            st.session_state.pop("u2_iter_resultado", None)
            st.session_state.u2_error = str(exc)
    if st.session_state.get("u2_error"):
        st.error(st.session_state.u2_error)
    if st.session_state.get("u2_iter_resultado") is not None:
        _mostrar_resultado_iterativo(st.session_state.u2_iter_resultado)


def _funciones_desde_texto(textos: list[str]):
    x, y = sp.symbols("x y")
    expresiones = [sp.sympify(texto, locals={"x": x, "y": y}) for texto in textos]
    return [sp.lambdify((x, y), expresion, "numpy") for expresion in expresiones]


def _mostrar_metodo_no_lineal(metodo: str) -> None:
    st.markdown("#### Sistema no lineal de dos ecuaciones")
    valor_f1 = "x**2+y**2-1" if metodo == "Newton-Raphson para sistemas" else "sqrt(1-y**2)"
    valor_f2 = "x-y" if metodo == "Newton-Raphson para sistemas" else "x"
    f1 = st.text_input("F₁(x,y) o g₁(x,y)", value=valor_f1, key=f"u2_f1_{metodo}")
    f2 = st.text_input("F₂(x,y) o g₂(x,y)", value=valor_f2, key=f"u2_f2_{metodo}")
    cols = st.columns(3)
    x0 = cols[0].number_input("x₀", value=0.5, key=f"u2_nl_x0_{metodo}")
    y0 = cols[1].number_input("y₀", value=0.5, key=f"u2_nl_y0_{metodo}")
    tolerancia = cols[2].number_input("Tolerancia", min_value=1e-14, value=1e-8, format="%.2e", key=f"u2_nl_tol_{metodo}")
    max_iter = st.number_input("Máximo de iteraciones", min_value=1, value=50, step=1, key=f"u2_nl_max_{metodo}")
    if st.button("Resolver sistema no lineal", type="primary", key=f"u2_resolver_{metodo}"):
        try:
            funciones_bivariadas = _funciones_desde_texto([f1, f2])
            funciones = [lambda valores, funcion=funcion: funcion(*valores) for funcion in funciones_bivariadas]
            if metodo == "Jacobi no lineal":
                resultado = resolver_jacobi_no_lineal(funciones, [x0, y0], tolerancia, int(max_iter))
            elif metodo == "Gauss-Seidel no lineal":
                resultado = resolver_gauss_seidel_no_lineal(funciones, [x0, y0], tolerancia, int(max_iter))
            else:
                resultado = resolver_newton_raphson(funciones, [x0, y0], tolerancia=tolerancia, max_iter=int(max_iter))
            st.session_state.u2_nl_resultado = resultado
            if metodo == "Newton-Raphson para sistemas":
                st.session_state.u2_newton_funciones = funciones_bivariadas
                st.session_state.u2_newton_textos = (f1, f2)
            st.session_state.pop("u2_error", None)
        except (ValueError, TypeError, ErrorSistemaNoLineal, sp.SympifyError) as exc:
            st.session_state.pop("u2_nl_resultado", None)
            st.session_state.u2_error = f"No se pudo interpretar o resolver el sistema: {exc}"
    if st.session_state.get("u2_error"):
        st.error(st.session_state.u2_error)
    if st.session_state.get("u2_nl_resultado") is not None:
        resultado = st.session_state.u2_nl_resultado
        if metodo == "Newton-Raphson para sistemas":
            _mostrar_resultado_newton_sistema(resultado)
        else:
            st.success("Convergió" if resultado.convergio else "No convergió dentro del máximo indicado.")
            st.metric("Error final", f"{resultado.error:.6e}")
            st.latex(f"x={latex_matriz(resultado.x, 8)}")
            st.dataframe(pd.DataFrame(resultado.historial), width="stretch")


def _mostrar_resultado_newton_sistema(resultado) -> None:
    """Presentación académica completa exclusiva para Newton-Raphson no lineal."""
    st.markdown("### Resultados: Newton-Raphson para sistemas")
    if resultado.convergio:
        st.success("El método convergió con los criterios de paso y residuo.")
    else:
        st.warning("No convergió dentro del máximo de iteraciones indicado.")
    funciones = st.session_state.get("u2_newton_funciones")
    textos = st.session_state.get("u2_newton_textos", ("F₁(x,y)", "F₂(x,y)"))
    tabs = st.tabs([
        "Resumen",
        "Resultado",
        "Matrices y operaciones",
        "Iteraciones",
        "Explicación paso a paso",
        "Comprobación",
        "Gráficas",
    ])
    with tabs[0]:
        columnas = st.columns(4)
        columnas[0].metric("Estado", "Convergió" if resultado.convergio else "Pendiente")
        columnas[1].metric("Iteraciones", resultado.iteraciones)
        columnas[2].metric("Error final ‖Δx‖∞", f"{resultado.error:.6e}")
        columnas[3].metric("Residuo final ‖F(x)‖∞", f"{resultado.residuo:.6e}")
        st.markdown("#### Sistema resuelto")
        st.latex(rf"F_1(x,y)={textos[0]}")
        st.latex(rf"F_2(x,y)={textos[1]}")
        st.markdown("#### Solución aproximada")
        st.latex(rf"x^*={latex_matriz(resultado.x, 10)}")
        st.info(
            "Newton busca simultáneamente el punto donde ambas funciones valen cero. "
            "La convergencia se acepta cuando el tamaño del paso y el residuo son menores "
            "que la tolerancia.",
            icon=":material/school:",
        )
    with tabs[1]:
        st.markdown("#### Vector solución")
        st.latex(rf"x^*=\begin{{bmatrix}}x\\y\end{{bmatrix}}={latex_matriz(resultado.x, 12)}")
        st.dataframe(
            pd.DataFrame({
                "Incógnita": ["x", "y"],
                "Valor aproximado": np.asarray(resultado.x, dtype=float),
            }),
            hide_index=True,
            width="stretch",
        )
        st.markdown("#### Indicadores numéricos")
        st.write(
            "La solución es aceptable cuando ambos indicadores son pequeños, "
            "no solamente cuando cambia poco el vector."
        )
        st.dataframe(pd.DataFrame([{
            "Iteraciones": resultado.iteraciones,
            "‖Δx‖∞": resultado.error,
            "‖F(x)‖∞": resultado.residuo,
            "Convergió": resultado.convergio,
        }]), hide_index=True, width="stretch")
    with tabs[2]:
        st.markdown("#### Jacobiano y operación de cada iteración")
        for fila in resultado.historial:
            with st.expander(f"Iteración {fila['iteracion']} · x=({fila['x'][0]:.8g}, {fila['x'][1]:.8g})"):
                st.latex(rf"x^{{({fila['iteracion']})}}={latex_matriz(fila['x'], 10)}")
                st.latex(rf"\|\Delta x\|_\infty={fila['error']:.8e}")
                st.latex(rf"\|F(x)\|_\infty={fila['residuo']:.8e}")
                if "jacobiano" in fila:
                    st.latex(rf"J(x^{{({fila['iteracion']-1})}})={latex_matriz(fila['jacobiano'], 8)}")
                if "funcion" in fila:
                    st.latex(rf"F(x^{{({fila['iteracion']-1})}})={latex_matriz(fila['funcion'], 8)}")
                if "delta" in fila:
                    st.latex(rf"\Delta x={latex_matriz(fila['delta'], 8)}")
        st.caption("El sistema lineal J·Δx=−F se resuelve en cada iteración; no se calcula una inversa explícita.")
    with tabs[3]:
        filas = []
        x_inicial = (
            np.asarray(resultado.x_inicial, dtype=float)
            if resultado.x_inicial is not None
            else (np.asarray(resultado.historial[0]["x"], dtype=float) if resultado.historial else resultado.x)
        )
        filas.append({"Iteración": 0, "x": x_inicial[0], "y": x_inicial[1], "‖Δx‖∞": np.nan, "‖F(x)‖∞": np.nan})
        for fila in resultado.historial:
            filas.append({
                "Iteración": fila["iteracion"],
                "x": fila["x"][0],
                "y": fila["x"][1],
                "‖Δx‖∞": fila["error"],
                "‖F(x)‖∞": fila["residuo"],
            })
        st.dataframe(pd.DataFrame(filas), hide_index=True, width="stretch")
    with tabs[4]:
        st.markdown("#### 1. Evaluar el sistema y el Jacobiano")
        st.latex(r"J(x^{(k)})=\begin{bmatrix}\frac{\partial F_1}{\partial x}&\frac{\partial F_1}{\partial y}\\\frac{\partial F_2}{\partial x}&\frac{\partial F_2}{\partial y}\end{bmatrix}")
        st.markdown("#### 2. Calcular la corrección")
        st.latex(r"J(x^{(k)})\Delta x=-F(x^{(k)})")
        st.markdown("#### 3. Actualizar la aproximación")
        st.latex(r"x^{(k+1)}=x^{(k)}+\Delta x")
        for fila in resultado.historial:
            st.markdown(f"**Iteración {fila['iteracion']}**")
            st.write(
                f"Se obtiene x=({fila['x'][0]:.10g}, {fila['x'][1]:.10g}), "
                f"con paso ‖Δx‖∞={fila['error']:.4e} y residuo ‖F(x)‖∞={fila['residuo']:.4e}."
            )
    with tabs[5]:
        st.markdown("#### Sustitución de la solución en cada ecuación")
        if funciones:
            valores = np.asarray([funcion(*np.asarray(resultado.x, dtype=float)) for funcion in funciones], dtype=float)
            for indice, (texto, valor) in enumerate(zip(textos, valores), start=1):
                st.markdown(f"**Ecuación {indice}**")
                st.latex(rf"{texto}\ \Longrightarrow\ F_{indice}(x^*)={valor:.12e}")
        st.metric("Norma del residuo", f"{resultado.residuo:.12e}")
        st.caption("Un residuo cercano a cero confirma que la aproximación satisface numéricamente las dos ecuaciones.")
    with tabs[6]:
        if funciones:
            mostrar_graficas_newton_sistema(funciones, resultado)
        else:
            st.warning("No hay funciones disponibles para construir la gráfica.")


def _mostrar_interpolacion_newton() -> None:
    st.markdown("#### Datos de interpolación")
    texto_x = st.text_input("Nodos x", value="0, 1, 2, 3", key="u2_interp_x")
    texto_y = st.text_input("Valores y", value="1, 2, 5, 10", key="u2_interp_y")
    valor = st.number_input("Evaluar en x", value=1.5, key="u2_interp_eval")
    if st.button("Interpolar", type="primary", key="u2_resolver_interpolacion"):
        try:
            x = [float(v.strip()) for v in texto_x.split(",")]
            y = [float(v.strip()) for v in texto_y.split(",")]
            tabla = diferencias_divididas(x, y)
            aproximacion = evaluar_newton(x, y, valor)
            st.session_state.u2_interp_resultado = (tabla, aproximacion)
        except (ValueError, TypeError) as exc:
            st.error(str(exc))
    if st.session_state.get("u2_interp_resultado") is not None:
        tabla, aproximacion = st.session_state.u2_interp_resultado
        st.dataframe(pd.DataFrame(tabla), width="stretch")
        st.metric("P(x)", f"{float(aproximacion):.12g}")


def _mostrar_regresion(metodo: str) -> None:
    st.markdown("#### Datos de ajuste separados por comas")
    valor_x = "1, 2, 3, 4" if metodo == "Regresión polinomial" else "1; 2\n2; 1\n3; 4\n4; 3"
    x_texto = st.text_area("Variables explicativas X", value=valor_x, key=f"u2_reg_x_{metodo}")
    y_texto = st.text_input("Respuesta y", value="2, 4, 6, 8", key=f"u2_reg_y_{metodo}")
    grado = st.number_input("Grado del polinomio", min_value=0, max_value=8, value=2, step=1, key=f"u2_reg_grado_{metodo}") if metodo == "Regresión polinomial" else None
    if st.button("Calcular ajuste", type="primary", key=f"u2_resolver_reg_{metodo}"):
        try:
            y = np.array([float(v.strip()) for v in y_texto.split(",")])
            if metodo == "Regresión polinomial":
                x = np.array([float(v.strip()) for v in x_texto.split(",")])
                resultado = regresion_polinomial(x, y, int(grado))
            else:
                filas = [[float(v.strip()) for v in fila.split(";")] for fila in x_texto.splitlines() if fila.strip()]
                resultado = regresion_lineal_multiple(np.asarray(filas), y)
            st.session_state.u2_reg_resultado = resultado
        except (ValueError, TypeError) as exc:
            st.error(str(exc))
    if st.session_state.get("u2_reg_resultado") is not None:
        resultado = st.session_state.u2_reg_resultado
        st.dataframe(pd.DataFrame({"Observado": resultado.predicciones + resultado.residuos, "Ajustado": resultado.predicciones, "Residuo": resultado.residuos}), width="stretch")
        st.write(f"Coeficientes: {resultado.coeficientes}")
        st.metric("R²", f"{resultado.r2:.8f}")


def _mostrar_pasos_factorizacion(resultado, decimales: int) -> None:
    for paso in resultado.pasos:
        if "etapa" not in paso or "fila_pivote" not in paso:
            continue
        with st.expander(f"Etapa {paso['etapa']} · pivote en fila {paso['fila_pivote']}"):
            if paso.get("intercambio"):
                f1, f2 = paso["intercambio"]
                st.warning(f"Pivoteo parcial: se intercambian las filas {f1} y {f2}.")
            st.latex(f"p_{{{paso['etapa']}}}={latex_numero(paso['pivote'], decimales)}")
            if resultado.metodo in ("Doolittle", "Matriz inversa"):
                for i, j, numerador, pivote, valor in paso.get("calculos_L", []):
                    st.latex(
                        rf"l_{{{i}{j}}}=\frac{{{latex_numero(numerador, decimales)}}}"
                        rf"{{{latex_numero(pivote, decimales)}}}={latex_numero(valor, decimales)}"
                    )
                for operacion in paso.get("operaciones_fila", []):
                    st.latex(
                        rf"F_{{{operacion['fila']}}}\leftarrow F_{{{operacion['fila']}}}-"
                        rf"{latex_numero(operacion['multiplicador'], decimales)}"
                        rf"F_{{{operacion['fila_pivote']}}}"
                    )
            else:
                for i, j, elemento, suma, valor in paso.get("calculos_L", []):
                    st.latex(
                        rf"l_{{{i}{j}}}={latex_numero(elemento, decimales)}-"
                        rf"{latex_numero(suma, decimales)}={latex_numero(valor, decimales)}"
                    )
                for i, j, elemento, suma, pivote, valor in paso.get("calculos_U", []):
                    st.latex(
                        rf"u_{{{i}{j}}}=\frac{{{latex_numero(elemento, decimales)}-"
                        rf"{latex_numero(suma, decimales)}}}{{{latex_numero(pivote, decimales)}}}="
                        rf"{latex_numero(valor, decimales)}"
                    )
            if "L" in paso:
                cols = st.columns(2)
                cols[0].caption("L acumulada")
                cols[0].dataframe(
                    dataframe_matriz(
                        paso["L"], columnas_variables=False, filas_ecuaciones=False
                    )
                )
                cols[1].caption("U acumulada")
                cols[1].dataframe(
                    dataframe_matriz(
                        paso["U"], columnas_variables=False, filas_ecuaciones=False
                    )
                )


def _mostrar_eliminacion_determinante(pasos, decimales: int) -> None:
    """Muestra pivotes, intercambios y matrices triangulares del determinante."""

    for paso in pasos:
        if "matriz_triangular" not in paso:
            continue
        st.markdown(f"**Etapa {paso['etapa']}**")
        if paso.get("intercambio"):
            f1, f2 = paso["intercambio"]
            st.write(f"Intercambio de filas: F{f1} ↔ F{f2}.")
        st.latex(rf"p_{{{paso['etapa']}}}={latex_numero(paso['pivote'], decimales)}")
        for fila, multiplicador in paso.get("multiplicadores", []):
            st.latex(
                rf"F_{{{fila}}}\leftarrow F_{{{fila}}}-"
                rf"{latex_numero(multiplicador, decimales)}F_{{{paso['etapa']}}}"
            )
        st.dataframe(dataframe_matriz(paso["matriz_triangular"]))


def _mostrar_resultado(resultado, decimales: int) -> None:
    st.markdown('<div class="step-label">Paso 2 · Análisis</div>', unsafe_allow_html=True)
    st.subheader("Resultados del sistema")
    tabs = st.tabs(
        [
            "Resumen",
            "Resultados",
            "Matrices y operaciones",
            "Explicación paso a paso",
            "Comprobación",
            "Gráficas",
        ]
    )

    with tabs[0]:
        mostrar_resumen(resultado, decimales)

    with tabs[1]:
        mostrar_resultados_completos(resultado, decimales)

    with tabs[2]:
        st.caption("Matriz original A y vector b")
        cols = st.columns(2)
        mostrar_matriz(cols[0], resultado.A, "A")
        mostrar_vector(cols[1], resultado.b, "b")
        st.latex(rf"\det(A)={latex_numero(resultado.determinante, decimales)}")

        if resultado.inversa is not None:
            st.markdown("#### Factorización usada para construir A⁻¹")
            if resultado.hubo_pivoteo:
                st.warning("Se aplicó pivoteo parcial; la relación usada es PA = LU.")
            cols = st.columns(3)
            for col, nombre, matriz in zip(cols, ("P", "L", "U"), (resultado.P, resultado.L, resultado.U)):
                mostrar_matriz(
                    col,
                    matriz,
                    nombre,
                    columnas_variables=False,
                    filas_ecuaciones=False,
                )
            _mostrar_pasos_factorizacion(resultado, decimales)
            st.markdown("#### Construcción de A⁻¹ por columnas")
            st.write("Se resuelve $Az_j=e_j$ para cada columna, usando una factorización con pivoteo parcial.")
            for columna in resultado.columnas_inversa:
                with st.expander(f"Columna {columna['columna']} de A⁻¹"):
                    st.latex(f"e={latex_matriz(columna['e'], decimales)}")
                    st.latex(f"Pe={latex_matriz(columna['Pb'], decimales)}")
                    for paso in columna["pasos_y"]:
                        st.latex(
                            rf"y_{{{paso['indice']}}}=\frac{{{latex_numero(paso['termino'], decimales)}-"
                            rf"{latex_numero(paso['suma'], decimales)}}}{{{latex_numero(paso['pivote'], decimales)}}}="
                            rf"{latex_numero(paso['valor'], decimales)}"
                        )
                    for paso in columna["pasos_z"]:
                        st.latex(
                            rf"z_{{{paso['indice']}}}=\frac{{{latex_numero(paso['termino'], decimales)}-"
                            rf"{latex_numero(paso['suma'], decimales)}}}{{{latex_numero(paso['pivote'], decimales)}}}="
                            rf"{latex_numero(paso['valor'], decimales)}"
                        )
                    st.latex(f"y={latex_matriz(columna['y'], decimales)}")
                    st.latex(f"z={latex_matriz(columna['z'], decimales)}")
            st.caption("Matriz inversa obtenida")
            st.dataframe(dataframe_matriz(resultado.inversa))
            st.latex(f"x=A^{{-1}}b={latex_matriz(resultado.x, decimales)}")

        elif resultado.matrices_cramer:
            st.markdown("#### Matrices de Cramer")
            with st.expander("Cálculo de det(A) por eliminación"):
                _mostrar_eliminacion_determinante(resultado.pasos, decimales)
            for i, (Ai, det_ai) in enumerate(
                zip(resultado.matrices_cramer, resultado.determinantes_cramer), start=1
            ):
                with st.expander(f"A{i} y det(A{i})"):
                    st.dataframe(dataframe_matriz(Ai))
                    detalle = next(
                        paso.get("pasos_determinante", [])
                        for paso in resultado.pasos
                        if paso.get("cramer") == i
                    )
                    _mostrar_eliminacion_determinante(detalle, decimales)
                    st.latex(
                        rf"x_{{{i}}}=\frac{{\det(A_{{{i}}})}}{{\det(A)}}="
                        rf"\frac{{{latex_numero(det_ai, decimales)}}}{{{latex_numero(resultado.determinante, decimales)}}}="
                        f"{latex_numero(resultado.x[i - 1], decimales)}"
                    )
        else:
            st.markdown("#### Factorización LU")
            if resultado.hubo_pivoteo:
                st.warning("Se aplicó pivoteo parcial; por eso la relación correcta es PA = LU.")
            else:
                st.info("No fue necesario intercambiar filas; la relación es A = LU.")
            cols = st.columns(3)
            for col, nombre, matriz in zip(cols, ("P", "L", "U"), (resultado.P, resultado.L, resultado.U)):
                mostrar_matriz(
                    col,
                    matriz,
                    nombre,
                    columnas_variables=False,
                    filas_ecuaciones=False,
                )
            _mostrar_pasos_factorizacion(resultado, decimales)
            st.latex(f"y={latex_matriz(resultado.y, decimales)}")

    with tabs[3]:
        for seccion in generar_explicacion(resultado, decimales):
            st.markdown(f"#### {seccion.titulo}")
            st.markdown(seccion.texto)
            for formula in seccion.formulas:
                st.latex(formula)
            if seccion.matrices:
                columnas = st.columns(min(3, len(seccion.matrices)))
                for columna, (nombre, matriz) in zip(columnas, seccion.matrices.items()):
                    columna.caption(nombre)
                    columna.dataframe(
                        dataframe_matriz(
                            matriz,
                            columnas_variables=nombre not in {"P", "L", "U"},
                            filas_ecuaciones=nombre not in {"P", "L", "U"},
                        )
                    )

    with tabs[4]:
        mostrar_comprobacion_detallada(resultado, decimales)

    with tabs[5]:
        mostrar_graficas(resultado)


def _mostrar_metodo_ampliado(metodo: str) -> None:
    """Panel introductorio para los métodos recuperados del temario.

    Los algoritmos viven en módulos puros y este panel ofrece un ejemplo
    reproducible sin reutilizar el editor de sistemas directos.
    """
    info = METODOS_UNIDAD_2[metodo]
    st.markdown('<div class="step-label">Unidad 2 · Tema recuperado</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="method-card"><h3>{info["icono"]} &nbsp;{metodo} '
        f'<span style="float:right;color:#2563eb;font-size:.78rem">{info["tipo"]}</span>'
        f'</h3><p>{info["descripcion"]}</p></div>', unsafe_allow_html=True,
    )
    st.latex(info["formula"])
    st.info("El cálculo numérico está disponible desde "
            "`unidades.unidad_2.metodos`; este panel conserva el flujo de la interfaz directa.")
    if metodo in {"Jacobi", "Gauss-Seidel"}:
        from .metodos.iterativos import resolver_gauss_seidel, resolver_jacobi
        A = np.array([[4.0, 1.0], [2.0, 3.0]])
        b = np.array([1.0, 2.0])
        resolver = resolver_jacobi if metodo == "Jacobi" else resolver_gauss_seidel
        resultado = resolver(A, b, tolerancia=1e-10, max_iter=100)
        st.caption(f"Ejemplo: {resultado.iteraciones} iteraciones · "
                   f"residuo ‖Ax−b‖∞ = {np.linalg.norm(A @ resultado.x - b, ord=np.inf):.3e}")
        st.dataframe(pd.DataFrame([resultado.x], columns=["x1", "x2"]))
    elif metodo == "Interpolación de Newton":
        from .metodos.interpolacion import evaluar_newton
        valor = evaluar_newton([0.0, 1.0, 2.0], [1.0, 3.0, 7.0], 1.5)
        st.caption(f"Ejemplo: P(1.5) = {valor:.6g}")
    elif metodo == "Regresión polinomial":
        from .metodos.regresion import regresion_polinomial
        resultado = regresion_polinomial([0, 1, 2], [1, 3, 7], 2)
        st.caption(f"Ejemplo: R² = {resultado.r2:.6f}")
    elif metodo == "Regresión lineal múltiple":
        from .metodos.regresion import regresion_lineal_multiple
        resultado = regresion_lineal_multiple([[1, 2], [2, 1], [3, 4]], [4, 5, 10])
        st.caption(f"Ejemplo: R² = {resultado.r2:.6f}")
    else:
        st.caption("Ejemplo disponible mediante las funciones puras del módulo de sistemas no lineales.")


def mostrar_unidad_2(metodo: str) -> None:
    """Renderiza el flujo completo de ingreso, solución y explicación."""

    if metodo == "Gauss-Seidel":
        _mostrar_tarjeta_metodo(metodo)
        mostrar_gauss_seidel()
        return
    if metodo in ("Jacobi", "Gauss-Seidel"):
        _mostrar_tarjeta_metodo(metodo)
        _mostrar_metodo_iterativo_lineal(metodo)
        return
    if metodo in ("Jacobi no lineal", "Gauss-Seidel no lineal", "Newton-Raphson para sistemas"):
        _mostrar_tarjeta_metodo(metodo)
        _mostrar_metodo_no_lineal(metodo)
        return
    if metodo == "Interpolación de Newton":
        _mostrar_tarjeta_metodo(metodo)
        _mostrar_interpolacion_newton()
        return
    if metodo in ("Regresión polinomial", "Regresión lineal múltiple"):
        _mostrar_tarjeta_metodo(metodo)
        _mostrar_regresion(metodo)
        return

    if metodo not in {"Matriz inversa", "Regla de Cramer", "Doolittle", "Crout"}:
        _mostrar_metodo_ampliado(metodo)
        return

    _inicializar_estado()
    st.markdown('<div class="step-label">Unidad 2 · Sistemas lineales</div>', unsafe_allow_html=True)
    st.subheader("Configure el sistema de ecuaciones")
    _mostrar_tarjeta_metodo(metodo)

    st.selectbox(
        "Número de incógnitas",
        list(range(2, 9)),
        key="u2_dimension",
        on_change=_cambiar_dimension,
        help="Se admiten sistemas cuadrados desde 2×2 hasta 8×8.",
    )

    with st.container(horizontal=True):
        st.button(
            "✨ Cargar ejemplo",
            key="u2_cargar_ejemplo",
            on_click=_cargar_ejemplo,
            args=(metodo,),
        )
        st.button("↻ Nuevo sistema", key="u2_nuevo_sistema", on_click=_nuevo_sistema)

    st.caption(st.session_state.get("u2_origen_ejemplo", ""))
    version = st.session_state.u2_editor_version
    n = int(st.session_state.u2_dimension)
    columnas_numericas = {
        f"x{i}": st.column_config.NumberColumn(f"x{i}", format="%.8g", required=True)
        for i in range(1, n + 1)
    }

    st.markdown("#### Matriz de coeficientes A")
    A_editada = st.data_editor(
        st.session_state.u2_A_base,
        key=f"u2_A_editor_{version}",
        num_rows="fixed",
        column_config=columnas_numericas,
        on_change=limpiar_resultado_unidad_2,
        width="stretch",
    )
    st.markdown("#### Vector de términos independientes b")
    b_editado = st.data_editor(
        st.session_state.u2_b_base,
        key=f"u2_b_editor_{version}",
        num_rows="fixed",
        column_config={"b": st.column_config.NumberColumn("b", format="%.8g", required=True)},
        on_change=limpiar_resultado_unidad_2,
        width="stretch",
    )

    try:
        A = A_editada.to_numpy(dtype=float)
        b = b_editado["b"].to_numpy(dtype=float)
        st.markdown("#### Sistema ingresado")
        _mostrar_sistema(A, b, 6)
    except (TypeError, ValueError):
        A = A_editada.to_numpy()
        b = b_editado["b"].to_numpy()
        st.warning("Complete todas las celdas con valores numéricos para visualizar el sistema.")

    st.caption(
        "Tolerancia numérica: 10⁻¹² multiplicado por max(1, ‖A‖∞). "
        "Los pivotes con magnitud menor o igual a ese valor se consideran numéricamente nulos."
    )

    if st.button("Resolver sistema", type="primary", width="stretch", key="u2_resolver"):
        try:
            st.session_state.u2_resultado = resolver_sistema(metodo, A, b)
            st.session_state.pop("u2_error", None)
        except ErrorSistemaLineal as exc:
            st.session_state.pop("u2_resultado", None)
            st.session_state.u2_error = str(exc)
        except Exception:
            st.session_state.pop("u2_resultado", None)
            st.session_state.u2_error = "No fue posible completar el cálculo por un error numérico inesperado."

    if st.session_state.get("u2_error"):
        st.error(st.session_state.u2_error)
    if st.session_state.get("u2_resultado") is not None:
        _mostrar_resultado(st.session_state.u2_resultado, 6)


__all__ = ["EJEMPLOS", "METODOS_UNIDAD_2", "limpiar_resultado_unidad_2", "mostrar_unidad_2"]
