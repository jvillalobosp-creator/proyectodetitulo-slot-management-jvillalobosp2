import streamlit as st
from streamlit_calendar import calendar
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import qrcode
from PIL import Image
import io
import os
import requests

def send_telegram_notification(patente, cliente, fecha_hora, operacion):
    # IMPORTANTE: Reemplaza TU_CHAT_ID_AQUI con el ID que te dio @userinfobot
    TOKEN = "8842761101:AAEohY3XHP_vIBTg30EdEysjA7ISWm2VQMk"
    CHAT_ID = "5859396891"
    
    texto = f"🏢 *NUEVO AGENDAMIENTO INTERNO*\n\n" \
            f"🤝 *Cliente:* {cliente}\n" \
            f"🆔 *Patente:* {patente}\n" \
            f"⚙️ *Operación:* {operacion}\n" \
            f"⏰ *Cita:* {fecha_hora}\n\n" \
            f"🖥️ _Registrado por Personal de Planta_"
            
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, json={'chat_id': CHAT_ID, 'text': texto, 'parse_mode': 'Markdown'}, timeout=5)
    except:
        pass

# Configuración de página
st.set_page_config(page_title="Slot Management FP1", layout="wide", page_icon="📅")

# --- SISTEMA DE LOGIN (SEGURIDAD) ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown('<div style="background-color: #2D2D3F; padding: 30px; border-radius: 10px; border-top: 4px solid #FF5252; max-width: 500px; margin: 0 auto;">', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>🔒 Acceso Restringido</h3>", unsafe_allow_html=True)
    st.write("Esta herramienta es de uso exclusivo para el personal de la Planta FP1.")
    pwd = st.text_input("Ingrese la Contraseña Administrativa", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Desbloquear", use_container_width=True):
            if pwd == "tesis2026": # <--- Contraseña
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Contraseña incorrecta")
    with col2:
        if st.button("Soy Transportista", use_container_width=True):
            st.switch_page(os.path.join("pages", "1_Portal_Transportistas.py"))
            
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()
# ------------------------------------

# Estilos WOW
st.markdown("""
<style>
    .main-header { font-size: 36px; font-weight: bold; color: #00E5FF; text-align: center; margin-bottom: 20px;}
    .sub-header { font-size: 20px; color: #A0A0B0; text-align: center; margin-bottom: 30px;}
    .qr-card { background-color: #1E1E2E; padding: 20px; border-radius: 15px; box-shadow: 0 8px 16px rgba(0,0,0,0.5); text-align: center; border: 1px solid #333;}
    .form-container { background-color: #2D2D3F; padding: 30px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); border-left: 5px solid #00E5FF;}
    .stButton>button { background: linear-gradient(90deg, #00E5FF 0%, #007BFF 100%); color: white; border: none; border-radius: 8px; font-weight: bold; padding: 10px 20px; transition: transform 0.2s;}
    .stButton>button:hover { transform: scale(1.05); }
</style>
""", unsafe_allow_html=True)

def setup_db():
    conn = sqlite3.connect("planta_fp1.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Agendamientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patente TEXT NOT NULL,
            cliente TEXT NOT NULL,
            tipo_operacion TEXT NOT NULL,
            tipo_carga TEXT NOT NULL,
            fecha_hora DATETIME NOT NULL,
            estado TEXT NOT NULL
        )
    ''')
    conn.commit()
    return conn

conn = setup_db()

st.markdown('<div class="main-header">📅 Sistema de Slot Management - Planta FP1</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Gestión de Agendamientos para Andenes de Frío</div>', unsafe_allow_html=True)

tabs = st.tabs(["📊 Dashboard Calendario", "📝 Gestión de Agendamientos y QR"])

# TAB 1: Calendario
with tabs[0]:
    st.subheader("Dashboard de Agendamientos")
    
    df_citas = pd.read_sql_query("SELECT * FROM Agendamientos", conn)
    
    events = []
    for _, row in df_citas.iterrows():
        try:
            inicio = datetime.strptime(row['fecha_hora'], "%Y-%m-%d %H:%M:%S")
        except:
            inicio = pd.to_datetime(row['fecha_hora'])
            
        fin = inicio + timedelta(hours=1) # Asumimos 1 hora por slot
        
        # Color según operación
        color = "#3F51B5" if row['tipo_operacion'] == "Recepción" else "#9C27B0"
        
        events.append({
            "title": f"{row['patente']} - {row['cliente']}",
            "start": inicio.isoformat(),
            "end": fin.isoformat(),
            "backgroundColor": color,
            "borderColor": color,
        })
        
    calendar_options = {
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "timeGridDay,timeGridWeek,dayGridMonth",
        },
        "initialView": "timeGridWeek",
        "slotMinTime": "06:00:00",
        "slotMaxTime": "23:00:00",
        "allDaySlot": False,
    }
    
    if not df_citas.empty:
        calendar(events=events, options=calendar_options, custom_css="""
            .fc-event { border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }
            .fc-toolbar-title { color: #FFFFFF; font-weight: bold; }
            .fc-col-header-cell-cushion { color: #00E5FF; }
            .fc-timegrid-slot-label-cushion { color: #A0A0B0; }
        """)
        
        st.markdown("---")
        st.subheader("📋 Lista de Citas Programadas")
        st.dataframe(df_citas[['fecha_hora', 'patente', 'cliente', 'tipo_operacion', 'tipo_carga', 'estado']].sort_values('fecha_hora'), use_container_width=True, hide_index=True)
    else:
        st.info("No hay agendamientos registrados actualmente en el sistema.")

# TAB 2: Formulario de Agendamiento y QR
with tabs[1]:
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.subheader("Ingresar Nuevo Agendamiento")
    
    col_form, col_qr = st.columns([2, 1])
    
    with col_form:
        with st.form("form_agendamiento"):
            col1, col2 = st.columns(2)
            with col1:
                patente = st.text_input("Patente del Camión", placeholder="Ej: AB1234")
                cliente = st.text_input("Cliente / Proveedor", placeholder="Ej: Distribuidora Sur")
                fecha = st.date_input("Fecha de Agendamiento", min_value=datetime.today())
            with col2:
                tipo_op = st.selectbox("Tipo de Operación", ["Recepción", "Despacho"])
                tipo_carga = st.selectbox("Tipo de Carga", ["Paletizada", "Suelta"])
                hora = st.time_input("Hora de Llegada", step=1800) # Intervalos de 30 min
                
            submit_btn = st.form_submit_button("Agendar Cita (Interno)")
            
            if submit_btn:
                if not patente or not cliente:
                    st.error("Por favor, complete todos los campos obligatorios (Patente y Cliente).")
                else:
                    fecha_hora = datetime.combine(fecha, hora)
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO Agendamientos (patente, cliente, tipo_operacion, tipo_carga, fecha_hora, estado)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (patente.upper(), cliente, tipo_op, tipo_carga, fecha_hora.strftime("%Y-%m-%d %H:%M:%S"), 'Programado'))
                    conn.commit()
                    st.success(f"✅ Agendamiento para {patente} registrado con éxito el {fecha_hora.strftime('%Y-%m-%d a las %H:%M')}.")
                    
                    # Notificación Telegram
                    send_telegram_notification(
                        patente.upper(), 
                        cliente, 
                        fecha_hora.strftime('%d-%m-%Y %H:%M'), 
                        tipo_op
                    )
                    
                    st.rerun()
                    
    with col_qr:
        st.markdown('<div class="qr-card">', unsafe_allow_html=True)
        st.subheader("📲 Portal Móvil")
        st.write("QR para transportistas.")
        
        url_base = st.text_input("URL del Portal", value="http://192.168.1.6:8502", help="URL donde está alojado el portal móvil")
        
        # Generar QR dinámico
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(url_base)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        st.image(byte_im, caption="Escanea para Agendar", use_container_width=True)
        
        st.download_button(
            label="Descargar Código QR",
            data=byte_im,
            file_name="qr_agendamiento_fp1.png",
            mime="image/png"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #888; font-size: 12px; padding: 10px;'>"
    "Proyecto creado por el señor <b>Jorge Villalobos Padilla</b>, "
    "Ingeniero Industrial de la Universidad Católica de la Santísima Concepción."
    "</div>", 
    unsafe_allow_html=True
)

conn.close()
