import streamlit as st
import sqlite3
from datetime import datetime, timedelta
import qrcode
import io
import socket

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

# Configuración enfocada en móviles y kioskos
st.set_page_config(page_title="Portal Agendamiento FP1", layout="wide", page_icon="📱")

st.markdown("""
<style>
    .mobile-header { font-size: 28px; font-weight: bold; color: #00E5FF; text-align: center; margin-bottom: 10px;}
    .mobile-subheader { font-size: 16px; color: #A0A0B0; text-align: center; margin-bottom: 20px;}
    .form-box { background-color: #2D2D3F; padding: 20px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.4); border-top: 4px solid #00E5FF;}
    .stButton>button { background: linear-gradient(90deg, #00E5FF 0%, #007BFF 100%); color: white; border: none; border-radius: 8px; font-weight: bold; padding: 15px; width: 100%; transition: transform 0.2s;}
    .stButton>button:hover { transform: scale(1.02); }
    .warning-box { background-color: #332D20; border-left: 4px solid #FFC107; padding: 10px; margin-bottom: 20px; border-radius: 5px; color: #E0E0E0;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="mobile-header">🚚 Portal de Agendamiento FP1</div>', unsafe_allow_html=True)
st.markdown('<div class="mobile-subheader">Gestión de Andenes de Frío para Transportistas</div>', unsafe_allow_html=True)

st.markdown("""
<div class="warning-box">
    ⚠️ <b>Atención:</b> Los agendamientos solo pueden realizarse con un mínimo de <b>24 horas</b> y un máximo de <b>48 horas</b> de anticipación.
</div>
""", unsafe_allow_html=True)

def setup_db():
    conn = sqlite3.connect("planta_fp1.db")
    return conn

conn = setup_db()

ahora = datetime.now()
min_fecha = (ahora + timedelta(hours=24)).date()
max_fecha = (ahora + timedelta(hours=48)).date()

col_izq, col_der = st.columns([2, 1])

with col_izq:
    st.markdown('<div class="form-box">', unsafe_allow_html=True)
    with st.form("agendamiento_mobile"):
        st.subheader("Datos del Viaje")
        patente = st.text_input("Patente del Camión", placeholder="Ej: AB1234")
        cliente = st.text_input("Empresa / Proveedor", placeholder="Ej: Transportes Sur")
        
        st.write("---")
        st.subheader("Detalles de Carga")
        col1, col2 = st.columns(2)
        with col1:
            tipo_op = st.selectbox("Operación", ["Recepción", "Despacho"])
        with col2:
            tipo_carga = st.selectbox("Formato", ["Paletizada", "Suelta"])
        
        st.write("---")
        st.subheader("Programación (24-48 hrs)")
        col3, col4 = st.columns(2)
        with col3:
            fecha = st.date_input("Fecha de Llegada", min_value=min_fecha, max_value=max_fecha, value=min_fecha)
        with col4:
            hora = st.time_input("Hora Estimada", step=1800)
        
        submitted = st.form_submit_button("Confirmar Agendamiento")
        
        if submitted:
            if not patente or not cliente:
                st.error("❌ Por favor, ingrese Patente y Empresa.")
            else:
                fecha_hora_sel = datetime.combine(fecha, hora)
                diferencia_horas = (fecha_hora_sel - ahora).total_seconds() / 3600
                
                if diferencia_horas < 24 or diferencia_horas > 48:
                    st.error(f"❌ La fecha seleccionada ({fecha_hora_sel.strftime('%d-%m %H:%M')}) no cumple con la regla de 24 a 48 horas de anticipación.")
                else:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO Agendamientos (patente, cliente, tipo_operacion, tipo_carga, fecha_hora, estado)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (patente.upper(), cliente, tipo_op, tipo_carga, fecha_hora_sel.strftime("%Y-%m-%d %H:%M:%S"), 'Programado'))
                    conn.commit()
                    st.success(f"✅ ¡Éxito! Cita agendada para la patente {patente.upper()} el día {fecha_hora_sel.strftime('%d-%m-%Y a las %H:%M')}.")
                    st.balloons()
    st.markdown('</div>', unsafe_allow_html=True)

with col_der:
    st.markdown('<div class="form-box" style="text-align: center;">', unsafe_allow_html=True)
    st.subheader("📲 Escanea y Agenda")
    st.write("Si lo prefieres, escanea este QR para llenar el formulario directamente desde tu celular.")
    
    url_portal = f"http://{get_local_ip()}:8502"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url_portal)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()
    
    st.image(byte_im, caption=f"Acceso móvil: {url_portal}", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br><p style='text-align: center; color: #888; font-size: 11px;'>Desarrollado por Jorge Villalobos Padilla</p>", unsafe_allow_html=True)

conn.close()
