import json
from pathlib import Path


class GeneralConfig:
    ARCHIVO = Path(__file__).parent / "config.json"
    
    DEFAULTS = {"version": "1.0", "empresa": "Eclipcom", "anio": 2026}
    
    @staticmethod
    def _leer():
        try:
            with open(GeneralConfig.ARCHIVO, encoding="utf-8") as f:
                return {**GeneralConfig.DEFAULTS, **json.load(f)}
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"No se pudo leer config.json, usando valores por defecto: {e}")
            return dict(GeneralConfig.DEFAULTS)

    @staticmethod
    def get(clave, defecto=None):
        return GeneralConfig._leer().get(clave, defecto)

    @staticmethod
    def version():
        return GeneralConfig.get("version")
    @staticmethod
    def guardar(clave, valor):
        # Guarda una opción en config.json (por ejemplo el tema elegido en Configuración)
        datos = GeneralConfig._leer()
        datos[clave] = valor
        try:
            with open(GeneralConfig.ARCHIVO, "w", encoding="utf-8") as f:
                json.dump(datos, f, ensure_ascii=False, indent=4)
        except OSError as e:
            print(f"No se pudo guardar config.json: {e}")
