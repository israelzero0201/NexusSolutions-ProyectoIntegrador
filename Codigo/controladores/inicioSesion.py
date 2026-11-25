from trabajadores.trabajadores import Trabajadores
from configuraciones import sesion

def controlador_iniciarSesion(ventana, usuario, password, vista_menuPrincipal, recordar=False):
    resultado = Trabajadores.iniciarSesion(usuario, password)
    if resultado:
        # resultado = (id_trabajadores, usuario, rol, nombre)
        sesion.iniciar(resultado[0], resultado[1], resultado[2], resultado[3], recordar)
        ventana.after(150, vista_menuPrincipal)
        return True
    return False
