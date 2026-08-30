import streamlit as st
import sympy as sp
import hashlib

from metodos.biseccion import biseccion
from metodos.regla_falsa import regla_falsa
from metodos.punto_fijo import punto_fijo
from metodos.newton_raphson import newton_raphson
from metodos.secante import secante
from utilidades.exportacion import crear_excel
from utilidades.graficas import crear_grafica
from utilidades.lector_imagen import extraer_funcion
from utilidades.parser_funciones import analizar_funcion, funcion_numerica, X
from utilidades.punto_fijo_ayuda import sugerir_despejes, evaluar_convergencia_local


def mejorar_encabezados_tabla(filas, metodo):
    """Renombra encabezados de tabla para hacerlos más comprensibles."""
    if not filas:
        return []
    
    mapeos = {
        "Bisección": {
            "i": "Iteración",
            "ai": "Extremo izquierdo",
            "bi": "Extremo derecho",
            "mi": "Aproximación",
            "f(ai)": "f(a)",
            "f(mi)": "f(aproximación)",
            "f(bi)": "f(b)",
            "Ea (%)": "Error (%)",
        },
        "Regla falsa": {
            "i": "Iteración",
            "ai": "Extremo izquierdo",
            "bi": "Extremo derecho",
            "mi": "Aproximación",
            "f(ai)": "f(a)",
            "f(mi)": "f(aproximación)",
            "f(bi)": "f(b)",
            "Ea (%)": "Error (%)",
        },
        "Newton-Raphson": {
            "i": "Iteración",
            "xi": "Valor actual",
            "f(xi)": "f(xi)",
            "f'(xi)": "f'(xi)",
            "xi+1": "Nueva aproximación",
            "Ea (%)": "Error (%)",
        },
        "Secante": {
            "i": "Iteración",
            "xi-1": "Valor anterior",
            "xi": "Valor actual",
            "f(xi-1)": "f(anterior)",
            "f(xi)": "f(actual)",
            "xi+1": "Nueva aproximación",
            "Ea (%)": "Error (%)",
        },
        "Punto fijo": {
            "i": "Iteración",
            "xi": "Valor actual",
            "g(xi)": "g(xi)",
            "Ea (%)": "Error (%)",
        },
    }
    
    mapeo = mapeos.get(metodo, {})
    
    filas_mejoradas = []
    for fila in filas:
        fila_nueva = {}
        for clave, valor in fila.items():
            nueva_clave = mapeo.get(clave, clave)
            fila_nueva[nueva_clave] = valor
        filas_mejoradas.append(fila_nueva)
    
    return filas_mejoradas

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


def calcular_hash_imagen(imagen_bytes):
    """Calcula el hash SHA-256 de los bytes de la imagen."""
    return hashlib.sha256(imagen_bytes).hexdigest()


def limpiar_estado_ocr():
    """Limpia el estado relacionado con OCR e imagen."""
    st.session_state.pop("imagen_hash", None)
    st.session_state.pop("texto_ocr", None)
    st.session_state.pop("imagen_confirmada", None)


def limpiar_funcion_manual():
    """Limpia el estado cuando se cambia de modo manual a imagen."""
    st.session_state.pop("funcion_input", None)
    limpiar_estado_ocr()


def callback_cambiar_origen():
    """Callback cuando se cambia entre modos de entrada."""
    origen_actual = st.session_state.get("origen_selector")
    origen_anterior = st.session_state.get("origen_anterior", None)
    
    if origen_anterior is None:
        # Primera vez que se carga
        st.session_state.origen_anterior = origen_actual
        if origen_actual == "Subir una imagen":
            st.session_state.pop("funcion_input", None)
        return
    
    if origen_anterior != origen_actual:
        # Cambio de modo detectado
        if origen_actual == "Subir una imagen":
            # Cambiar a modo imagen: limpiar manual
            st.session_state.pop("funcion_input", None)
            limpiar_estado_ocr()
        else:
            # Cambiar a modo manual: limpiar OCR
            limpiar_estado_ocr()
        
        st.session_state.origen_anterior = origen_actual


def limpiar():
    """Limpia todos los estados: resultado, imagen y confirmación."""
    for clave in ("resultado", "expresion", "funcion_input", "imagen_hash", 
                  "imagen_confirmada", "texto_ocr", "error_ocr"):
        st.session_state.pop(clave, None)


