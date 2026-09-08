from io import BytesIO
import math
from datetime import datetime
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.graphics.shapes import Circle, Drawing, Line, PolyLine, String


AZUL_OSCURO = colors.HexColor("#0F172A")
AZUL = colors.HexColor("#1D4ED8")
AZUL_CLARO = colors.HexColor("#EFF6FF")
GRIS = colors.HexColor("#475569")
GRIS_CLARO = colors.HexColor("#F8FAFC")
VERDE = colors.HexColor("#15803D")
ROJO = colors.HexColor("#B91C1C")


def _texto_numero(valor, decimales=8):
    if valor is None:
        return "—"
    if isinstance(valor, complex):
        if abs(valor.imag) < 1e-14:
            return f"{valor.real:.{decimales}f}"
        signo = "+" if valor.imag >= 0 else "−"
        return f"{valor.real:.{decimales}f} {signo} {abs(valor.imag):.{decimales}f}i"
    if isinstance(valor, float):
        if not math.isfinite(valor):
            return "No disponible"
        return f"{valor:.{decimales}f}"
    return str(valor)


def _parrafo(texto, estilo):
    return Paragraph(escape(str(texto)).replace("\n", "<br/>"), estilo)


def _encabezado_pie(canvas, documento):
    canvas.saveState()
    ancho, alto = landscape(A4)
    canvas.setFillColor(AZUL_OSCURO)
    canvas.rect(0, alto - 1.15 * cm, ancho, 1.15 * cm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(1.3 * cm, alto - 0.72 * cm, "SOFTWARE DE MÉTODOS NUMÉRICOS")
    canvas.setFillColor(GRIS)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(1.3 * cm, 0.65 * cm, "Reporte académico generado automáticamente")
    canvas.drawCentredString(ancho / 2, 0.65 * cm, datetime.now().strftime("%d/%m/%Y · %H:%M"))
    canvas.drawRightString(ancho - 1.3 * cm, 0.65 * cm, f"Página {documento.page}")
    canvas.restoreState()


def _grafica_reporte(expresion, raiz, iteraciones, limites):
    """Crea una gráfica vectorial ligera para incrustarla en el PDF."""
    ancho, alto = 700, 220
    dibujo = Drawing(ancho, alto)
    margen_x, margen_y = 44, 28
    util_x, util_y = ancho - 2 * margen_x, alto - 2 * margen_y
    raiz_compleja = complex(raiz)
    es_compleja = abs(raiz_compleja.imag) >= 1e-14
    if es_compleja:
        valores = [complex(fila["x3"]) for fila in iteraciones if "x3" in fila] or [raiz_compleja]
        reales = [v.real for v in valores] + [raiz_compleja.real, 0]
        imaginarios = [v.imag for v in valores] + [raiz_compleja.imag, 0]
        x_min, x_max = min(reales), max(reales)
        y_min, y_max = min(imaginarios), max(imaginarios)
        titulo = "Recorrido de aproximaciones en el plano complejo"
    else:
        if expresion is None or limites is None:
            return None
        x_min, x_max = limites
        muestras = []
        for indice in range(180):
            x = x_min + (x_max - x_min) * indice / 179
            try:
                y = float(expresion.subs({"x": x}).evalf())
                if math.isfinite(y) and abs(y) < 1e8:
                    muestras.append((x, y))
            except (TypeError, ValueError, OverflowError, ZeroDivisionError):
                continue
        if not muestras:
            return None
        valores = muestras
        ordenados = sorted(y for _, y in muestras)
        y_min = ordenados[max(0, int(len(ordenados) * 0.02) - 1)]
        y_max = ordenados[min(len(ordenados) - 1, int(len(ordenados) * 0.98))]
        titulo = "Comportamiento de f(x) y raíz aproximada"
    if abs(x_max - x_min) < 1e-12:
        x_min, x_max = x_min - 1, x_max + 1
    if abs(y_max - y_min) < 1e-12:
        y_min, y_max = y_min - 1, y_max + 1
    margen_vertical = (y_max - y_min) * 0.12
    y_min, y_max = y_min - margen_vertical, y_max + margen_vertical

    def px(x):
        return margen_x + (x - x_min) / (x_max - x_min) * util_x

    def py(y):
        return margen_y + (y - y_min) / (y_max - y_min) * util_y

    dibujo.add(String(margen_x, alto - 12, titulo, fontName="Helvetica-Bold", fontSize=10, fillColor=AZUL_OSCURO))
    for paso in range(6):
        gx = margen_x + util_x * paso / 5
        gy = margen_y + util_y * paso / 5
        dibujo.add(Line(gx, margen_y, gx, margen_y + util_y, strokeColor=colors.HexColor("#E2E8F0"), strokeWidth=0.5))
        dibujo.add(Line(margen_x, gy, margen_x + util_x, gy, strokeColor=colors.HexColor("#E2E8F0"), strokeWidth=0.5))
    if x_min <= 0 <= x_max:
        dibujo.add(Line(px(0), margen_y, px(0), margen_y + util_y, strokeColor=GRIS, strokeWidth=0.8))
    if y_min <= 0 <= y_max:
        dibujo.add(Line(margen_x, py(0), margen_x + util_x, py(0), strokeColor=GRIS, strokeWidth=0.8))
    if es_compleja:
        coordenadas = [(px(v.real), py(v.imag)) for v in valores]
    else:
        coordenadas = [(px(x), py(max(y_min, min(y_max, y)))) for x, y in valores]
    if len(coordenadas) > 1:
        dibujo.add(PolyLine(coordenadas, strokeColor=AZUL, strokeWidth=1.6))
    dibujo.add(Circle(px(raiz_compleja.real), py(raiz_compleja.imag if es_compleja else 0), 4.5, fillColor=ROJO, strokeColor=colors.white, strokeWidth=1))
    dibujo.add(String(margen_x, 7, f"x: [{x_min:.3g}, {x_max:.3g}]", fontName="Helvetica", fontSize=7, fillColor=GRIS))
    dibujo.add(String(ancho - 150, 7, f"y: [{y_min:.3g}, {y_max:.3g}]", fontName="Helvetica", fontSize=7, fillColor=GRIS))
    return dibujo


def crear_pdf(titulo, funcion, metodo, parametros, valor_criterio, raiz,
              error_final, iteraciones, criterio, estado, motivo,
              expresion=None, limites=None, residuo=None, tiempo=None):
    """Genera un reporte PDF completo y legible del ejercicio resuelto."""
    salida = BytesIO()
    documento = SimpleDocTemplate(
        salida,
        pagesize=landscape(A4),
        rightMargin=1.3 * cm,
        leftMargin=1.3 * cm,
        topMargin=1.65 * cm,
        bottomMargin=1.25 * cm,
        title=titulo,
        author="Software de Métodos Numéricos",
    )
    estilos_base = getSampleStyleSheet()
    titulo_estilo = ParagraphStyle(
        "TituloReporte", parent=estilos_base["Title"], fontName="Helvetica-Bold",
        fontSize=22, leading=26, textColor=AZUL_OSCURO, alignment=TA_LEFT,
        spaceAfter=8,
    )
    subtitulo = ParagraphStyle(
        "Subtitulo", parent=estilos_base["Heading2"], fontName="Helvetica-Bold",
        fontSize=13, leading=16, textColor=AZUL_OSCURO, spaceBefore=10, spaceAfter=7,
    )
    normal = ParagraphStyle(
        "NormalReporte", parent=estilos_base["BodyText"], fontName="Helvetica",
        fontSize=9, leading=13, textColor=GRIS,
    )
    pequeno = ParagraphStyle(
        "Pequeno", parent=normal, fontSize=6.2, leading=8, alignment=TA_CENTER,
    )
    pequeno_izquierda = ParagraphStyle(
        "PequenoIzquierda", parent=pequeno, alignment=TA_LEFT,
    )
    etiqueta = ParagraphStyle(
        "Etiqueta", parent=normal, fontName="Helvetica-Bold", textColor=AZUL_OSCURO,
    )
    raiz_estilo = ParagraphStyle(
        "Raiz", parent=normal, fontName="Helvetica-Bold", fontSize=14,
        leading=18, textColor=AZUL,
    )

    historia = [
        Spacer(1, 0.2 * cm),
        _parrafo("Reporte completo del ejercicio", titulo_estilo),
        _parrafo("Resumen del procedimiento, resultado e historial de iteraciones.", normal),
        Spacer(1, 0.35 * cm),
    ]

    datos_principales = [
        [_parrafo("Método", etiqueta), _parrafo(metodo, normal),
         _parrafo("Función", etiqueta), _parrafo(funcion, normal)],
        [_parrafo("Criterio", etiqueta), _parrafo(criterio, normal),
         _parrafo("Valor solicitado", etiqueta), _parrafo(_texto_numero(valor_criterio), normal)],
    ]
    tabla_principal = Table(datos_principales, colWidths=[2.6 * cm, 7.2 * cm, 3.2 * cm, 12.1 * cm])
    tabla_principal.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), GRIS_CLARO),
        ("BACKGROUND", (0, 0), (0, -1), AZUL_CLARO),
        ("BACKGROUND", (2, 0), (2, -1), AZUL_CLARO),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    historia.append(tabla_principal)

    if isinstance(parametros, dict):
        parametros_visibles = [
            (clave, valor) for clave, valor in parametros.items()
            if clave in {"a", "b", "x0", "x1", "x2"}
        ]
        if parametros_visibles:
            historia.extend([Spacer(1, 0.25 * cm), _parrafo("Datos iniciales", subtitulo)])
            celdas = [[_parrafo(clave, etiqueta), _parrafo(_texto_numero(valor), normal)] for clave, valor in parametros_visibles]
            tabla_parametros = Table(celdas, colWidths=[2.2 * cm, 5.2 * cm], hAlign="LEFT")
            tabla_parametros.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (0, -1), AZUL_CLARO),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]))
            historia.append(tabla_parametros)

    color_estado = VERDE if "Convergi" in estado else (ROJO if "No convergi" in estado else AZUL)
    resultado_tabla = Table([
        [_parrafo("RAÍZ APROXIMADA", etiqueta), _parrafo("ERROR FINAL (%)", etiqueta),
         _parrafo("ITERACIONES", etiqueta), _parrafo("ESTADO", etiqueta)],
        [_parrafo(_texto_numero(raiz), raiz_estilo), _parrafo(_texto_numero(error_final), raiz_estilo),
         _parrafo(len(iteraciones), raiz_estilo), _parrafo(estado, raiz_estilo)],
    ], colWidths=[8.2 * cm, 5.5 * cm, 4.5 * cm, 6.8 * cm])
    resultado_tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), AZUL_OSCURO),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 1), (-1, 1), colors.white),
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#CBD5E1")),
        ("LINEBEFORE", (3, 1), (3, 1), 4, color_estado),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    historia.extend([
        Spacer(1, 0.35 * cm),
        _parrafo("Resultado", subtitulo),
        resultado_tabla,
        Spacer(1, 0.25 * cm),
        KeepTogether([
            _parrafo("Motivo de detención", etiqueta),
            _parrafo(motivo, normal),
        ]),
    ])

    detalles = []
    if residuo is not None:
        detalles.append(f"Residuo |f(x)|: {_texto_numero(residuo)}")
    if tiempo is not None:
        detalles.append(f"Tiempo de cálculo: {tiempo * 1000:.3f} ms")
    if detalles:
        historia.extend([Spacer(1, 0.18 * cm), _parrafo(" · ".join(detalles), normal)])

    grafica = _grafica_reporte(expresion, raiz, iteraciones, limites)
    if grafica is not None:
        historia.extend([_parrafo("Representación gráfica", subtitulo), grafica])

    if iteraciones:
        historia.extend([PageBreak(), _parrafo("Historial completo de iteraciones", subtitulo)])
        columnas = list(iteraciones[0].keys())
        encabezados = [_parrafo(columna, pequeno) for columna in columnas]
        cuerpo = [encabezados]
        for fila in iteraciones:
            cuerpo.append([_parrafo(_texto_numero(fila.get(columna)), pequeno_izquierda) for columna in columnas])
        ancho_util = landscape(A4)[0] - 2.6 * cm
        pesos = [max(5, min(18, len(str(columna)))) for columna in columnas]
        total_pesos = sum(pesos)
        anchos = [ancho_util * peso / total_pesos for peso in pesos]
        tabla_iteraciones = Table(cuerpo, colWidths=anchos, repeatRows=1)
        tabla_iteraciones.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), AZUL_OSCURO),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, GRIS_CLARO]),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E1")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 2),
            ("RIGHTPADDING", (0, 0), (-1, -1), 2),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        historia.append(tabla_iteraciones)

    historia.extend([
        Spacer(1, 0.35 * cm),
        _parrafo("Interpretación", subtitulo),
        _parrafo(
            "La raíz aproximada es el valor de x para el cual f(x) es cero o suficientemente cercano a cero. "
            "El historial conserva la precisión utilizada durante el cálculo; los valores del reporte se formatean solo para facilitar su lectura.",
            normal,
        ),
    ])
    documento.build(historia, onFirstPage=_encabezado_pie, onLaterPages=_encabezado_pie)
    return salida.getvalue()
