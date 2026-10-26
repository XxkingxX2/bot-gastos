import sqlite3
from datetime import datetime

DB_NAME = "gastos.db"

def init_db():
    """Crea la tabla de gastos incluyendo el ID del usuario de Telegram."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            monto REAL NOT NULL,
            categoria TEXT NOT NULL,
            descripcion TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def registrar_gasto(user_id: int, monto: float, categoria: str, descripcion: str = ""):
    """Inserta un nuevo gasto asociado al usuario específico."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO gastos (user_id, monto, categoria, descripcion)
        VALUES (?, ?, ?, ?)
    ''', (user_id, monto, categoria.lower(), descripcion))
    conn.commit()
    conn.close()

def obtener_resumen_mes(user_id: int):
    """Obtiene el acumulado del mes actual solo para ese usuario."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    mes_actual = datetime.now().strftime('%Y-%m')
    
    # Total general del mes filtrado por usuario
    cursor.execute('''
        SELECT SUM(monto) FROM gastos 
        WHERE user_id = ? AND strftime('%Y-%m', fecha) = ?
    ''', (user_id, mes_actual))
    total_mes = cursor.fetchone()[0] or 0.0

    # Total por categoría en el mes filtrado por usuario
    cursor.execute('''
        SELECT categoria, SUM(monto) 
        FROM gastos 
        WHERE user_id = ? AND strftime('%Y-%m', fecha) = ?
        GROUP BY categoria
        ORDER BY SUM(monto) DESC
    ''', (user_id, mes_actual))
    desglose = cursor.fetchall()
    
    conn.close()
    return total_mes, desglose