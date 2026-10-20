import streamlit as st

import sympy as sp

import hashlib

import logging

from time import perf_counter

import pandas as pd



from unidades.unidad_1.metodos import biseccion

from unidades.unidad_1.metodos import regla_falsa

from unidades.unidad_1.metodos import punto_fijo

from unidades.unidad_1.metodos import newton_raphson

from unidades.unidad_1.metodos import secante

from unidades.unidad_1.metodos import muller

from utilidades.exportacion import crear_excel

from utilidades.exportacion_pdf import crear_pdf

from unidades.unidad_1.explicaciones import generar_explicacion

from unidades.unidad_2.interfaz import limpiar_resultado_unidad_2, mostrar_unidad_2

from utilidades.graficas import crear_grafica, crear_grafica_compleja, crear_grafica_con_tangente

from utilidades.lector_imagen import extraer_funcion

from utilidades.parser_funciones import analizar_funcion, funcion_numerica, funcion_numerica_compleja, X

from utilidades.punto_fijo_ayuda import sugerir_despejes, evaluar_convergencia_local

from componentes.catalogo import (
    METODOS,
    UNIDADES,
    cargar_ejemplo_en_estado,
    obtener_metodos_por_unidad,
)

from componentes.interfaz import (

    aplicar_estilo,

    crear_csv,

    formatear_numero,

    mostrar_encabezado,

    mostrar_explicaciones,

    mostrar_metodo,

    preparar_filas,

    registrar_historial,

    texto_conclusion,

)





logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

LOGGER = logging.getLogger("metodos_numericos")



st.set_page_config(page_title="Métodos Numéricos | Laboratorio", page_icon="∑", layout="wide", initial_sidebar_state="expanded")

aplicar_estilo()





def calcular_hash_imagen(imagen_bytes):

    """Calcula el hash SHA-256 de los bytes de la imagen."""

    return hashlib.sha256(imagen_bytes).hexdigest()





def limpiar_resultado():

    """Descarta resultados que ya no corresponden al método seleccionado."""

    for clave in ("resultado", "parametros_resultado", "metodo_resultado",

                  "criterio_resultado", "valor_criterio_resultado",

                  "funcion_resultado", "expresion_resultado",

                  "residuo_resultado", "tiempo_resultado"):

        st.session_state.pop(clave, None)





def limpiar_estado_ocr():

    """Limpia el estado relacionado con OCR e imagen."""

    st.session_state.pop("imagen_hash", None)

    st.session_state.pop("texto_ocr", None)

    st.session_state.pop("imagen_confirmada", None)

    st.session_state.pop("ocr_confianza", None)





# Mensajes educativos de validación de la función. El usuario solo debe ver

# estos textos; el detalle técnico de cualquier error se registra en el log.

MENSAJE_FUNCION_VALIDA = "✅ Función válida. Puedes continuar con el cálculo."

MENSAJE_FUNCION_INVALIDA = (

    "⚠️ La función está mal escrita o no pudo interpretarse. "

    "Revisa los exponentes, multiplicaciones, paréntesis y nombres "

    "de las funciones antes de continuar."

)

MENSAJE_OCR_POSIBLES_ERRORES = (

    "⚠️ La fórmula detectada podría contener errores. "

    "Revisa especialmente los exponentes y signos."

)



EJEMPLOS_ESCRITURA = [

    ("Potencia", "x^3"),

    ("Multiplicación", "3*x"),

    ("Seno", "sin(x)"),

    ("Exponencial", "exp(x)"),

    ("Logaritmo natural", "log(x)"),

    ("Raíz cuadrada", "sqrt(x)"),

]





def mostrar_ejemplos_escritura():

    """Muestra ejemplos de escritura correcta para orientar al usuario."""

    with st.expander("✏️ Ejemplos de escritura correcta"):

        for nombre, ejemplo in EJEMPLOS_ESCRITURA:

            st.markdown(f"- **{nombre}:** `{ejemplo}`")





def mostrar_validacion_ocr():

    """Advierte cuando la función viene de una imagen con reconocimiento dudoso."""

    if (

        st.session_state.get("ocr_confianza") in ("baja", "media")

        and st.session_state.get("texto_ocr")

    ):

        st.warning(MENSAJE_OCR_POSIBLES_ERRORES)





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





