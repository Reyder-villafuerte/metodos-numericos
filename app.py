import streamlit as st
import sympy as sp

from metodos.biseccion import biseccion
from metodos.regla_falsa import regla_falsa
from metodos.punto_fijo import punto_fijo
from metodos.newton_raphson import newton_raphson
from metodos.secante import secante
from utilidades.exportacion import crear_excel
from utilidades.graficas import crear_grafica
from utilidades.lector_imagen import extraer_funcion
from utilidades.parser_funciones import analizar_funcion, funcion_numerica, X

st.set_page_config(page_title="Software de Métodos Numéricos", page_icon="∑", layout="wide")
st.markdown("""
<style>
.main { background: #f8fafc; }
.block-container { max-width: 1250px; padding-top: 2rem; }
.hero { background: linear-gradient(120deg, #0f172a, #1e3a5f); color: white; padding: 2rem 2.3rem; border-radius: 14px; margin-bottom: 1.5rem; }
.hero h1 { margin: 0; font-size: 2.25rem; }
.hero p { color: #cbd5e1; margin-bottom: 0; }
</style>
""", unsafe_allow_html=True)


def limpiar():
    for clave in ("resultado", "expresion", "funcion_texto", "imagen_confirmada"):
        st.session_state.pop(clave, None)


st.markdown('<div class="hero"><h1>Software de Métodos Numéricos</h1><p>Laboratorio universitario para aproximar raíces, estudiar iteraciones y exportar resultados.</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Configuración")
    metodo = st.selectbox("Método numérico", ["Bisección", "Regla falsa", "Punto fijo", "Newton-Raphson", "Secante"])
    error_permitido = st.number_input("Error porcentual permitido", min_value=0.000001, value=0.01, step=0.01, format="%.6f")
    max_iteraciones = st.number_input("Máximo de iteraciones", min_value=1, value=100, step=1)
    decimales = st.select_slider("Decimales para visualizar", options=[4, 6, 8, 10], value=6)
    st.divider()
    st.caption("Los cálculos se realizan con precisión completa. El redondeo solo se aplica a la presentación.")

st.subheader("1. Ingreso del ejercicio")
origen = st.radio("Origen de la función", ["Escribir función manualmente", "Subir una imagen"], horizontal=True)
imagen_confirmada = True
if origen == "Subir una imagen":
    imagen = st.file_uploader("Cargue una imagen PNG, JPG o JPEG", type=["png", "jpg", "jpeg"])
    if imagen:
        st.image(imagen, caption="Vista previa", width=420)
        texto_detectado, mensaje_ocr = extraer_funcion(imagen)
        st.info(mensaje_ocr)
        if texto_detectado and "funcion_texto" not in st.session_state:
            st.session_state.funcion_texto = texto_detectado
        imagen_confirmada = st.checkbox("Confirmo que la función es correcta o ya la corregí", key="imagen_confirmada")

funcion_texto = st.text_input("f(x)", value=st.session_state.get("funcion_texto", "exp(-x)-x"), help="Ejemplos: 2x+5, sen(x), ln(x), x^3+2*x^2+10*x-20")
st.session_state.funcion_texto = funcion_texto
try:
    expresion = analizar_funcion(funcion_texto)
    st.session_state.expresion = expresion
    st.latex(f"f(x) = {sp.latex(expresion)}")
except ValueError as error:
    expresion = None
    st.warning(str(error))

parametros = {}
if metodo in ("Bisección", "Regla falsa"):
    col_a, col_b = st.columns(2)
    parametros["a"] = col_a.number_input("Extremo inferior (a)", value=0.0, format="%.10f")
    parametros["b"] = col_b.number_input("Extremo superior (b)", value=1.0, format="%.10f")
elif metodo == "Punto fijo":
    despeje_texto = st.text_input("Despeje g(x)", value="20/(x^2+2*x+10)")
    parametros["x0"] = st.number_input("Valor inicial (x0)", value=1.5, format="%.10f")
    try:
        despeje = analizar_funcion(despeje_texto)
        parametros["despeje"] = despeje
        derivada_g = sp.diff(despeje, X)
        criterio = abs(float(derivada_g.subs(X, parametros["x0"]).evalf()))
        st.latex(f"g'(x) = {sp.latex(derivada_g)}")
        (st.success if criterio < 1 else st.warning)(f"Criterio |g'(x0)| = {criterio:.6g}: " + ("se cumple; se espera convergencia local." if criterio < 1 else "no se cumple; podría divergir."))
    except (ValueError, TypeError, ZeroDivisionError):
        parametros["despeje"] = None
        st.warning("El despeje g(x) no es válido o no puede evaluarse en x0.")
elif metodo == "Newton-Raphson":
    parametros["x0"] = st.number_input("Valor inicial (x0)", value=0.5, format="%.10f")
    derivada = sp.diff(expresion, X) if expresion is not None else None
    if derivada is not None:
        parametros["derivada"] = derivada
        st.latex(f"f'(x) = {sp.latex(derivada)}")
else:
    col_x0, col_x1 = st.columns(2)
    parametros["x0"] = col_x0.number_input("Primer valor inicial (x0)", value=0.0, format="%.10f")
    parametros["x1"] = col_x1.number_input("Segundo valor inicial (x1)", value=1.0, format="%.10f")

resolver, limpiar_boton = st.columns([1, 1])
if limpiar_boton.button("Limpiar", use_container_width=True):
    limpiar()
    st.rerun()
if resolver.button("Resolver", type="primary", use_container_width=True):
    if expresion is None:
        st.error("Corrija la función antes de resolver.")
    elif origen == "Subir una imagen" and not imagen_confirmada:
        st.error("Confirme o corrija la función detectada antes de resolver.")
    elif error_permitido <= 0 or max_iteraciones <= 0:
        st.error("El error permitido y el máximo de iteraciones deben ser positivos.")
    else:
        try:
            funcion = funcion_numerica(expresion)
            if metodo == "Bisección":
                resultado = biseccion(funcion, parametros["a"], parametros["b"], error_permitido, max_iteraciones)
            elif metodo == "Regla falsa":
                resultado = regla_falsa(funcion, parametros["a"], parametros["b"], error_permitido, max_iteraciones)
            elif metodo == "Punto fijo":
                if parametros.get("despeje") is None:
                    raise ValueError("Corrija el despeje g(x) antes de resolver.")
                resultado = punto_fijo(funcion, funcion_numerica(parametros["despeje"]), parametros["x0"], error_permitido, max_iteraciones)
            elif metodo == "Newton-Raphson":
                resultado = newton_raphson(funcion, funcion_numerica(parametros["derivada"]), parametros["x0"], error_permitido, max_iteraciones)
            else:
                resultado = secante(funcion, parametros["x0"], parametros["x1"], error_permitido, max_iteraciones)
            st.session_state.resultado = resultado
            st.session_state.parametros_resultado = parametros
            st.session_state.metodo_resultado = metodo
        except ValueError as error:
            st.error(str(error))
        except Exception:
            st.error("No fue posible completar el cálculo. Revise los valores y el dominio de la función.")

if "resultado" in st.session_state:
    resultado = st.session_state.resultado
    st.subheader("2. Resultados")
    tarjetas = st.columns(4)
    tarjetas[0].metric("Raíz aproximada", f"{resultado.raiz:.{decimales}f}")
    tarjetas[1].metric("Error final (%)", f"{resultado.error_final:.{decimales}f}")
    tarjetas[2].metric("Iteraciones", len(resultado.iteraciones))
    tarjetas[3].metric("Estado", "Convergió" if resultado.convergio else "No convergió")
    (st.success if resultado.convergio else st.warning)(resultado.motivo)
    st.caption(f"Método: {st.session_state.metodo_resultado} | Función: {funcion_texto}")
    filas = resultado.iteraciones
    if filas:
        st.dataframe([{clave: (round(valor, decimales) if isinstance(valor, float) and valor == valor and abs(valor) != float("inf") else valor) for clave, valor in fila.items()} for fila in filas], use_container_width=True, hide_index=True)
    raiz = resultado.raiz
    parametros_grafica = st.session_state.parametros_resultado
    puntos = []
    if "a" in parametros_grafica:
        puntos = [parametros_grafica["a"], parametros_grafica["b"]]
        rango_defecto = (min(puntos + [raiz]) - 0.5, max(puntos + [raiz]) + 0.5)
    else:
        puntos = [parametros_grafica.get("x0", raiz)] + ([parametros_grafica["x1"]] if "x1" in parametros_grafica else [])
        rango_defecto = (min(puntos + [raiz]) - 2, max(puntos + [raiz]) + 2)
    st.subheader("3. Gráfica")
    rango_personalizado = st.checkbox("Indicar rango personalizado")
    limites = rango_defecto
    if rango_personalizado:
        col_min, col_max = st.columns(2)
        limites = (col_min.number_input("Mínimo del eje x", value=float(rango_defecto[0])), col_max.number_input("Máximo del eje x", value=float(rango_defecto[1])))
    try:
        st.plotly_chart(crear_grafica(expresion, raiz, limites, puntos), use_container_width=True)
    except ValueError as error:
        st.error(str(error))
    st.subheader("4. Exportación")
    try:
        archivo = crear_excel("Software de Métodos Numéricos", funcion_texto, st.session_state.metodo_resultado, str(parametros_grafica), error_permitido, raiz, resultado.error_final, filas)
        st.download_button("Descargar resultados en Excel", archivo, "resultado_metodos_numericos.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except Exception:
        st.error("Ocurrió un error al preparar el archivo Excel.")
