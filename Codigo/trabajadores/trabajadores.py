from conexion import cursor

class Trabajadores:
    def __init__(self, nombre, usuario, contrasena, rol, especialidad, status):
        self._nombre = nombre
        self._usuario = usuario
        self._contrasena = contrasena
        self._rol = rol
        self._especialidad = especialidad
        self._status = status

    def iniciarSesion(self):
        pass

    def cerrarSesion(self):
        pass

    def detalle(self):
        pass

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
    def stutus(self, value):
        self._status = value

    @staticmethod
    def consultar():
        try:
            cursor.execute("select * from trabajadores")
            return cursor.fetchall()
        except:
            return []

    def insertar(self):
        try:
            cursor.execute("insert into trabajadores values(null, %s, %s, %s, %s, %s, %s)", (self.nombre, self.usuario, self.contrasena, self.rol, self.especialidad, self.status))
            cursor.commit()
            return True
        except:
            return False

    def actulizar(self, id):
        try:
            cursor.execute("update trabajadores set nombre = %s, usuario = %s, contrasena = %s, rol = %s, especialidad = %s, status = %s where id = s%", (self.nombre, self.usuario, self.contrasena, self.rol, self.especialidad, self.status))
            cursor.commit()
            return True
        except:
            return False

    @staticmethod
    def eliminar(id):
        try:
            cursor.execute("delete from trabajadores where id = %s", (id))
            cursor.commit()
            return True
        except:
            return False


        