def sugerir_x0(expresion, derivada):

    """Busca un cambio de signo de f(x) en [-10, 10] y sugiere x0 = (a+b)/2.



    Antes de aceptar el valor, comprueba que la derivada en x0 sea distinta

    de cero. Si no encuentra un cambio de signo, muestra una advertencia y

    permite que el usuario ingrese x0 manualmente.

    """

    evalar = funcion_numerica(expresion)

    evalar_der = funcion_numerica(derivada)



    a_ini, b_ini = -10.0, 10.0

    PUNTOS = 10000

    paso = (b_ini - a_ini) / PUNTOS



    valores = []

    for i in range(PUNTOS + 1):

        x = a_ini + i * paso

        try:

            valores.append((x, evalar(x)))

        except ValueError:

            valores.append(None)



    primera_f = None

    for idx, v in enumerate(valores):

        if v is None:

            continue

        f_act = v[1]

        if primera_f is None:

            primera_f = f_act

            continue

        if primera_f == 0 or f_act == 0 or (primera_f < 0) != (f_act < 0):

            a = valores[idx - 1][0]

            b = v[0]

            x0_sugerido = (a + b) / 2

            try:

                df_x0 = evalar_der(x0_sugerido)

            except ValueError:

                df_x0 = None

            if df_x0 is not None and df_x0 != 0:

                st.session_state["newton_x0"] = x0_sugerido

                st.success(f"Se encontró una raíz entre a = {a:.2f} y b = {b:.2f}. Valor inicial sugerido: x0 = {x0_sugerido:.4f}.")

                st.rerun()

            else:

                st.warning(f"Se encontró un cambio de signo entre a = {a:.2f} y b = {b:.2f}, pero la derivada en el punto medio es cero o no es evaluable en el dominio. Ingrese x0 manualmente.")

            return

        primera_f = f_act



    st.warning("No se encontró un cambio de signo en el intervalo de -10 a 10. Ingrese el valor inicial x0 manualmente.")





def limpiar():

    """Limpia todos los estados: resultado, imagen y confirmación."""

    for clave in ("resultado", "expresion", "funcion_input", "imagen_hash",

                  "imagen_confirmada", "texto_ocr", "error_ocr",

                  "parametros_resultado", "metodo_resultado",

                  "criterio_resultado", "valor_criterio_resultado",

                  "funcion_resultado", "expresion_resultado",

                  "residuo_resultado", "tiempo_resultado"):

        st.session_state.pop(clave, None)

    for clave in ("intervalo_a", "intervalo_b", "punto_fijo_x0", "despeje_input",

                  "newton_x0", "secante_x0", "secante_x1", "muller_x0",

                  "muller_x1", "muller_x2"):

        st.session_state.pop(clave, None)





def callback_cambiar_unidad():

    """Limpia el ejercicio cuando el usuario navega a otra unidad."""

    unidad_actual = st.session_state.get("unidad_selector")

    unidad_anterior = st.session_state.get("unidad_anterior")

    if unidad_actual != unidad_anterior:

        limpiar()

        limpiar_resultado_unidad_2()

        st.session_state.unidad_anterior = unidad_actual




mostrar_encabezado()



titulos_unidades = [unidad["titulo"] for unidad in UNIDADES.values()]

unidad_por_titulo = {

    unidad["titulo"]: unidad_id for unidad_id, unidad in UNIDADES.items()

}

st.session_state.setdefault("unidad_selector", UNIDADES["unidad_1"]["titulo"])

st.session_state.setdefault("unidad_anterior", st.session_state.unidad_selector)



