from datetime import datetime
import math

import pandas as pd
import streamlit as st


MAPEOS_COLUMNAS = {
    "Bisección": {"i": "Iteración", "ai": "Extremo izquierdo", "bi": "Extremo derecho", "mi": "Aproximación", "f(ai)": "f(a)", "f(mi)": "f(aproximación)", "f(bi)": "f(b)", "Ea (%)": "Error (%)"},
    "Regla falsa": {"i": "Iteración", "ai": "Extremo izquierdo", "bi": "Extremo derecho", "mi": "Aproximación", "f(ai)": "f(a)", "f(mi)": "f(aproximación)", "f(bi)": "f(b)", "Ea (%)": "Error (%)"},
    "Newton-Raphson": {"i": "Iteración", "xi": "Valor actual", "f(xi)": "f(xi)", "f'(xi)": "f'(xi)", "xi+1": "Nueva aproximación", "Ea (%)": "Error (%)"},
    "Secante": {"i": "Iteración", "xi-1": "Valor anterior", "xi": "Valor actual", "f(xi-1)": "f(anterior)", "f(xi)": "f(actual)", "xi+1": "Nueva aproximación", "Ea (%)": "Error (%)"},
    "Punto fijo": {"i": "Iteración", "xi": "Valor actual", "g(xi)": "g(xi)", "Ea (%)": "Error (%)"},
    "Müller": {"i": "Iteración", "x3": "Nueva aproximación x3", "Ea (%)": "Error (%)"},
}

EXPLICACIONES = {
    "Iteración": "Número secuencial del paso realizado.", "Extremo izquierdo": "Límite izquierdo del intervalo.",
    "Extremo derecho": "Límite derecho del intervalo.", "Aproximación": "Estimación de la raíz en este paso.",
    "f(a)": "Evaluación en el extremo izquierdo.", "f(b)": "Evaluación en el extremo derecho.",
    "f(aproximación)": "Evaluación en la aproximación.", "Valor actual": "Valor de x usado en el paso.",
    "Valor anterior": "Aproximación previa.", "f(xi)": "Evaluación en el valor actual.",
    "f'(xi)": "Derivada evaluada en el valor actual.", "Nueva aproximación": "Siguiente valor calculado.",
    "g(xi)": "Resultado de aplicar el despeje g(x).", "Error (%)": "Cambio porcentual entre las dos últimas aproximaciones.",
    "x0": "Primera aproximación de la parábola.", "x1": "Segunda aproximación de la parábola.",
    "x2": "Tercera aproximación de la parábola.", "f(x0)": "Evaluación de la función en x0.",
    "f(x1)": "Evaluación de la función en x1.", "f(x2)": "Evaluación de la función en x2.",
    "a": "Coeficiente cuadrático de la parábola interpoladora.", "b": "Coeficiente lineal de la parábola interpoladora.",
    "c": "Término independiente de la parábola interpoladora.", "Discriminante": "Valor b²-4ac.",
    "Nueva aproximación x3": "Aproximación obtenida con la parábola de Müller.",
}


