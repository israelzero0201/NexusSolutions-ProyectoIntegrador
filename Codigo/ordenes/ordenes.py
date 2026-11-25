import datetime
import json
from conexion import cursor, conexion, deshacer

class ordenTrabajo:
    TIPOS = ("instalacion", "mantenimiento")
    STATUS = ("pendiente", "asignada", "en_proceso", "concluida", "cancelada")
    CERRADOS = ("concluida", "cancelada")

    # Nombres de cada columna que regresan consultar() y consultar_id() (en ese orden)
    CAMPOS = ("id", "id_cliente", "tipo", "direccion", "proyecto", "fecha", "hora", "status", "monto",
              "anticipo_pagado", "tecnicos", "concepto", "cantidad", "precio_unitario", "con_iva",
              "monto_anticipo", "calle", "numero", "colonia", "levantada_por", "pagos", "bitacora")

    def __init__(self, idCliente, tipo, direccionSitio, descripcion, fechaProgramada, horaInicio, status, montoTotal, anticipoPagado,
                 concepto=None, cantidad=1, precioUnitario=None, conIva=True, montoAnticipo=0,
                 calle=None, numero=None, colonia=None, levantadaPor=None, pagos=None, bitacora=None):
        self._idOrden = None
        self._idCliente = idCliente
        self._tipo = tipo
        self._direccionSitio = direccionSitio
        self._descripcion = descripcion
        self._fechaProgramada = fechaProgramada
        self._horaInicio = horaInicio
        self._status = status
        self._montoTotal = montoTotal
        self._anticipoPagado = anticipoPagado
        self._concepto = concepto
        self._cantidad = cantidad
        self._precioUnitario = precioUnitario
        self._conIva = conIva
        self._montoAnticipo = montoAnticipo
        self._calle = calle
        self._numero = numero
        self._colonia = colonia
        self._levantadaPor = levantadaPor
        self._pagos = pagos or []          # lista de pagos (anticipos y abonos)
        self._bitacora = bitacora          # texto de la bitácora (notas)

    def crearOrden(self):
        try:
            cursor.execute("insert into ordenes_info (id_cliente, tipo, direccion_sitio, descripcion, fecha_programada, hora_inicio, status, monto_total, anticipo_pagado, "
                           "concepto, cantidad, precio_unitario, con_iva, monto_anticipo, calle, numero, colonia, levantada_por, pagos, bitacora) "
                           "values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                           self._datos() + (json.dumps(self._pagos, ensure_ascii=False) if self._pagos else None, self._bitacora or None))
            conexion.commit()
            self._idOrden = cursor.lastrowid
            return True
        except:
            deshacer()
            return False

    def actualizarOrden(self, id):
        try:
            cursor.execute("update ordenes_info set id_cliente = %s, tipo = %s, direccion_sitio = %s, descripcion = %s, fecha_programada = %s, hora_inicio = %s, status = %s, monto_total = %s, anticipo_pagado = %s, "
                           "concepto = %s, cantidad = %s, precio_unitario = %s, con_iva = %s, monto_anticipo = %s, calle = %s, numero = %s, colonia = %s, levantada_por = %s "
                           "where id_orden = %s", self._datos() + (id,))
            conexion.commit()
            return True
        except:
            deshacer()
            return False

    @staticmethod
    def asignarTecnico(idOrden, idTrabajador):
        try:
            # No se asigna a órdenes cerradas ni dos veces al mismo técnico
            if ordenTrabajo._estado(idOrden) in (None,) + ordenTrabajo.CERRADOS:
                return False
            cursor.execute("select 1 from ordenes_tecnicos where id_orden_trabajo = %s and id_trabajadores = %s", (idOrden, idTrabajador))
            if cursor.fetchone():
                return False
            conexion.start_transaction()
            cursor.execute("insert into ordenes_tecnicos (id_trabajadores, id_orden_trabajo) values (%s, %s)", (idTrabajador, idOrden))
            cursor.execute("update ordenes_info set status = 'asignada' where id_orden = %s and status = 'pendiente'", (idOrden,))
            conexion.commit()
            return True
        except:
            deshacer()
            return False

    @staticmethod
    def quitarTecnico(idOrden, idTrabajador):
        try:
            if ordenTrabajo._estado(idOrden) in (None,) + ordenTrabajo.CERRADOS:
                return False
            conexion.start_transaction()
            cursor.execute("delete from ordenes_tecnicos where id_orden_trabajo = %s and id_trabajadores = %s", (idOrden, idTrabajador))
            # Si ya no queda ningún técnico, la orden vuelve a pendiente
            cursor.execute("select count(*) from ordenes_tecnicos where id_orden_trabajo = %s", (idOrden,))
            if cursor.fetchone()[0] == 0:
                cursor.execute("update ordenes_info set status = 'pendiente' where id_orden = %s and status = 'asignada'", (idOrden,))
            conexion.commit()
            return True
        except:
            deshacer()
            return False

    @staticmethod
    def tecnicosDeOrden(idOrden):
        # [(id_trabajadores, nombre, especialidad), ...]
        try:
            cursor.execute("select t.id_trabajadores, t.nombre, t.especialidad from ordenes_tecnicos ot "
                           "join trabajadores t on t.id_trabajadores = ot.id_trabajadores "
                           "where ot.id_orden_trabajo = %s order by t.nombre", (idOrden,))
            return cursor.fetchall()
        except:
            return []

    @staticmethod
    def actualizarTecnico(idOrden, idTrabajador):
        try:
            cursor.execute("select 1 from ordenes_tecnicos where id_orden_trabajo = %s", (idOrden,))
            if len(cursor.fetchall()) == 0:
                return False
            cursor.execute("update ordenes_tecnicos set id_trabajadores = %s where id_orden_trabajo = %s", (idTrabajador, idOrden))
            conexion.commit()
            return True
        except:
            deshacer()
            return False

    @staticmethod
    def registrarConclusion(idOrden):
        try:
            if ordenTrabajo._estado(idOrden) not in ("asignada", "en_proceso"):
                return False
            cursor.execute("update ordenes_info set status = 'concluida' where id_orden = %s", (idOrden,))
            conexion.commit()
            return True
        except:
            deshacer()
            return False

    @staticmethod
    def cancelarOrden(idOrden):
        try:
            if ordenTrabajo._estado(idOrden) in (None, "concluida", "cancelada"):
                return False
            cursor.execute("update ordenes_info set status = 'cancelada' where id_orden = %s", (idOrden,))
            conexion.commit()
            return True
        except:
            deshacer()
            return False

    @staticmethod
    def statusPermitidos(actual):
        # Estados a los que puede pasar una orden desde su estado actual (incluye el actual)
        if actual in ordenTrabajo.CERRADOS:
            return [actual]
        permitidos = []
        for status in ordenTrabajo.STATUS:
            if status == "concluida" and actual not in ("asignada", "en_proceso"):
                continue
            permitidos.append(status)
        return permitidos

    @staticmethod
    def cambiarStatus(idOrden, nuevo):
        try:
            actual = ordenTrabajo._estado(idOrden)
            if actual is None or nuevo not in ordenTrabajo.statusPermitidos(actual):
                return False
            if nuevo == actual:
                return True
            if nuevo == "concluida":
                return ordenTrabajo.registrarConclusion(idOrden)
            if nuevo == "cancelada":
                return ordenTrabajo.cancelarOrden(idOrden)
            cursor.execute("update ordenes_info set status = %s where id_orden = %s", (nuevo, idOrden))
            conexion.commit()
            return True
        except:
            deshacer()
            return False

    @staticmethod
    def eliminarOrden(idOrden):
        try:
            cursor.execute("delete from ordenes_info where id_orden = %s", (idOrden,))
            conexion.commit()
            return True
        except:
            deshacer()
            return False

    # Una orden puede tener varios técnicos: se juntan en un solo texto para no repetir la orden
    CONSULTA = ("select o.id_orden, o.id_cliente, o.tipo, o.direccion_sitio, o.descripcion, o.fecha_programada, "
                "o.hora_inicio, o.status, o.monto_total, o.anticipo_pagado, "
                "(select group_concat(t.nombre separator ', ') from ordenes_tecnicos ot "
                "join trabajadores t on t.id_trabajadores = ot.id_trabajadores "
                "where ot.id_orden_trabajo = o.id_orden), "
                "o.concepto, o.cantidad, o.precio_unitario, o.con_iva, o.monto_anticipo, o.calle, o.numero, o.colonia, o.levantada_por, "
                "o.pagos, o.bitacora "
                "from ordenes_info o")

    @staticmethod
    def a_dict(fila):
        # Convierte la tupla de la consulta en diccionario: venta["concepto"], venta["status"], ...
        if fila is None:
            return None
        venta = dict(zip(ordenTrabajo.CAMPOS, fila))
        venta["pagos"] = ordenTrabajo._leer_pagos(venta["pagos"], venta["monto_anticipo"], venta["fecha"])
        return venta

    # -------------------------------------------------------------------------------------------------------------------------
    #   Pagos (anticipos y abonos). Por el límite de 3 tablas se guardan en la columna "pagos" como una lista JSON:
    #   [{"fecha": "2026-11-24", "monto": 1000.0, "tipo": "Anticipo", "registro": "Ana (Administrativo)", "nota": ""}, ...]
    # -------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _leer_pagos(texto, monto_anticipo, fecha):
        try:
            pagos = json.loads(texto) if texto else []
        except (TypeError, ValueError):
            pagos = []
        if not isinstance(pagos, list):
            pagos = []
        # Ventas de la v4: solo tenían el monto del anticipo, se muestra como un solo pago
        if not pagos and float(monto_anticipo or 0) > 0:
            pagos = [{"fecha": fecha.isoformat() if isinstance(fecha, datetime.date) else str(fecha or ""),
                      "monto": float(monto_anticipo), "tipo": "Anticipo", "registro": "Registro anterior", "nota": ""}]
        return pagos

    @staticmethod
    def agregarPago(idOrden, pago):
        try:
            conexion.start_transaction()
            cursor.execute("select pagos, monto_anticipo, fecha_programada, monto_total, status from ordenes_info "
                           "where id_orden = %s for update", (idOrden,))
            fila = cursor.fetchone()
            if fila is None or fila[4] == "cancelada":
                deshacer()
                return False
            pagos = ordenTrabajo._leer_pagos(fila[0], fila[1], fila[2])
            pagado = round(sum(float(p["monto"]) for p in pagos) + float(pago["monto"]), 2)
            # No se puede pagar más que el total
            if float(pago["monto"]) <= 0 or pagado > float(fila[3] or 0) + 0.001:
                deshacer()
                return False
            pagos.append(pago)
            cursor.execute("update ordenes_info set pagos = %s, monto_anticipo = %s, anticipo_pagado = 1 where id_orden = %s",
                           (json.dumps(pagos, ensure_ascii=False), pagado, idOrden))
            conexion.commit()
            return True
        except:
            deshacer()
            return False

    @staticmethod
    def quitarPago(idOrden, indice):
        try:
            conexion.start_transaction()
            cursor.execute("select pagos, monto_anticipo, fecha_programada from ordenes_info where id_orden = %s for update", (idOrden,))
            fila = cursor.fetchone()
            pagos = ordenTrabajo._leer_pagos(fila[0], fila[1], fila[2]) if fila else []
            if not 0 <= indice < len(pagos):
                deshacer()
                return None
            quitado = pagos.pop(indice)
            pagado = round(sum(float(p["monto"]) for p in pagos), 2)
            cursor.execute("update ordenes_info set pagos = %s, monto_anticipo = %s, anticipo_pagado = %s where id_orden = %s",
                           (json.dumps(pagos, ensure_ascii=False), pagado, 1 if pagos else 0, idOrden))
            conexion.commit()
            return quitado
        except:
            deshacer()
            return None

    @staticmethod
    def estadoDeCuenta(venta):
        # Precio inicial, cada pago (ordenado por fecha) con lo que resta después, total pagado y saldo
        total = float(venta["monto"] or 0)
        saldo = total
        movimientos = []
        for indice, pago in sorted(enumerate(venta["pagos"]), key=lambda x: (str(x[1].get("fecha", "")), x[0])):
            saldo = round(saldo - float(pago["monto"]), 2)
            movimientos.append(dict(pago, indice=indice, saldo=saldo))
        return {"total": total, "pagado": round(total - saldo, 2), "saldo": saldo, "movimientos": movimientos}

    @staticmethod
    def desglose(venta):
        # Concepto, cantidad, precio, subtotal, IVA y total de una venta guardada
        total = float(venta["monto"] or 0)
        if venta["precio_unitario"] is not None:
            cantidad = int(venta["cantidad"] or 1)
            precio = float(venta["precio_unitario"])
            con_iva = bool(venta["con_iva"])
            subtotal = round(cantidad * precio, 2)
        else:
            # Ventas anteriores a la v4: solo tenían el total con IVA
            cantidad, con_iva = 1, True
            precio = total / 1.16
            subtotal = round(precio, 2)
        concepto = venta["concepto"] or {"instalacion": "Instalación", "mantenimiento": "Mantenimiento"}.get(venta["tipo"], "")
        return {"concepto": concepto, "cantidad": cantidad, "precio": precio, "subtotal": subtotal,
                "iva": round(total - subtotal, 2), "total": total, "con_iva": con_iva}

    # -------------------------------------------------------------------------------------------------------------------------
    #   Bitácora: un solo bloque de texto. Cada nota lleva quién la escribió y cuándo
    # -------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def entradaBitacora(autor, texto):
        return f"── {datetime.datetime.now():%d/%m/%Y %H:%M} · {autor} ──\n{texto.strip()}\n\n"

    @staticmethod
    def agregarNota(idOrden, autor, texto):
        try:
            cursor.execute("update ordenes_info set bitacora = concat(ifnull(bitacora, ''), %s) where id_orden = %s",
                           (ordenTrabajo.entradaBitacora(autor, texto), idOrden))
            conexion.commit()
            return True
        except:
            deshacer()
            return False

    @staticmethod
    def borrarBitacora(idOrden, autor):
        # Se borra todo, pero queda anotado quién la eliminó y cuándo
        try:
            cursor.execute("update ordenes_info set bitacora = %s where id_orden = %s",
                           (ordenTrabajo.entradaBitacora(autor, "Se eliminó la bitácora anterior."), idOrden))
            conexion.commit()
            return True
        except:
            deshacer()
            return False

    @staticmethod
    def bitacoraDe(idOrden):
        try:
            cursor.execute("select bitacora from ordenes_info where id_orden = %s", (idOrden,))
            fila = cursor.fetchone()
            return (fila[0] or "") if fila else None
        except:
            return None

    @staticmethod
    def consultar():
        # Lista de diccionarios (ver CAMPOS)
        try:
            cursor.execute(ordenTrabajo.CONSULTA + " order by o.id_orden")
            return [ordenTrabajo.a_dict(fila) for fila in cursor.fetchall()]
        except:
            return []

    @staticmethod
    def consultar_id(idOrden):
        try:
            cursor.execute(ordenTrabajo.CONSULTA + " where o.id_orden = %s", (idOrden,))
            return ordenTrabajo.a_dict(cursor.fetchone())
        except:
            return None

    @staticmethod
    def componer_direccion(calle, numero, colonia):
        # ("Av. Juárez", "120", "Centro") -> "Av. Juárez #120, Col. Centro"  (se guarda en direccion_sitio)
        texto = (calle or "").strip()
        if numero:
            texto = f"{texto} #{numero.strip()}".strip()
        if colonia:
            texto = f"{texto}, Col. {colonia.strip()}" if texto else f"Col. {colonia.strip()}"
        return texto

    @staticmethod
    def cantidad_ventas():
        try:
            cursor.execute("SELECT COUNT(id_orden) FROM ordenes_info")
            return cursor.fetchone()[0]
        except:
            return 0

    @staticmethod
    def siguiente_id():
        # Solo es una vista previa del folio; el id real lo asigna la base de datos al guardar
        try:
            cursor.execute("select ifnull(max(id_orden), 0) + 1 from ordenes_info")
            return int(cursor.fetchone()[0])
        except:
            return 1

    @staticmethod
    def folio(idOrden, fecha=None):
        # (6, 2026-11-04) -> "V-2026-006"
        anio = fecha.year if isinstance(fecha, datetime.date) else datetime.date.today().year
        return f"V-{anio}-{int(idOrden):03d}"

    @staticmethod
    def _estado(idOrden):
        cursor.execute("select status from ordenes_info where id_orden = %s", (idOrden,))
        fila = cursor.fetchone()
        if fila is None:
            return None
        return fila[0]

    @property
    def idOrden(self):
        return self._idOrden

    def _datos(self):
        return (self.idCliente, self.tipo, self.direccionSitio, self.descripcion or None, self.fechaProgramada or None, self.horaInicio or None, self.status, self.montoTotal or 0, self.anticipoPagado,
                self.concepto or None, self.cantidad or 1, self.precioUnitario, 1 if self.conIva else 0, self.montoAnticipo or 0,
                self.calle or None, self.numero or None, self.colonia or None, self.levantadaPor or None)

    @property
    def idCliente(self):
        return self._idCliente

    @idCliente.setter
    def idCliente(self, value):
        self._idCliente = value

    @property
    def tipo(self):
        return self._tipo

    @tipo.setter
    def tipo(self, value):
        self._tipo = value

    @property
    def direccionSitio(self):
        return self._direccionSitio

    @direccionSitio.setter
    def direccionSitio(self, value):
        self._direccionSitio = value

    @property
    def descripcion(self):
        return self._descripcion

    @descripcion.setter
    def descripcion(self, value):
        self._descripcion = value

    @property
    def fechaProgramada(self):
        return self._fechaProgramada

    @fechaProgramada.setter
    def fechaProgramada(self, value):
        self._fechaProgramada = value

    @property
    def horaInicio(self):
        return self._horaInicio

    @horaInicio.setter
    def horaInicio(self, value):
        self._horaInicio = value

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    @property
    def montoTotal(self):
        return self._montoTotal

    @montoTotal.setter
    def montoTotal(self, value):
        self._montoTotal = value

    @property
    def anticipoPagado(self):
        return self._anticipoPagado

    @anticipoPagado.setter
    def anticipoPagado(self, value):
        self._anticipoPagado = value

    @property
    def concepto(self):
        return self._concepto

    @concepto.setter
    def concepto(self, value):
        self._concepto = value

    @property
    def cantidad(self):
        return self._cantidad

    @cantidad.setter
    def cantidad(self, value):
        self._cantidad = value

    @property
    def precioUnitario(self):
        return self._precioUnitario

    @precioUnitario.setter
    def precioUnitario(self, value):
        self._precioUnitario = value

    @property
    def conIva(self):
        return self._conIva

    @conIva.setter
    def conIva(self, value):
        self._conIva = value

    @property
    def montoAnticipo(self):
        return self._montoAnticipo

    @montoAnticipo.setter
    def montoAnticipo(self, value):
        self._montoAnticipo = value

    @property
    def calle(self):
        return self._calle

    @calle.setter
    def calle(self, value):
        self._calle = value

    @property
    def numero(self):
        return self._numero

    @numero.setter
    def numero(self, value):
        self._numero = value

    @property
    def colonia(self):
        return self._colonia

    @colonia.setter
    def colonia(self, value):
        self._colonia = value

    @property
    def levantadaPor(self):
        return self._levantadaPor

    @levantadaPor.setter
    def levantadaPor(self, value):
        self._levantadaPor = value
