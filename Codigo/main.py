from estilos.estilos import Colors, Sizes, apply_theme, ctk
from estilos.inicioSesion import InicioSesion
from trabajadores.trabajadores import Trabajadores
from configuraciones import sesion
from conexion import cursor

sesion_iniciada = sesion.cargar()

# ROLES = ("Tecnico", "Ingeniero", "Administrativo", "Dueño")
# STATUS_TRABAJADOR = ("activo", "inactivo")
# TIPOS_ORDEN = ("instalacion", "mantenimiento")
# STATUS_ORDEN = ("pendiente", "asignada", "en_proceso", "concluida", "cancelada")

class App():
    def __init__(self, ventana):
        self.ventana = ventana
        apply_theme()
        w, h = Sizes.WINDOW
        self.ventana.geometry(f"{w}x{h}")
        self.ventana.minsize(720, 560)
        # Esto maximiza la ventana por defecto
        self.ventana.after(0, lambda: self.ventana.state("zoomed"))
        self.ventana.configure(fg_color=Colors.BG)
        self.ventana.grid_columnconfigure(0, weight=1)
        self.ventana.grid_rowconfigure(1, weight=1)
        # Intercepta el botón cerrar
        self.ventana.protocol("WM_DELETE_WINDOW", self.cerrar)
        self.main()

#     # ------Utilidades-------

    def borrarPantalla(self):
        for widget in self.ventana.winfo_children():
            widget.destroy()

    def cerrar(self):
        cursor.close()
        self.ventana.destroy()
        sesion.borrar()

#     def campo(self, padre, texto, valores=None, oculto=False):
#         Label(padre, text=texto).pack()
#         if valores:
#             entrada = ttk.Combobox(padre, values=valores, state="readonly")
#             entrada.current(0)
#         elif oculto:
#             entrada = Entry(padre, show="*")
#         else:
#             entrada = Entry(padre)
#         entrada.pack(pady=5)
#         return entrada

#     def respuesta_sql(self, respuesta):
#         if respuesta:
#             messagebox.showinfo(title="... Exitoso ...", message="...¡Accion Realizada con Exito!...")
#         else:
#             messagebox.showerror(title="...Verifica por favor!", message="... ¡Esta accion no pudo realizarse en este momento!...")

#     def id_view(self, mensaje, boton, controller, regresar):
#         self.borrarPantalla()
#         Label(self.ventana, text = mensaje).pack(pady= 10)
#         Label(self.ventana, text = "ID: ").pack()
#         self.id = Entry(self.ventana)
#         self.id.focus()
#         self.id.pack(pady=5)

#         Button(self.ventana, text=boton, command= controller).pack(pady=10)
#         Button(self.ventana, text="Regresar", command= regresar).pack(pady=10)

#     # ------------------------------------------------------------------------------------------------------------------------------
#                                                           VIstas
#       ------------------------------------------------------------------------------------------------------------------------------
    def main(self):
        if sesion_iniciada:
            self.vista_menuPrincipal()    
        else:
            self.vista_inicioSesion()


    def vista_inicioSesion(self):
        self.borrarPantalla()
        inicia = InicioSesion(self.ventana, self.controlador_iniciarSesion)
        return inicia

    def vista_menuPrincipal(self):
        self.borrarPantalla()
        ctk.CTkLabel(self.ventana, text="\n...::: SISTEMA DE ÓRDENES ECLIPSE :::...").pack(pady=10)
        ctk.CTkButton(self.ventana, text="1.- Clientes", command="self.menu_clientes").pack(pady=5)
        ctk.CTkButton(self.ventana, text="2.- Trabajadores", command="self.menu_trabajadores").pack(pady=5)
        ctk.CTkButton(self.ventana, text="3.- Órdenes", command="self.menu_ordenes").pack(pady=5)
        ctk.CTkButton(self.ventana, text="4.- Salir", command=self.cerrar).pack(pady=5)
    

