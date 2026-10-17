from datetime import datetime
import io
from fpdf import FPDF
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Calculadora de Finiquito Chile", page_icon="⚖️", layout="centered"
)


# Función para formatear montos en pesos chilenos ($ 1.000.000 CLP)
def formatear_clp(monto):
  return f"${monto:,.0f}".replace(",", ".") + " CLP"


# Clase para la generación del reporte PDF
class PDF(FPDF):

  def header(self):
    self.set_font("Helvetica", "B", 14)
    self.cell(
        0,
        10,
        "COMPROBANTE DE ESTIMACIÓN DE FINIQUITO LABORAL",
        border=False,
        ln=True,
        align="C",
    )
    self.set_font("Helvetica", "I", 9)
    self.cell(
        0,
        5,
        "Según normativa del Código del Trabajo de Chile",
        border=False,
        ln=True,
        align="C",
    )
    self.ln(5)

  def footer(self):
    self.set_y(-15)
    self.set_font("Helvetica", "I", 8)
    self.cell(
        0,
        10,
        f"Página {self.page_no()} - Documento informativo no vinculante",
        align="C",
    )


def generar_pdf(
    fecha_inicio,
    fecha_termino,
    remuneracion,
    motivo,
    aviso,
    dias_trabajados,
    anios_indemnizacion,
    monto_anios,
    monto_aviso,
    dias_vacaciones,
    monto_feriado,
    total_finiquito,
):
  pdf = PDF()
  pdf.add_page()
  pdf.set_font("Helvetica", size=10)

  # Resumen de Datos
  pdf.set_font("Helvetica", "B", 11)
  pdf.cell(0, 7, "1. Datos del Contrato y Remuneración", ln=True)
  pdf.set_font("Helvetica", size=10)
  pdf.cell(0, 6, f"Fecha de Inicio: {fecha_inicio.strftime('%d/%m/%Y')}", ln=True)
  pdf.cell(
      0, 6, f"Fecha de Término: {fecha_termino.strftime('%d/%m/%Y')}", ln=True
  )
  pdf.cell(0, 6, f"Tiempo Total Trabajado: {dias_trabajados} días", ln=True)
  pdf.cell(
      0,
      6,
      f"Remuneración Imponible Total: {formatear_clp(remuneracion)}",
      ln=True,
  )
  pdf.cell(0, 6, f"Causal de Término: {motivo}", ln=True)
  pdf.cell(0, 6, f"Aviso Previo Dado: {aviso}", ln=True)
  pdf.ln(5)

  # Detalle de Conceptos
  pdf.set_font("Helvetica", "B", 11)
  pdf.cell(0, 7, "2. Detalle de Indemnizaciones y Haberes", ln=True)
  pdf.set_font("Helvetica", size=10)

  pdf.cell(
      0,
      6,
      f"Indemnización por Años de Servicio ({anios_indemnizacion} años):"
      f" {formatear_clp(monto_anios)}",
      ln=True,
  )
  pdf.cell(
      0,
      6,
      f"Indemnización Sustitutiva Mes de Aviso: {formatear_clp(monto_aviso)}",
      ln=True,
  )
  pdf.cell(
      0,
      6,
      f"Feriado Proporcional ({dias_vacaciones:.1f} días hábiles pendientes):"
      f" {formatear_clp(monto_feriado)}",
      ln=True,
  )
  pdf.ln(5)

  # Total
  pdf.set_font("Helvetica", "B", 12)
  pdf.cell(
      0,
      8,
      f"TOTAL ESTIMADO FINIQUITO: {formatear_clp(total_finiquito)}",
      ln=True,
  )
  pdf.ln(10)

  # Nota legal
  pdf.set_font("Helvetica", "I", 8)
  pdf.multi_cell(
      0,
      4,
      "Nota: Este documento constituye una estimación informativa basada en la"
      " normativa del Código del Trabajo de Chile (Art. 159, 161, 163, 172 y"
      " 73). No reemplaza el finiquito legal ratificado ante un ministro de fe"
      " o la Inspección del Trabajo.",
  )

  return pdf.output()


# --- INTERFAZ STREAMLIT ---
st.title("⚖️ Calculadora de Finiquito Laboral Chile")
st.markdown(
    "Calcula fácilmente tu estimación de finiquito según el **Código del"
    " Trabajo de Chile**."
)

st.header("1. Datos del Contrato")
col1, col2 = st.columns(2)

with col1:
  fecha_inicio = st.date_input(
      "Fecha de Inicio de Contrato", value=datetime(2022, 1, 1)
  )

with col2:
  fecha_termino = st.date_input("Fecha de Término de Contrato")

