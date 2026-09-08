import pytest
from pathlib import Path
from streamlit.testing.v1 import AppTest


APP = Path(__file__).resolve().parents[1] / "app.py"


@pytest.mark.parametrize("metodo", [
    "Bisección", "Regla falsa", "Punto fijo", "Newton-Raphson", "Secante", "Müller",
])
def test_app_resuelve_ejemplo_de_cada_metodo(metodo):
    app = AppTest.from_file(APP, default_timeout=30).run()
    app.selectbox[0].select(metodo).run()
    next(boton for boton in app.button if "Cargar ejemplo" in boton.label).click().run()
    resolver = next(boton for boton in app.button if boton.label == "Resolver")
    assert resolver.disabled is False
    resolver.click().run()
    assert not app.exception
    assert not app.error
    assert len(app.metric) == 5
    assert len(app.tabs) == 4
    assert len(app.get("download_button")) == 3


def test_app_desactiva_resolver_sin_funcion():
    app = AppTest.from_file(APP, default_timeout=20).run()
    resolver = next(boton for boton in app.button if boton.label == "Resolver")
    assert resolver.disabled is True
