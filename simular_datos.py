import sqlite3
import random
from datetime import datetime, timedelta

def get_db():
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

def generar_datos():
    conn = get_db()
    cursor = conn.cursor()
    
    # Limpiamos tabla para la simulación
    cursor.execute("DELETE FROM Agendamientos")
    conn.commit()

    clientes = ["Transportes Sur", "Logística Norte", "Distribuidora Central", "Frigorífico del Pacífico", "Exportadora Andina", "Alimentos Secos SA", "Supermercados Unidos"]
    cargas = ["Paletizada", "Suelta"]
    
    ahora = datetime.now()
    fecha_inicio = (ahora - timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
    
    letras = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    numeros = "0123456789"
    
    def random_patente():
        return "".join(random.choices(letras, k=2)) + "".join(random.choices(numeros, k=4))

        # Simularemos 5 días (2 pasados, hoy, 2 futuros)
    for i in range(5):
        dia_actual = fecha_inicio + timedelta(days=i)
        
        # Bloques de 15 minutos (96 bloques en el día)
        bloques = []
        base_time = dia_actual
        for b in range(96):
            bloques.append(base_time + timedelta(minutes=15*b))
            
        operaciones_dia = 38
        # Mezclamos los bloques
        cupos_disponibles = bloques * 2
        random.shuffle(cupos_disponibles)
        
        cupos_seleccionados = cupos_disponibles[:operaciones_dia]
        
        for slot in cupos_seleccionados:
            is_madrugada = slot.hour >= 23 or slot.hour < 7
            
            if is_madrugada:
                tipo_op = "Recepción"
            else:
                tipo_op = random.choice(["Recepción", "Despacho"])
                
            estado = "Programado"
            
            if slot < ahora:
                if (ahora - slot).total_seconds() < 7200:
                    estado = random.choice(["En Patio", "Descargando", "Cargando", "Completado"])
                else:
                    estado = "Completado"
            else:
                if (slot - ahora).total_seconds() < 3600:
                    estado = random.choice(["Programado", "En Patio"])
                else:
                    estado = "Programado"
                    
            # Check overlap manually
            duracion = 285 if random.choice(cargas) == 'Suelta' else 105
            dt_end = slot + timedelta(minutes=duracion)
            
            cursor.execute("""
                SELECT COUNT(*) FROM Agendamientos 
                WHERE fecha_hora < ? 
                  AND (
                    CASE WHEN tipo_carga = 'Suelta' THEN datetime(fecha_hora, '+285 minutes')
                         ELSE datetime(fecha_hora, '+105 minutes')
                    END
                  ) > ?
            """, (dt_end.strftime("%Y-%m-%d %H:%M:%S"), slot.strftime("%Y-%m-%d %H:%M:%S")))
            
            if cursor.fetchone()[0] < 4:
                cursor.execute('''
                    INSERT INTO Agendamientos (patente, cliente, tipo_operacion, tipo_carga, fecha_hora, estado)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (random_patente(), random.choice(clientes), tipo_op, "Suelta" if duracion == 285 else "Paletizada", slot.strftime("%Y-%m-%d %H:%M:%S"), estado))
            
    conn.commit()
    print("Simulación completada. Se generaron aprox. 150 registros (30 por día).")
    conn.close()

if __name__ == "__main__":
    generar_datos()
