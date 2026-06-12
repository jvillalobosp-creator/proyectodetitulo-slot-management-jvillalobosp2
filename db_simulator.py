import sqlite3
import random
from datetime import datetime, timedelta
import time

def setup_db(db_name="planta_fp1.db"):
    conn = sqlite3.connect(db_name, timeout=30.0)
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS Camiones')
    cursor.execute('DROP TABLE IF EXISTS Andenes')
    cursor.execute('DROP TABLE IF EXISTS Gateways')
    cursor.execute('DROP TABLE IF EXISTS Sensores_IoT')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Andenes (
        id_anden INTEGER PRIMARY KEY,
        estado TEXT NOT NULL,
        camion_actual_id INTEGER
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Gateways (
        id_gateway TEXT PRIMARY KEY,
        modelo TEXT,
        estado TEXT,
        ultima_conexion DATETIME
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Sensores_IoT (
        deveui TEXT PRIMARY KEY,
        id_anden INTEGER,
        modelo TEXT,
        temperatura REAL,
        movimiento BOOLEAN,
        bateria INTEGER,
        rssi INTEGER,
        ultima_lectura DATETIME,
        FOREIGN KEY(id_anden) REFERENCES Andenes(id_anden)
    )
    ''')

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

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Camiones (
        id_camion INTEGER PRIMARY KEY AUTOINCREMENT,
        patente TEXT NOT NULL,
        cliente TEXT NOT NULL,
        tipo_operacion TEXT NOT NULL,
        tipo_carga TEXT NOT NULL,
        cita_programada DATETIME,
        hora_llegada DATETIME,
        hora_inicio_anden DATETIME,
        hora_fin_anden DATETIME,
        estado TEXT NOT NULL,
        anden_asignado INTEGER,
        equipo_asignado TEXT,
        temperatura REAL
    )
    ''')

    cursor.execute("SELECT COUNT(*) FROM Andenes")
    if cursor.fetchone()[0] == 0:
        for i in range(1, 11):
            cursor.execute('INSERT INTO Andenes (id_anden, estado) VALUES (?, ?)', (i, 'Disponible'))
            
    cursor.execute("SELECT COUNT(*) FROM Gateways")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO Gateways (id_gateway, modelo, estado, ultima_conexion) VALUES (?, ?, ?, ?)", 
                       ('GW-LPS8N-01', 'lps8v2 gateway lorawan 4g lte', 'Activo', datetime.now()))
        
    cursor.execute("SELECT COUNT(*) FROM Sensores_IoT")
    if cursor.fetchone()[0] == 0:
        for i in range(1, 11):
            deveui = f"383930{i:02d}000000{i:02d}"
            cursor.execute('''
            INSERT INTO Sensores_IoT (deveui, id_anden, modelo, temperatura, movimiento, bateria, rssi, ultima_lectura)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (deveui, i, 'MOKOSmart LW007-PIR', -20.0, False, 100, -65, datetime.now()))
    
    conn.commit()
    return conn

def generate_patente():
    return f"{chr(random.randint(65, 90))}{chr(random.randint(65, 90))}{random.randint(1000, 9999)}"

def run_simulation():
    conn = setup_db()
    cursor = conn.cursor()
    clientes = ['LANDES', 'KIENER', 'VIMA FOODS', 'MB MARTIN BROWER', 'CARGILL', 'ALIMENTOS CARNICOS', 'CALYPSO']
    equipos = ['Grúa Horquilla 1', 'Grúa Horquilla 2', 'Montacargas 1', 'Cuadrilla Manual', 'Apilador Eléctrico']
    
    print("Iniciando simulador dinámico... (Presiona Ctrl+C para detener)")
    print("El simulador está actualizando la base de datos cada 3 segundos.")
    
    # Limpiar datos previos para reiniciar en limpio
    cursor.execute('DELETE FROM Camiones')
    cursor.execute('DELETE FROM Agendamientos')
    cursor.execute('UPDATE Andenes SET estado = "Disponible", camion_actual_id = NULL')
    conn.commit()

    # Cargar estado inicial (sembrar camiones para ver colores de inmediato)
    now = datetime.now()
    
    # 1. Ocupar andenes (apuntando al ~75% de ocupación inicial)
    for i in range(1, 11):
        if random.random() < 0.75: # 75% ocupado al inicio
            inicio_anden = now - timedelta(minutes=random.randint(10, 148))
            tipo_op = random.choice(['Recepción', 'Despacho'])
            tipo_carga = random.choice(['Paletizada', 'Suelta'])
            
            temp_inicial = round(random.uniform(-20.0, -17.0), 1)
            cursor.execute('''
            INSERT INTO Camiones (patente, cliente, tipo_operacion, tipo_carga, hora_llegada, hora_inicio_anden, estado, anden_asignado, equipo_asignado, temperatura)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (generate_patente(), random.choice(clientes), tipo_op, tipo_carga, 
                  inicio_anden - timedelta(minutes=10), inicio_anden, 'En Andén', i, random.choice(equipos), temp_inicial))
            camion_id = cursor.lastrowid
            cursor.execute('UPDATE Andenes SET estado = "Ocupado", camion_actual_id = ? WHERE id_anden = ?', (camion_id, i))
            
    # 2. Patio inicial despejado (efecto slot management perfecto al arrancar)
    # Ya no sembramos camiones en patio al inicio para evitar el atasco prolongado.
    # 3. Sembrar Agendamientos futuros para el Slot Management Dashboard
    for _ in range(random.randint(8, 15)):
        # Citas entre ahora y las proximas 48 horas
        fecha_cita = now + timedelta(hours=random.randint(1, 48), minutes=random.choice([0, 30]))
        cursor.execute('''
        INSERT INTO Agendamientos (patente, cliente, tipo_operacion, tipo_carga, fecha_hora, estado)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (generate_patente(), random.choice(clientes), random.choice(['Recepción', 'Despacho']), random.choice(['Paletizada', 'Suelta']), fecha_cita.strftime("%Y-%m-%d %H:%M:%S"), 'Programado'))

    conn.commit()

    # Bucle infinito
    while True:
        now = datetime.now()
        
        # 1. Finalizar camiones aleatoriamente
        cursor.execute("SELECT id_camion, anden_asignado FROM Camiones WHERE estado = 'En Andén'")
        en_anden = cursor.fetchall()
        for camion_id, anden_id in en_anden:
            # 6% probabilidad de terminar. Más rápido para evitar cuellos de botella.
            if random.random() < 0.06: 
                cursor.execute("UPDATE Camiones SET estado = 'Finalizado', hora_fin_anden = ? WHERE id_camion = ?", (now, camion_id))
                cursor.execute("UPDATE Andenes SET estado = 'Disponible', camion_actual_id = NULL WHERE id_anden = ?", (anden_id,))
                print(f"Camión {camion_id} ha finalizado en el Andén {anden_id}.")
        
        # 2. Agregar camiones nuevos al patio (simulando agendamiento ordenado)
        # 42% de prob de llegada. (0.42 llegadas vs 7*0.06 = 0.42 salidas -> Mantiene ~7 andenes y limpia el patio rápido)
        if random.random() < 0.42: 
            llegada = now
            cita = llegada + timedelta(minutes=random.choice([-10, 0, 10]))
            cursor.execute('''
            INSERT INTO Camiones (patente, cliente, tipo_operacion, tipo_carga, cita_programada, hora_llegada, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (generate_patente(), random.choice(clientes), random.choice(['Recepción', 'Despacho']), random.choice(['Paletizada', 'Suelta']), cita, llegada, 'En Patio'))
            print("Camión agendado ha llegado al patio.")
            
        # 2.1 Simular nuevos agendamientos creados vía web (Slot Management)
        if random.random() < 0.1: # 10% probabilidad de nuevo agendamiento futuro
            fecha_cita = now + timedelta(hours=random.randint(2, 72), minutes=random.choice([0, 30]))
            cursor.execute('''
            INSERT INTO Agendamientos (patente, cliente, tipo_operacion, tipo_carga, fecha_hora, estado)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (generate_patente(), random.choice(clientes), random.choice(['Recepción', 'Despacho']), random.choice(['Paletizada', 'Suelta']), fecha_cita.strftime("%Y-%m-%d %H:%M:%S"), 'Programado'))
            print("Nuevo agendamiento registrado en Slot Management.")
            
        # 3. Asignar camiones en patio a andenes disponibles
        cursor.execute("SELECT id_camion, tipo_carga FROM Camiones WHERE estado = 'En Patio' ORDER BY hora_llegada ASC")
        en_patio = cursor.fetchall()
        
        cursor.execute("SELECT id_anden FROM Andenes WHERE estado = 'Disponible'")
        disponibles = cursor.fetchall()
        
        for (camion_id, tipo_carga), (anden_id,) in zip(en_patio, disponibles):
            temp_inicial = round(random.uniform(-20.0, -17.0), 1)
            cursor.execute("UPDATE Camiones SET estado = 'En Andén', anden_asignado = ?, hora_inicio_anden = ?, equipo_asignado = ?, temperatura = ? WHERE id_camion = ?", 
                           (anden_id, now, random.choice(equipos), temp_inicial, camion_id))
            cursor.execute("UPDATE Andenes SET estado = 'Ocupado', camion_actual_id = ? WHERE id_anden = ?", (camion_id, anden_id))
            print(f"Camión {camion_id} asignado al Andén {anden_id}.")
        
        # 4. Envejecer artificialmente los camiones en el andén para que se note el cambio de tiempo más rápido en la demo (Acelera 5 minutos por cada ciclo de 3s)
        cursor.execute("SELECT id_camion, hora_inicio_anden, temperatura FROM Camiones WHERE estado = 'En Andén'")
        para_envejecer = cursor.fetchall()
        for cid, inicio_str, temp in para_envejecer:
            try:
                inicio = datetime.strptime(inicio_str, "%Y-%m-%d %H:%M:%S.%f")
            except:
                inicio = datetime.strptime(inicio_str, "%Y-%m-%d %H:%M:%S")
            # Le restamos 1 minuto extra a la hora de inicio para que el tiempo avance rápido en el dashboard
            nuevo_inicio = inicio - timedelta(minutes=1)
            
            # Subir temperatura por exposición (0.0 a 0.2 grados por ciclo)
            nueva_temp = temp if temp is None else temp + random.uniform(0.0, 0.2)
            if nueva_temp is not None:
                nueva_temp = round(nueva_temp, 1)

            cursor.execute("UPDATE Camiones SET hora_inicio_anden = ?, temperatura = ? WHERE id_camion = ?", (nuevo_inicio, nueva_temp, cid))

        # 5. Simular recepción de datos LoRaWAN (Gateway y Sensores)
        cursor.execute("UPDATE Gateways SET ultima_conexion = ? WHERE id_gateway = 'GW-LPS8N-01'", (now,))
        
        cursor.execute("SELECT id_anden, estado, camion_actual_id FROM Andenes")
        andenes_estado = cursor.fetchall()
        
        for anden_id, estado, camion_id in andenes_estado:
            # Detecta movimiento constantemente si el anden está ocupado (operario trabajando), esporádicamente si está libre
            movimiento = True if estado == 'Ocupado' else random.random() < 0.05
            
            if estado == 'Ocupado':
                cursor.execute("SELECT temperatura FROM Camiones WHERE id_camion = ?", (camion_id,))
                res = cursor.fetchone()
                temp_sensor = res[0] if res and res[0] is not None else random.uniform(-18.0, -15.0)
                temp_sensor = round(temp_sensor, 1)
            else:
                # Andén desocupado: Sensor en precámara a 5°C (Monitoreo de cadena de frío pausado)
                temp_sensor = None
                
            bateria = random.randint(85, 100) # Simulación de porcentaje de batería del sensor
            rssi = random.randint(-95, -50)   # Simulación de intensidad de señal LoRaWAN
            
            cursor.execute('''
            UPDATE Sensores_IoT 
            SET temperatura = ?, movimiento = ?, bateria = ?, rssi = ?, ultima_lectura = ?
            WHERE id_anden = ?
            ''', (temp_sensor, movimiento, bateria, rssi, now, anden_id))

        conn.commit()
        time.sleep(3)

if __name__ == "__main__":
    run_simulation()