#     def menu_acciones(self, tipo, acciones):
#         self.borrarPantalla()
#         Label(self.ventana, text=f"...::: Menu de {tipo} :::...").pack(pady=10)
#         numero = 1
#         for texto, comando in acciones:
#             Button(self.ventana, text=f"{numero}.- {texto}", command=comando).pack(pady=5)
#             numero += 1
#         Button(self.ventana, text=f"{numero}.- Salir", command=self.main).pack(pady=5)

#     def menu_clientes(self):
#         self.menu_acciones("Clientes", [
#             ("Agregar", self.insertar_cliente_view),
#             ("Borrar", self.borrar_cliente_view),
#             ("Modificar", self.modificar_cliente_view),
#             ("Mostrar", self.consultar_cliente_view)])

#     def menu_trabajadores(self):
#         self.menu_acciones("Trabajadores", [
#             ("Agregar", self.insertar_trabajador_view),
#             ("Borrar", self.borrar_trabajador_view),
#             ("Modificar", self.modificar_trabajador_view),
#             ("Mostrar", self.consultar_trabajador_view)])

#     def menu_ordenes(self):
#         self.menu_acciones("Órdenes", [
#             ("Crear orden", self.insertar_orden_view),
#             ("Borrar", self.borrar_orden_view),
#             ("Modificar", self.modificar_orden_view),
#             ("Mostrar", self.consultar_orden_view),
#             ("Asignar técnico", self.tecnico_view),
#             ("Concluir orden", self.concluir_orden_view),
#             ("Cancelar orden", self.cancelar_orden_view)])

#     # ------Vistas Clientes-------

#     def campos_cliente(self):
#         self.razon = self.campo(self.ventana, "Razón social: ")
#         self.razon.focus()
#         self.contacto = self.campo(self.ventana, "Persona de contacto: ")
#         self.telefono = self.campo(self.ventana, "Teléfono: ")
#         self.email = self.campo(self.ventana, "Email: ")

#     def insertar_cliente_view(self):
#         self.borrarPantalla()
#         Label(self.ventana, text = "... Ingresar los datos del cliente ...").pack(pady= 10)
#         self.campos_cliente()
#         Button(self.ventana, text="Guardar", command= self.insertar_cliente_controller).pack(pady=10)
#         Button(self.ventana, text="Regresar", command= self.menu_clientes).pack(pady=10)

#     def borrar_cliente_view(self):
#         self.id_view("... Ingresa el ID del cliente a eliminar ...", "Eliminar", self.eliminar_cliente_controller, self.menu_clientes)

#     def modificar_cliente_view(self):
#         self.borrarPantalla()
#         Label(self.ventana, text = "... Ingresa el ID del cliente a modificar ...").pack(pady= 10)
#         self.id = self.campo(self.ventana, "ID: ")
#         self.id.focus()
#         self.campos_cliente()
#         Button(self.ventana, text="Modificar", command= self.modificar_cliente_controller).pack(pady=10)
#         Button(self.ventana, text="Regresar", command= self.menu_clientes).pack(pady=10)

#     def consultar_cliente_view(self):
#         self.borrarPantalla()
#         Label(self.ventana, text="::: Consultar los clientes:::" ).pack(pady=10)
#         filas = ""
#         filas=self.consultar_cliente_controller(filas)
#         Label(self.ventana, text=f"{'NO':<6}{'ID':<6}{'RAZON SOCIAL':<20}{'CONTACTO':<18}{'TELEFONO':<14}{'EMAIL':<20}").pack(pady=5)
#         Label(self.ventana, text="-"*200).pack(pady=5)
#         Label(self.ventana, text=f"{filas}").pack(pady=5)
#         Label(self.ventana, text="-"*200).pack(pady=5)
#         Button(self.ventana, text="regresar", command=self.menu_clientes).pack(pady=5)

#     # ------Vistas Trabajadores-------

#     def campos_trabajador(self):
#         self.nombre = self.campo(self.ventana, "Nombre: ")
#         self.nombre.focus()
#         self.usuario = self.campo(self.ventana, "Usuario: ")
#         self.contrasena = self.campo(self.ventana, "Contraseña: ", oculto=True)
#         self.rol = self.campo(self.ventana, "Rol: ", ROLES)
#         self.especialidad = self.campo(self.ventana, "Especialidad: ")
#         self.status = self.campo(self.ventana, "Status: ", STATUS_TRABAJADOR)

