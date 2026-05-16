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
            st.switch_page(os.path.join("pages", "1_Portal_Transportistas.py"))
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
</style>
""", unsafe_allow_html=True)

def get_db_connection():
    try:
        conn = sqlite3.connect("planta_fp1.db")
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
    st.markdown("### 📱 Monitoreo Móvil")
    st.write("Escanea este código para llevar el dashboard en tu celular o tablet (requiere Wi-Fi local).")
    
    local_ip = get_local_ip()
    dashboard_url = f"http://{local_ip}:8501"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(dashboard_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()
    
    st.image(byte_im, caption=dashboard_url, use_container_width=True)
    st.markdown("---")
    
    st.markdown("### 🚚 Portal Transportistas")
    portal_url = f"http://{local_ip}:8502"
    st.info(f"URL de Agendamiento:\n{portal_url}")

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
            equipo = camion_info['equipo_asignado']
            temperatura = camion_info.get('temperatura', -18.0)
            if pd.isna(temperatura): temperatura = -18.0
            
            # Variables propuestas para mejorar monitoreo
            velocidad = "2.3 pallets/min" if carga == "Paletizada" else "0.8 bultos/min"
            eta_mins = max(0, 150 - mins) if proceso == 'Despacho' else max(0, 45 - mins)
            
            # Alarmas visuales (KPI de tiempo)
            if mins >= 130:
                alerta_texto = "🚨 CRÍTICO - RIESGO DE INCUMPLIMIENTO KPI"
                color_clase = "val-critical"
                alerta_bg = "#382525"
                border_color = "#FF5252"
            elif mins >= 90:
                alerta_texto = "⚠️ PRECAUCIÓN - SUPERVISAR DESEMPEÑO"
                color_clase = "val-warning"
                alerta_bg = "#332D20"
                border_color = "#FFC107"
            else:
                alerta_texto = "✅ OPERACIÓN NORMAL"
                color_clase = "val-normal"
                alerta_bg = "#1b1b28"
                border_color = "#4CAF50"

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
            <div style="background-color: {alerta_bg}; border-left: 6px solid {border_color}; padding: 20px; border-radius: 8px;">
                <h3 style="margin-top:0;">Estado: {alerta_texto}</h3>
                <div style="display:flex; justify-content:space-between;">
                    <div>
                        <p><b>🚚 Patente:</b> {patente}</p>
                        <p><b>🏢 Cliente:</b> {cliente}</p>
                        <p><b>🔄 Proceso:</b> {proceso} de Carga {carga}</p>
                    </div>
                    <div>
                        <p><b>🚜 Equipo Asignado:</b> {equipo}</p>
                        <p><b>⚡ Velocidad Estimada:</b> {velocidad}</p>
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
            if progress > 0.8:
                st.progress(progress, text="Tiempo consumido del KPI máximo")
            else:
                st.progress(progress, text="Tiempo consumido del KPI máximo")
                
            st.markdown("---")
            # --- Módulo IoT (Simulado) ---
            st.markdown("### 📹 Módulo IoT: Sensores y Monitoreo de Operación")
            
            # Simular estado del sensor de movimiento basado en el tiempo (estable por minuto)
            seed_val = i * 100 + ahora.minute
            random.seed(seed_val)
            hay_movimiento = random.random() > 0.15 # 85% de probabilidad de tener actividad
            random.seed() # Reset seed
            
            col_iot1, col_iot2 = st.columns(2)
            
            with col_iot1:
                st.markdown("<div style='background-color:#1E1E2E; padding:15px; border-radius:8px; height:100%; border: 1px solid #333;'>", unsafe_allow_html=True)
                st.markdown("#### 📡 Sensor de Movimiento Infrarrojo")
                if hay_movimiento:
                    st.markdown("<div style='color:#4CAF50; font-size:18px;'><b>🟢 DETECTANDO ACTIVIDAD (Operación en curso)</b></div>", unsafe_allow_html=True)
                    st.write("Registrando movimiento constante de personal y maquinaria en la zona de carga.")
                else:
                    st.markdown("<div style='color:#FF5252; font-size:18px; animation: blinker 1s linear infinite;'><b>🔴 ALERTA: TIEMPO MUERTO DETECTADO</b></div>", unsafe_allow_html=True)
                    st.write("⚠️ El sensor no registra movimiento en los últimos minutos. Riesgo de interrupción operativa.")
                st.markdown("</div>", unsafe_allow_html=True)
                
            with col_iot2:
                st.markdown("<div style='background-color:#1E1E2E; padding:15px; border-radius:8px; height:100%; border: 1px solid #333;'>", unsafe_allow_html=True)
                st.markdown("#### 📸 Cámara IP - Feed en Vivo")
                if hay_movimiento:
                    # Usamos un placeholder verde/celeste para simular el feed activo
                    st.markdown('<div style="background-color:#2D2D3F; color:#00E5FF; text-align:center; padding:30px; border: 2px dashed #00E5FF; border-radius: 5px;"><b>[ 🔴 REC ] FEED CÁMARA ACTIVO - MOVIMIENTO DETECTADO</b></div>', unsafe_allow_html=True)
                else:
                    # Placeholder rojo para cuando hay inactividad
                    st.markdown('<div style="background-color:#382525; color:#FF5252; text-align:center; padding:30px; border: 2px dashed #FF5252; border-radius: 5px;"><b>[ ⏸️ PAUSA ] FEED CÁMARA - SIN ACTIVIDAD RECIENTE</b></div>', unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
        else:
            st.success(f"El Andén {i} se encuentra actualmente **DISPONIBLE** y listo para recibir un nuevo camión.")
            st.info("Revisando asignaciones automáticas en el patio...")

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
time.sleep(3)
st.rerun()
