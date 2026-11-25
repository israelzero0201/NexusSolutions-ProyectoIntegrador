import os, json
from pathlib import Path

# En Windows se guarda en %APPDATA%\Eclipcom; si no existe APPDATA se usa la carpeta del usuario
ARCHIVO = Path(os.getenv("APPDATA") or Path.home()) / "Eclipcom" / "sesion.json"

# Usuario con la sesión abierta. Vive en memoria y se llena con datos de la BD,
# así nadie se sube de nivel editando sesion.json
_actual = {}

def iniciar(id, usuario, rol, nombre, recordar=False):
    _actual.clear()
    _actual.update({"id": id, "usuario": usuario, "rol": rol, "nombre": nombre})
    if recordar:
        guardar(id, usuario)
    else:
        borrar()

def actual():
    return dict(_actual)

def actualizar(**datos):
    # Cuando el usuario edita sus propios datos (nombre, usuario)
    _actual.update(datos)
    if "usuario" in datos and cargar().get("recordar"):
        guardar(_actual["id"], datos["usuario"])

def terminar():
    _actual.clear()
    borrar()

# ---------- Archivo de "Recordarme": solo guarda id y usuario; el rol se vuelve a leer de la BD ----------
def guardar(id, usuario):
    try:
        archivo = {"id": id, "usuario": usuario, "recordar": True}
        ARCHIVO.parent.mkdir(parents=True, exist_ok=True)
        ARCHIVO.write_text(json.dumps(archivo), encoding="utf-8")
    except OSError as e:
        print(f"Error al crear el archivo de sesión: {e}")

def cargar():
    if ARCHIVO.exists():
        try:
            return json.loads(ARCHIVO.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            print(f"No se pudo leer sesion.json: {e}")
            return {}
    else:
        return {}

def borrar():
    try:
        if ARCHIVO.exists():
            ARCHIVO.unlink()  # Esto borra el archivo
    except OSError as e:
        print(f"No se pudo borrar sesion.json: {e}")
