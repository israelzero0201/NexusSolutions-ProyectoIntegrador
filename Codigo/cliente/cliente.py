from conexion import cursor, conexion

class Clientes:
    def __init__(self, razon, contacto, telefono, email):
        self.__razon = razon
        self.__contacto = contacto
        self.__telefono = telefono
        self.__email = email

    def registrarCliente(self):
        pass

    def actualizarDatos(self, telefonoNuevo):
        pass
    
    def obtenerHistorialPedidos(self):
        pass

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
    def consultar():
        try:
            cursor.execute("select * from clientes")
            return cursor.fetchall()
        except:
            return []

    def insertar(self):
        try:
            cursor.execute("insert into clientes values(null, %s, %s, %s, %s)", (self.razon, self.contacto, self.telefono, self.email))
            conexion.commit()
            return True
        except:
            return False

    def actualizar(self, id):
        try:
            cursor.execute("update clientes set razon_social = %s, persona_contacto = %s, telefono = %s, email = %s where id_cliente = %s", (self.razon, self.contacto, self.telefono, self.email, id))
            conexion.commit()
            return True
        except:
            return False

    @staticmethod
    def eliminar(id):
        try:
            cursor.execute("delete from clientes where id_cliente = %s", (id,))
            conexion.commit()
            return True
        except:
            return False