with st.sidebar:

    st.caption("CONFIGURACIÓN DEL EJERCICIO")

    unidad_titulo = st.selectbox(

        "Seleccionar unidad",

        titulos_unidades,

        key="unidad_selector",

        on_change=callback_cambiar_unidad,

    )

    unidad_id = unidad_por_titulo[unidad_titulo]

    if unidad_id == "unidad_1":

        metodo = st.selectbox(

            "Método numérico",

            obtener_metodos_por_unidad(unidad_id),

            key="metodo_selector",

            on_change=limpiar_resultado,

        )

        # Selector de criterio de parada

        criterio_parada = st.radio("Detener cálculo por:", ["Error porcentual permitido", "Número fijo de iteraciones"], horizontal=True, key="criterio_selector", on_change=limpiar_resultado)

        if criterio_parada == "Error porcentual permitido":

            error_permitido = st.number_input("Error permitido (%)", min_value=0.000001, value=1.0, step=0.01, format="%.6f", on_change=limpiar_resultado)

            max_iteraciones = st.number_input("Máximo de iteraciones (seguridad)", min_value=1, max_value=10000, value=100, step=1, on_change=limpiar_resultado)

        else:

            max_iteraciones = st.number_input("Número de iteraciones", min_value=1, max_value=10000, value=4, step=1, on_change=limpiar_resultado)

            error_permitido = 0.0  # No se usa con criterio de iteraciones

        if max_iteraciones > 1000:

            st.warning("Una cantidad elevada de iteraciones puede afectar el tiempo de respuesta y el tamaño de los reportes.")

        decimales = st.select_slider("Decimales para visualizar", options=[4, 6, 8, 10], value=6)

        st.divider()

        st.caption("Los cálculos se realizan con precisión completa. El redondeo solo se aplica a la presentación.")

        if st.session_state.get("historial_ejercicios"):

            with st.expander("🕘 Historial de la sesión"):

                for item in st.session_state.historial_ejercicios[:5]:

                    st.markdown(f"**{item['metodo']}** · `{item['raiz']}`  \n{item['fecha']}")

    else:

        metodo_unidad_2 = st.selectbox(

            "Método numérico",

            obtener_metodos_por_unidad(unidad_id),

            key="metodo_u2_selector",

            on_change=limpiar_resultado_unidad_2,

        )



if unidad_id == "unidad_2":

    mostrar_unidad_2(metodo_unidad_2)

    st.stop()



st.markdown('<div class="step-label">Paso 1 · Preparación</div>', unsafe_allow_html=True)

st.subheader("Configure el ejercicio")

mostrar_metodo(METODOS[metodo], metodo)

col_ejemplo, col_nuevo = st.columns([1, 1])

if col_ejemplo.button("✨ Cargar ejemplo recomendado", width="stretch"):

    cargar_ejemplo_en_estado(st.session_state, metodo)

    limpiar_resultado()

    st.rerun()

if col_nuevo.button("↻ Nuevo ejercicio", width="stretch"):

    limpiar()

    st.rerun()

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

    if imagen and imagen.size > 10 * 1024 * 1024:

        st.error("La imagen supera el límite de 10 MB. Redúzcala antes de continuar.")

        imagen = None



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

            # Limpiar estado anterior (no conservar resultados del ejercicio previo)

            st.session_state.pop("funcion_input", None)

            st.session_state.pop("imagen_confirmada", None)

            st.session_state.pop("error_ocr", None)

            st.session_state.pop("ocr_confianza", None)

            limpiar_resultado()

            

            # Ejecutar OCR

            texto_detectado, mensaje_ocr, confianza_ocr = extraer_funcion(imagen)

            st.session_state.imagen_hash = imagen_hash_nuevo

            st.session_state.texto_ocr = texto_detectado

            

            # Guardar mensaje para mostrar

            if texto_detectado:

                st.session_state["funcion_input"] = texto_detectado

                st.session_state["ocr_confianza"] = confianza_ocr

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

        help="Ejemplos: 2x+5, sen(x), ln(x), x^3+2*x^2+10*x-20",

        on_change=limpiar_resultado,

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

        help="Ejemplos: 2x+5, sen(x), ln(x), x^3+2*x^2+10*x-20",

        on_change=limpiar_resultado,

    )



# ============================================================================

# ANÁLISIS DE LA FUNCIÓN (común para ambos modos)

# ============================================================================

expresion = None

funcion_es_de_imagen = origen == "Subir una imagen"



if funcion_texto.strip():

    try:

        expresion = analizar_funcion(funcion_texto)

        st.session_state.expresion = expresion

        st.latex(f"f(x) = {sp.latex(expresion)}")

        st.success(MENSAJE_FUNCION_VALIDA)

        mostrar_validacion_ocr()

    except Exception as error:

        # Nunca mostrar el detalle técnico al usuario; solo se registra aquí.

        LOGGER.warning(

            "Función no válida ingresada: %r (%s: %s)",

            funcion_texto,

            type(error).__name__,

            error,

        )

        expresion = None

        st.session_state.pop("expresion", None)

        # No conservar resultados del ejercicio anterior mientras la

        # función sea inválida.

        limpiar_resultado()

        st.warning(MENSAJE_FUNCION_INVALIDA)

        mostrar_ejemplos_escritura()

        mostrar_validacion_ocr()