#     def insertar_trabajador_view(self):
#         self.borrarPantalla()
#         Label(self.ventana, text = "... Ingresar los datos del trabajador ...").pack(pady= 10)
#         self.campos_trabajador()
#         Button(self.ventana, text="Guardar", command= self.insertar_trabajador_controller).pack(pady=10)
#         Button(self.ventana, text="Regresar", command= self.menu_trabajadores).pack(pady=10)

#     def borrar_trabajador_view(self):
#         self.id_view("... Ingresa el ID del trabajador a eliminar ...", "Eliminar", self.eliminar_trabajador_controller, self.menu_trabajadores)

#     def modificar_trabajador_view(self):
#         self.borrarPantalla()
#         Label(self.ventana, text = "... Ingresa el ID del trabajador a modificar ...").pack(pady= 10)
#         self.id = self.campo(self.ventana, "ID: ")
#         self.id.focus()
#         self.campos_trabajador()
#         Button(self.ventana, text="Modificar", command= self.modificar_trabajador_controller).pack(pady=10)
#         Button(self.ventana, text="Regresar", command= self.menu_trabajadores).pack(pady=10)

#     def consultar_trabajador_view(self):
#         self.borrarPantalla()
#         Label(self.ventana, text="::: Consultar los trabajadores:::" ).pack(pady=10)
#         filas = ""
#         filas=self.consultar_trabajador_controller(filas)
#         Label(self.ventana, text=f"{'NO':<6}{'ID':<6}{'NOMBRE':<20}{'USUARIO':<14}{'ROL':<16}{'ESPECIALIDAD':<16}{'STATUS':<10}").pack(pady=5)
#         Label(self.ventana, text="-"*200).pack(pady=5)
#         Label(self.ventana, text=f"{filas}").pack(pady=5)
#         Label(self.ventana, text="-"*200).pack(pady=5)
#         Button(self.ventana, text="regresar", command=self.menu_trabajadores).pack(pady=5)

#     # ------Vistas Ordenes-------

#     def campos_orden(self):
#         contenedor = Frame(self.ventana)
#         contenedor.pack(pady=5)
#         izquierda = Frame(contenedor)
#         izquierda.pack(side="left", padx=20, anchor="n")
#         derecha = Frame(contenedor)
#         derecha.pack(side="left", padx=20, anchor="n")

#         self.id_cliente = self.campo(izquierda, "ID del cliente: ")
#         self.id_cliente.focus()
#         self.tipo = self.campo(izquierda, "Tipo: ", TIPOS_ORDEN)
#         self.direccion = self.campo(izquierda, "Dirección del sitio: ")
#         self.descripcion = self.campo(izquierda, "Descripción: ")

#         self.fecha = self.campo(derecha, "Fecha (AAAA-MM-DD): ")
#         self.hora = self.campo(derecha, "Hora de inicio (HH:MM): ")
#         self.status = self.campo(derecha, "Status: ", STATUS_ORDEN)
#         self.monto = self.campo(derecha, "Monto total: ")
#         self.anticipo = self.campo(derecha, "Anticipo pagado: ", ("No", "Si"))

#     def insertar_orden_view(self):
#         self.borrarPantalla()
#         Label(self.ventana, text = "... Ingresar los datos de la orden ...").pack(pady= 10)
#         self.campos_orden()
#         Button(self.ventana, text="Guardar", command= self.insertar_orden_controller).pack(pady=10)
#         Button(self.ventana, text="Regresar", command= self.menu_ordenes).pack(pady=10)

#     def borrar_orden_view(self):
#         self.id_view("... Ingresa el ID de la orden a eliminar ...", "Eliminar", self.eliminar_orden_controller, self.menu_ordenes)

