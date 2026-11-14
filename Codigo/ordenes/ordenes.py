from conexion import cursor, conexion

class ordenTrabajo:
    def __init__(self, idCliente, tipo, direccionSitio, descripcion, fechaProgramada, horaInicio, status, montoTotal, anticipoPagado):
        self._idCliente = idCliente
        self._tipo = tipo
        self._direccionSitio = direccionSitio
        self._descripcion = descripcion
        self._fechaProgramada = fechaProgramada
        self._horaInicio = horaInicio
        self._status = status
        self._montoTotal = montoTotal
        self._anticipoPagado = anticipoPagado

    def crearOrden(self):
        try:
            cursor.execute("insert into ordenes_info (id_cliente, tipo, direccion_sitio, descripcion, fecha_programada, hora_inicio, status, monto_total, anticipo_pagado) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)", self._datos())
            conexion.commit()
            return True
        except:
            return False

    def actualizarOrden(self, id):
        try:
            cursor.execute("update ordenes_info set id_cliente = %s, tipo = %s, direccion_sitio = %s, descripcion = %s, fecha_programada = %s, hora_inicio = %s, status = %s, monto_total = %s, anticipo_pagado = %s where id_orden = %s", self._datos() + (id,))
            conexion.commit()
            return True
        except:
            return False

    @staticmethod
    def asignarTecnico(idOrden, idTrabajador):
        try:
            cursor.execute("insert into ordenes_tecnicos (id_trabajadores, id_orden_trabajo) values (%s, %s)", (idTrabajador, idOrden))
            cursor.execute("update ordenes_info set status = 'asignada' where id_orden = %s and status = 'pendiente'", (idOrden,))
            conexion.commit()
            return True
        except:
            conexion.rollback()
            return False

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
            conexion.rollback()
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
            return False

    @staticmethod
    def eliminarOrden(idOrden):
        try:
            cursor.execute("delete from ordenes_info where id_orden = %s", (idOrden,))
            conexion.commit()
            return True
        except:
            return False

    @staticmethod
    def consultar():
        try:
            cursor.execute("select o.id_orden, o.id_cliente, o.tipo, o.direccion_sitio, o.descripcion, o.fecha_programada, o.hora_inicio, o.status, o.monto_total, o.anticipo_pagado, t.nombre from ordenes_info o left join ordenes_tecnicos ot on ot.id_orden_trabajo = o.id_orden left join trabajadores t on t.id_trabajadores = ot.id_trabajadores order by o.id_orden")
            return cursor.fetchall()
        except:
            return []

    @staticmethod
    def _estado(idOrden):
        cursor.execute("select status from ordenes_info where id_orden = %s", (idOrden,))
        fila = cursor.fetchone()
        if fila is None:
            return None
        return fila[0]

    def _datos(self):
        return (self.idCliente, self.tipo, self.direccionSitio, self.descripcion or None, self.fechaProgramada or None, self.horaInicio or None, self.status, self.montoTotal or 0, self.anticipoPagado)

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