else:

    st.session_state.pop("expresion", None)

    limpiar_resultado()

    if funcion_es_de_imagen and st.session_state.get("ocr_confianza") == "baja":

        st.warning(MENSAJE_OCR_POSIBLES_ERRORES)



parametros = {}

if metodo in ("Bisección", "Regla falsa"):

    col_a, col_b = st.columns(2)

    st.session_state.setdefault("intervalo_a", 0.0)

    st.session_state.setdefault("intervalo_b", 1.0)

    parametros["a"] = col_a.number_input("Extremo inferior (a)", format="%.10f", key="intervalo_a", on_change=limpiar_resultado)

    parametros["b"] = col_b.number_input("Extremo superior (b)", format="%.10f", key="intervalo_b", on_change=limpiar_resultado)

elif metodo == "Punto fijo":

    st.info("**Punto Fijo**: Para usar este método, debe despejar la ecuación f(x)=0 en la forma x = g(x).")

    

    # Mostrar sugerencias

    if expresion is not None:

        with st.expander("💡 Sugerencias de despejes"):

            sugerencias = sugerir_despejes(funcion_texto)

            for titulo, desc in sugerencias:

                st.caption(f"**{titulo}**: {desc}")

    

    st.session_state.setdefault("despeje_input", "20/(x^2+2*x+10)")

    st.session_state.setdefault("punto_fijo_x0", 1.5)

    despeje_texto = st.text_input("Despeje g(x)", help="Ejemplo: 1-sin(x), (4-log(x))/2", key="despeje_input", on_change=limpiar_resultado)

    parametros["x0"] = st.number_input("Valor inicial (x0)", format="%.10f", key="punto_fijo_x0", on_change=limpiar_resultado)

    

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

        LOGGER.warning("Despeje g(x) no válido: %r (%s: %s)", despeje_texto, type(e).__name__, e)

        st.warning(

            "⚠️ El despeje g(x) está mal escrito o no pudo interpretarse. "

            "Revisa los paréntesis, operaciones y nombres de las funciones."

        )

elif metodo == "Newton-Raphson":

    st.session_state.setdefault("newton_x0", 0.5)

    parametros["x0"] = st.number_input("Valor inicial (x0)", format="%.10f", key="newton_x0", on_change=limpiar_resultado)

    derivada = sp.diff(expresion, X) if expresion is not None else None

    if derivada is not None:

        parametros["derivada"] = derivada

        st.latex(f"f'(x) = {sp.latex(derivada)}")



    sugerir_habilitado = expresion is not None and derivada is not None

    st.button(

        "💡 Sugerir valor inicial",

        width="stretch",

        type="secondary",

        disabled=not sugerir_habilitado,

        key="newton_sugerir",

        on_click=sugerir_x0,

        args=(expresion, derivada),

    )

elif metodo == "Secante":

    col_x0, col_x1 = st.columns(2)

    st.session_state.setdefault("secante_x0", 0.0)

    st.session_state.setdefault("secante_x1", 1.0)

    parametros["x0"] = col_x0.number_input("Primer valor inicial (x0)", format="%.10f", key="secante_x0", on_change=limpiar_resultado)

    parametros["x1"] = col_x1.number_input("Segundo valor inicial (x1)", format="%.10f", key="secante_x1", on_change=limpiar_resultado)

else:

    col_x0, col_x1, col_x2 = st.columns(3)

    st.session_state.setdefault("muller_x0", 4.5)

    st.session_state.setdefault("muller_x1", 5.5)

    st.session_state.setdefault("muller_x2", 5.0)

    parametros["x0"] = col_x0.number_input("Primer valor inicial (x0)", format="%.10f", key="muller_x0", on_change=limpiar_resultado)

    parametros["x1"] = col_x1.number_input("Segundo valor inicial (x1)", format="%.10f", key="muller_x1", on_change=limpiar_resultado)

    parametros["x2"] = col_x2.number_input("Tercer valor inicial (x2)", format="%.10f", key="muller_x2", on_change=limpiar_resultado)



