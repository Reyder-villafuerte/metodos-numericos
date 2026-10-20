"""Prueba de integración de Gauss-Seidel dentro de la aplicación Streamlit."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"
UNIDAD_2 = "Unidad 2 — Sistemas de ecuaciones lineales"
PESTANAS = [
    "Resumen",
    "Resultados",
    "Matrices y operaciones",
    "Explicación paso a paso",
    "Comprobación",
    "Gráficas",
]


def _abrir_gauss_seidel():
    app = AppTest.from_file(APP, default_timeout=60).run()
    app.selectbox(key="unidad_selector").select(UNIDAD_2).run()
    app.selectbox(key="metodo_u2_selector").select("Gauss-Seidel").run()
    return app


def test_gauss_seidel_muestra_formulario():
    app = _abrir_gauss_seidel()
    assert not app.exception
    assert app.button(key="gs_cargar_ejemplo").label == "✨ Cargar ejercicio de ejemplo"
    assert app.button(key="gs_resolver").label == "Resolver sistema"
    assert app.text_input(key="gs_tol").value == "0.001"
    assert not app.tabs


def test_gauss_seidel_ejemplo_se_resuelve_automaticamente():
    app = _abrir_gauss_seidel()
    app.button(key="gs_cargar_ejemplo").click().run()

    assert not app.exception
    resultado = app.session_state.filtered_state["gs_resultado"]
    assert resultado.convergio and resultado.iteraciones == 4
    assert [tab.label for tab in app.tabs] == PESTANAS
    metricas = {m.label: m.value for m in app.metric}
    assert metricas["Convergencia"] == "Convergió"
    assert metricas["Iteraciones"] == "4"


def test_gauss_seidel_cambiar_de_metodo_limpia_resultado():
    app = _abrir_gauss_seidel()
    app.button(key="gs_cargar_ejemplo").click().run()
    assert "gs_resultado" in app.session_state.filtered_state

    app.selectbox(key="metodo_u2_selector").select("Jacobi").run()
    assert "gs_resultado" not in app.session_state.filtered_state
    assert not app.exception
