import os
import re
from pathlib import Path
import sympy as sp


# Posibles ubicaciones de Tesseract en Windows
RUTAS_TESSERACT = [
    Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe"),
    Path(r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"),
    Path.home()
    / "AppData"
    / "Local"
    / "Programs"
    / "Tesseract-OCR"
    / "tesseract.exe",
]


def configurar_tesseract(pytesseract):
    """
    Busca Tesseract en las ubicaciones habituales de Windows
    y configura pytesseract automáticamente.
    """

    # Si funciona mediante el PATH, no se necesita configurar una ruta
    try:
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        pass

    # Buscar el ejecutable en las rutas conocidas
    for ruta in RUTAS_TESSERACT:
        if ruta.exists():
            pytesseract.pytesseract.tesseract_cmd = str(ruta)

            try:
                pytesseract.get_tesseract_version()
                return True
            except Exception:
                continue

    return False


def preparar_imagen(imagen, Image, ImageOps, ImageEnhance, ImageFilter):
    """
    Mejora la imagen antes de enviarla al OCR.
    Convierte a escala de grises, aumenta el tamaño
    y mejora el contraste.
    """

    if not hasattr(imagen, "mode"):
        imagen = Image.open(imagen)

    # Convertir a RGB para evitar incompatibilidades
    imagen = imagen.convert("RGB")

    # Aumentar el tamaño para reconocer mejor símbolos pequeños
    ancho, alto = imagen.size

    if ancho < 1600:
        escala = max(2, int(1600 / max(ancho, 1)))

        imagen = imagen.resize(
            (ancho * escala, alto * escala),
            Image.Resampling.LANCZOS,
        )

    # Convertir a escala de grises
    imagen = ImageOps.grayscale(imagen)

    # Mejorar contraste
    imagen = ImageOps.autocontrast(imagen)
    imagen = ImageEnhance.Contrast(imagen).enhance(2.0)

    # Aumentar nitidez
    imagen = imagen.filter(ImageFilter.SHARPEN)

    return imagen


def limpiar_texto_detectado(texto):
    """
    Limpia errores comunes producidos por el OCR y trata
    de obtener solamente la expresión matemática.
    """

    if not texto:
        return None

    texto = texto.strip()

    # Normalizar símbolos
    reemplazos = {
        "−": "-",
        "–": "-",
        "—": "-",
        "×": "*",
        "÷": "/",
        "“": "",
        "”": "",
        "‘": "",
        "’": "",
    }

    for original, nuevo in reemplazos.items():
        texto = texto.replace(original, nuevo)

    # Eliminar espacios repetidos
    texto = re.sub(r"[ \t]+", " ", texto)

    # Separar líneas válidas
    lineas = [
        linea.strip()
        for linea in texto.splitlines()
        if linea.strip()
    ]

    if not lineas:
        return None

    # Buscar primero una línea que contenga f(x)
    linea_funcion = None

    for linea in lineas:
        linea_sin_espacios = linea.lower().replace(" ", "")

        if "f(x)" in linea_sin_espacios or "f{(x)" in linea_sin_espacios:
            linea_funcion = linea
            break

    # Si no aparece f(x), usar la línea con más símbolos matemáticos
    if linea_funcion is None:
        linea_funcion = max(
            lineas,
            key=lambda linea: sum(
                simbolo in linea
                for simbolo in (
                    "x",
                    "=",
                    "+",
                    "-",
                    "^",
                    "/",
                    "sin",
                    "cos",
                    "tan",
                    "ln",
                    "exp",
                )
            ),
        )

    # Obtener solamente lo que está después del signo igual
    if "=" in linea_funcion:
        linea_funcion = linea_funcion.split("=", 1)[1].strip()

    # Correcciones habituales del OCR
    linea_funcion = re.sub(
        r"\barctan\s*x\b",
        "arctan(x)",
        linea_funcion,
        flags=re.IGNORECASE,
    )

    linea_funcion = re.sub(
        r"\barcsin\s*x\b",
        "arcsin(x)",
        linea_funcion,
        flags=re.IGNORECASE,
    )

    linea_funcion = re.sub(
        r"\bsin\s*x\b",
        "sin(x)",
        linea_funcion,
        flags=re.IGNORECASE,
    )

    linea_funcion = re.sub(
        r"\bsen\s*x\b",
        "sen(x)",
        linea_funcion,
        flags=re.IGNORECASE,
    )

    linea_funcion = re.sub(
        r"\bcos\s*x\b",
        "cos(x)",
        linea_funcion,
        flags=re.IGNORECASE,
    )

    linea_funcion = re.sub(
        r"\bln\s*x\b",
        "ln(x)",
        linea_funcion,
        flags=re.IGNORECASE,
    )

    # Convertir algunas confusiones comunes
    linea_funcion = linea_funcion.replace("X", "x")
    linea_funcion = linea_funcion.replace("”", "")
    linea_funcion = linea_funcion.strip(" .,:;")

    return linea_funcion or None


def validar_expresion(texto):
    """
    Intenta validar si el texto es una expresión matemática válida con SymPy.
    Retorna True si es válida, False si no.
    """
    try:
        from utilidades.parser_funciones import analizar_funcion
        analizar_funcion(texto)
        return True
    except Exception:
        return False


def generar_candidatos_ocr(texto_ocr):
    """
    Genera múltiples candidatos de corrección a partir del OCR.
    
    Retorna:
        lista de (candidato, confianza)
    """
    candidatos = []
    
    if not texto_ocr:
        return candidatos
    
    # Candidato 1: Texto OCR limpio tal cual
    candidatos.append((texto_ocr, 0.5))
    
    # Candidato 2: Agregar paréntesis a funciones sin ellos (sin x -> sin(x))
    candidato2 = re.sub(r"\b(sin|cos|tan|asin|acos|atan)\s+([x])", r"\1(\2)", texto_ocr, flags=re.IGNORECASE)
    if candidato2 != texto_ocr:
        candidatos.append((candidato2, 0.7))
    
    # Candidato 3: Convertir multiplicación implícita (2x -> 2*x)
    candidato3 = re.sub(r"(\d)\s*([x(])", r"\1*\2", texto_ocr)
    if candidato3 != texto_ocr:
        candidatos.append((candidato3, 0.6))
    
    # Candidato 4: Combinación de 2 y 3
    candidato4 = re.sub(r"\b(sin|cos|tan|asin|acos|atan)\s+([x])", r"\1(\2)", texto_ocr, flags=re.IGNORECASE)
    candidato4 = re.sub(r"(\d)\s*([x(])", r"\1*\2", candidato4)
    if candidato4 != texto_ocr and candidato4 not in [c[0] for c in candidatos]:
        candidatos.append((candidato4, 0.8))
    
    # Candidato 5: Convertir sen a sin
    candidato5 = re.sub(r"\bsen\b", "sin", texto_ocr, flags=re.IGNORECASE)
    if candidato5 != texto_ocr:
        candidatos.append((candidato5, 0.75))
    
    return candidatos


def calcular_confianza_ocr(texto_ocr, texto_corregido, es_valido):
    """
    Calcula un indicador de confianza basado en:
    - Si la validación con SymPy pasó
    - Cuántas correcciones fueron necesarias
    """
    if not es_valido:
        return "baja"
    
    # Contar cambios
    cambios = 0
    for i, (c1, c2) in enumerate(zip(texto_ocr, texto_corregido)):
        if c1 != c2:
            cambios += 1
    
    # Si el OCR tenía paréntesis y otras cosas claras, y es válido = alta confianza
    if "(" in texto_ocr and ")" in texto_ocr:
        return "alta"
    
    # Si hubo pocas correcciones = media-alta confianza
    if cambios < len(texto_ocr) * 0.1:
        return "media"
    
    # Si hubo muchas correcciones = media-baja confianza
    return "media"


def extraer_funcion(imagen):
    """
    Extrae una función matemática desde una imagen con múltiples estrategias.

    Retorna:
        (funcion_detectada, mensaje)
    """

    try:
        import pytesseract
        from PIL import (
            Image,
            ImageOps,
            ImageEnhance,
            ImageFilter,
        )
    except ImportError:
        return (
            None,
            "Faltan dependencias. Instale pytesseract y Pillow.",
        )

    if not configurar_tesseract(pytesseract):
        return (
            None,
            "No se encontró Tesseract OCR. Verifique que esté "
            "instalado en C:\\Program Files\\Tesseract-OCR.",
        )

    try:
        imagen_preparada = preparar_imagen(
            imagen,
            Image,
            ImageOps,
            ImageEnhance,
            ImageFilter,
        )

        # Intentar con múltiples configuraciones PSM
        configuraciones = [
            "--oem 3 --psm 6",   # Asume un bloque de texto uniforme
            "--oem 3 --psm 11",  # Sparse text
            "--oem 3 --psm 7",   # Single text line
        ]

        texto = None

        # Intentar primero español e inglés, con múltiples configs
        for idioma in ("spa+eng", "eng"):
            for config in configuraciones:
                try:
                    resultado = pytesseract.image_to_string(
                        imagen_preparada,
                        lang=idioma,
                        config=config,
                    ).strip()

                    if resultado:
                        texto = resultado
                        break

                except pytesseract.TesseractError:
                    continue

            if texto:
                break

        if not texto:
            return (
                None,
                "No se detectó texto legible en la imagen.",
            )

        # Limpiar el texto OCR
        texto_ocr = limpiar_texto_detectado(texto)

        if not texto_ocr:
            return (
                None,
                "Se encontró texto, pero no fue posible identificar "
                "una función matemática confiable.",
            )

        # Generar candidatos de corrección
        candidatos = generar_candidatos_ocr(texto_ocr)
        
        # Validar cada candidato
        mejor_candidato = None
        mejor_confianza = "baja"
        confianzas_dict = {"alta": 3, "media": 2, "baja": 1}

        for candidato, confianza_inicial in candidatos:
            es_valido = validar_expresion(candidato)
            if es_valido:
                confianza = calcular_confianza_ocr(texto_ocr, candidato, es_valido)
                if confianzas_dict.get(confianza, 0) > confianzas_dict.get(mejor_confianza, 0):
                    mejor_candidato = candidato
                    mejor_confianza = confianza
        
        # Si no hay candidato válido, retornar el OCR limpio original
        if mejor_candidato is None:
            mejor_candidato = texto_ocr
            mejor_confianza = "baja"

        # Mapear confianza a mensaje
        if mejor_confianza == "alta":
            mensaje = "Función detectada con alta confianza."
        elif mejor_confianza == "media":
            mensaje = "Función detectada con confianza media. Revísela."
        else:
            mensaje = "Función detectada con baja confianza. Corrija manualmente si es necesario."

        return (
            mejor_candidato,
            mensaje,
        )

    except Exception as error:
        return (
            None,
            "No fue posible procesar la imagen. "
            f"Detalle: {error}",
        )