resolver, limpiar_boton = st.columns([1, 1])

if limpiar_boton.button("Limpiar", width="stretch"):

    limpiar()

    st.rerun()

resolver_deshabilitado = expresion is None or (origen == "Subir una imagen" and not imagen_confirmada)

if resolver_deshabilitado:

    st.caption("💡 Complete y valide la función para habilitar el cálculo.")

if resolver.button("Resolver", type="primary", width="stretch", disabled=resolver_deshabilitado):

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

            inicio_calculo = perf_counter()

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

            

            with st.spinner(f"Ejecutando {metodo} con precisión completa..."):

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

                elif metodo == "Secante":

                    resultado = secante(funcion, parametros["x0"], parametros["x1"], **metodo_kwargs)

                else:

                    resultado = muller(funcion_numerica_compleja(expresion), parametros["x0"], parametros["x1"], parametros["x2"], **metodo_kwargs)

            st.session_state.resultado = resultado

            st.session_state.parametros_resultado = parametros

            st.session_state.metodo_resultado = metodo

            st.session_state.criterio_resultado = criterio_parada

            st.session_state.valor_criterio_resultado = error_permitido if metodo_criterio == "error" else max_iteraciones

            st.session_state.funcion_resultado = funcion_texto

            st.session_state.expresion_resultado = expresion

            evaluador_resultado = funcion_numerica_compleja(expresion) if metodo == "Müller" else funcion

            st.session_state.residuo_resultado = abs(evaluador_resultado(resultado.raiz))

            st.session_state.tiempo_resultado = perf_counter() - inicio_calculo

            registrar_historial(st.session_state, {

                "metodo": metodo,

                "funcion": funcion_texto,

                "raiz": formatear_numero(resultado.raiz, decimales),

                "estado": "Convergió" if resultado.convergio is True else ("No convergió" if resultado.convergio is False else "Finalizado"),

            })

        except ValueError as error:

            st.error(str(error))

        except Exception as exc:

            st.error(f"No fue posible completar el cálculo. Revise los valores y el dominio de la función.")

            LOGGER.exception("Error interno durante el cálculo: %s", exc)



