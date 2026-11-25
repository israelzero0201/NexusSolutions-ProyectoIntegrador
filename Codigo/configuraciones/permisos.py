import unicodedata
from configuraciones import sesion

# -------------------------------------------------------------------------------------------------------------------------
#   Niveles de acceso. Para cambiar quién puede hacer qué, solo se edita este archivo.
# -------------------------------------------------------------------------------------------------------------------------

# Roles tal como están en la tabla trabajadores (Dueño = nivel ejecutivo)
ROLES = ("Tecnico", "Ingeniero", "Administrativo", "Dueño")
TODOS = ROLES
GESTION = ("Ingeniero", "Administrativo", "Dueño")      # ejecutivos, ingenieros y administración
DIRECCION = ("Ingeniero", "Dueño")                      # los únicos que pueden eliminar

PERMISOS = {
    "ver_ventas": TODOS,
    "crear_ventas": TODOS,
    "editar_ventas_parcial": TODOS,     # solo los campos de CAMPOS_VENTA_PARCIAL
    "editar_ventas": GESTION,           # edición completa: cliente, proyecto, concepto, anticipo, cancelar
    "asignar_tecnicos": GESTION,
    "imprimir_ventas": TODOS,
    "registrar_pagos": GESTION,         # anticipos y abonos
    "eliminar_pagos": DIRECCION,
    "escribir_bitacora": TODOS,         # notas: avances, material, problemas, pendientes
    "eliminar_bitacora": DIRECCION,
    "ver_clientes": TODOS,              # el técnico ve la información del cliente (sin editar)
    "editar_clientes": GESTION,
    "ver_usuarios": GESTION,
    "editar_usuarios": GESTION,
    "eliminar_usuarios": DIRECCION,     # administrativos no pueden eliminar usuarios
}

# Lo que un técnico puede cambiar de una venta ya registrada.
# Nombres posibles: cliente, proyecto, fecha, hora, direccion, concepto, estado, anticipo
CAMPOS_VENTA_PARCIAL = ("direccion", "fecha", "hora", "estado")

# Estados que solo puede poner alguien con "editar_ventas"
ESTADOS_SOLO_GESTION = ("cancelada",)

DESCRIPCIONES = {
    "Tecnico": "Consulta ventas y clientes, registra ventas nuevas, actualiza dirección, fecha, hora "
               "y estado, y escribe en la bitácora.",
    "Ingeniero": "Acceso completo, incluido eliminar usuarios, pagos y la bitácora.",
    "Administrativo": "Acceso completo a clientes, ventas, pagos, técnicos y usuarios, "
                      "pero no puede eliminar usuarios, pagos ni la bitácora.",
    "Dueño": "Acceso completo, incluido eliminar usuarios, pagos y la bitácora.",
}


def normalizar(texto):
    # "Técnico" -> "tecnico", "DUEÑO" -> "dueno" (así no importa cómo esté escrito en la BD)
    sin_acentos = unicodedata.normalize("NFKD", str(texto or "")).encode("ascii", "ignore").decode()
    return sin_acentos.strip().lower()


def rol_actual():
    return sesion.actual().get("rol", "")


def puede(permiso, rol=None):
    rol = normalizar(rol_actual() if rol is None else rol)
    return rol in {normalizar(r) for r in PERMISOS.get(permiso, ())}


def es_tecnico(rol=None):
    return normalizar(rol_actual() if rol is None else rol) == "tecnico"


def rol_valido(rol):
    return any(normalizar(r) == normalizar(rol) for r in ROLES)


def descripcion_rol(rol=None):
    rol = rol_actual() if rol is None else rol
    for nombre, texto in DESCRIPCIONES.items():
        if normalizar(nombre) == normalizar(rol):
            return texto
    return "Sin permisos asignados. Pide apoyo a administración."


def campos_parciales_txt():
    # ("direccion", "fecha", "hora", "estado") -> "dirección, fecha, hora y estado"
    nombres = {"cliente": "cliente", "proyecto": "proyecto", "fecha": "fecha", "hora": "hora",
               "direccion": "dirección", "concepto": "concepto", "estado": "estado", "anticipo": "anticipo"}
    lista = [nombres.get(c, c) for c in CAMPOS_VENTA_PARCIAL]
    if len(lista) <= 1:
        return "".join(lista)
    return ", ".join(lista[:-1]) + " y " + lista[-1]
