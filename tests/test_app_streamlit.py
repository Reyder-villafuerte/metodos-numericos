import pytest
from pathlib import Path
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"

UNIDAD_1 = "Unidad 1 — Raíces de ecuaciones"

UNIDAD_2 = "Unidad 2 — Sistemas de ecuaciones lineales"

METODOS_UNIDAD_1 = [
    "Bisección",
    "Regla falsa",
    "Punto fijo",
    "Newton-Raphson",
    "Secante",
    "Müller",
]

METODOS_UNIDAD_2 = [
    "Matriz inversa",
    "Regla de Cramer",
    "Doolittle",
    "Crout",
    "Jacobi",
    "Gauss-Seidel",
    "Jacobi no lineal",
    "Gauss-Seidel no lineal",
    "Newton-Raphson para sistemas",
    "Interpolación de Newton",
    "Regresión polinomial",
    "Regresión lineal múltiple",
]
METODOS_DIRECTOS_UNIDAD_2 = METODOS_UNIDAD_2[:4]


def test_app_muestra_selector_de_unidades_en_barra_lateral():
    app = AppTest.from_file(APP, default_timeout=20).run()

    selector = app.sidebar.selectbox(key="unidad_selector")

    assert selector.label == "Seleccionar unidad"
    assert selector.options == [UNIDAD_1, UNIDAD_2]


def test_app_selecciona_unidad_1_por_defecto():
    app = AppTest.from_file(APP, default_timeout=20).run()

    assert app.selectbox(key="unidad_selector").value == UNIDAD_1


def test_app_unidad_1_muestra_exactamente_sus_seis_metodos():
    app = AppTest.from_file(APP, default_timeout=20).run()

    selector_metodo = app.selectbox(key="metodo_selector")

    assert selector_metodo.label == "Método numérico"
    assert selector_metodo.options == METODOS_UNIDAD_1


def test_app_unidad_2_muestra_todos_sus_metodos():
    app = AppTest.from_file(APP, default_timeout=20).run()

    app.selectbox(key="unidad_selector").select(UNIDAD_2).run()

    assert not app.exception
    selector = app.selectbox(key="metodo_u2_selector")
    assert selector.label == "Método numérico"
    assert selector.options == METODOS_UNIDAD_2


def test_app_unidad_2_oculta_formularios_y_resultados_de_unidad_1():
    app = AppTest.from_file(APP, default_timeout=20).run()

    app.selectbox(key="unidad_selector").select(UNIDAD_2).run()

    assert not app.radio
    assert not app.number_input
    assert not app.text_input
    assert not app.metric
    assert not app.tabs
    assert app.selectbox(key="u2_dimension").label == "Número de incógnitas"
    assert {tabla.key for tabla in app.get("dataframe")} == {
        "u2_A_editor_0",
        "u2_b_editor_0",
    }
    assert app.button(key="u2_resolver").label == "Resolver sistema"


def test_app_cambiar_de_unidad_limpia_resultados_anteriores():
    app = AppTest.from_file(APP, default_timeout=30).run()

    next(boton for boton in app.button if "Cargar ejemplo" in boton.label).click().run()
    next(boton for boton in app.button if boton.label == "Resolver").click().run()

    assert "resultado" in app.session_state.filtered_state
    assert app.metric

    app.selectbox(key="unidad_selector").select(UNIDAD_2).run()

    claves_resultado = {
        "resultado",
        "parametros_resultado",
        "metodo_resultado",
        "criterio_resultado",
        "valor_criterio_resultado",
        "funcion_resultado",
        "expresion_resultado",
        "residuo_resultado",
        "tiempo_resultado",
    }
    assert claves_resultado.isdisjoint(app.session_state.filtered_state)
    assert not app.metric
    assert not app.tabs


def test_app_volver_a_unidad_1_permite_resolver_un_ejercicio_nuevo():
    app = AppTest.from_file(APP, default_timeout=30).run()

    app.selectbox(key="unidad_selector").select(UNIDAD_2).run()
    app.selectbox(key="unidad_selector").select(UNIDAD_1).run()

    assert app.selectbox(key="metodo_selector").options == METODOS_UNIDAD_1
    next(boton for boton in app.button if "Cargar ejemplo" in boton.label).click().run()

    resolver = next(boton for boton in app.button if boton.label == "Resolver")
    assert resolver.disabled is False

    resolver.click().run()

    assert not app.exception
    assert not app.error
    assert len(app.metric) == 5
    assert len(app.tabs) == 5


