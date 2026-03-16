import pathlib

# Directorio raíz del proyecto (donde está este archivo)
ROOT = pathlib.Path(__file__).resolve().parent

# Base de datos principal
DB_DIR  = ROOT / "data" / "db"
DB_PATH = DB_DIR / "equivalencias.sqlite"

# Directorio de exportaciones del usuario
EXPORT_DIR = ROOT / "data" / "export"

# Recursos estáticos
RESOURCES_DIR = ROOT / "resources"
ICON_PATH = RESOURCES_DIR / "icon.ico"