#     def modificar_orden_view(self):
#         self.borrarPantalla()
#         Label(self.ventana, text = "... Ingresa el ID de la orden a modificar ...").pack(pady= 10)
#         self.id = self.campo(self.ventana, "ID: ")
#         self.id.focus()
#         self.campos_orden()
#         Button(self.ventana, text="Modificar", command= self.modificar_orden_controller).pack(pady=10)
#         Button(self.ventana, text="Regresar", command= self.menu_ordenes).pack(pady=10)

#     def consultar_orden_view(self):
#         self.borrarPantalla()
#         Label(self.ventana, text="::: Consultar las órdenes:::" ).pack(pady=10)
#         filas = ""
#         filas=self.consultar_orden_controller(filas)
#         Label(self.ventana, text=f"{'NO':<5}{'ID':<5}{'CLIENTE':<9}{'TIPO':<15}{'FECHA':<13}{'HORA':<11}{'STATUS':<12}").pack(pady=5)
#         Label(self.ventana, text="-"*200).pack(pady=5)
#         Label(self.ventana, text=f"{filas}").pack(pady=5)
#         Label(self.ventana, text="-"*200).pack(pady=5)
#         Button(self.ventana, text="regresar", command=self.menu_ordenes).pack(pady=5)

#     def tecnico_view(self):
#         self.borrarPantalla()
#         Label(self.ventana, text = "... Asignar técnico a una orden ...").pack(pady= 10)
#         self.id_orden = self.campo(self.ventana, "ID de la orden: ")
#         self.id_orden.focus()
#         self.id_trabajador = self.campo(self.ventana, "ID del técnico: ")
#         Button(self.ventana, text="Asignar", command= self.asignar_tecnico_controller).pack(pady=10)
#         Button(self.ventana, text="Cambiar técnico", command= self.cambiar_tecnico_controller).pack(pady=10)
#         Button(self.ventana, text="Regresar", command= self.menu_ordenes).pack(pady=10)

#     def concluir_orden_view(self):
#         self.id_view("... Ingresa el ID de la orden a concluir ...", "Concluir", self.concluir_orden_controller, self.menu_ordenes)

#     def cancelar_orden_view(self):
#         self.id_view("... Ingresa el ID de la orden a cancelar ...", "Cancelar orden", self.cancelar_orden_controller, self.menu_ordenes)

# -------------------------------------------------------------------------------------------------------------------------
#                                           Controlador 
# -------------------------------------------------------------------------------------------------------------------------
    def controlador_iniciarSesion(self, usuario, password):
        resultado = Trabajadores.iniciarSesion(usuario, password)
        if len(resultado) > 0:
            sesion.guardar(usuario, resultado[2])  # Guardar usuario y rol en sesion.json
            self.ventana.after(150, self.vista_menuPrincipal)
            return True
        return False




#     def insertar_cliente_controller(self):
#         nuevo = cliente.Clientes(self.razon.get(), self.contacto.get(), self.telefono.get(), self.email.get())
#         respuesta = nuevo.insertar()
#         self.respuesta_sql(respuesta)

#     def eliminar_cliente_controller(self):
#         respuesta = cliente.Clientes.eliminar(self.id.get())
#         self.respuesta_sql(respuesta)

#     def modificar_cliente_controller(self):
#         modificado = cliente.Clientes(self.razon.get(), self.contacto.get(), self.telefono.get(), self.email.get())
#         respuesta = modificado.actualizar(self.id.get())
#         self.respuesta_sql(respuesta)
#         del modificado

#     def consultar_cliente_controller(self, filas):
#         registros = cliente.Clientes.consultar()
#         if len(registros) > 0:
#             num_clientes = 1
#             for fila in registros:
#                 filas = filas + f"\n#{num_clientes:<5}{fila[0]:<6}{fila[1]:<20}{fila[2]:<18}{fila[3]:<14}{(fila[4] or '')}"
#                 num_clientes += 1
#         else:
#             filas = "¡No existen datos que mostrar por el momento!"
#         return filas

# # ------ Controladores Trabajadores -------

#     def trabajador_desde_formulario(self):
#         return trabajadores.Trabajadores(self.nombre.get(), self.usuario.get(), self.contrasena.get(), self.rol.get(), self.especialidad.get(), self.status.get())

