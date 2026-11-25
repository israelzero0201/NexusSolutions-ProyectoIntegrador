from views.estilos import (enfocar_despues, Colors, Fonts, Sizes, primary_button, outline_button, danger_button, campo_formulario,
                           campo_select, marcar_error, deshabilitar, form_card, page_header, confirmar,
                           salir_sin_guardar, dialogo, text_input, ctk, sidebar, header, ROLES)
from configuraciones import sesion
from configuraciones.permisos import normalizar, descripcion_rol, puede
from trabajadores.trabajadores import Trabajadores

ESTADOS = {"activo": "Activo", "inactivo": "Inactivo"}
MIN_CONTRASENA = 4
AYUDA_ROLES = ("Técnico: consulta ventas y clientes, registra ventas nuevas, actualiza algunos datos y escribe en la bitácora.\n"
               "Administrativo: acceso completo, pero no elimina usuarios, pagos ni la bitácora.\n"
               "Ingeniero y Dueño: acceso completo, incluido eliminar.")

def validar_campos_usuario(nombre, usuario, contrasena, confirmacion, pedir_contrasena, excluir=None):
    # Recibe las cajas de texto, marca los errores y regresa True si todo está bien.
    # excluir = id del usuario que se está editando (para que no choque consigo mismo)
    usuario_txt = usuario.get().strip()
    if not usuario_txt:
        error_usuario = "Escribe el usuario."
    elif " " in usuario_txt:
        error_usuario = "El usuario no puede llevar espacios."
    elif Trabajadores.existeUsuario(usuario_txt, excluir):
        error_usuario = "Ese usuario ya existe. Elige otro."
    else:
        error_usuario = ""

    error_contrasena = error_confirmacion = ""
    if pedir_contrasena or contrasena.get() or confirmacion.get():
        if len(contrasena.get()) < MIN_CONTRASENA:
            error_contrasena = f"La contraseña debe tener al menos {MIN_CONTRASENA} caracteres."
        if contrasena.get() != confirmacion.get():
            error_confirmacion = "Las contraseñas no coinciden."

    errores = [
        (nombre, "" if nombre.get().strip() else "Escribe el nombre completo."),
        (usuario, error_usuario),
        (contrasena, error_contrasena),
        (confirmacion, error_confirmacion),
    ]
    primero = None
    for entrada, mensaje in errores:
        marcar_error(entrada, mensaje)
        if mensaje and primero is None:
            primero = entrada
    if primero is not None:
        primero.focus()
        return False
    return True


