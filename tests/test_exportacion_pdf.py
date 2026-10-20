import math
from utilidades.parser_funciones import analizar_funcion

from metodos.muller import muller
from utilidades.exportacion_pdf import crear_pdf


def _generar_pdf(resultado, funcion, parametros):
    return crear_pdf(
        "Software de Métodos Numéricos", funcion, "Müller", parametros,
        0.5, resultado.raiz, resultado.error_final, resultado.iteraciones,
        "Error porcentual permitido", "Convergió", resultado.motivo,
    )


def test_pdf_real_tiene_formato_valido_y_contenido():
    resultado = muller(lambda x: x ** 3 - 13 * x - 12, 4.5, 5.5, 5,
                       error_permitido=0.5, max_iteraciones=100)
    contenido = _generar_pdf(resultado, "x^3-13*x-12", {"x0": 4.5, "x1": 5.5, "x2": 5})
    assert contenido.startswith(b"%PDF-")
    assert contenido.endswith(b"%%EOF\n")
    assert len(contenido) > 3000


def test_pdf_complejo_se_genera_sin_error():
    resultado = muller(lambda x: x ** 2 + 1, 0, 1, 2,
                       error_permitido=0.01, max_iteraciones=20)
    assert isinstance(resultado.raiz, complex)
    assert math.isclose(abs(resultado.raiz.imag), 1.0)
    contenido = _generar_pdf(resultado, "x^2+1", {"x0": 0, "x1": 1, "x2": 2})
    assert contenido.startswith(b"%PDF-")
    assert len(contenido) > 3000


def test_pdf_incluye_grafica_vectorial_real():
    resultado = muller(lambda x: x ** 3 - 13 * x - 12, 4.5, 5.5, 5,
                       error_permitido=0.5, max_iteraciones=100)
    contenido = crear_pdf(
        "Reporte", "x^3-13*x-12", "Müller", {"x0": 4.5, "x1": 5.5, "x2": 5},
        0.5, resultado.raiz, resultado.error_final, resultado.iteraciones,
        "Error porcentual permitido", "Convergió", resultado.motivo,
        analizar_funcion("x^3-13*x-12"), (2, 7), 1e-8, 0.002,
    )
    assert contenido.startswith(b"%PDF-")
    assert len(contenido) > 5000