@pytest.mark.parametrize("metodo", METODOS_DIRECTOS_UNIDAD_2)
def test_app_unidad_2_resuelve_ejemplo_de_cada_metodo(metodo):
    app = AppTest.from_file(APP, default_timeout=40).run()

    app.selectbox(key="unidad_selector").select(UNIDAD_2).run()
    app.selectbox(key="metodo_u2_selector").select(metodo).run()
    app.button(key="u2_cargar_ejemplo").click().run()
    app.button(key="u2_resolver").click().run()

    assert not app.exception
    assert not app.error
    assert app.session_state.filtered_state["u2_resultado"].metodo == metodo
    assert [tab.label for tab in app.tabs] == [
        "Resumen",
        "Resultados",
        "Matrices y operaciones",
        "Explicación paso a paso",
        "Comprobación",
        "Gráficas",
    ]
    assert any(metrica.label == "‖Ax − b‖∞" for metrica in app.metric)


def test_app_cambiar_metodo_unidad_2_limpia_resultado_anterior():
    app = AppTest.from_file(APP, default_timeout=40).run()

    app.selectbox(key="unidad_selector").select(UNIDAD_2).run()
    app.button(key="u2_cargar_ejemplo").click().run()
    app.button(key="u2_resolver").click().run()
    assert "u2_resultado" in app.session_state.filtered_state

    app.selectbox(key="metodo_u2_selector").select("Regla de Cramer").run()

    assert "u2_resultado" not in app.session_state.filtered_state
    assert not app.tabs


def test_app_cambiar_desde_unidad_2_limpia_su_resultado():
    app = AppTest.from_file(APP, default_timeout=40).run()

    app.selectbox(key="unidad_selector").select(UNIDAD_2).run()
    app.button(key="u2_cargar_ejemplo").click().run()
    app.button(key="u2_resolver").click().run()
    assert "u2_resultado" in app.session_state.filtered_state

    app.selectbox(key="unidad_selector").select(UNIDAD_1).run()

    assert "u2_resultado" not in app.session_state.filtered_state
    assert app.selectbox(key="metodo_selector").options == METODOS_UNIDAD_1


@pytest.mark.parametrize(
    "metodo",
    ["Bisección", "Regla falsa", "Punto fijo", "Newton-Raphson", "Secante", "Müller"],
)
def test_app_resuelve_ejemplo_de_cada_metodo(metodo):
    app = AppTest.from_file(APP, default_timeout=30).run()

    app.selectbox(key="metodo_selector").select(metodo).run()

    next(boton for boton in app.button if "Cargar ejemplo" in boton.label).click().run()

    resolver = next(boton for boton in app.button if boton.label == "Resolver")

    assert resolver.disabled is False

    resolver.click().run()

    assert not app.exception

    assert not app.error

    assert len(app.metric) == 5

    assert len(app.tabs) == 5

    assert len(app.get("download_button")) == 3


def test_app_desactiva_resolver_sin_funcion():
    app = AppTest.from_file(APP, default_timeout=20).run()

    resolver = next(boton for boton in app.button if boton.label == "Resolver")

    assert resolver.disabled is True


@pytest.mark.parametrize(
    "funcion_invalida",
    ["sin(", "x+", "x^", "foo(x)", "x-", "3**3", "9^(9^(9^(9^9)))"],
)
def test_app_funcion_invalida_muestra_advertencia_educativa(funcion_invalida):
    app = AppTest.from_file(APP, default_timeout=20).run()

    assert not app.exception

    app.text_input(key="funcion_input").set_value(funcion_invalida).run()

    assert not app.exception

    textos = " ".join(str(getattr(e, "value", "")) for e in app.warning)

    assert "mal escrita o no pudo interpretarse" in textos

    resolver = next(boton for boton in app.button if boton.label == "Resolver")

    assert resolver.disabled is True


def test_app_funcion_invalida_no_muestra_detalle_tecnico():
    app = AppTest.from_file(APP, default_timeout=20).run()

    assert not app.exception

    app.text_input(key="funcion_input").set_value("sin(").run()

    assert not app.exception

    textos_warning = " ".join(str(getattr(e, "value", "")) for e in app.warning)

    textos_error = " ".join(str(getattr(e, "value", "")) for e in app.error)

    assert "TokenError" not in (textos_warning + textos_error)

    assert "invalid syntax" not in (textos_warning + textos_error).lower()


def test_app_funcion_valida_permite_resolver():
    app = AppTest.from_file(APP, default_timeout=20).run()

    assert not app.exception

    app.text_input(key="funcion_input").set_value("x^2-4").run()

    assert not app.exception

    textos_exito = " ".join(str(getattr(e, "value", "")) for e in app.success)

    assert "Función válida. Puedes continuar con el cálculo" in textos_exito

    resolver = next(boton for boton in app.button if boton.label == "Resolver")

    assert resolver.disabled is False