class FormularioUsuario(ctk.CTkFrame):
    # usuario = None para uno nuevo, o la tupla (id, nombre, usuario, rol, especialidad, status)
    def __init__(self, master, on_logout, mainMenu, customers, orders, users, settings, guardar, usuario=None, eliminar=None):
        super().__init__(master, fg_color=Colors.BG, corner_radius=0)
        self.guardar = guardar
        self.eliminar = eliminar
        self.usuario_bd = usuario
        self.users = users
        self.nuevo = usuario is None
        # Nadie puede cambiar su propio rol ni desactivarse (así no se queda sin acceso)
        self.propio = not self.nuevo and usuario[0] == sesion.actual().get("id")
        master.title("Eclipcom - Nuevo usuario" if self.nuevo else "Eclipcom - Editar usuario")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        header(self)
        sidebar(self, lambda: self._salir(on_logout), lambda: self._salir(mainMenu),
                lambda: self._salir(customers), lambda: self._salir(orders), "usuarios", subpagina=True,
                users=lambda: self._salir(users), settings=lambda: self._salir(settings))
        self._build_content()
        self._llenar()
        self.inicial = self._valores()

    def _build_content(self):
        pad = Sizes.CONTENT_PAD
        content = ctk.CTkScrollableFrame(self, fg_color=Colors.BG, corner_radius=0)
        content.grid(row=1, column=1, sticky="nsew")
        content.grid_columnconfigure(0, weight=1)
        cuerpo = ctk.CTkFrame(content, fg_color="transparent")
        cuerpo.grid(row=0, column=0, sticky="nsew", padx=pad, pady=pad)
        cuerpo.grid_columnconfigure(0, weight=1)

        if self.nuevo:
            top = page_header(cuerpo, "Inicio / Usuarios / Nuevo usuario", "Nuevo usuario",
                              "Registra a un integrante del equipo y elige su nivel de acceso.")
        else:
            clave = Trabajadores.clave(self.usuario_bd[0])
            top = page_header(cuerpo, f"Inicio / Usuarios / {clave}", "Editar usuario",
                              f"Actualiza los datos y el acceso de {self.usuario_bd[1]}.")
        # Eliminar: solo Ingeniero y Dueño, y solo a otra persona (nadie se elimina a sí mismo)
        if not self.nuevo and not self.propio and self.eliminar is not None and puede("eliminar_usuarios"):
            danger_button(top, "Eliminar usuario", command=self._dialogo_eliminar, width=150
                          ).grid(row=0, column=1, rowspan=2, sticky="e", padx=(0, 10))
        outline_button(top, "Volver a usuarios", command=lambda: self._salir(self.users),
                       icon="←", width=170).grid(row=0, column=2, rowspan=2, sticky="e")

        # Datos del usuario
        detalle = "ID asignado al guardar" if self.nuevo else f"Usuario {Trabajadores.clave(self.usuario_bd[0])}"
        card, datos = form_card(cuerpo, "Datos del usuario", detalle)
        card.grid(row=2, column=0, sticky="ew")
        marco, self.nombre = campo_formulario(datos, "Nombre completo *", "Ej. Ana Martínez")
        marco.grid(row=0, column=0, sticky="new", padx=(0, 10))
        marco, self.especialidad = campo_formulario(datos, "Especialidad", "Ej. CCTV, redes, cableado",
                                                    ayuda="Útil para técnicos. Opcional.")
        marco.grid(row=0, column=1, sticky="new", padx=(10, 0))

        # Acceso al sistema
        card, acceso = form_card(cuerpo, "Acceso al sistema", "El rol define qué puede hacer en Eclipcom")
        card.grid(row=3, column=0, sticky="ew", pady=(16, 0))
        marco, self.usuario = campo_formulario(acceso, "Usuario *", "Ej. amartinez",
                                               ayuda="Sin espacios. Con él inicia sesión.")
        marco.grid(row=0, column=0, sticky="new", padx=(0, 10))
        marco, self.var_rol, self.menu_rol, self.lbl_rol = campo_select(
            acceso, "Rol *", list(ROLES), ROLES[0], command=self._mostrar_rol,
            ayuda=descripcion_rol(ROLES[0]), tooltip_texto=AYUDA_ROLES)
        marco.grid(row=0, column=1, sticky="new", padx=(10, 0))

        if self.nuevo:
            marco, self.contrasena = campo_formulario(acceso, "Contraseña *", "Mínimo 4 caracteres", show="•")
            marco2, self.confirmacion = campo_formulario(acceso, "Confirmar contraseña *", "Repite la contraseña", show="•")
        else:
            marco, self.contrasena = campo_formulario(acceso, "Nueva contraseña", "Mínimo 4 caracteres",
                                                      ayuda="Déjala vacía para conservar la actual.", show="•")
            marco2, self.confirmacion = campo_formulario(acceso, "Confirmar nueva contraseña", "Repite la contraseña", show="•")
        marco.grid(row=1, column=0, sticky="new", padx=(0, 10), pady=(4, 0))
        marco2.grid(row=1, column=1, sticky="new", padx=(10, 0), pady=(4, 0))

        marco, self.var_estado, self.menu_estado, self.lbl_estado = campo_select(
            acceso, "Estado", list(ESTADOS.values()), ESTADOS["activo"],
            ayuda="Un usuario inactivo no puede iniciar sesión.")
        marco.grid(row=2, column=0, sticky="new", padx=(0, 10), pady=(4, 0))

        # Pie
        pie = ctk.CTkFrame(cuerpo, fg_color="transparent")
        pie.grid(row=4, column=0, sticky="ew", pady=(16, 0))
        pie.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(pie, text="* Campos obligatorios", font=Fonts.TINY(),
                     text_color=Colors.TEXT_MUTED).grid(row=0, column=0, sticky="w")
        outline_button(pie, "Cancelar", command=lambda: self._salir(self.users),
                       width=110).grid(row=0, column=1, padx=(0, 10))
        primary_button(pie, "Guardar usuario" if self.nuevo else "Guardar cambios",
                       command=self._guardar, icon="", width=150).grid(row=0, column=2)

    def _llenar(self):
        if self.nuevo:
            enfocar_despues(self.nombre)
            return
        id_trabajador, nombre, usuario, rol, especialidad, status = self.usuario_bd
        if nombre:
            self.nombre.insert(0, nombre)
        if especialidad:
            self.especialidad.insert(0, especialidad)
        if usuario:
            self.usuario.insert(0, usuario)
        # El rol de la BD puede venir con otro acento/mayúsculas: se busca el equivalente
        rol_lista = next((r for r in ROLES if normalizar(r) == normalizar(rol)), ROLES[0])
        self.var_rol.set(rol_lista)
        self._mostrar_rol()
        self.var_estado.set(ESTADOS.get(str(status).lower(), ESTADOS["activo"]))
        if self.propio:
            deshabilitar(self.menu_rol)
            deshabilitar(self.menu_estado)
            self.lbl_estado.configure(text="No puedes cambiar tu propio rol ni desactivarte.")

    def _mostrar_rol(self, _valor=None):
        self.lbl_rol.configure(text=descripcion_rol(self.var_rol.get()))

    def _valores(self):
        return (self.nombre.get().strip(), self.especialidad.get().strip(), self.usuario.get().strip(),
                self.var_rol.get(), self.contrasena.get(), self.confirmacion.get(), self.var_estado.get())

    # -------------------------------------------------------------------------------------------------------------------------
    #                         Validación y guardado
    # -------------------------------------------------------------------------------------------------------------------------
    def _validar(self):
        return validar_campos_usuario(self.nombre, self.usuario, self.contrasena, self.confirmacion,
                                      pedir_contrasena=self.nuevo,
                                      excluir=None if self.nuevo else self.usuario_bd[0])

    def _guardar(self):
        if not self._validar():
            return
        nombre, especialidad, usuario, rol, contrasena, confirmacion, estado = self._valores()
        status = next(clave for clave, texto in ESTADOS.items() if texto == estado)

        if self.nuevo:
            self.guardar(nombre, usuario, contrasena, rol, especialidad, status)
        elif self._valores() == self.inicial:
            dialogo(self, "No hay cambios por guardar",
                    "Modifica algún dato del usuario o usa «Volver a usuarios».")
        else:
            confirmar(self, "¿Estás seguro de hacer los cambios?",
                      lambda: self.guardar(nombre, usuario, contrasena, rol, especialidad, status))

    def _dialogo_eliminar(self):
        # Pide otra vez la contraseña de quien tiene la sesión abierta antes de eliminar
        id_usuario, nombre = self.usuario_bd[0], self.usuario_bd[1]
        ventas = Trabajadores.ventasAsignadas(id_usuario)
        aviso = "Esta acción no se puede deshacer."
        if ventas:
            aviso += (f" Tiene {ventas} venta(s) asignada(s): se quitará de ellas y las que se queden"
                      " sin técnico volverán a Pendiente.")
        aviso += " Si solo quieres quitarle el acceso, mejor márcalo como Inactivo."
        campos = {}

        def construir(marco):
            ctk.CTkLabel(marco, text="Escribe tu contraseña para confirmar", font=Fonts.SMALL(),
                         text_color=Colors.TEXT_BODY, anchor="w").pack(anchor="w")
            campos["contrasena"] = text_input(marco, "Tu contraseña", show="•")
            campos["contrasena"].pack(fill="x", pady=(6, 0))
            campos["error"] = ctk.CTkLabel(marco, text="", font=Fonts.TINY(), height=18,
                                           text_color=Colors.ERROR, anchor="w")
            campos["error"].pack(anchor="w")
            # Se programa en la ventana principal y se revisa que el campo siga existiendo
            self.winfo_toplevel().after(150, lambda: campos["contrasena"].focus()
                                        if campos["contrasena"].winfo_exists() else None)

        def confirmar_eliminacion():
            contrasena = campos["contrasena"].get()
            if not Trabajadores.verificarContrasena(sesion.actual().get("id"), contrasena):
                campos["contrasena"].con_error = True
                campos["contrasena"].configure(border_color=Colors.ERROR)
                campos["error"].configure(text="Contraseña incorrecta.")
                campos["contrasena"].delete(0, "end")
                return False        # el diálogo sigue abierto
            self.after(10, lambda: self.eliminar(id_usuario, contrasena))
            return True

        dialogo(self, f"¿Eliminar a {nombre}?", aviso,
                [("Cancelar", None, "contorno"), ("Eliminar", confirmar_eliminacion, "peligro", True)],
                construir=construir, ancho=440)

    def _salir(self, destino):
        if self._valores() != self.inicial:
            salir_sin_guardar(self, destino)
        else:
            destino()
