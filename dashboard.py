import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import time
import qrcode
import io
import socket
from zoneinfo import ZoneInfo
import random
import threading
import os

# Configuración de la página
st.set_page_config(page_title="Dashboard Dinámico FP1", layout="wide", page_icon="🏭")

# --- SISTEMA DE LOGIN (SEGURIDAD) ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col_izq, col_der = st.columns(2)
    
    with col_izq:
        st.markdown('<div style="background-color: #2D2D3F; padding: 30px; border-radius: 10px; border-top: 4px solid #FF5252;">', unsafe_allow_html=True)
        st.markdown("### 🔒 Acceso Interno Planta FP1")
        st.write("Ingrese la clave administrativa para ver el Dashboard y los KPIs.")
        pwd = st.text_input("Contraseña", type="password")
        if st.button("Ingresar al Dashboard"):
            if pwd == "tesis2026": # <--- Contraseña
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Contraseña incorrecta")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_der:
        st.markdown('<div style="background-color: #1E1E2E; padding: 30px; border-radius: 10px; border-top: 4px solid #00E5FF; text-align: center;">', unsafe_allow_html=True)
        st.markdown("### 🚚 Portal Externos")
        st.write("¿Eres una empresa de transporte o un chofer buscando agendar una cita de carga/descarga?")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Ir al Portal de Transportistas ➡️", use_container_width=True):
            st.switch_page("pages/1_Portal_Transportistas.py")
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.stop() # Detiene la ejecución del dashboard si no está logueado
# ------------------------------------

# Estilos CSS personalizados para "WOW" effect
st.markdown("""
<style>
    .kpi-card { background-color: #1E1E2E; border-radius: 10px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); text-align: center; }
    .kpi-value { font-size: 36px; font-weight: bold; color: #00E5FF; }
    .kpi-label { font-size: 14px; color: #A0A0B0; text-transform: uppercase; }
    
    .dock-card { background-color: #2D2D3F; border-radius: 12px; padding: 15px; margin-bottom: 20px; border-left: 5px solid #4CAF50; box-shadow: 0 4px 6px rgba(0,0,0,0.2); }
    .dock-card.warning { border-left-color: #FFC107; background-color: #332D20; }
    .dock-card.danger { border-left-color: #FF5252; background-color: #382525; animation: blinker 2s linear infinite; }
    .dock-card.available { border-left-color: #9E9E9E; background-color: #242433; }
    
    @keyframes blinker { 50% { opacity: 0.8; box-shadow: 0 0 15px #FF5252; } }

    .dock-title { font-size: 20px; font-weight: bold; margin-bottom: 10px; color: #FFFFFF; }
    .dock-info { font-size: 15px; color: #E0E0E0; margin: 4px 0; }
    .status-badge { display: inline-block; padding: 5px 10px; border-radius: 4px; font-size: 13px; font-weight: bold; margin-top: 10px; margin-right: 5px; }
    
    .status-recepcion { background-color: #3F51B5; color: white; }
    .status-despacho { background-color: #9C27B0; color: white; }
    .status-suelta { background-color: #E65100; color: white; }
    .status-paletizada { background-color: #006064; color: white; }
    
    .metric-row { display: flex; justify-content: space-between; background: #1b1b28; padding: 10px; border-radius: 8px; margin-top: 15px; border: 1px solid #3a3a4e;}
    .metric-item { text-align: center; width: 33%; }
    .metric-title { font-size: 12px; color: #888; text-transform: uppercase;}
    .metric-val { font-size: 20px; color: #fff; font-weight: bold;}
    .val-normal { color: #4CAF50;}
    .val-warning { color: #FFC107;}
    .val-critical { color: #FF5252;}
    
    @keyframes pulse-warning {
        0% { box-shadow: 0 0 0 0 rgba(255, 193, 7, 0.7); }
        70% { box-shadow: 0 0 0 15px rgba(255, 193, 7, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 193, 7, 0); }
    }
    @keyframes pulse-danger {
        0% { box-shadow: 0 0 0 0 rgba(255, 82, 82, 0.8); }
        70% { box-shadow: 0 0 0 20px rgba(255, 82, 82, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 82, 82, 0); }
    }
    .alert-box-warning { animation: pulse-warning 2s infinite; border: 1px solid #FFC107 !important; }
    .alert-box-danger { animation: pulse-danger 1s infinite; border: 2px solid #FF5252 !important; }
</style>
""", unsafe_allow_html=True)

def get_db_connection():
    try:
        conn = sqlite3.connect("planta_fp1.db", timeout=30.0)
        return conn
    except:
        return None

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

