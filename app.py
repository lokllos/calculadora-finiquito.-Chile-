import datetime
import io
import math
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import streamlit as st

# 1. Configuración de la página web
st.set_page_config(
    page_title="Calculadora de Finiquito Chile",
    page_icon="⚖️",
    layout="centered",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": (
            "### Calculadora de Finiquito Laboral Chile\nDesarrollada por"
            " **Adrian Cazor**\nIngeniería en Administración de Empresas."
        ),
    },
)

# 2. INYECCIÓN DE ESTILOS CSS (ALTO CONTRASTE Y ENMARCADO AZUL CORPORATIVO)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    .stApp {
        background-color: #f8fafc !important;
        color: #000000 !important;
        font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
        border-left: 8px solid #1e3a8a !important;
        border-right: 8px solid #1e3a8a !important;
        box-sizing: border-box !important;
    }

    p, label, span, .stMarkdown, .stRadio, .stNumberInput, .stDateInput {
        color: #000000 !important;
        font-weight: 500 !important;
    }

    h2, h3, h4 {
        color: #0f172a !important;
        font-weight: 700 !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.75rem !important;
    }

    h1 {
        color: #1e3a8a !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
    }

    div[data-baseweb="input"] input, div[data-baseweb="select"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        border-radius: 8px !important;
    }

    div[data-baseweb="select"] > div {
        border: 1.5px solid #cbd5e1 !important;
        background-color: #ffffff !important;
    }

    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"], li[role="option"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        font-weight: 500 !important;
    }

    div.stButton > button, div.stDownloadButton > button {
        background: linear-gradient(90deg, #1e3a8a 0%, #1e40af 100%) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.2rem !important;
        margin-top: 0.5rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(30, 58, 138, 0.2) !important;
    }

    div.stButton > button:hover, div.stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(30, 58, 138, 0.4) !important;
    }

    div[data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        color: #15803d !important;
    }

    .footer {
        margin-top: 3rem;
        padding: 1.5rem;
        text-align: center;
        background-color: #f1f5f9;
        border: 1px solid #cbd5e1;
        border-top: 3px solid #1e3a8a;
        border-radius: 10px;
    }
    .footer p {
        margin: 0;
        color: #334155 !important;
        font-size: 0.95rem;
    }
    .footer strong {
        color: #1e3a8a !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def formato_clp(monto):
  return f"${int(round(monto)):,}".replace(",", ".")


def limpiar_texto(texto):
  replacements = {
      "Á": "A",
      "É": "E",
      "Í": "I",
      "Ó": "O",
      "Ú": "U",
      "á": "a",
      "é": "e",
      "í": "i",
      "ó": "o",
      "ú": "u",
      "Ñ": "N",
      "ñ": "n",
      "°": " deg.",
  }
  for orig, repl in replacements.items():
    texto = texto.replace(orig, repl)
  return texto


# --- FUNCIÓN PARA GENERAR EL COMPROBANTE PDF EN MEMORIA ---
def generar_pdf_comprobante(
    fecha_ini,
    fecha_ter,
    sueldo,
    causal,
    aviso,
    dias_trab,
    monto_anos,
    monto_aviso,
    monto_feriado,
    monto_ext,
    total,
):
  pdf = FPDF()
  pdf.add_page()
  pdf.set_auto_page_break(auto=True, margin=15)

  # Encabezado
  pdf.set_font("Helvetica", "B", 15)
  pdf.set_text_color(30, 58, 138)
  pdf.cell(
      0,
      10,
      "COMPROBANTE DE CALCULO DE FINIQUITO LABORAL",
      new_x=XPos.LMARGIN,
      new_y=YPos.NEXT,
      align="C",
  )
  pdf.set_font("Helvetica", "", 10)
  pdf.set_text_color(100, 100, 100)
  pdf.cell(
      0,
      6,
      f"Fecha de emision: {datetime.date.today().strftime('%d/%m/%Y')}",
      new_x=XPos.LMARGIN,
      new_y=YPos.NEXT,
      align="C",
  )
  pdf.ln(6)

  # Línea divisoria
  pdf.set_draw_color(30, 58, 138)
  pdf.set_line_width(0.8)
  pdf.line(10, pdf.get_y(), 200, pdf.get_y())
  pdf.ln(6)

  # Sección 1: Datos Contractuales
  pdf.set_font("Helvetica", "B", 11)
  pdf.set_text_color(15, 23, 42)
  pdf.cell(
      0, 7, "1. RESUMEN CONTRACTUAL", new_x=XPos.LMARGIN, new_y=YPos.NEXT
  )

  pdf.set_font("Helvetica", "", 10)
  pdf.set_text_color(0, 0, 0)
  pdf.cell(
      0,
      6,
      f"Periodo trabajado: Desde {fecha_ini.strftime('%d/%m/%Y')} hasta"
      f" {fecha_ter.strftime('%d/%m/%Y')} ({dias_trab} dias)",
      new_x=XPos.LMARGIN,
      new_y=YPos.NEXT,
  )
  pdf.cell(
      0,
      6,
      f"Sueldo Base Mensual: {formato_clp(sueldo)} CLP",
      new_x=XPos.LMARGIN,
      new_y=YPos.NEXT,
  )
  pdf.cell(
      0,
      6,
      f"Causal de termino: {limpiar_texto(causal)}",
      new_x=XPos.LMARGIN,
      new_y=YPos.NEXT,
  )
  pdf.cell(
      0,
      6,
      f"Aviso previo (30 dias): {limpiar_texto(aviso)}",
      new_x=XPos.LMARGIN,
      new_y=YPos.NEXT,
  )
  pdf.ln(6)

  # Sección 2: Desglose de Haberes
  pdf.set_font("Helvetica", "B", 11)
  pdf.set_text_color(15, 23, 42)
  pdf.cell(
      0,
      7,
      "2. DESGLOSE DE INDEMNIZACIONES Y HABERES",
      new_x=XPos.LMARGIN,
      new_y=YPos.NEXT,
  )

  pdf.set_font("Helvetica", "", 10)
  pdf.cell(
      0,
      6,
      f"- Indemnizacion por Anos de Servicio: {formato_clp(monto_anos)} CLP",
      new_x=XPos.LMARGIN,
      new_y=YPos.NEXT,
  )
  pdf.cell(
      0,
      6,
      f"- Indemnizacion Mes de Aviso Previo: {formato_clp(monto_aviso)} CLP",
      new_x=XPos.LMARGIN,
      new_y=YPos.NEXT,
  )
  pdf.cell(
      0,
      6,
      f"- Feriado Proporcional (Vacaciones): {formato_clp(monto_feriado)} CLP",
      new_x=XPos.LMARGIN,
      new_y=YPos.NEXT,
  )
  pdf.cell(
      0,
      6,
      f"- Turnos / Haberes Pendientes: {formato_clp(monto_ext)} CLP",
      new_x=XPos.LMARGIN,
      new_y=YPos.NEXT,
  )
  pdf.ln(6)

  # Recuadro Total
  pdf.set_fill_color(241, 245, 249)
  pdf.set_draw_color(21, 128, 61)
  pdf.rect(10, pdf.get_y(), 190, 16, style="FD")

  pdf.set_xy(15, pdf.get_y() + 3)
  pdf.set_font("Helvetica", "B", 12)
  pdf.set_text_color(21, 128, 61)
  pdf.cell(
      0,
      10,
      f"TOTAL ESTIMADO A PAGAR: {formato_clp(total)} CLP",
      new_x=XPos.LMARGIN,
      new_y=YPos.NEXT,
  )
  pdf.ln(12)

  # Nota legal
  pdf.set_font("Helvetica", "I", 8)
  pdf.set_text_color(100, 100, 100)
  pdf.multi_cell(
      0,
      4,
      "Nota: Este documento constituye una estimacion informativa basada en"
      " las disposiciones del Codigo del Trabajo de Chile y no reemplaza el"
      " finiquito oficial firmado ante ministro de fe.",
  )
  pdf.ln(8)

  # Firma institucional
  pdf.set_font("Helvetica", "B", 10)
  pdf.set_text_color(30, 58, 138)
  pdf.cell(
      0,
      5,
      "Desarrollado por: Adrian Cazor",
      new_x=XPos.LMARGIN,
      new_y=YPos.NEXT,
      align="C",
  )
  pdf.set_font("Helvetica", "", 9)
  pdf.set_text_color(71, 85, 105)
  pdf.cell(
      0,
      5,
      "Ingenieria en Administracion de Empresas",
      new_x=XPos.LMARGIN,
      new_y=YPos.NEXT,
      align="C",
  )

  return bytes(pdf.output())


# --- ENCABEZADO Y PRESENTACIÓN ---
st.title("⚖️ Calculadora de Finiquito Laboral")
st.write(
    "Herramienta profesional para calcular el finiquito de trabajo según el"
    " Código del Trabajo de Chile."
)

st.markdown("---")

FECHA_MINIMA = datetime.date(2000, 1, 1)
FECHA_MAXIMA = datetime.date.today()

# --- SECCIÓN 1: DATOS CONTRACTUALES ---
st.header("1. Datos Contractuales y Fechas")

col1, col2 = st.columns(2)
with col1:
  fecha_inicio = st.date_input(
      "Fecha de Inicio de Contrato",
      value=datetime.date(2022, 1, 1),
      min_value=FECHA_MINIMA,
      max_value=FECHA_MAXIMA,
      help="Seleccione la fecha de inicio (Mínimo: Año 2000)",
  )
with col2:
  fecha_termino = st.date_input(
      "Fecha de Término de Contrato",
      value=FECHA_MAXIMA,
      min_value=FECHA_MINIMA,
      max_value=FECHA_MAXIMA,
      help="Seleccione la fecha de término (Máximo: Año en curso)",
  )

sueldo_base = st.number_input(
    "Sueldo Base Mensual (CLP $)", min_value=0, value=600000, step=10000
)

st.markdown("### Causal de Término de Contrato")
motivo = st.selectbox(
    "Seleccione la causal legal correspondiente:",
    [
        "Necesidades de la empresa (Art. 161)",
        "Renuncia voluntaria (Art. 159 N° 2)",
        "Vencimiento del plazo del contrato (Art. 159 N° 4)",
        "Mutuo acuerdo entre las partes (Art. 159 N° 1)",
    ],
    label_visibility="collapsed",
)

if "Art. 161" in motivo:
  st.info(
      "💡 **Efecto legal:** Esta causal genera derecho a Indemnización por"
      " Años de Servicio y Mes de Aviso (si corresponde)."
  )
else:
  st.warning(
      "ℹ️ **Efecto legal:** Esta causal **no** genera indemnización por años de"
      " servicio. Solo considera feriado proporcional y haberes pendientes."
  )

st.markdown("### ¿Se dio aviso previo con 30 días de anticipación?")
aviso_previo = st.radio(
    "Aviso previo",
    ["Sí", "No (Corresponde indemnización)"],
    label_visibility="collapsed",
)

# --- SECCIÓN 2: HABERES Y TURNOS EXTRAS ---
st.header("2. Turnos Extras y Haberes Pendientes")

monto_extras = st.number_input(
    "Monto por Turnos Extras / Horas Extras pendientes (CLP $)",
    min_value=0,
    value=0,
    step=5000,
)

dias_vacaciones_tomadas = st.number_input(
    "Días de vacaciones tomados en el último periodo",
    min_value=0,
    max_value=30,
    value=0,
)

st.markdown("---")

# --- LÓGICA DE CÁLCULO Y GENERACIÓN DE COMPROBANTE ---
if st.button("📊 Calcular Finiquito Exacto", use_container_width=True):
  if fecha_termino < fecha_inicio:
    st.error(
        "❌ **Error en las fechas:** La fecha de término no puede ser anterior"
        " a la fecha de inicio del contrato. Por favor corrija la fecha e"
        " intente de nuevo."
    )
    st.session_state["calculado"] = False
  else:
    dias_trabajados = (fecha_termino - fecha_inicio).days

    if dias_trabajados == 0:
      st.error(
          "❌ **Error en las fechas:** La fecha de término debe ser al menos"
          " un día posterior a la fecha de inicio."
      )
      st.session_state["calculado"] = False
    else:
      anios_completos = dias_trabajados // 365
      meses_remanentes = (dias_trabajados % 365) // 30

      anios_indemnizacion = anios_completos
      if anios_completos >= 1 and meses_remanentes >= 6:
        anios_indemnizacion += 1

      anios_indemnizacion = min(anios_indemnizacion, 11)

      if "Art. 161" in motivo:
        monto_anos_servicio = sueldo_base * anios_indemnizacion
      else:
        monto_anos_servicio = 0

      if "Art. 161" in motivo and "No" in aviso_previo:
        monto_aviso_previo = sueldo_base
      else:
        monto_aviso_previo = 0

      meses_totales = dias_trabajados / 30
      dias_vacaciones_ganados = meses_totales * 1.25
      dias_vacaciones_pendientes = max(
          0, dias_vacaciones_ganados - dias_vacaciones_tomadas
      )

      sueldo_diario = sueldo_base / 30
      monto_feriado = dias_vacaciones_pendientes * sueldo_diario

      total_finiquito = (
          monto_anos_servicio
          + monto_aviso_previo
          + monto_feriado
          + monto_extras
      )

      st.session_state["total_finiquito"] = total_finiquito
      st.session_state["desglose_texto"] = f"""
    - **Tiempo trabajado:** {anios_completos} años y {meses_remanentes} meses ({dias_trabajados} días totales).
    - **Indemnización Años de Servicio:** {formato_clp(monto_anos_servicio)} ({anios_indemnizacion} años reconocidos por ley)
    - **Indemnización Mes de Aviso Previo:** {formato_clp(monto_aviso_previo)}
    - **Feriado Proporcional ({dias_vacaciones_pendientes:.1f} días):** {formato_clp(monto_feriado)}
    - **Turnos extras / Haberes pendientes:** {formato_clp(monto_extras)}
    """

      st.session_state["pdf_bytes"] = generar_pdf_comprobante(
          fecha_inicio,
          fecha_termino,
          sueldo_base,
          motivo,
          aviso_previo,
          dias_trabajados,
          monto_anos_servicio,
          monto_aviso_previo,
          monto_feriado,
          monto_extras,
          total_finiquito,
      )
      st.session_state["calculado"] = True

# Despliegue persistente de resultados y botón de descarga PDF
if st.session_state.get("calculado", False):
  st.success("¡Cálculo realizado con éxito!")
  st.metric(
      "TOTAL A PAGAR POR EL EMPLEADOR",
      formato_clp(st.session_state["total_finiquito"]),
  )

  st.subheader("Desglose detallado del finiquito:")
  st.markdown(st.session_state["desglose_texto"])

  st.markdown("---")
  st.subheader("📄 Descargar Comprobante")
  st.download_button(
      label="⬇️ Descargar Comprobante en PDF",
      data=st.session_state["pdf_bytes"],
      file_name=(
          f"Comprobante_Finiquito_{datetime.date.today().strftime('%Y%m%d')}.pdf"
      ),
      mime="application/pdf",
      use_container_width=True,
  )

# --- PIE DE PÁGINA ---
st.markdown(
    """
    <div class="footer">
        <p>👨‍💻 Aplicación desarrollada por <strong>Adrian Cazor</strong></p>
        <p>Ingeniería en Administración de Empresas</p>
    </div>
    """,
    unsafe_allow_html=True,
)