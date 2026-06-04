import streamlit as st
import sqlite3
from datetime import datetime
import requests
import qrcode
import io

# Configuración enfocada en móviles
st.set_page_config(page_title="Check-In Portería FP1", layout="wide", page_icon="🛑")

def send_checkin_notification(patente, cliente, fecha_hora):
    # IMPORTANTE: Debes configurar tu TOKEN y CHAT_ID reales para que funcione
    TOKEN = "8842761101:AAEohY3XHP_vIBTg30EdEysjA7ISWm2VQMk" 
    CHAT_ID = "5859396891"
    
    texto = f"🛑 *NUEVO INGRESO A PLANTA*\n\n" \
            f"🚛 *El camión patente* {patente} *acaba de registrar su llegada en portería.*\n\n" \
            f"🏢 *Cliente:* {cliente}\n" \
            f"⏰ *Agendamiento original:* {fecha_hora}\n\n" \
            f"⚠️ _A la espera de asignación de andén._"
            
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, json={'chat_id': CHAT_ID, 'text': texto, 'parse_mode': 'Markdown'}, timeout=5)
    except:
        pass

st.markdown("""
<style>
    .mobile-header { font-size: 28px; font-weight: bold; color: #00E5FF; text-align: center; margin-bottom: 10px;}
    .mobile-subheader { font-size: 16px; color: #A0A0B0; text-align: center; margin-bottom: 20px;}
    .form-box { background-color: #2D2D3F; padding: 30px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.4); border-top: 4px solid #FF5252;}
    .stButton>button { background: linear-gradient(90deg, #FF5252 0%, #E64A19 100%); color: white; border: none; border-radius: 8px; font-weight: bold; padding: 15px; width: 100%; transition: transform 0.2s; font-size: 18px;}
    .stButton>button:hover { transform: scale(1.02); }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="mobile-header">🛑 Control de Ingreso FP1</div>', unsafe_allow_html=True)
st.markdown('<div class="mobile-subheader">Notifica tu llegada al patio de maniobras</div>', unsafe_allow_html=True)

def setup_db():
    conn = sqlite3.connect("planta_fp1.db", timeout=30.0)
    return conn

conn = setup_db()

col_form, col_qr = st.columns([2, 1])

with col_form:
    st.markdown('<div class="form-box">', unsafe_allow_html=True)
    with st.form("checkin_mobile"):
        st.subheader("Confirma tu Llegada")
        patente = st.text_input("Ingresa tu Patente", placeholder="Ej: AB1234").upper()
        
        submitted = st.form_submit_button("Registrar Ingreso al Patio")
        
        if submitted:
            if not patente:
                st.error("❌ Por favor, ingresa tu patente.")
            else:
                cursor = conn.cursor()
                # Buscar si el camión tiene un agendamiento programado para hoy o pendiente
                cursor.execute("SELECT id, cliente, fecha_hora FROM Agendamientos WHERE patente = ? AND estado = 'Programado'", (patente,))
                cita = cursor.fetchone()
                
                if cita:
                    id_cita, cliente, fecha_hora = cita
                    # Actualizar estado
                    cursor.execute("UPDATE Agendamientos SET estado = 'En Patio' WHERE id = ?", (id_cita,))
                    conn.commit()
                    
                    # Notificar a Telegram
                    send_checkin_notification(patente, cliente, fecha_hora)
                    
                    st.success(f"✅ ¡Bienvenido! Tu llegada ha sido notificada a la planta.")
                    st.info(f"**Empresa:** {cliente}\n\n**Cita:** {fecha_hora}\n\nPor favor, espera en el patio hasta que se te asigne un andén de descarga/carga.")
                    st.balloons()
                else:
                    st.error("❌ No se encontró un agendamiento 'Programado' para esta patente. Por favor verifica en portería o realiza un agendamiento.")
    st.markdown('</div>', unsafe_allow_html=True)

with col_qr:
    st.markdown('<div class="form-box" style="text-align: center; border-top: 4px solid #FF5252;">', unsafe_allow_html=True)
    st.subheader("🛑 QR Portería")
    st.write("Escanea este código para acceder rápidamente desde tu móvil.")
    
    port_url = "https://proyectodetitulo-slot-management-jvillalobosp2-gwoohdfkxqqvjru.streamlit.app/CheckIn_Porteria"
    qr_p = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
    qr_p.add_data(port_url)
    qr_p.make(fit=True)
    img_p = qr_p.make_image(fill_color="#FF5252", back_color="white")
    buf_p = io.BytesIO()
    img_p.save(buf_p, format="PNG")
    
    st.image(buf_p.getvalue(), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br><p style='text-align: center; color: #888; font-size: 11px;'>Desarrollado por Jorge Villalobos Padilla</p>", unsafe_allow_html=True)

conn.close()
