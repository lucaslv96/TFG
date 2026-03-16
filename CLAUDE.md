# CLAUDE.md — TFG: Financial Data Scraper

## ¿Qué es este proyecto?

Aplicación de escritorio (Python + PyQt5) para un **Trabajo de Fin de Grado** que agrega, compara y exporta datos financieros de tres fuentes simultáneamente:

- **Google Finance** — scraping con Selenium (Firefox headless)
- **Yahoo Finance** — API a través de la librería `yfinance`
- **Macrotrends** — scraping con Selenium + BeautifulSoup

El usuario introduce un ticker bursátil (p.ej. `AAPL`, `SAN`, `TEF`), la app lanza búsquedas en paralelo y muestra los datos comparados en una tabla. Soporta exportación/importación en Excel y SQLite.

---

## Cómo ejecutar

```bash
pip install -r requirements.txt
python main.py
```

> Requiere Firefox instalado (para Selenium en Google Finance y Macrotrends).

---

## Estructura de directorios

```
TFG/
├── main.py                          # Punto de entrada
├── config.py                        # Paths centralizados (DB, export, icono)
├── requirements.txt                 # Dependencias Python
├── data/
│   ├── db/
│   │   └── equivalencias.sqlite     # Base de datos principal (se crea al iniciar)
│   └── export/                      # Archivos exportados por ticker (xlsx + sqlite)
├── resources/
│   └── icon.ico
├── controller/                      # Lógica de negocio (MVC — Controlador)
│   ├── __init__.py
│   ├── main_controller.py           # Orquestador principal
│   ├── chart_controller.py          # Gráficos con matplotlib
│   ├── equivalencias_controller.py  # Gestión de equivalencias entre fuentes
│   └── datos_equivalentes_controller.py  # Visualización comparada de datos
├── model/                           # Capa de datos (MVC — Modelo)
│   ├── __init__.py
│   ├── database_setup.py            # Inicialización del esquema y datos por defecto
│   ├── database_manager.py          # CRUD sobre SQLite
│   ├── data_manager.py              # Filtrado, transformación y modelo Qt de tablas
│   └── data_import_export.py        # Lectura/escritura de Excel y SQLite
├── view/                            # Interfaz de usuario (MVC — Vista)
│   ├── __init__.py
│   ├── main_view.py                 # Ventana principal (QMainWindow)
│   ├── equivalencias_view.py        # Diálogo de gestión de equivalencias
│   └── ayuda_view.py                # Ventana de ayuda y documentación
├── scrapers/                        # Capa de adquisición de datos externos
│   ├── __init__.py
│   ├── google_finance_scraper.py    # Selenium → Google Finance
│   ├── yahoo_finance_scraper.py     # yfinance → Yahoo Finance
│   └── macrotrends_scraper.py       # Selenium + BS4 → Macrotrends
└── tests/
    ├── __init__.py
    ├── integration_test.py
    └── performance_tests.py
```

---

## Arquitectura: MVC + capa de scrapers

```
VIEW (PyQt5)
  main_view.py · equivalencias_view.py · ayuda_view.py
        │
        ▼  señales / slots
CONTROLLER (lógica de negocio)
  main_controller.py · chart_controller.py
  equivalencias_controller.py · datos_equivalentes_controller.py
        │
        ▼
MODEL (datos)
  data_manager.py · database_manager.py
  database_setup.py · data_import_export.py
        │
        ▼
SCRAPERS (fuentes externas)
  google_finance_scraper.py · yahoo_finance_scraper.py · macrotrends_scraper.py
```

---

## Flujo de datos principal

1. **Usuario escribe ticker** en `main_view.py` (`QLineEdit`) y pulsa Enter o el botón de búsqueda.
2. `main_controller.py → buscar_datos()` lanza **tres hilos QThread en paralelo**:
   - `Worker` → `google_finance_scraper.py`
   - `YahooWorker` → `yahoo_finance_scraper.py`
   - `MacrotrendsWorker` → `macrotrends_scraper.py`
3. Cada scraper devuelve un `pandas.DataFrame`.
4. `data_manager.py` filtra y transforma los DataFrames según tipo (`income`, `balance`, `cashflow`):
   - `filtrar_datos_google()`
   - `filtrar_datos_yahoo()`
   - `filtrar_datos_macrotrends()`
5. El `PandasModel` (en `data_manager.py`) adapta el DataFrame a `QTableView`.
6. La tabla se actualiza en la UI. Opcionalmente:
   - **Exportar**: `data_import_export.py` escribe `.xlsx` (multi-hoja) o `.sqlite` en `/export/`.
   - **Gráfico**: `chart_controller.py` genera un gráfico matplotlib incrustado en Qt.

