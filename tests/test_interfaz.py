import math

from componentes.catalogo import METODOS, cargar_ejemplo_en_estado
from componentes.interfaz import crear_csv, formatear_numero, preparar_filas


def test_catalogo_contiene_todos_los_metodos_y_ejemplos():
    esperados = {"Bisección", "Regla falsa", "Punto fijo", "Newton-Raphson", "Secante", "Müller"}
    assert set(METODOS) == esperados
    assert all(info["ejemplo"] and info["formula"] for info in METODOS.values())


def test_cargar_ejemplo_actualiza_estado():
    estado = {}
    cargar_ejemplo_en_estado(estado, "Müller")
    assert estado["funcion_input"] == "x^3-13*x-12"
    assert (estado["muller_x0"], estado["muller_x1"], estado["muller_x2"]) == (4.5, 5.5, 5.0)


def test_formato_complejo_es_legible():
    assert formatear_numero(2.5 + 1.7320508j, 6) == "2.500000 + 1.732051i"
    assert "j" not in formatear_numero(-2j, 4)


def test_preparar_filas_no_muestra_infinito_interno():
    filas = preparar_filas([{"i": 1, "mi": 0.5, "Ea (%)": math.inf}], "Bisección", 6)
    assert filas[0]["Iteración"] == 1
    assert filas[0]["Aproximación"] == 0.5
    assert filas[0]["Error (%)"] == math.inf


def test_csv_incluye_encabezados_amigables():
    contenido = crear_csv([{"i": 1, "xi": 0.5, "xi+1": 0.6, "Ea (%)": 1.0}], "Newton-Raphson", 6)
    texto = contenido.decode("utf-8-sig")
    assert "Iteración" in texto
    assert "Nueva aproximación" in texto