def aplicar_estilo():
    st.markdown("""
    <style>
    :root { --primary:#8b5cf6; --primary-soft:#a78bfa; --accent:#f59e0b; --cyan:#22d3ee; --text:#f1f5f9; --muted:#94a3b8; --line:#26324d; --surface:#11182b; --surface-2:#151e34; --sidebar:#0b1120; }
    html, body, [class*="css"] { color:var(--text); }
    .stApp { background:radial-gradient(circle at 78% 4%,rgba(124,58,237,.18),transparent 25%),radial-gradient(circle at 38% 82%,rgba(37,99,235,.10),transparent 28%),#080c1a; color:var(--text); }
    .block-container { max-width:1360px; padding-top:1.25rem; padding-bottom:3rem; }
    [data-testid="stHeader"] { background:rgba(8,12,26,.82); border-bottom:1px solid rgba(148,163,184,.12); backdrop-filter:blur(14px); }
    [data-testid="stSidebar"] { background:linear-gradient(180deg,#0b1120,#0d1425); border-right:1px solid var(--line); }
    [data-testid="stSidebar"] .block-container { padding-top:1.5rem; }
    [data-testid="stSidebar"] * { color:var(--text); }
    [data-testid="stSidebar"] hr { border-color:var(--line); }
    .hero { position:relative; overflow:hidden; background:linear-gradient(125deg,#121a30 0%,#172044 48%,#321b63 100%); color:white; padding:1.8rem 2.2rem; border:1px solid rgba(167,139,250,.28); border-radius:20px; box-shadow:0 22px 55px rgba(0,0,0,.28),inset 0 1px rgba(255,255,255,.04); margin-bottom:1.25rem; }
    .hero:before { content:''; position:absolute; width:260px; height:260px; border-radius:50%; right:-70px; top:-135px; background:radial-gradient(circle,rgba(245,158,11,.30),rgba(124,58,237,.10) 45%,transparent 70%); }
    .hero:after { content:'Σ'; position:absolute; right:2.2rem; top:-1.2rem; font-size:8rem; color:#c4b5fd; opacity:.10; font-weight:800; }
    .hero-badge { display:inline-block; color:#ddd6fe; background:rgba(139,92,246,.12); padding:.3rem .75rem; border:1px solid rgba(167,139,250,.38); border-radius:999px; font-size:.76rem; letter-spacing:.07em; text-transform:uppercase; }
    .hero h1 { color:#fff; margin:.65rem 0 .35rem; font-size:2.25rem; letter-spacing:-.03em; }
    .hero p { color:#cbd5e1; margin:0; max-width:780px; font-size:1rem; }
    .method-card { background:linear-gradient(145deg,rgba(21,30,52,.98),rgba(15,23,42,.98)); border:1px solid var(--line); border-left:4px solid var(--primary); border-radius:15px; padding:1rem 1.2rem; margin:.35rem 0 1rem; box-shadow:0 12px 30px rgba(0,0,0,.20); }
    .method-card h3 { margin:0 0 .35rem; color:#f8fafc; font-size:1.05rem; }
    .method-card h3 span { color:#c4b5fd !important; background:rgba(139,92,246,.12); padding:.2rem .55rem; border-radius:999px; }
    .method-card p { margin:.25rem 0; color:#cbd5e1; font-size:.9rem; }
    .method-card b { color:#f8fafc; }
    .step-label { color:#a78bfa; font-weight:750; font-size:.76rem; letter-spacing:.10em; text-transform:uppercase; margin-bottom:.18rem; }
    [data-testid="stMetric"] { background:linear-gradient(145deg,#151e34,#101729); border:1px solid var(--line); padding:1rem 1.05rem; border-radius:15px; box-shadow:0 10px 24px rgba(0,0,0,.18); }
    [data-testid="stMetricLabel"] { color:var(--muted); }
    [data-testid="stMetricValue"] { color:#f8fafc; }
    .conclusion { padding:1rem 1.2rem; background:linear-gradient(135deg,rgba(91,33,182,.24),rgba(30,64,175,.18)); border:1px solid rgba(167,139,250,.38); border-radius:14px; color:#e9e5ff; line-height:1.55; }
    .stButton button, .stDownloadButton button { border-radius:10px; font-weight:650; min-height:2.7rem; background:#151e34; border:1px solid #334155; color:#f8fafc !important; box-shadow:0 5px 14px rgba(0,0,0,.16); }
    .stButton button:hover, .stDownloadButton button:hover { background:#1e2944; border-color:#8b5cf6; color:#fff !important; transform:translateY(-1px); }
    .stButton button:disabled { background:#111827 !important; border-color:#26324d !important; color:#94a3b8 !important; opacity:.72; }
    [data-testid="stBaseButton-primary"] { background:linear-gradient(100deg,#7c3aed,#9333ea 64%,#f59e0b) !important; border:0 !important; color:white !important; }
    [data-testid="stBaseButton-primary"]:hover { filter:brightness(1.10); }
    [data-baseweb="input"] > div, [data-baseweb="select"] > div, [data-baseweb="textarea"] > div { background:#0f172a !important; border-color:#334155 !important; color:#f8fafc !important; }
    input, textarea, [data-baseweb="select"] * { color:#f8fafc !important; }
    [data-testid="stFileUploaderDropzone"] { background:#11182b; border:1px dashed #475569; color:#e2e8f0; }
    [data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:14px; overflow:hidden; background:#11182b; }
    [data-testid="stExpander"] { background:#11182b; border:1px solid var(--line); border-radius:12px; }
    div[data-testid="stTabs"] button { color:#94a3b8; font-weight:650; }
    div[data-testid="stTabs"] button[aria-selected="true"] { color:#c4b5fd; }
    div[data-testid="stTabs"] [data-baseweb="tab-highlight"] { background:#8b5cf6; }
    code { color:#e9d5ff !important; }
    a { color:#a78bfa; }
    @media (max-width:700px) { .hero { padding:1.5rem; } .hero h1 { font-size:1.75rem; } .hero:after { display:none; } }
    </style>
    """, unsafe_allow_html=True)