st.header("2. Remuneración y Causal")

remuneracion_imponible = st.number_input(
    "Remuneración Mensual Imponible Total (CLP $)",
    min_value=0,
    value=750000,
    step=10000,
    help=(
        "Sueldo base + gratificación legal mensual + bonos fijos e imponibles"
        " regulares."
    ),
)

st.info(
    "💡 **Nota legal (Art. 172):** Para las indemnizaciones de años de servicio"
    " y mes de aviso, la ley exige considerar la **última remuneración"
    " imponible completa** (incluyendo gratificación mensual y bonos fijos),"
    " excluyendo horas extras o asignaciones no imponibles."
)

motivo = st.selectbox(
    "Causal de Término de Contrato",
    [
        "Necesidades de la empresa (Art. 161)",
        "Renuncia voluntaria (Art. 159 N° 2)",
        "Vencimiento del plazo del contrato (Art. 159 N° 4)",
        "Mutuo acuerdo entre las partes (Art. 159 N° 1)",
    ],
)

aviso_previo = "No aplica"
if "Art. 161" in motivo:
  aviso_previo = st.radio(
      "¿El empleador le dio el aviso previo con 30 días de anticipación?",
      ["Sí", "No"],
      horizontal=True,
  )

st.header("3. Vacaciones / Feriado Anual")
dias_vacaciones_tomadas = st.number_input(
    "Días hábiles de vacaciones ya tomados/gozados",
    min_value=0.0,
    value=0.0,
    step=0.5,
)

st.write("")  # Espaciado

# --- LÓGICA DE CÁLCULO Y BOTÓN ---
btn_calcular = st.button(
    "📊 Calcular Finiquito", type="primary", use_container_width=True
)

if btn_calcular:
  if fecha_termino <= fecha_inicio:
    st.error(
        "La fecha de término debe ser posterior a la fecha de inicio del"
        " contrato."
    )
  else:
    dias_trabajados = (fecha_termino - fecha_inicio).days

    # 1. Años de Servicio (Art. 161 y 163)
    anios_completos = dias_trabajados // 365
    meses_remanentes = (dias_trabajados % 365) // 30

    anios_indemnizacion = 0
    monto_anios = 0

    if "Art. 161" in motivo:
      anios_indemnizacion = anios_completos
      if anios_completos >= 1 and meses_remanentes >= 6:
        anios_indemnizacion += 1
      anios_indemnizacion = min(anios_indemnizacion, 11)
      monto_anios = anios_indemnizacion * remuneracion_imponible

    # 2. Mes de Aviso Previo
    monto_aviso = 0
    if "Art. 161" in motivo and aviso_previo == "No":
      monto_aviso = remuneracion_imponible

    # 3. Feriado Proporcional (Art. 73)
    meses_totales = dias_trabajados / 30
    dias_vacaciones_ganados = meses_totales * 1.25
    dias_vacaciones_pendientes = max(
        0.0, dias_vacaciones_ganados - dias_vacaciones_tomadas
    )

    sueldo_diario = remuneracion_imponible / 30
    monto_feriado = dias_vacaciones_pendientes * sueldo_diario

    # Total
    total_finiquito = monto_anios + monto_aviso + monto_feriado

    # --- RESULTADOS EN PANTALLA ---
    st.success("### Resultado de la Estimación")

    st.metric("Total Estimado de Finiquito", formatear_clp(total_finiquito))

    st.markdown("#### Desglose de Rubros:")
    st.write(
        f"- **Indemnización por Años de Servicio ({anios_indemnizacion}"
        f" años):** {formatear_clp(monto_anios)}"
    )
    st.write(
        "- **Indemnización Sustitutiva Mes de Aviso:**"
        f" {formatear_clp(monto_aviso)}"
    )
    st.write(
        f"- **Feriado Proporcional ({dias_vacaciones_pendientes:.1f} días"
        f" pendientes):** {formatear_clp(monto_feriado)}"
    )

    # --- BOTÓN DESCARGA PDF ---
    pdf_bytes = generar_pdf(
        fecha_inicio,
        fecha_termino,
        remuneracion_imponible,
        motivo,
        aviso_previo,
        dias_trabajados,
        anios_indemnizacion,
        monto_anios,
        monto_aviso,
        dias_vacaciones_pendientes,
        monto_feriado,
        total_finiquito,
    )

    nombre_pdf = f"finiquito_estimado_{fecha_termino.strftime('%Y%m%d')}.pdf"

    st.download_button(
        label="📄 Descargar Comprobante en PDF",
        data=bytes(pdf_bytes),
        file_name=nombre_pdf,
        mime="application/pdf",
        use_container_width=True,
    )