#     def insertar_trabajador_controller(self):
#         nuevo = self.trabajador_desde_formulario()
#         respuesta = nuevo.insertar()
#         self.respuesta_sql(respuesta)

#     def eliminar_trabajador_controller(self):
#         respuesta = trabajadores.Trabajadores.eliminar(self.id.get())
#         self.respuesta_sql(respuesta)

#     def modificar_trabajador_controller(self):
#         modificado = self.trabajador_desde_formulario()
#         respuesta = modificado.actualizar(self.id.get())
#         self.respuesta_sql(respuesta)
#         del modificado

#     def consultar_trabajador_controller(self, filas):
#         registros = trabajadores.Trabajadores.consultar()
#         if len(registros) > 0:
#             num_trabajadores = 1
#             for fila in registros:
#                 filas = filas + f"\n#{num_trabajadores:<5}{fila[0]:<6}{fila[1]:<20}{fila[2]:<14}{fila[3]:<16}{(fila[4] or ''):<16}{fila[5]:<10}"
#                 num_trabajadores += 1
#         else:
#             filas = "¡No existen datos que mostrar por el momento!"
#         return filas

# # ------ Controladores Ordenes -------

#     def orden_desde_formulario(self):
#         anticipo = 1 if self.anticipo.get() == "Si" else 0
#         return ordenes.ordenTrabajo(self.id_cliente.get(), self.tipo.get(), self.direccion.get(), self.descripcion.get(), self.fecha.get(), self.hora.get(), self.status.get(), self.monto.get(), anticipo)

#     def insertar_orden_controller(self):
#         nueva = self.orden_desde_formulario()
#         respuesta = nueva.crearOrden()
#         self.respuesta_sql(respuesta)

#     def eliminar_orden_controller(self):
#         respuesta = ordenes.ordenTrabajo.eliminarOrden(self.id.get())
#         self.respuesta_sql(respuesta)

#     def modificar_orden_controller(self):
#         modificada = self.orden_desde_formulario()
#         respuesta = modificada.actualizarOrden(self.id.get())
#         self.respuesta_sql(respuesta)
#         del modificada

#     def asignar_tecnico_controller(self):
#         respuesta = ordenes.ordenTrabajo.asignarTecnico(self.id_orden.get(), self.id_trabajador.get())
#         self.respuesta_sql(respuesta)

#     def cambiar_tecnico_controller(self):
#         respuesta = ordenes.ordenTrabajo.actualizarTecnico(self.id_orden.get(), self.id_trabajador.get())
#         self.respuesta_sql(respuesta)

#     def concluir_orden_controller(self):
#         respuesta = ordenes.ordenTrabajo.registrarConclusion(self.id.get())
#         self.respuesta_sql(respuesta)

#     def cancelar_orden_controller(self):
#         respuesta = ordenes.ordenTrabajo.cancelarOrden(self.id.get())
#         self.respuesta_sql(respuesta)

#     def consultar_orden_controller(self, filas):
#         registros = ordenes.ordenTrabajo.consultar()
#         if len(registros) > 0:
#             num_ordenes = 1
#             for fila in registros:
#                 fecha = str(fila[5]) if fila[5] else "-"
#                 hora = str(fila[6]) if fila[6] else "-"
#                 anticipo = "Si" if fila[9] else "No"
#                 tecnico = fila[10] if fila[10] else "Sin asignar"
#                 filas = filas + f"\n#{num_ordenes:<4}{fila[0]:<5}{fila[1]:<9}{fila[2]:<15}{fecha:<13}{hora:<11}{fila[7]:<12}"
#                 filas = filas + f"\n      Monto: ${fila[8]:.2f}  Anticipo: {anticipo}  Técnico: {tecnico}  Sitio: {fila[3][:30]}\n"
#                 num_ordenes += 1
#         else:
#             filas = "¡No existen datos que mostrar por el momento!"
#         return filas

if __name__ == "__main__":
    ventana = ctk.CTk()
    app = App(ventana)
    ventana.mainloop()