# --- SIDEBAR PARA CÓDIGO QR ---
with st.sidebar:
    # URLs Públicas de la Nube
    dashboard_url = "https://proyectodetitulo-slot-management-jvillalobosp2-gwoohdfkxqqvjru.streamlit.app/"
    portal_url = "https://proyectodetitulo-slot-management-jvillalobosp2-gwoohdfkxqqvjru.streamlit.app/Portal_Transportistas"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(dashboard_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()
    
    st.image(byte_im, caption="DASHBOARD EN VIVO (PÚBLICO)", use_container_width=True)
    st.markdown("---")
    
    st.markdown("### 🚚 Portal Transportistas")
    st.info(f"Link de Agendamiento:\n{portal_url}")
    
    qr_p = qrcode.QRCode(version=1, box_size=10, border=4)
    qr_p.add_data(portal_url)
    qr_p.make(fit=True)
    img_p = qr_p.make_image(fill_color="black", back_color="white")
    
    buf_p = io.BytesIO()
    img_p.save(buf_p, format="PNG")
    st.image(buf_p.getvalue(), caption="PORTAL MÓVIL (PÚBLICO)", use_container_width=True)

st.title("🏭 Panel de Monitoreo Dinámico - Planta FP1 Talcahuano")

# --- AUTO-INICIO DEL SIMULADOR PARA LA NUBE ---
@st.cache_resource
def start_background_simulator():
    try:
        import db_simulator
        thread = threading.Thread(target=db_simulator.run_simulation, daemon=True)
        thread.start()
        return True
    except Exception as e:
        return False

start_background_simulator()
# ----------------------------------------------

hora_chile = datetime.now(ZoneInfo('America/Santiago')).strftime('%H:%M:%S')
st.markdown(f"<h3 style='text-align: center; color: #00E5FF; margin-top: -15px;'>🕒 Hora Actual (Chile): {hora_chile}</h3>", unsafe_allow_html=True)

conn = get_db_connection()
if not conn:
    st.error("No se encontró la base de datos. Ejecuta 'python db_simulator.py' en otra terminal.")
    st.stop()

# Leer datos en vivo con mecanismo de espera (para la nube)
tablas_listas = False
for _ in range(5):
    try:
        df_andenes = pd.read_sql_query("SELECT * FROM Andenes", conn)
        df_camiones = pd.read_sql_query("SELECT * FROM Camiones", conn)
        df_sensores = pd.read_sql_query("SELECT * FROM Sensores_IoT", conn)
        tablas_listas = True
        break
    except:
        time.sleep(1)

if not tablas_listas:
    st.warning("⏳ Construyendo planta en la nube... Esto toma unos segundos. La página se recargará automáticamente.")
    time.sleep(2)
    st.rerun()

try:
    df_agendamientos = pd.read_sql_query("SELECT * FROM Agendamientos", conn)
except:
    df_agendamientos = pd.DataFrame()
conn.close()

if df_camiones.empty or df_andenes.empty:
    st.warning("⏳ Ingresando primeros camiones al simulador... por favor espera un momento.")
    time.sleep(2)
    st.rerun()

# Convertir fechas
df_camiones['hora_llegada'] = pd.to_datetime(df_camiones['hora_llegada'])
df_camiones['hora_inicio_anden'] = pd.to_datetime(df_camiones['hora_inicio_anden'])
df_camiones['cita_programada'] = pd.to_datetime(df_camiones['cita_programada'])

ahora = datetime.now()

# KPIs Globales
camiones_en_planta = len(df_camiones[df_camiones['estado'] != 'Finalizado'])
andenes_ocupados = len(df_andenes[df_andenes['estado'] == 'Ocupado'])
utilizacion = (andenes_ocupados / 10) * 100
camiones_en_patio = len(df_camiones[df_camiones['estado'] == 'En Patio'])

col1, col2, col3, col4 = st.columns(4)
col1.markdown(f'<div class="kpi-card"><div class="kpi-value">{camiones_en_planta}</div><div class="kpi-label">Camiones en Planta</div></div>', unsafe_allow_html=True)
col2.markdown(f'<div class="kpi-card"><div class="kpi-value">{andenes_ocupados}/10</div><div class="kpi-label">Andenes en Uso</div></div>', unsafe_allow_html=True)
col3.markdown(f'<div class="kpi-card"><div class="kpi-value">{utilizacion:.0f}%</div><div class="kpi-label">Utilización</div></div>', unsafe_allow_html=True)
col4.markdown(f'<div class="kpi-card"><div class="kpi-value">{camiones_en_patio}</div><div class="kpi-label">En Patio (Espera)</div></div>', unsafe_allow_html=True)

st.markdown("---")

# Crear las pestañas (Tabs): Visión Global + 10 Andenes
nombres_tabs = ["Visión Global"] + [f"Andén {i}" for i in range(1, 11)]
tabs = st.tabs(nombres_tabs)

# --- TAB 0: Visión Global ---
with tabs[0]:
    st.subheader("⏱️ Mapa de Andenes")
    filas = [st.columns(5), st.columns(5)]
    
    for idx, row in df_andenes.iterrows():
        anden_id = row['id_anden']
        estado_anden = row['estado']
        camion_id = row['camion_actual_id']
        col_dest = filas[0][idx] if idx < 5 else filas[1][idx - 5]
        
        if estado_anden == 'Ocupado' and pd.notna(camion_id):
            camion_info = df_camiones[df_camiones['id_camion'] == camion_id].iloc[0]
            if pd.notna(camion_info['hora_inicio_anden']):
                mins_trans = int((ahora - camion_info['hora_inicio_anden']).total_seconds() / 60)
            else:
                mins_trans = 0
                
            css_class = "dock-card"
            # KPI Alarma
            if mins_trans >= 130: css_class += " danger"
            elif mins_trans >= 90: css_class += " warning"
                
            op_class = "status-recepcion" if camion_info['tipo_operacion'] == 'Recepción' else "status-despacho"
            carga_class = "status-paletizada" if camion_info['tipo_carga'] == 'Paletizada' else "status-suelta"

            html = f"""
            <div class="{css_class}">
                <div class="dock-title">Andén {anden_id}</div>
                <div class="dock-info">⏱️ {mins_trans} min</div>
                <div class="dock-info">🚛 {camion_info['patente']}</div>
                <div class="dock-info" style="font-size: 13px; color: #B0B0C0; margin-bottom: 5px;">🏢 {camion_info['cliente']}</div>
                <div><span class="status-badge {op_class}">{camion_info['tipo_operacion']}</span></div>
            </div>
            """
        else:
            html = f'<div class="dock-card available"><div class="dock-title" style="color: #9E9E9E;">Andén {anden_id}</div><div class="dock-info">Disponible</div><br><br></div>'
        col_dest.markdown(html, unsafe_allow_html=True)

    st.markdown("---")
    
    colA, colB = st.columns(2)
    with colA:
        st.subheader("📋 Recepción en Patio (Espera actual)")
        df_espera = df_camiones[df_camiones['estado'] == 'En Patio'].copy()
        if not df_espera.empty:
            df_espera['Espera (min)'] = ((ahora - df_espera['hora_llegada']).dt.total_seconds() / 60).astype(int)
            st.dataframe(df_espera[['patente', 'cliente', 'tipo_operacion', 'tipo_carga', 'Espera (min)']], use_container_width=True, hide_index=True)
        else:
            st.success("Patio despejado.")
            
    with colB:
        st.subheader("📅 Próximos Agendamientos (Slot Management)")
        if not df_agendamientos.empty:
            # Filtrar agendamientos futuros
            df_agendamientos['fecha_hora'] = pd.to_datetime(df_agendamientos['fecha_hora'])
            futuros = df_agendamientos[df_agendamientos['fecha_hora'] >= ahora].sort_values('fecha_hora').head(10)
            if not futuros.empty:
                futuros['Fecha / Hora'] = futuros['fecha_hora'].dt.strftime('%d-%m-%Y %H:%M')
                st.dataframe(futuros[['Fecha / Hora', 'patente', 'cliente', 'tipo_operacion', 'tipo_carga']], use_container_width=True, hide_index=True)
            else:
                st.info("No hay agendamientos futuros programados.")
        else:
            st.info("Sin datos de agendamiento.")

# --- TABS 1 al 10: Detalle por Andén ---
for i in range(1, 11):
    with tabs[i]:
        anden_data = df_andenes[df_andenes['id_anden'] == i].iloc[0]
        st.subheader(f"Monitor Detallado - Andén {i}")
        
        if anden_data['estado'] == 'Ocupado' and pd.notna(anden_data['camion_actual_id']):
            camion_info = df_camiones[df_camiones['id_camion'] == anden_data['camion_actual_id']].iloc[0]
            if pd.notna(camion_info['hora_inicio_anden']):
                mins = int((ahora - camion_info['hora_inicio_anden']).total_seconds() / 60)
            else:
                mins = 0
            
            # Variables de ET1
            proceso = camion_info['tipo_operacion']
            carga = camion_info['tipo_carga']
            cliente = camion_info['cliente']
            patente = camion_info['patente']
            temperatura = camion_info.get('temperatura', -18.0)
            if pd.isna(temperatura): temperatura = -18.0
            
            # Variables propuestas para mejorar monitoreo
            eta_mins = max(0, 150 - mins) if proceso == 'Despacho' else max(0, 45 - mins)
            
            # Alarmas visuales (KPI de tiempo)
            if mins >= 130:
                alerta_texto = "🚨 CRÍTICO - RIESGO DE INCUMPLIMIENTO KPI"
                color_clase = "val-critical"
                alerta_bg = "#382525"
                border_color = "#FF5252"
                extra_css = "alert-box-danger"
            elif mins >= 90:
                alerta_texto = "⚠️ PRECAUCIÓN - SUPERVISAR DESEMPEÑO"
                color_clase = "val-warning"
                alerta_bg = "#332D20"
                border_color = "#FFC107"
                extra_css = "alert-box-warning"
            else:
                alerta_texto = "✅ OPERACIÓN NORMAL"
                color_clase = "val-normal"
                alerta_bg = "#1b1b28"
                border_color = "#4CAF50"
                extra_css = ""

            # Alarma de Cadena de Frío
            frio_alerta = ""
            temp_clase = "val-normal"
            if temperatura > -12.0:
                frio_alerta = "<div style='background-color:#FF5252; color:white; padding:10px; border-radius:5px; margin-bottom:15px; font-weight:bold; text-align:center;'>❄️ ¡ALERTA CRÍTICA DE CADENA DE FRÍO! EXPOSICIÓN PROLONGADA ❄️</div>"
                temp_clase = "val-critical"
            elif temperatura > -15.0:
                frio_alerta = "<div style='background-color:#FFC107; color:black; padding:10px; border-radius:5px; margin-bottom:15px; font-weight:bold; text-align:center;'>❄️ ADVERTENCIA: TEMPERATURA DE CARGA ACERCÁNDOSE A LÍMITE (-15°C) ❄️</div>"
                temp_clase = "val-warning"
            else:
                temp_clase = "val-normal"
                
            st.markdown(f"""
            {frio_alerta}
            <div class="{extra_css}" style="background-color: {alerta_bg}; border-left: 6px solid {border_color}; padding: 20px; border-radius: 8px;">
                <h3 style="margin-top:0;">Estado: {alerta_texto}</h3>
                <div style="display:flex; justify-content:space-between;">
                    <div>
                        <p><b>🚚 Patente:</b> {patente}</p>
                        <p><b>🏢 Cliente:</b> {cliente}</p>
                        <p><b>🔄 Proceso:</b> {proceso} de Carga {carga}</p>
                    </div>
                </div>
                <div class="metric-row">
                    <div class="metric-item">
                        <div class="metric-title">Tiempo Transcurrido</div>
                        <div class="metric-val {color_clase}">{mins} mins</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-title">Límite KPI</div>
                        <div class="metric-val">150 mins</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-title">ETA (Restante)</div>
                        <div class="metric-val">{eta_mins} mins</div>
                    </div>
                    <div class="metric-item" style="border-left: 1px solid #3a3a4e; padding-left: 10px;">
                        <div class="metric-title">Temp. Carga</div>
                        <div class="metric-val {temp_clase}">{temperatura:.1f} °C</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Progress bar para visualización rápida del tiempo (Max 150 mins)
            progress = min(mins / 150.0, 1.0)
            porcentaje = progress * 100
            texto_progreso = f"Tiempo consumido del KPI máximo ({porcentaje:.1f}%)"
            
            st.progress(progress, text=texto_progreso)
                
        else:
            st.success(f"El Andén {i} se encuentra actualmente **DISPONIBLE** y listo para recibir un nuevo camión.")
            st.info("Revisando asignaciones automáticas en el patio...")

        st.markdown("---")
        # --- Módulo IoT LoRaWAN (Real DB) ---
        st.markdown(f"### 📡 Módulo IoT: Monitoreo LoRaWAN (lps8v2 gateway lorawan 4g lte & MOKOSmart LW007-PIR - Tag {i})")
        
        if 'df_sensores' in locals() and not df_sensores.empty:
            sensor_data = df_sensores[df_sensores['id_anden'] == i].iloc[0]
            hay_movimiento = bool(sensor_data['movimiento'])
            temp_sensor = sensor_data['temperatura']
            bateria = sensor_data['bateria']
            rssi = sensor_data['rssi']
            
            # ultima_lectura puede venir como string o datetime, dependiendo de la BD y SQLite
            ultima_lectura_str = sensor_data['ultima_lectura']
            try:
                ultima_lectura = pd.to_datetime(ultima_lectura_str)
                segundos_inactivo = int((ahora - ultima_lectura).total_seconds())
            except:
                segundos_inactivo = 0
                
            estado_enlace = "🟢 En Línea" if segundos_inactivo < 15 else "🔴 Con Retraso"
            
            col_iot1, col_iot2, col_iot3 = st.columns(3)
            
            with col_iot1:
                st.markdown("<div style='background-color:#1E1E2E; padding:15px; border-radius:8px; height:100%; border: 1px solid #333;'>", unsafe_allow_html=True)
                st.markdown(f"#### 🌡️ Sensor Temperatura (Tag {i})")
                
                if pd.isna(temp_sensor) or temp_sensor is None:
                    st.markdown("<div style='font-size:24px; font-weight:bold; color:#A0A0B0; margin-top:10px;'>En Reposo</div>", unsafe_allow_html=True)
                    st.markdown("<div style='color:#A0A0B0; font-size:14px; margin-top:5px;'>Precámara (5°C)</div>", unsafe_allow_html=True)
                else:
                    color_temp = "#4CAF50" # Verde
                    if temp_sensor > -15.0: color_temp = "#FFC107" # Amarillo
                    if temp_sensor > -12.0: color_temp = "#FF5252" # Rojo
                    
                    st.markdown(f"<div style='font-size:32px; font-weight:bold; color:{color_temp}; margin-top:10px;'>{temp_sensor:.1f} °C</div>", unsafe_allow_html=True)
                    if temp_sensor > -15.0:
                        st.markdown("<div style='color:#FFC107; font-size:14px; margin-top:5px;'>⚠️ Acercándose a límite (-15°C)</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div style='color:#4CAF50; font-size:14px; margin-top:5px;'>✅ Temperatura óptima</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with col_iot2:
                st.markdown("<div style='background-color:#1E1E2E; padding:15px; border-radius:8px; height:100%; border: 1px solid #333;'>", unsafe_allow_html=True)
                st.markdown(f"#### 🚶 Sensor de Movimiento (PIR) - Tag {i}")
                if hay_movimiento:
                    st.markdown("<div style='color:#4CAF50; font-size:18px; margin-top:15px;'><b>🟢 DETECTANDO ACTIVIDAD</b></div>", unsafe_allow_html=True)
                    st.markdown("<div style='color:#A0A0B0; font-size:14px; margin-top:5px;'>Registrando presencia de personal/maquinaria.</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div style='color:#FF5252; font-size:18px; margin-top:15px;'><b>🔴 SIN MOVIMIENTO</b></div>", unsafe_allow_html=True)
                    st.markdown("<div style='color:#A0A0B0; font-size:14px; margin-top:5px;'>Área despejada.</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
            with col_iot3:
                st.markdown("<div style='background-color:#1E1E2E; padding:15px; border-radius:8px; height:100%; border: 1px solid #333;'>", unsafe_allow_html=True)
                st.markdown("#### 🌐 Enlace LoRaWAN")
                st.markdown(f"<div style='margin-top:10px; font-size:15px;'><b>Estado:</b> {estado_enlace}</div>", unsafe_allow_html=True)
                
                color_bat = "#4CAF50" if bateria > 20 else "#FF5252"
                st.markdown(f"<div style='margin-top:5px; font-size:15px;'><b>🔋 Batería:</b> <span style='color:{color_bat};'>{bateria}%</span></div>", unsafe_allow_html=True)
                
                color_rssi = "#4CAF50" if rssi > -85 else ("#FFC107" if rssi > -105 else "#FF5252")
                st.markdown(f"<div style='margin-top:5px; font-size:15px;'><b>📶 Señal (RSSI):</b> <span style='color:{color_rssi};'>{rssi} dBm</span></div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Buscando señal de sensores IoT...")

# Footer del creador
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #888; font-size: 12px; padding: 10px;'>"
    "Proyecto creado por el señor <b>Jorge Villalobos Padilla</b>, "
    "Ingeniero Industrial de la Universidad Católica de la Santísima Concepción."
    "</div>", 
    unsafe_allow_html=True
)

# Autorefresh cada 3 segundos
time.sleep(10)
st.rerun()