---

## Base de datos (`bbdd/equivalencias.sqlite`)

Cuatro tablas:

| Tabla | Propósito |
|---|---|
| `google_finance` | Tipos de dato de Google Finance (`tipo_dato`, `dato_inicial`, `dato_actual`) |
| `yahoo_finance` | Tipos de dato de Yahoo Finance |
| `macrotrends` | Tipos de dato de Macrotrends |
| `equivalencias` | Mapeos cruzados: qué campo de cada fuente representa la misma métrica |

La tabla `equivalencias` tiene claves foráneas a las otras tres y permite al usuario definir qué campo de Google Finance corresponde con cuál de Yahoo Finance y cuál de Macrotrends, agrupados por `tipo_dato` (`income`, `balance`, `cashflow`).

Se inicializa automáticamente en `database_setup.py` con 6 equivalencias por defecto al primer arranque.

---

## Componentes clave en detalle

### `main_controller.py` (946 líneas)
El controlador más importante. Gestiona:
- Búsqueda paralela con workers QThread
- Ensamblado de resultados de las tres fuentes
- Llamadas a exportación/importación
- Apertura de la ventana de gráficos

### `data_manager.py` (385 líneas)
- **`PandasModel`**: adaptador Qt que convierte DataFrames en modelos de tabla para `QTableView`.
- Funciones `filtrar_datos_*`: filtran filas por tipo de estado financiero.

### `google_finance_scraper.py` (292 líneas)
- Selenium Firefox headless, acepta cookies automáticamente.
- Soporta múltiples bolsas: NASDAQ, NYSE, BME, XMAD, LON, etc.
- Prefija los índices con `"Income_"`, `"Balance_"`, `"Cashflow_"` para distinguir origen.

### `yahoo_finance_scraper.py` (104 líneas)
- Usa `yfinance`. Prueba sufijos de mercado (`.MC`, `.DE`, `.L`, `.PA`…) si el ticker base falla.
- Devuelve los últimos 4 años de datos anuales.

### `macrotrends_scraper.py` (165 líneas)
- Selenium + BeautifulSoup para extraer tablas HTML de Macrotrends.
- Acepta dialogs de cookies antes de scraping.

### `chart_controller.py` (359 líneas)
- `ChartWindow`: widget Qt con figura matplotlib embebida.
- Normaliza valores numéricos de distintas fuentes para graficarlos comparados.

### `datos_equivalentes_controller.py` (605 líneas)
- `GroupedPandasModel`: modelo Qt con coloreo por grupos.
- `GroupFrameDelegate`: delegado personalizado para bordes de grupo.
- Muestra datos equivalentes de las tres fuentes en paralelo.

---

## Stack tecnológico

| Tecnología | Uso |
|---|---|
| Python 3.12 | Lenguaje principal |
| PyQt5 | GUI de escritorio |
| Selenium | Scraping de Google Finance y Macrotrends |
| BeautifulSoup4 | Parsing HTML en Macrotrends |
| yfinance | API de Yahoo Finance |
| pandas | Manipulación de datos tabulares |
| matplotlib | Visualización / gráficos |
| SQLite3 | Base de datos local (stdlib) |
| OpenPyXL | Exportación/importación Excel |
| NumPy | Operaciones numéricas |

---

## Funcionalidades principales

1. **Búsqueda multi-fuente** por ticker con soporte de bolsas internacionales.
2. **Comparación de datos** financieros (income, balance, cashflow) entre tres fuentes.
3. **Gestión de equivalencias**: el usuario puede editar qué campo de cada fuente mapea al mismo concepto financiero y restaurar los valores por defecto.
4. **Exportación/Importación** en `.xlsx` (multi-hoja) y `.sqlite`.
5. **Gráficos comparativos** con matplotlib embebido en Qt.
6. **Ayuda integrada**: ventana con descripción de la app y referencia de campos de datos.

---

## Datos de ejemplo exportados

En `data/export/` hay archivos pre-generados para: `AAPL`, `META`, `NFLX`, `NVDA`, `SAN`, `TEF` (formatos `.xlsx` y `.sqlite`), útiles para pruebas sin conexión.

---

## Tests

```bash
python tests/integration_test.py    # Flujo completo: búsqueda → exportar → importar → comparar
python tests/performance_tests.py   # Benchmarks de rendimiento
```
