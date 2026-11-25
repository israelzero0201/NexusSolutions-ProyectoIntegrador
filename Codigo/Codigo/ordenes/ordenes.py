from conexion import cursor

class ordenTrabajo:
    def __init__(self, tipo, direccionSitio, descripcion, fechaProgramada, horaInicio, status, montoTotal, anticipoPagado):
        self._tipo = tipo
        self._direccionSitio = direccionSitio
        self._descripcion = descripcion
        self._fechaProgramada = fechaProgramada
        self._horaInicio = horaInicio
        self._status = status
        self._montoTotal = montoTotal
        self._anticipoPagado = anticipoPagado

    def crearOrden(self):
        pass

    def asignarTecnico(self):
        pass

    def ctualizarTecnico(self):
        pass

    def registrarConclusion(self):
        pass

    def cancelarOrden(self):
        pass

    def eliminarOrden(self):
        pass

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

