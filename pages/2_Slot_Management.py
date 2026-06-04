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

def send_email_notification(patente, cliente, fecha_hora, operacion, tipo_origen):
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    # Intentar obtener credenciales desde st.secrets, o usar valores por defecto/configurables
    try:
        sender_email = st.secrets.get("EMAIL_SENDER", "jvpdashboard@gmail.com")
        sender_password = st.secrets.get("EMAIL_PASSWORD", "")
    except Exception:
        sender_email = "jvpdashboard@gmail.com"
        sender_password = ""

    # Si no hay contraseña configurada en secrets ni en código, no intentamos enviar para evitar esperas/bloqueos
    if not sender_password:
        print("⚠️ Advertencia: No se ha configurado la contraseña de aplicación de correo (EMAIL_PASSWORD) en st.secrets.")
        return

    asunto = f"🚛 Nuevo Agendamiento ({tipo_origen}) - Patente {patente}"
    receiver_email = "jvpdashboard@gmail.com"
    
    cuerpo_html = f"""
    <html>
    <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; color: #333333;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-top: 5px solid #00E5FF;">
            <!-- Encabezado -->
            <div style="background: linear-gradient(135deg, #1e1e2e 0%, #2d2d3f 100%); padding: 30px 20px; text-align: center; color: #ffffff;">
                <h1 style="margin: 0; font-size: 24px; letter-spacing: 1px; color: #00E5FF;">🚛 NUEVO AGENDAMIENTO</h1>
                <p style="margin: 5px 0 0 0; font-size: 14px; color: #a0a0b0; text-transform: uppercase;">Notificación de Sistema - Planta FP1</p>
            </div>
            
            <!-- Contenido principal -->
            <div style="padding: 30px 25px;">
                <p style="font-size: 16px; line-height: 1.6; color: #4e5d6c; margin-top: 0;">
                    Estimado Administrador, se ha registrado exitosamente una nueva cita en el sistema de slots. A continuación se presentan los detalles del agendamiento:
                </p>
                
                <div style="background-color: #f8fafc; border-radius: 8px; padding: 20px; border: 1px solid #e2e8f0; margin: 25px 0;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr style="border-bottom: 1px solid #edf2f7;">
                            <td style="padding: 12px 0; font-weight: bold; color: #4a5568; width: 40%; font-size: 14px;">🏢 Empresa / Cliente:</td>
                            <td style="padding: 12px 0; color: #1a202c; font-size: 15px;">{cliente}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #edf2f7;">
                            <td style="padding: 12px 0; font-weight: bold; color: #4a5568; font-size: 14px;">🆔 Patente:</td>
                            <td style="padding: 12px 0; color: #1a202c; font-size: 15px; font-weight: bold;">{patente}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #edf2f7;">
                            <td style="padding: 12px 0; font-weight: bold; color: #4a5568; font-size: 14px;">⚙️ Operación:</td>
                            <td style="padding: 12px 0; color: #1a202c; font-size: 15px;">
                                <span style="background-color: {'#eef2ff' if operacion == 'Recepción' else '#faf5ff'}; color: {'#3730a3' if operacion == 'Recepción' else '#6b21a8'}; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 13px;">
                                    {operacion}
                                </span>
                            </td>
                        </tr>
                        <tr style="border-bottom: 1px solid #edf2f7;">
                            <td style="padding: 12px 0; font-weight: bold; color: #4a5568; font-size: 14px;">⏰ Fecha y Hora:</td>
                            <td style="padding: 12px 0; color: #007BFF; font-size: 15px; font-weight: bold;">{fecha_hora}</td>
                        </tr>
                        <tr>
                            <td style="padding: 12px 0; font-weight: bold; color: #4a5568; font-size: 14px;">📱 Origen del Registro:</td>
                            <td style="padding: 12px 0; color: #718096; font-size: 14px; font-style: italic;">{tipo_origen}</td>
                        </tr>
                    </table>
                </div>
                
                <p style="font-size: 14px; color: #718096; line-height: 1.5; margin-bottom: 0;">
                    Por favor, asegúrese de que el andén correspondiente esté preparado a la hora citada para mantener la fluidez logística y la cadena de frío.
                </p>
            </div>
            
            <!-- Pie de página -->
            <div style="background-color: #f7fafc; padding: 20px; text-align: center; border-top: 1px solid #edf2f7;">
                <p style="margin: 0; font-size: 12px; color: #a0aec0; font-weight: bold;">SISTEMA DE SLOT MANAGEMENT - PLANTA FP1 TALCAHUANO</p>
                <p style="margin: 5px 0 0 0; font-size: 11px; color: #cbd5e0;">
                    Desarrollado por Jorge Villalobos Padilla<br>
                    Ingeniero Industrial - Universidad Católica de la Santísima Concepción
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = asunto
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg.attach(MIMEText(cuerpo_html, "html"))
    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, [receiver_email], msg.as_string())
        server.quit()
        print("✅ Correo enviado exitosamente a jvpdashboard@gmail.com")
    except Exception as e:
        print(f"❌ Error al enviar correo de notificación: {e}")

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
        
    # Enviar notificación a correo electrónico
    send_email_notification(patente, cliente, fecha_hora, operacion, "Registro Interno - Planta")

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
            st.switch_page("pages/1_Portal_Transportistas.py")
            
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
    conn = sqlite3.connect("planta_fp1.db", timeout=30.0)
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
st.markdown("---")
# KPIs Superiores
df_citas = pd.read_sql_query("SELECT * FROM Agendamientos", conn)
hoy = datetime.now().date()

try:
    df_citas['fecha_dt'] = pd.to_datetime(df_citas['fecha_hora'])
    df_hoy = df_citas[df_citas['fecha_dt'].dt.date == hoy]
    citas_hoy = len(df_hoy)
    completadas_hoy = len(df_hoy[df_hoy['estado'].isin(['Completado', 'Descargando', 'Cargando'])])
    en_patio = len(df_citas[df_citas['estado'] == 'En Patio'])
    recepciones_hoy = len(df_hoy[df_hoy['tipo_operacion'] == 'Recepción'])
    despachos_hoy = len(df_hoy[df_hoy['tipo_operacion'] == 'Despacho'])
except:
    citas_hoy, completadas_hoy, en_patio, recepciones_hoy, despachos_hoy = 0, 0, 0, 0, 0

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric("📅 Agendado Hoy (Meta: 30)", citas_hoy, delta=f"{citas_hoy - 30} sobre la meta" if citas_hoy >= 30 else f"{30 - citas_hoy} faltantes")
with kpi2:
    st.metric("✅ Operaciones Avanzadas Hoy", completadas_hoy, delta=f"{citas_hoy - completadas_hoy} restantes", delta_color="inverse")
with kpi3:
    st.metric("🛑 Camiones En Patio", en_patio)
with kpi4:
    st.metric("📊 Mix Operativo (Hoy)", f"📥 {recepciones_hoy} | 📤 {despachos_hoy}")

st.markdown("---")

col_calendario, col_panel = st.columns([2, 1])

with col_calendario:
    st.subheader("📊 Monitoreo de Andenes")
    events = []
    for _, row in df_citas.iterrows():
        try:
            inicio = pd.to_datetime(row['fecha_hora'])
        except:
            continue
            
        duracion_min = 285 if row['tipo_carga'] == 'Suelta' else 105
        fin = inicio + timedelta(minutes=duracion_min)
        color = "#3F51B5" if row['tipo_operacion'] == "Recepción" else "#9C27B0"
        
        titulo = f"[{row['estado']}] {row['patente']} - {row['cliente']}" if row['estado'] == 'En Patio' else f"{row['patente']} - {row['cliente']}"
        bg_color = "#FF5252" if row['estado'] == 'En Patio' else color
        
        events.append({
            "title": titulo,
            "start": inicio.isoformat(),
            "end": fin.isoformat(),
            "backgroundColor": bg_color,
            "borderColor": bg_color,
        })
        
    calendar_options = {
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "timeGridDay,timeGridWeek,dayGridMonth",
        },
        "initialView": "timeGridDay",
        "allDaySlot": False,
    }
    
    if not df_citas.empty:
        calendar(events=events, options=calendar_options, custom_css="""
            .fc-event { border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }
            .fc-toolbar-title { color: #FFFFFF; font-weight: bold; }
            .fc-col-header-cell-cushion { color: #00E5FF; }
            .fc-timegrid-slot-label-cushion { color: #A0A0B0; }
        """)
    else:
        st.info("No hay agendamientos registrados actualmente.")

with col_panel:
    st.subheader("🚛 Camiones en Patio")
    df_patio = df_citas[df_citas['estado'] == 'En Patio']
    if not df_patio.empty:
        for _, row in df_patio.iterrows():
            st.markdown(f"""
            <div style="background-color: #332D20; border-left: 4px solid #FFC107; padding: 10px; margin-bottom: 10px; border-radius: 5px;">
                <b>Patente:</b> {row['patente']} <br>
                <b>Empresa:</b> {row['cliente']} <br>
                <b>Operación:</b> {row['tipo_operacion']}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("No hay camiones en espera.")

    st.markdown("---")
    st.subheader("📝 Cita Manual (Interno)")
    with st.expander("Ingresar Nuevo Agendamiento", expanded=False):
        with st.form("form_agendamiento"):
            patente = st.text_input("Patente del Camión", placeholder="Ej: AB1234")
            cliente = st.text_input("Cliente / Proveedor", placeholder="Ej: Distribuidora Sur")
            fecha = st.date_input("Fecha de Agendamiento", min_value=datetime.today())
            tipo_op = st.selectbox("Tipo de Operación", ["Recepción", "Despacho"])
            tipo_carga = st.selectbox("Tipo de Carga", ["Paletizada", "Suelta"])
            hora = st.time_input("Hora de Llegada", step=900) # Intervalos de 15 min
            
            submit_btn = st.form_submit_button("Agendar Cita")
            
            if submit_btn:
                if not patente or not cliente:
                    st.error("Campos obligatorios incompletos.")
                else:
                    fecha_hora = datetime.combine(fecha, hora)
                    fecha_hora_str = fecha_hora.strftime("%Y-%m-%d %H:%M:%S")
                    
                    is_madrugada = fecha_hora.hour >= 23 or fecha_hora.hour < 7
                    if is_madrugada and tipo_op == "Despacho":
                        st.error("❌ El turno de madrugada (23:00 a 07:00) está restringido para Recepción.")
                    else:
                        def is_slot_available(dt, carga):
                            duracion = 285 if carga == 'Suelta' else 105
                            dt_end = dt + timedelta(minutes=duracion)
                            cursor.execute("""
                                SELECT COUNT(*) FROM Agendamientos 
                                WHERE fecha_hora < ? 
                                  AND (
                                    CASE WHEN tipo_carga = 'Suelta' THEN datetime(fecha_hora, '+285 minutes')
                                         ELSE datetime(fecha_hora, '+105 minutes')
                                    END
                                  ) > ?
                            """, (dt_end.strftime("%Y-%m-%d %H:%M:%S"), dt.strftime("%Y-%m-%d %H:%M:%S")))
                            return cursor.fetchone()[0] < 4

                        cursor = conn.cursor()
                        if not is_slot_available(fecha_hora, tipo_carga):
                            next_slot = fecha_hora
                            while True:
                                next_slot += timedelta(minutes=15)
                                if tipo_op == "Despacho" and (next_slot.hour >= 23 or next_slot.hour < 7):
                                    if next_slot.hour < 7:
                                        next_slot = next_slot.replace(hour=7, minute=0)
                                    else:
                                        next_slot = next_slot.replace(hour=7, minute=0) + timedelta(days=1)
                                
                                if is_slot_available(next_slot, tipo_carga):
                                    break
                            
                            st.error(f"❌ El bloque seleccionado choca con operaciones en curso para una carga {tipo_carga}.")
                            st.warning(f"💡 Próximo horario libre disponible: **{next_slot.strftime('%d-%m-%Y a las %H:%M')}**")
                        else:
                            cursor.execute('''
                                INSERT INTO Agendamientos (patente, cliente, tipo_operacion, tipo_carga, fecha_hora, estado)
                                VALUES (?, ?, ?, ?, ?, ?)
                            ''', (patente.upper(), cliente, tipo_op, tipo_carga, fecha_hora_str, 'Programado'))
                            conn.commit()
                            st.success(f"✅ Agendamiento para {patente} registrado con éxito.")
                            
                            send_telegram_notification(patente.upper(), cliente, fecha_hora.strftime('%d-%m-%Y %H:%M'), tipo_op)
                            st.rerun()

st.markdown("---")
st.subheader("📋 Lista de Citas Programadas")
st.dataframe(df_citas[['fecha_hora', 'patente', 'cliente', 'tipo_operacion', 'tipo_carga', 'estado']].sort_values('fecha_hora'), use_container_width=True, hide_index=True)

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
