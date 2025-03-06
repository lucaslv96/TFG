import sqlite3
from PyQt5 import QtGui
from PyQt5.QtWidgets import QMessageBox

_bbdd_ = 'bbdd/equivalencias.sqlite'

# Definir constantes para las consultas SQL
UPDATE_MACROTRENDS = '''UPDATE macrotrends SET dato_actual = ? WHERE id = ?'''
UPDATE_YAHOO_FINANCE = '''UPDATE yahoo_finance SET dato_actual = ? WHERE id = ?'''
UPDATE_GOOGLE_FINANCE = '''UPDATE google_finance SET dato_actual = ? WHERE id = ?'''
SELECT_MACROTRENDS = '''SELECT id, dato_actual FROM macrotrends WHERE tipo_dato = ?'''
SELECT_YAHOO_FINANCE = '''SELECT id, dato_actual FROM yahoo_finance WHERE tipo_dato = ?'''

def populate_table(ui, data_type):
    """Carga los datos en la tabla desde Google Finance, Macrotrends y Yahoo Finance para un tipo de dato específico."""
    conn = sqlite3.connect(_bbdd_)
    cursor = conn.cursor()

    # Consulta para obtener los datos de Google Finance aunque no haya datos en Macrotrends o Yahoo Finance
    cursor.execute('''
        SELECT 
            google_finance.dato_actual AS google,
            COALESCE(macrotrends.dato_actual, '') AS macrotrends, 
            COALESCE(yahoo_finance.dato_actual, '') AS yahoo
        FROM google_finance
        LEFT JOIN equivalencias ON google_finance.id = equivalencias.google_finance_id
        LEFT JOIN macrotrends ON equivalencias.macrotrends_id = macrotrends.id
        LEFT JOIN yahoo_finance ON equivalencias.yahoo_finance_id = yahoo_finance.id
        WHERE google_finance.tipo_dato = ?
        AND google_finance.dato_actual IS NOT NULL
    ''', (data_type,))

    datos = cursor.fetchall()

    conn.close()

    # Limpiar la tabla antes de insertar nuevos datos
    ui.tableModel.clear()
    ui.tableModel.setHorizontalHeaderLabels(["Google Finance", "Macrotrends", "Yahoo Finance"])

    # Aplicar negrita a los encabezados
    for col in range(ui.tableModel.columnCount()):
        item = ui.tableModel.horizontalHeaderItem(col)
        if item:
            font = item.font()
            font.setBold(True)
            item.setFont(font)

    # Insertar los datos en la tabla
    for row in datos:
        table_row = [
            QtGui.QStandardItem(str(row[0])),  # Siempre tiene valor en Google
            QtGui.QStandardItem(str(row[1])),  # Si no hay valor en Macrotrends, queda en blanco
            QtGui.QStandardItem(str(row[2]))   # Si no hay valor en Yahoo, queda en blanco
        ]
        ui.tableModel.appendRow(table_row)
    
    
def restaurar_valores_por_defecto():
    """Restaura dato_actual con dato_inicial en todas las tablas de la base de datos."""
    conn = sqlite3.connect(_bbdd_)
    cursor = conn.cursor()

    try:
        cursor.execute("UPDATE google_finance SET dato_actual = dato_inicial")
        cursor.execute("UPDATE yahoo_finance SET dato_actual = dato_inicial")
        cursor.execute("UPDATE macrotrends SET dato_actual = dato_inicial")
        conn.commit()
        print("Valores restaurados correctamente.")
    except Exception as e:
        print(f"Error al restaurar valores: {e}")
    finally:
        conn.close()


def actualizar_valor(fuente, nuevo_valor, id):
    """Actualiza el valor de la equivalencia (Macrotrends o Yahoo Finance) con un nuevo valor."""
    conn = sqlite3.connect(_bbdd_)
    cursor = conn.cursor()

    if fuente == "Macrotrends":
        cursor.execute(UPDATE_MACROTRENDS, (nuevo_valor, id))
    elif fuente == "Yahoo Finance":
        cursor.execute(UPDATE_YAHOO_FINANCE, (nuevo_valor, id))
    elif fuente == "Google Finance":
        cursor.execute(UPDATE_GOOGLE_FINANCE, (nuevo_valor, id))
    
    conn.commit()
    conn.close()

# Moved functions from equivalencias_view_functions.py
macrotrends_map = {'balance': {}, 'income': {}, 'cashflow': {}}
yahoo_map = {'balance': {}, 'income': {}, 'cashflow': {}}
previous_values = {}

def confirmar_restauracion(ventana):
    mensaje = (
        "⚠️ Esto restaurará los valores actuales a sus valores originales y "
        "perderás cualquier cambio realizado. ¿Quieres continuar?"
    )

    respuesta = QMessageBox.question(
        None,
        "Confirmar Restauración",
        mensaje,
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No
    )

    if respuesta == QMessageBox.Yes:
        restaurar_valores(ventana)

def restaurar_valores(ventana):
    restaurar_valores_por_defecto()
    QMessageBox.information(None, "Restauración", "Se han restaurado los valores por defecto.")
    populate_table(ventana, 'balance')

def populate_mappings():
    conn = sqlite3.connect(_bbdd_)
    cursor = conn.cursor()

    for data_type in ['balance', 'income', 'cashflow']:
        cursor.execute(SELECT_MACROTRENDS, (data_type,))
        for row in cursor.fetchall():
            macrotrends_map[data_type][row[1]] = row[0]

        cursor.execute(SELECT_YAHOO_FINANCE, (data_type,))
        for row in cursor.fetchall():
            yahoo_map[data_type][row[1]] = row[0]

    conn.close()

def actualizar_valor_inmediato(ventana, item):
    row = item.row()
    col = item.column()
    new_value = item.text()

    conn = sqlite3.connect(_bbdd_)
    cursor = conn.cursor()

    data_type = ventana.current_data_type

    if col == 1:
        previous_value = previous_values.get((row, col), "")
        macrotrends_id = macrotrends_map[data_type].get(previous_value)
        if macrotrends_id:
            cursor.execute(UPDATE_MACROTRENDS, (new_value, macrotrends_id))
    elif col == 2:
        previous_value = previous_values.get((row, col), "")
        yahoo_id = yahoo_map[data_type].get(previous_value)
        if yahoo_id:
            cursor.execute(UPDATE_YAHOO_FINANCE, (new_value, yahoo_id))

    previous_values[(row, col)] = new_value

    conn.commit()
    conn.close()

def guardar_cambios(ventana):
    conn = sqlite3.connect(_bbdd_)
    cursor = conn.cursor()

    for row in range(ventana.tableModel.rowCount()):
        macrotrends_value = ventana.tableModel.item(row, 1).text()
        yahoo_value = ventana.tableModel.item(row, 2).text()

        data_type = ventana.current_data_type

        macrotrends_id = macrotrends_map[data_type].get(macrotrends_value)
        if macrotrends_id:
            cursor.execute(UPDATE_MACROTRENDS, (macrotrends_value, macrotrends_id))

        yahoo_id = yahoo_map[data_type].get(yahoo_value)
        if yahoo_id:
            cursor.execute(UPDATE_YAHOO_FINANCE, (yahoo_value, yahoo_id))

    conn.commit()
    conn.close()
    QMessageBox.information(None, "Guardar Cambios", "Los cambios han sido guardados exitosamente.")