if "resultado" in st.session_state:

    resultado = st.session_state.resultado

    metodo_resultado = st.session_state.metodo_resultado

    funcion_resultado = st.session_state.get("funcion_resultado", funcion_texto)

    expresion_resultado = st.session_state.get("expresion_resultado", expresion)

    criterio_resultado = st.session_state.get("criterio_resultado", "Tolerancia")

    parametros_grafica = st.session_state.parametros_resultado

    residuo = st.session_state.get("residuo_resultado", float("nan"))

    tiempo = st.session_state.get("tiempo_resultado", 0.0)

    filas = resultado.iteraciones

    filas_presentacion = preparar_filas(filas, metodo_resultado, decimales)

    raiz = resultado.raiz

    raiz_es_compleja = isinstance(raiz, complex) and abs(raiz.imag) >= 1e-14

    estado = "Convergió ✓" if resultado.convergio is True else ("No convergió ✗" if resultado.convergio is False else "Finalizado")



    puntos = []

    if "a" in parametros_grafica:

        puntos = [parametros_grafica["a"], parametros_grafica["b"]]

        rango_defecto = (min(puntos + [float(complex(raiz).real)]) - 0.5, max(puntos + [float(complex(raiz).real)]) + 0.5)

    else:

        puntos = [parametros_grafica.get("x0", float(complex(raiz).real))]

        puntos += [parametros_grafica[clave] for clave in ("x1", "x2") if clave in parametros_grafica]

        valores_rango = puntos if raiz_es_compleja else puntos + [float(complex(raiz).real)]

        rango_defecto = (min(valores_rango) - 2, max(valores_rango) + 2)



    st.markdown('<div class="step-label">Paso 2 · Análisis</div>', unsafe_allow_html=True)

    st.subheader("Resultados del ejercicio")

    tab_resumen, tab_iteraciones, tab_explicacion, tab_grafica, tab_exportar =     resumen, iteraciones, explicacion, grafica, exportacion = st.tabs([
        "Resumen", "Iteraciones", "Explicación paso a paso", "Gráfica", "Exportación"
    ])



    with tab_resumen:

        tarjetas = st.columns(5)

        tarjetas[0].metric("Raíz aproximada", formatear_numero(raiz, decimales))

        tarjetas[1].metric("Error final", f"{resultado.error_final:.{decimales}f} %")

        tarjetas[2].metric("Residuo |f(x)|", formatear_numero(residuo, decimales))

        tarjetas[3].metric("Iteraciones", len(filas))

        tarjetas[4].metric("Tiempo", f"{tiempo * 1000:.2f} ms")

        mensaje_estado = st.success if resultado.convergio is True else (st.warning if resultado.convergio is False else st.info)

        mensaje_estado(f"{estado} · {resultado.motivo}")

        st.markdown(

            f'<div class="conclusion">{texto_conclusion(metodo_resultado, raiz, resultado.error_final, len(filas), estado, residuo, decimales)}</div>',

            unsafe_allow_html=True,

        )

        st.divider()

        col_dato1, col_dato2, col_dato3 = st.columns(3)

        col_dato1.caption("MÉTODO")

        col_dato1.write(metodo_resultado)

        col_dato2.caption("FUNCIÓN")

        col_dato2.code(funcion_resultado, language=None)

        col_dato3.caption("CRITERIO")

        col_dato3.write(criterio_resultado)



    with tab_iteraciones:

        if filas_presentacion:

            df_iteraciones = pd.DataFrame(filas_presentacion)

            def resaltar_ultima(fila):

                return ["background-color: #312e81; color: #f8fafc; font-weight: 600" if fila.name == len(df_iteraciones) - 1 else "" for _ in fila]

            st.dataframe(df_iteraciones.style.apply(resaltar_ultima, axis=1), width="stretch", hide_index=True)

            st.caption("La última fila se resalta porque contiene la aproximación final del proceso.")

            mostrar_explicaciones(list(df_iteraciones.columns))

        else:

            st.info("El método identificó una raíz en los datos iniciales; no fue necesario iterar.")



    with tab_explicacion:

        criterio_explicacion = "error" if criterio_resultado == "Error porcentual permitido" else "fijo"

        valor_criterio = st.session_state.get("valor_criterio_resultado", None)

        if criterio_explicacion == "error":

            error_porcentual_valor = valor_criterio if valor_criterio is not None else error_permitido

            iteraciones_valor = max_iteraciones

        else:

            error_porcentual_valor = None

            iteraciones_valor = int(valor_criterio) if valor_criterio is not None else int(max_iteraciones)



        if not filas:

            st.info("El método identificó una raíz en los datos iniciales; hubo pocos o ningún cálculo iterativo. Se muestra la comprobación matemática.")

        try:

            contenido_explicacion = generar_explicacion(

                metodo_resultado,

                expresion_resultado,

                filas,

                resultado,

                parametros_grafica,

                funcion_texto=funcion_resultado,

                error_permitido=error_porcentual_valor,

                max_iteraciones=iteraciones_valor,

                criterio=criterio_explicacion,

                decimales=decimales,

            )

            st.markdown(contenido_explicacion, unsafe_allow_html=True)

        except Exception as error_explicacion:

            LOGGER.exception("No fue posible generar la explicación: %s", error_explicacion)

            st.warning("No fue posible generar la explicación dinámica. Verifique la función y los parámetros.")



    with tab_grafica:

        if raiz_es_compleja:

            st.info("La raíz es compleja; el recorrido se representa mediante sus partes real e imaginaria.")

            st.plotly_chart(crear_grafica_compleja(filas, raiz), width="stretch")

        else:

            rango_personalizado = st.toggle("Definir rango personalizado", value=False)

            limites = rango_defecto

            if rango_personalizado:

                col_min, col_max = st.columns(2)

                limites = (

                    col_min.number_input("Mínimo del eje x", value=float(rango_defecto[0])),

                    col_max.number_input("Máximo del eje x", value=float(rango_defecto[1])),

                )

            try:

                if metodo_resultado == "Newton-Raphson" and filas and len(parametros_grafica) > 0:

                    iteraciones_disponibles = [fila["i"] for fila in filas]

                    indice_por_defecto = len(iteraciones_disponibles) - 1

                    iteracion_seleccion = st.selectbox(

                        "Seleccione la iteración para ver su recta tangente",

                        iteraciones_disponibles,

                        index=indice_por_defecto,

                        key="grafica_iteracion_tangente",

                    )

                    fila_tangente = filas[int(iteracion_seleccion) - 1]

                    st.plotly_chart(crear_grafica_con_tangente(expresion_resultado, fila_tangente, limites, puntos), width="stretch")

                    st.caption(

                        f"Iteración {int(iteracion_seleccion)}: el punto rojo es (x_n, f(x_n)), la línea verde "

                        "discontinua es la recta tangente, y el rombo amarillo indica dónde la tangente cruza "

                        "el eje x: esa intersección es la nueva aproximación x_(n+1)."

                    )

                else:

                    st.plotly_chart(crear_grafica(expresion_resultado, float(complex(raiz).real), limites, puntos), width="stretch")

                    st.caption("El marcador rojo representa la raíz aproximada; los marcadores amarillos corresponden a los datos iniciales.")

            except ValueError as error:

                st.error(str(error))



    with tab_exportar:

        st.write("Descargue el ejercicio completo en el formato que necesite.")

        valor_criterio = st.session_state.get("valor_criterio_resultado", error_permitido)

        archivo_excel = reporte_pdf = archivo_csv = None

        errores_exportacion = []



        try:

            archivo_excel = crear_excel(

                "Software de Métodos Numéricos", funcion_resultado, metodo_resultado,

                parametros_grafica, valor_criterio, raiz, resultado.error_final,

                filas, criterio_resultado, estado,

            )

        except Exception as exc:

            errores_exportacion.append("Excel")

            LOGGER.exception("No fue posible preparar Excel: %s", exc)



        try:

            reporte_pdf = crear_pdf(

                "Software de Métodos Numéricos", funcion_resultado, metodo_resultado,

                parametros_grafica, valor_criterio, raiz, resultado.error_final,

                filas, criterio_resultado, estado, resultado.motivo,

                expresion_resultado, rango_defecto, residuo, tiempo,

            )

        except Exception as exc:

            LOGGER.warning("El PDF con gráfica falló; se intentará una versión sin gráfica: %s", exc)

            try:

                reporte_pdf = crear_pdf(

                    "Software de Métodos Numéricos", funcion_resultado, metodo_resultado,

                    parametros_grafica, valor_criterio, raiz, resultado.error_final,

                    filas, criterio_resultado, estado, resultado.motivo,

                )

            except Exception as segundo_error:

                errores_exportacion.append("PDF")

                LOGGER.exception("No fue posible preparar PDF: %s", segundo_error)



        try:

            archivo_csv = crear_csv(filas, metodo_resultado, decimales)

        except Exception as exc:

            errores_exportacion.append("CSV")

            LOGGER.exception("No fue posible preparar CSV: %s", exc)



        col_excel, col_pdf, col_csv = st.columns(3)

        if archivo_excel is not None:

            col_excel.download_button("📥 Excel completo", archivo_excel, "resultado_metodos_numericos.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", width="stretch")

        else:

            col_excel.error("Excel no disponible")

        if reporte_pdf is not None:

            col_pdf.download_button("📄 Reporte PDF", reporte_pdf, "resumen_metodos_numericos.pdf", "application/pdf", width="stretch")

        else:

            col_pdf.error("PDF no disponible")

        if archivo_csv is not None:

            col_csv.download_button("🗂 Tabla CSV", archivo_csv, "iteraciones_metodos_numericos.csv", "text/csv", width="stretch")

        else:

            col_csv.error("CSV no disponible")

        if errores_exportacion:

            st.warning(f"No se pudieron preparar estos formatos: {', '.join(errores_exportacion)}. Los demás continúan disponibles.")

        else:

            st.success("✓ Los tres formatos están listos para descargar.")

        st.caption("Excel y PDF incluyen el resumen completo. CSV contiene la tabla visible de iteraciones.")

else:

    st.markdown('<div class="method-card"><h3>Listo para comenzar</h3><p>Ingrese una función, revise los parámetros y pulse <b>Resolver</b>. Los resultados aparecerán organizados en cinco pestañas.</p></div>', unsafe_allow_html=True)







