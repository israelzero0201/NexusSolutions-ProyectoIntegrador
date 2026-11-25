from conexion import cursor, conexion, deshacer

class Clientes:
    def __init__(self, razon, contacto, telefono, email):
        self.__razon = razon
        self.__contacto = contacto
        self.__telefono = telefono
        self.__email = email

    def registrarCliente(self):
        return self.insertar()

    def actualizarDatos(self, id, telefonoNuevo):
        self.telefono = telefonoNuevo
        return self.actualizar(id)

    @staticmethod
    def obtenerHistorialPedidos(id):
        try:
            cursor.execute("select id_orden, descripcion, fecha_programada, status, monto_total from ordenes_info where id_cliente = %s order by id_orden desc", (id,))
            return cursor.fetchall()
        except:
            return []

    @property
    def razon(self):
        return self.__razon

    @razon.setter
    def razon(self, value):
        self.__razon = value

    @property
    def contacto(self):
        return self.__contacto

    @contacto.setter
    def contacto(self, value):
        self.__contacto = value

    @property
    def telefono(self):
        return self.__telefono

    @telefono.setter
    def telefono(self, value):
        self.__telefono = value

    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, value):
        self.__email = value

    @staticmethod
    def clave(id):
        # 1 -> "CL-001"
        return f"CL-{int(id):03d}"

    @staticmethod
    def consultar():
        # Columnas en orden fijo: id, razon_social, persona_contacto, telefono, email
        try:
            cursor.execute("select id_cliente, razon_social, persona_contacto, telefono, email from clientes order by id_cliente")
            return cursor.fetchall()
        except:
            return []

    @staticmethod
    def consultar_id(id):
        try:
            cursor.execute("select id_cliente, razon_social, persona_contacto, telefono, email from clientes where id_cliente = %s", (id,))
            return cursor.fetchone()
        except:
            return None

    def insertar(self):
        try:
            cursor.execute("insert into clientes (razon_social, persona_contacto, telefono, email) values (%s, %s, %s, %s)", (self.razon, self.contacto, self.telefono, self.email))
            conexion.commit()
            return True
        except:
            deshacer()
            return False

    def actualizar(self, id):
        try:
            cursor.execute("update clientes set razon_social = %s, persona_contacto = %s, telefono = %s, email = %s where id_cliente = %s", (self.razon, self.contacto, self.telefono, self.email, id))
            conexion.commit()
            return True
        except:
            deshacer()
            return False

    @staticmethod
    def eliminar(id):
        try:
            cursor.execute("delete from clientes where id_cliente = %s", (id,))
            conexion.commit()
            return True
        except:
            deshacer()
            return False

    @staticmethod
    def cantidad_clientes():
        try:
            cursor.execute("SELECT COUNT(id_cliente) FROM clientes")
            return cursor.fetchone()[0]
        except:
            return 0
