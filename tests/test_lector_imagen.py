from PIL import Image, ImageEnhance, ImageFilter, ImageOps

from utilidades.lector_imagen import (
    calcular_confianza_ocr,
    generar_candidatos_ocr,
    limpiar_texto_detectado,
    preparar_imagen,
    validar_expresion,
)


def test_limpiar_texto_extrae_funcion_despues_del_igual():
    assert limpiar_texto_detectado("Ejercicio\nf(x) = x^2 - 4") == "x^2 - 4"


def test_generar_candidatos_corrige_multiplicacion_implicita():
    candidatos = [texto for texto, _ in generar_candidatos_ocr("2x+5")]
    assert "2*x+5" in candidatos


def test_validar_expresion_ocr():
    assert validar_expresion("sin(x)-x/2") is True
    assert validar_expresion("texto sin expresion") is False


def test_confianza_alta_con_parentesis_y_expresion_valida():
    assert calcular_confianza_ocr("sin(x)", "sin(x)", True) == "alta"


def test_preparar_imagen_convierte_a_escala_de_grises_y_amplia():
    imagen = Image.new("RGB", (100, 50), "white")
    preparada = preparar_imagen(imagen, Image, ImageOps, ImageEnhance, ImageFilter)
    assert preparada.mode == "L"
    assert preparada.width >= 1600