def mostrar_encabezado():
    st.markdown('<div class="hero"><span class="hero-badge">Laboratorio académico · v2.0</span><h1>Software de Métodos Numéricos</h1><p>Analiza, aproxima y documenta raíces de funciones reales y complejas con resultados verificables.</p></div>', unsafe_allow_html=True)


def mostrar_metodo(info, metodo):
    st.markdown(f'<div class="method-card"><h3>{info["icono"]} &nbsp;{metodo} <span style="float:right;color:#2563eb;font-size:.78rem">{info["tipo"]}</span></h3><p>{info["descripcion"]}</p><p><b>Ventaja:</b> {info["ventaja"]}</p><p><b>Atención:</b> {info["limitacion"]}</p></div>', unsafe_allow_html=True)
    st.latex(info["formula"])


def formatear_numero(valor, decimales=6):
    if isinstance(valor, complex):
        if abs(valor.imag) < 1e-14:
            return f"{valor.real:.{decimales}f}"
        signo = "+" if valor.imag >= 0 else "-"
        return f"{valor.real:.{decimales}f} {signo} {abs(valor.imag):.{decimales}f}i"
    if isinstance(valor, float) and not math.isfinite(valor):
        return "No disponible"
    if isinstance(valor, (int, float)):
        return f"{valor:.{decimales}f}"
    return str(valor)


def preparar_filas(filas, metodo, decimales):
    mapeo = MAPEOS_COLUMNAS.get(metodo, {})
    salida = []
    for fila in filas:
        nueva = {}
        for clave, valor in fila.items():
            encabezado = mapeo.get(clave, clave)
            if isinstance(valor, complex):
                nueva[encabezado] = formatear_numero(valor, decimales)
            elif isinstance(valor, float) and math.isfinite(valor):
                nueva[encabezado] = round(valor, decimales)
            else:
                nueva[encabezado] = valor
        salida.append(nueva)
    return salida


def crear_csv(filas, metodo, decimales):
    return pd.DataFrame(preparar_filas(filas, metodo, decimales)).to_csv(index=False).encode("utf-8-sig")


def mostrar_explicaciones(columnas):
    with st.expander("¿Qué significa cada columna?"):
        for titulo, descripcion in EXPLICACIONES.items():
            if titulo in columnas:
                st.markdown(f"**{titulo}:** {descripcion}")


def texto_conclusion(metodo, raiz, error, iteraciones, estado, residuo, decimales):
    return (
        f"El método <strong>{metodo}</strong> finalizó con la aproximación "
        f"<strong>x = {formatear_numero(raiz, decimales)}</strong> después de "
        f"<strong>{iteraciones} iteraciones</strong>. El error aproximado final fue "
        f"<strong>{formatear_numero(error, decimales)} %</strong> y |f(x)| = "
        f"<strong>{formatear_numero(residuo, decimales)}</strong>. Estado: <strong>{estado}</strong>."
    )


def registrar_historial(estado, entrada):
    historial = estado.setdefault("historial_ejercicios", [])
    entrada = {**entrada, "fecha": datetime.now().strftime("%d/%m/%Y %H:%M")}
    historial.insert(0, entrada)
    del historial[10:]
