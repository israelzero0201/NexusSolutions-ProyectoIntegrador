from conexion import cursor

# -------------------------------------------------------------------------------------------------------------------------
#   Columnas que necesita esta versión del programa. Al abrirse, el programa revisa cada tabla y agrega
#   SOLO las que falten (no borra ni cambia nada de lo que ya existe). Así cada integrante del equipo
#   tiene su copia local de la BD al día sin entrar a phpMyAdmin. El mismo cambio está en sql/actualizacion_v4.sql y sql/actualizacion_v5.sql
# -------------------------------------------------------------------------------------------------------------------------
COLUMNAS = {
    "ordenes_info": [
        ("concepto", "VARCHAR(150) NULL"),                       # texto libre del concepto de venta
        ("cantidad", "INT NOT NULL DEFAULT 1"),
        ("precio_unitario", "DECIMAL(10,2) NULL"),
        ("con_iva", "TINYINT(1) NOT NULL DEFAULT 1"),             # 1 = el total incluye 16 % de IVA
        ("monto_anticipo", "DECIMAL(10,2) NOT NULL DEFAULT 0"),   # cuánto dejó el cliente de anticipo
        ("calle", "VARCHAR(120) NULL"),
        ("numero", "VARCHAR(20) NULL"),
        ("colonia", "VARCHAR(80) NULL"),
        ("levantada_por", "VARCHAR(100) NULL"),                   # quién llenó el formulario de la venta
        # v5
        ("pagos", "TEXT NULL"),                                   # historial de anticipos y abonos (lista JSON)
        ("bitacora", "LONGTEXT NULL"),                            # notas: avances, material, problemas, pendientes
    ],
}


def columnas_de(tabla):
    cursor.execute("select column_name from information_schema.columns "
                   "where table_schema = database() and table_name = %s", (tabla,))
    return {str(fila[0]).lower() for fila in cursor.fetchall()}


def actualizar_bd():
    # Regresa la lista de columnas agregadas, p. ej. ["ordenes_info.concepto", ...]
    agregadas = []
    for tabla, columnas in COLUMNAS.items():
        existentes = columnas_de(tabla)
        for nombre, definicion in columnas:
            if nombre.lower() not in existentes:
                cursor.execute(f"alter table {tabla} add column {nombre} {definicion}")
                agregadas.append(f"{tabla}.{nombre}")
    return agregadas