st.markdown('<div class="hero"><h1>Software de Métodos Numéricos</h1><p>Laboratorio universitario para aproximar raíces, estudiar iteraciones y exportar resultados.</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Configuración")
    metodo = st.selectbox("Método numérico", ["Bisección", "Regla falsa", "Punto fijo", "Newton-Raphson", "Secante"])
    
    # Selector de criterio de parada
    criterio_parada = st.radio("Detener cálculo por:", ["Error porcentual permitido", "Número fijo de iteraciones"], horizontal=True)
    
    if criterio_parada == "Error porcentual permitido":
        error_permitido = st.number_input("Error permitido (%)", min_value=0.000001, value=1.0, step=0.01, format="%.6f")
        max_iteraciones = st.number_input("Máximo de iteraciones (seguridad)", min_value=1, value=100, step=1)
    else:
        max_iteraciones = st.number_input("Número de iteraciones", min_value=1, value=4, step=1)
        error_permitido = 0.0  # No se usa con criterio de iteraciones
    
    decimales = st.select_slider("Decimales para visualizar", options=[4, 6, 8, 10], value=6)
    st.divider()
    st.caption("Los cálculos se realizan con precisión completa. El redondeo solo se aplica a la presentación.")

st.subheader("1. Ingreso del ejercicio")
origen = st.radio(
    "Origen de la función", 
    ["Escribir función manualmente", "Subir una imagen"], 
    horizontal=True,
    key="origen_selector",
    on_change=callback_cambiar_origen
)

imagen_confirmada = True

# ============================================================================
# SECCIÓN 1: MODO IMAGEN
# ============================================================================
if origen == "Subir una imagen":
    imagen = st.file_uploader("Cargue una imagen PNG, JPG o JPEG", type=["png", "jpg", "jpeg"])
    
    if imagen:
        # Calcular hash SHA-256 de la imagen
        imagen_bytes = imagen.read()
        imagen.seek(0)  # Reiniciar el puntero para poder leerla de nuevo
        imagen_hash_nuevo = calcular_hash_imagen(imagen_bytes)
        imagen_hash_anterior = st.session_state.get("imagen_hash")
        
        # Mostrar vista previa
        st.image(imagen, caption="Vista previa", width=420)
        
        # Si cambió la imagen, ejecutar OCR nuevamente
        if imagen_hash_nuevo != imagen_hash_anterior:
            # Limpiar estado anterior
            st.session_state.pop("funcion_input", None)
            st.session_state.pop("imagen_confirmada", None)
            st.session_state.pop("error_ocr", None)
            
            # Ejecutar OCR
            texto_detectado, mensaje_ocr = extraer_funcion(imagen)
            st.session_state.imagen_hash = imagen_hash_nuevo
            st.session_state.texto_ocr = texto_detectado
            
            # Guardar mensaje para mostrar
            if texto_detectado:
                st.session_state["funcion_input"] = texto_detectado
                st.info(mensaje_ocr)
            else:
                st.session_state.pop("funcion_input", None)
                st.session_state["error_ocr"] = mensaje_ocr
                st.warning(mensaje_ocr)
        else:
            # Imagen no cambió, mostrar estado anterior
            if "error_ocr" in st.session_state:
                st.warning(st.session_state["error_ocr"])
            elif st.session_state.get("funcion_input"):
                st.info("Función detectada automáticamente. Revísela y confirme.")
    else:
        # No hay imagen cargada
        st.session_state.pop("funcion_input", None)
        limpiar_estado_ocr()
        st.info("Suba una imagen para detectar la función.")
    
    # Campo de entrada de función (se llena automáticamente si hay OCR)
    funcion_texto = st.text_input(
        "f(x)",
        key="funcion_input",
        placeholder="Se llenará automáticamente al cargar una imagen",
        help="Ejemplos: 2x+5, sen(x), ln(x), x^3+2*x^2+10*x-20"
    )
    
    # Checkbox de confirmación (solo si hay imagen)
    if imagen:
        imagen_confirmada = st.checkbox(
            "Confirmo que la función es correcta o ya la corregí",
            key="imagen_confirmada"
        )

# ============================================================================
# SECCIÓN 2: MODO MANUAL
# ============================================================================
else:
    # Modo manual: limpiar OCR
    limpiar_estado_ocr()
    
    funcion_texto = st.text_input(
        "f(x)",
        key="funcion_input",
        placeholder="Ej: 2*x+5, sin(x), ln(x), x**3-2*x+1",
        help="Ejemplos: 2x+5, sen(x), ln(x), x^3+2*x^2+10*x-20"
    )

# ============================================================================
# ANÁLISIS DE LA FUNCIÓN (común para ambos modos)
# ============================================================================
try:
    if funcion_texto.strip():
        expresion = analizar_funcion(funcion_texto)
        st.session_state.expresion = expresion
        st.latex(f"f(x) = {sp.latex(expresion)}")
    else:
        expresion = None
        st.session_state.pop("expresion", None)
except ValueError as error:
    expresion = None
    st.session_state.pop("expresion", None)
    st.warning(str(error))

parametros = {}
if metodo in ("Bisección", "Regla falsa"):
    col_a, col_b = st.columns(2)
    parametros["a"] = col_a.number_input("Extremo inferior (a)", value=0.0, format="%.10f")
    parametros["b"] = col_b.number_input("Extremo superior (b)", value=1.0, format="%.10f")
elif metodo == "Punto fijo":
    st.info("**Punto Fijo**: Para usar este método, debe despejar la ecuación f(x)=0 en la forma x = g(x).")
    
    # Mostrar sugerencias
    if expresion is not None:
        with st.expander("💡 Sugerencias de despejes"):
            sugerencias = sugerir_despejes(funcion_texto)
            for titulo, desc in sugerencias:
                st.caption(f"**{titulo}**: {desc}")
    
    despeje_texto = st.text_input("Despeje g(x)", value="20/(x^2+2*x+10)", help="Ejemplo: 1-sin(x), (4-log(x))/2")
    parametros["x0"] = st.number_input("Valor inicial (x0)", value=1.5, format="%.10f")
    
    try:
        despeje = analizar_funcion(despeje_texto)
        parametros["despeje"] = despeje
        
        # Evaluación del criterio de convergencia
        converge, criterio, mensaje = evaluar_convergencia_local(despeje, parametros["x0"])
        
        # Mostrar derivada
        derivada_g = sp.diff(despeje, X)
        st.latex(f"g'(x) = {sp.latex(derivada_g)}")
        
        # Mostrar resultado del criterio
        if converge is not None:
            (st.success if converge else st.warning)(mensaje)
        else:
            st.warning(mensaje)
    
    except (ValueError, TypeError, ZeroDivisionError) as e:
        parametros["despeje"] = None
        st.warning(f"El despeje g(x) no es válido: {str(e)}")
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
    elif criterio_parada == "Error porcentual permitido" and error_permitido <= 0:
        st.error("El error permitido debe ser mayor que cero.")
    elif criterio_parada == "Número fijo de iteraciones" and max_iteraciones <= 0:
        st.error("El número de iteraciones debe ser un entero positivo.")
    else:
        try:
            funcion = funcion_numerica(expresion)
            
            # Preparar parámetros según criterio de parada
            if criterio_parada == "Error porcentual permitido":
                metodo_criterio = "error"
                metodo_kwargs = {
                    "error_permitido": error_permitido,
                    "max_iteraciones": max_iteraciones,
                    "criterio": "error"
                }
            else:
                metodo_criterio = "fijo"
                metodo_kwargs = {
                    "error_permitido": None,
                    "max_iteraciones": None,
                    "criterio": "fijo",
                    "iteraciones_fijas": max_iteraciones
                }
            
            if metodo == "Bisección":
                resultado = biseccion(funcion, parametros["a"], parametros["b"], **metodo_kwargs)
            elif metodo == "Regla falsa":
                resultado = regla_falsa(funcion, parametros["a"], parametros["b"], **metodo_kwargs)
            elif metodo == "Punto fijo":
                if parametros.get("despeje") is None:
                    raise ValueError("Corrija el despeje g(x) antes de resolver.")
                resultado = punto_fijo(funcion, funcion_numerica(parametros["despeje"]), parametros["x0"], **metodo_kwargs)
            elif metodo == "Newton-Raphson":
                resultado = newton_raphson(funcion, funcion_numerica(parametros["derivada"]), parametros["x0"], **metodo_kwargs)
            else:
                resultado = secante(funcion, parametros["x0"], parametros["x1"], **metodo_kwargs)
            st.session_state.resultado = resultado
            st.session_state.parametros_resultado = parametros
            st.session_state.metodo_resultado = metodo
            st.session_state.criterio_parada = criterio_parada
        except ValueError as error:
            st.error(str(error))
        except Exception as exc:
            st.error(f"No fue posible completar el cálculo. Revise los valores y el dominio de la función.")
            print(f"Error interno: {exc}", flush=True)

if "resultado" in st.session_state:
    resultado = st.session_state.resultado
    st.subheader("2. Resultados")
    tarjetas = st.columns(4)
    tarjetas[0].metric("Raíz aproximada", f"{resultado.raiz:.{decimales}f}")
    tarjetas[1].metric("Error final (%)", f"{resultado.error_final:.{decimales}f}")
    tarjetas[2].metric("Iteraciones", len(resultado.iteraciones))
    tarjetas[3].metric("Estado", "Convergió ✓" if resultado.convergio else "No convergió ✗")
    (st.success if resultado.convergio else st.warning)(resultado.motivo)
    st.caption(f"Método: {st.session_state.metodo_resultado} | Función: {funcion_texto} | Criterio: {st.session_state.get('criterio_parada', 'Tolerancia')}")
    
    filas = resultado.iteraciones
    filas_mejoradas = mejorar_encabezados_tabla(filas, st.session_state.metodo_resultado)
    
    if filas_mejoradas:
        # Aplicar redondeo a valores numéricos
        filas_redondeadas = []
        for fila in filas_mejoradas:
            fila_redonda = {}
            for clave, valor in fila.items():
                if isinstance(valor, float) and valor == valor and abs(valor) != float("inf"):
                    fila_redonda[clave] = round(valor, decimales)
                else:
                    fila_redonda[clave] = valor
            filas_redondeadas.append(fila_redonda)
        
        st.dataframe(filas_redondeadas, use_container_width=True, hide_index=True)
        
        # Explicación desplegable
        with st.expander("¿Qué significa cada columna?"):
            explicaciones = {
                "Iteración": "Número secuencial de la iteración.",
                "Extremo izquierdo": "Valor del extremo izquierdo del intervalo.",
                "Extremo derecho": "Valor del extremo derecho del intervalo.",
                "Aproximación": "Punto medio o aproximación de la raíz en esta iteración.",
                "f(a)": "Valor de f en el extremo izquierdo.",
                "f(b)": "Valor de f en el extremo derecho.",
                "f(aproximación)": "Valor de f en la aproximación.",
                "Valor actual": "Valor actual de x.",
                "Valor anterior": "Valor anterior de x.",
                "f(xi)": "Valor de la función en el punto actual.",
                "f'(xi)": "Valor de la derivada en el punto actual.",
                "Nueva aproximación": "Siguiente valor de x calculado por el método.",
                "g(xi)": "Valor de g(x) en el punto actual.",
                "Error (%)": "Error porcentual aproximado, calculado como |x_nuevo - x_anterior| / |x_nuevo| * 100.",
            }
            
            for titulo, desc in explicaciones.items():
                if any(titulo in str(col) for col in filas_redondeadas[0].keys() if filas_redondeadas):
                    st.caption(f"**{titulo}**: {desc}")
    
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
    col_grafica_auto, col_grafica_manual = st.columns([3, 1])
    with col_grafica_manual:
        rango_personalizado = st.checkbox("Rango personalizado")
    limites = rango_defecto
    if rango_personalizado:
        col_min, col_max = st.columns(2)
        limites = (col_min.number_input("Mínimo del eje x", value=float(rango_defecto[0])), col_max.number_input("Máximo del eje x", value=float(rango_defecto[1])))
    
    try:
        st.plotly_chart(crear_grafica(expresion, raiz, limites, puntos), use_container_width=True)
        st.caption("La raíz se encuentra donde la curva azul cruza el eje x (y=0). El punto rojo marca la aproximación obtenida.")
    except ValueError as error:
        st.error(str(error))
    
    st.subheader("4. Exportación")
    try:
        archivo = crear_excel("Software de Métodos Numéricos", funcion_texto, st.session_state.metodo_resultado, str(parametros_grafica), error_permitido if criterio_parada == "Error porcentual permitido" else max_iteraciones, raiz, resultado.error_final, filas)
        st.download_button("📥 Descargar resultados en Excel", archivo, "resultado_metodos_numericos.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    except Exception as exc:
        st.error(f"Ocurrió un error al preparar el archivo Excel.")
        print(f"Error de exportación: {exc}", flush=True)
