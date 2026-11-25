from conexion import cursor, conexion, deshacer
from configuraciones.permisos import normalizar, puede

class Trabajadores:
    def __init__(self, nombre, usuario, contrasena, rol, especialidad, status):
        self._nombre = nombre
        self._usuario = usuario
        self._contrasena = contrasena
        self._rol = rol
        self._especialidad = especialidad
        self._status = status
        self._sesion = False

    @staticmethod
    def iniciarSesion(usuario, contrasena):
        try:
            # Regresa (id_trabajadores, usuario, rol, nombre) o None si no coincide
            cursor.execute("select id_trabajadores, usuario, rol, nombre from trabajadores where usuario = %s and contrasena = %s and status = 'activo'", (usuario, contrasena))
            return cursor.fetchone()
        except:
            return None

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
    def clave(id):
        # 3 -> "US-003"
        return f"US-{int(id):03d}"

    @staticmethod
    def consultar():
        # (id, nombre, usuario, rol, especialidad, status)
        try:
            cursor.execute("select id_trabajadores, nombre, usuario, rol, especialidad, status from trabajadores order by id_trabajadores")
            return cursor.fetchall()
        except:
            return []

    @staticmethod
    def consultar_id(id):
        try:
            cursor.execute("select id_trabajadores, nombre, usuario, rol, especialidad, status from trabajadores where id_trabajadores = %s", (id,))
            return cursor.fetchone()
        except:
            return None

    @staticmethod
    def consultar_tecnicos():
        # Técnicos activos que se pueden asignar a una orden: (id, nombre, especialidad)
        try:
            cursor.execute("select id_trabajadores, nombre, especialidad, rol from trabajadores where status = 'activo' order by nombre")
            return [(id, nombre, especialidad) for id, nombre, especialidad, rol in cursor.fetchall()
                    if normalizar(rol) == "tecnico"]
        except:
            return []

    @staticmethod
    def hay_administrador():
        # True si existe al menos un usuario activo que pueda dar de alta usuarios
        # (Ingeniero, Administrativo o Dueño). Si no hay, se muestra la configuración inicial.
        try:
            cursor.execute("select rol from trabajadores where status = 'activo'")
            return any(puede("editar_usuarios", fila[0]) for fila in cursor.fetchall())
        except:
            return True     # si la consulta falla no se ofrece crear un administrador

    @staticmethod
    def existeUsuario(usuario, excluir=None):
        # True si otro trabajador ya usa ese nombre de usuario (excluir = id del que se está editando)
        try:
            cursor.execute("select id_trabajadores from trabajadores where usuario = %s", (usuario,))
            return any(fila[0] != excluir for fila in cursor.fetchall())
        except:
            return False

    def insertar(self):
        try:
            cursor.execute("insert into trabajadores (nombre, usuario, contrasena, rol, especialidad, status) values (%s, %s, %s, %s, %s, %s)", (self.nombre, self.usuario, self.contrasena, self.rol, self.especialidad or None, self.status))
            conexion.commit()
            return True
        except:
            deshacer()
            return False

    def actualizar(self, id):
        # Si la contraseña viene vacía se conserva la que ya tenía
        try:
            if self.contrasena:
                cursor.execute("update trabajadores set nombre = %s, usuario = %s, contrasena = %s, rol = %s, especialidad = %s, status = %s where id_trabajadores = %s", (self.nombre, self.usuario, self.contrasena, self.rol, self.especialidad or None, self.status, id))
            else:
                cursor.execute("update trabajadores set nombre = %s, usuario = %s, rol = %s, especialidad = %s, status = %s where id_trabajadores = %s", (self.nombre, self.usuario, self.rol, self.especialidad or None, self.status, id))
            conexion.commit()
            return True
        except:
            deshacer()
            return False

    @staticmethod
    def verificarContrasena(id, contrasena):
        # Para confirmar acciones delicadas (por ejemplo, eliminar un usuario)
        try:
            cursor.execute("select 1 from trabajadores where id_trabajadores = %s and contrasena = %s and status = 'activo'", (id, contrasena))
            return cursor.fetchone() is not None
        except:
            return False

    @staticmethod
    def ventasAsignadas(id):
        try:
            cursor.execute("select count(*) from ordenes_tecnicos where id_trabajadores = %s", (id,))
            return cursor.fetchone()[0]
        except:
            return 0

    @staticmethod
    def eliminar(id):
        # Quita al trabajador de sus ventas (si alguna se queda sin técnico vuelve a pendiente) y lo borra
        try:
            cursor.execute("select id_orden_trabajo from ordenes_tecnicos where id_trabajadores = %s", (id,))
            ordenes = [fila[0] for fila in cursor.fetchall()]
            conexion.start_transaction()
            cursor.execute("delete from ordenes_tecnicos where id_trabajadores = %s", (id,))
            for id_orden in ordenes:
                cursor.execute("select count(*) from ordenes_tecnicos where id_orden_trabajo = %s", (id_orden,))
                if cursor.fetchone()[0] == 0:
                    cursor.execute("update ordenes_info set status = 'pendiente' where id_orden = %s and status = 'asignada'", (id_orden,))
            cursor.execute("delete from trabajadores where id_trabajadores = %s", (id,))
            conexion.commit()
            return True
        except:
            deshacer()
            return False
