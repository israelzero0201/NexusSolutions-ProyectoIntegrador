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