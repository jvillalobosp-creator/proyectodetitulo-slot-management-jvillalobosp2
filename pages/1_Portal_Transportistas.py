import streamlit as st
import sqlite3
from datetime import datetime, timedelta
import qrcode
import io
import socket
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
    # IMPORTANTE: Debes configurar tu TOKEN y CHAT_ID reales para que funcione
    TOKEN = "8842761101:AAEohY3XHP_vIBTg30EdEysjA7ISWm2VQMk" 
    CHAT_ID = "5859396891"
    
    texto = f"🚛 *NUEVO AGENDAMIENTO MÓVIL*\n\n" \
            f"🏢 *Cliente:* {cliente}\n" \
            f"🆔 *Patente:* {patente}\n" \
            f"⚙️ *Operación:* {operacion}\n" \
            f"⏰ *Cita:* {fecha_hora}\n\n" \
            f"📱 _Enviado desde el Portal de Transportistas_"
            
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, json={'chat_id': CHAT_ID, 'text': texto, 'parse_mode': 'Markdown'}, timeout=5)
    except:
        pass
        
    # Enviar notificación a correo electrónico
    send_email_notification(patente, cliente, fecha_hora, operacion, "Portal Móvil - Transportistas")

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
    conn = sqlite3.connect("planta_fp1.db", timeout=30.0)
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
            hora = st.time_input("Hora Estimada", step=900)
        
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
                    fecha_hora_str = fecha_hora_sel.strftime("%Y-%m-%d %H:%M:%S")
                    
                    is_madrugada = fecha_hora_sel.hour >= 23 or fecha_hora_sel.hour < 7
                    if is_madrugada and tipo_op == "Despacho":
                        st.error("❌ El turno de madrugada (23:00 a 07:00) está restringido exclusivamente para operaciones de Recepción (Descarga).")
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
                        if not is_slot_available(fecha_hora_sel, tipo_carga):
                            next_slot = fecha_hora_sel
                            while True:
                                next_slot += timedelta(minutes=15)
                                if tipo_op == "Despacho" and (next_slot.hour >= 23 or next_slot.hour < 7):
                                    if next_slot.hour < 7:
                                        next_slot = next_slot.replace(hour=7, minute=0)
                                    else:
                                        next_slot = next_slot.replace(hour=7, minute=0) + timedelta(days=1)
                                
                                if is_slot_available(next_slot, tipo_carga):
                                    break
                            
                            st.error(f"❌ El horario choca con operaciones en curso para carga {tipo_carga}.")
                            st.warning(f"💡 Próximo horario libre disponible: **{next_slot.strftime('%d-%m-%Y a las %H:%M')}**")
                        else:
                            cursor.execute('''
                                INSERT INTO Agendamientos (patente, cliente, tipo_operacion, tipo_carga, fecha_hora, estado)
                                VALUES (?, ?, ?, ?, ?, ?)
                            ''', (patente.upper(), cliente, tipo_op, tipo_carga, fecha_hora_str, 'Programado'))
                            conn.commit()
                            st.success(f"✅ ¡Éxito! Cita agendada para la patente {patente.upper()} el día {fecha_hora_sel.strftime('%d-%m-%Y a las %H:%M')}.")
                        
                        # Enviar notificación a Telegram
                        send_telegram_notification(
                            patente.upper(), 
                            cliente, 
                            fecha_hora_sel.strftime('%d-%m-%Y %H:%M'), 
                            tipo_op
                        )
                        
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
