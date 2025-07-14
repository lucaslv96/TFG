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
            google_finance.id AS google_id,
            google_finance.dato_actual AS google,
            macrotrends.id AS macro_id,
            COALESCE(macrotrends.dato_actual, '') AS macrotrends, 
            yahoo_finance.id AS yahoo_id,
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

    ui.tableModel.clear()
    ui.tableModel.setHorizontalHeaderLabels(["Google Finance", "Yahoo Finance", "Macrotrends"])

    # Guardar los IDs por fila
    ui.row_ids = []

    for row in datos:
        # row: (google_id, google, macro_id, macrotrends, yahoo_id, yahoo)
        table_row = [
            QtGui.QStandardItem(str(row[1])),  # Google
            QtGui.QStandardItem(str(row[5])),  # Yahoo
            QtGui.QStandardItem(str(row[3]))   # Macrotrends
        ]
        ui.tableModel.appendRow(table_row)
        ui.row_ids.append((row[0], row[2], row[4]))  # (google_id, macro_id, yahoo_id)

    # Aplicar negrita a los encabezados
    for col in range(ui.tableModel.columnCount()):
        item = ui.tableModel.horizontalHeaderItem(col)
        if item:
            font = item.font()
            font.setBold(True)
            item.setFont(font)
    
    
def restaurar_valores_por_defecto():
    """Restaura dato_actual con dato_inicial en todas las tablas de la base de datos."""
    conn = sqlite3.connect(_bbdd_)
    cursor = conn.cursor()

    try:
        cursor.execute("UPDATE google_finance SET dato_actual = dato_inicial")
        cursor.execute("UPDATE yahoo_finance SET dato_actual = dato_inicial")
        cursor.execute("UPDATE macrotrends SET dato_actual = dato_inicial")
        conn.commit()
    except Exception as e:
        pass
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
google_map = {'balance': {}, 'income': {}, 'cashflow': {}}  # Añadir este mapeo
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

        # Poblar google_map
        cursor.execute("SELECT id, dato_actual FROM google_finance WHERE tipo_dato = ?", (data_type,))
        for row in cursor.fetchall():
            google_map[data_type][row[1]] = row[0]

    conn.close()

def actualizar_valor_inmediato(ventana, item):
    row = item.row()
    col = item.column()
    new_value = item.text()

    conn = sqlite3.connect(_bbdd_)
    cursor = conn.cursor()

    # Obtener los IDs de la fila
    google_id, macro_id, yahoo_id = ventana.row_ids[row]

    if col == 0 and google_id:  # Google Finance
        cursor.execute(UPDATE_GOOGLE_FINANCE, (new_value, google_id))
    elif col == 1 and yahoo_id:  # Yahoo Finance (ahora es la segunda columna)
        cursor.execute(UPDATE_YAHOO_FINANCE, (new_value, yahoo_id))
    elif col == 2 and macro_id:  # Macrotrends (ahora es la tercera columna)
        cursor.execute(UPDATE_MACROTRENDS, (new_value, macro_id))

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
