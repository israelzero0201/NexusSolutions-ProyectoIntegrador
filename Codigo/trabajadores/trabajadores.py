from conexion import cursor, conexion

class Trabajadores:
    def __init__(self, nombre, usuario, contrasena, rol, especialidad, status):
        self._nombre = nombre
        self._usuario = usuario
        self._contrasena = contrasena
        self._rol = rol
        self._especialidad = especialidad
        self._status = status
        self._sesion = False

    def iniciarSesion(self):
        try:
            cursor.execute("select id_trabajadores from trabajadores where usuario = %s and contrasena = %s and status = 'activo'", (self.usuario, self.contrasena))
            self._sesion = cursor.fetchone() is not None
            return self._sesion
        except:
            self._sesion = False
            return False

    def cerrarSesion(self):
        self._sesion = False
        return True

    def detalle(self):
        especialidad = self.especialidad if self.especialidad else "N/A"
        return f"Nombre: {self.nombre} | Usuario: {self.usuario} | Rol: {self.rol} | Especialidad: {especialidad} | Status: {self.status}"

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, value):
        self._nombre = value

    @property
    def usuario(self):
        return self._usuario

    @usuario.setter
    def usuario(self, value):
        self._usuario = value

    @property
    def contrasena(self):
        return self._contrasena

    @contrasena.setter
    def contrasena(self, value):
        self._contrasena = value

    @property
    def rol(self):
        return self._rol

    @rol.setter
    def rol(self, value):
        self._rol = value

    @property
    def especialidad(self):
        return self._especialidad

    @especialidad.setter
    def especialidad(self, value):
        self._especialidad = value

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    @property
    def sesion(self):
        return self._sesion

    @staticmethod
    def consultar():
        try:
            cursor.execute("select id_trabajadores, nombre, usuario, rol, especialidad, status from trabajadores")
            return cursor.fetchall()
        except:
            return []

    def insertar(self):
        try:
            cursor.execute("insert into trabajadores (nombre, usuario, contrasena, rol, especialidad, status) values (%s, %s, %s, %s, %s, %s)", (self.nombre, self.usuario, self.contrasena, self.rol, self.especialidad or None, self.status))
            conexion.commit()
            return True
        except:
            return False

    def actualizar(self, id):
        try:
            cursor.execute("update trabajadores set nombre = %s, usuario = %s, contrasena = %s, rol = %s, especialidad = %s, status = %s where id_trabajadores = %s", (self.nombre, self.usuario, self.contrasena, self.rol, self.especialidad or None, self.status, id))
            conexion.commit()
            return True
        except:
            return False

    @staticmethod
    def eliminar(id):
        try:
            cursor.execute("delete from trabajadores where id_trabajadores = %s", (id,))
            conexion.commit()
            return True
        except:
            return False
