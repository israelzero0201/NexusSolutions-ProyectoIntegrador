import os, json
from pathlib import Path

ARCHIVO = Path(os.getenv("APPDATA", Path.home())) / "Eclipcom" / "sesion.json"

def guardar(usuario, rol):
    try:
        archivo = {"ruta": str(ARCHIVO), "usuario": usuario, "rol": rol}
        ARCHIVO.parent.mkdir(parents=True, exist_ok=True)
        ARCHIVO.write_text(json.dumps(archivo), encoding="utf-8")
    except:
        print("error al crear el archivo json")

def cargar():
    if ARCHIVO.exists():
        try:
            return json.loads(ARCHIVO.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"No se pudo leer sesion.json: {e}")
            return {}
    else:
        return {}

def borrar():
    archivo = Path(os.getenv("APPDATA")) / "Eclipcom" / "sesion.json"
    if archivo.exists():
        archivo.unlink()  # Esto borra el archivo
    else:
        print("No se encontró el archivo de sesión para borrar.")
