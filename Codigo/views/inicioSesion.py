from views.estilos import (enfocar_despues, Colors, Fonts, Sizes, primary_button, link_button, brand_logo,
                           text_input, checkbox, dialogo, ctk)
from configuraciones import generalConfiguracion

INTENTOS = 3            # intentos antes de bloquear el botón
ESPERA_SEGUNDOS = 30    # tiempo de bloqueo

class View_inicioSesion(ctk.CTkFrame):
    def __init__(self, master, inicio_sesion, vista_menuPrincipal):
        super().__init__(master, fg_color="transparent", corner_radius=0)
        self.inicio_sesion = inicio_sesion
        self.vista_menuPrincipal = vista_menuPrincipal
        self.intentos = INTENTOS
        master.title("Eclipcom - Inicio de Sesion")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build_header()
        self._build_body()
        self._build_footer()
        enfocar_despues(self.usuario)
    # -------------------------------------------------------------------------------------------------------------------------
    #                         View Pestaña Inicio de Sesión
    # -------------------------------------------------------------------------------------------------------------------------
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color=Colors.PRIMARY_DARK, corner_radius=0,
                              height=Sizes.HEADER_HEIGHT)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(1, weight=1)
        header.grid_rowconfigure(0, weight=1)

        brand_logo(header).grid(row=0, column=0, padx=32, sticky="w")
        ctk.CTkLabel(header, text="Sistema de gestión comercial", font=Fonts.SMALL(),
                     text_color=Colors.TEXT_ON_DARK).grid(row=0, column=2, padx=32, sticky="e")

    def _build_body(self):
        body = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(0, weight=1)

        center = ctk.CTkFrame(body, fg_color="transparent")
        center.grid(row=0, column=0)

        card = ctk.CTkFrame(center, fg_color=Colors.SURFACE, corner_radius=Sizes.CARD_RADIUS,
                            border_width=1, border_color=Colors.BORDER)
        card.pack()
        card.grid_columnconfigure(0, weight=1, minsize=Sizes.FORM_CARD_WIDTH)

        pad = 32
        # Ícono
        ctk.CTkLabel(card, text="🔒", width=40, height=40, font=Fonts.get(16),
                     text_color=Colors.TEXT_TITLE, fg_color=Colors.ACCENT_LIGHT,
                     corner_radius=Sizes.BUTTON_RADIUS
                     ).grid(row=0, column=0, sticky="w", padx=pad, pady=(32, 0))

        # Título
        ctk.CTkLabel(card, text="Inicio de sesión", font=Fonts.H1(),
                     text_color=Colors.TEXT_TITLE, anchor="w"
                     ).grid(row=1, column=0, sticky="w", padx=pad, pady=(14, 4))
        ctk.CTkLabel(card, text="Accede a tu cuenta para administrar tus clientes y\nventas en un solo lugar.",
                     font=Fonts.SMALL(), text_color=Colors.TEXT_MUTED, anchor="w", justify="left"
                     ).grid(row=2, column=0, sticky="w", padx=pad, pady=(0, 20))

        # Campos
        ctk.CTkLabel(card, text="Usuario", font=Fonts.SMALL(),
                     text_color=Colors.TEXT_BODY, anchor="w"
                     ).grid(row=3, column=0, sticky="w", padx=pad)
        self.usuario = text_input(card)
        self.usuario.grid(row=4, column=0, sticky="ew", padx=pad, pady=(6, 16))

        ctk.CTkLabel(card, text="Contraseña", font=Fonts.SMALL(),
                     text_color=Colors.TEXT_BODY, anchor="w"
                     ).grid(row=5, column=0, sticky="w", padx=pad)
        self.password = text_input(card, show="•")
        self.password.grid(row=6, column=0, sticky="ew", padx=pad, pady=(6, 0))

        # Mensaje de error (vacío hasta que haga falta)
        self.lbl_error = ctk.CTkLabel(card, text="", font=Fonts.SMALL(), height=20,
                                      text_color=Colors.ERROR, anchor="w")
        self.lbl_error.grid(row=7, column=0, sticky="w", padx=pad, pady=(4, 4))

        # Recordarme  /  ¿Olvidaste tu contraseña?
        opciones = ctk.CTkFrame(card, fg_color="transparent")
        opciones.grid(row=8, column=0, sticky="ew", padx=pad)
        opciones.grid_columnconfigure(0, weight=1)
        self.recordar = checkbox(opciones, "Recordarme")
        self.recordar.grid(row=0, column=0, sticky="w")
        link_button(opciones, "¿Olvidaste tu contraseña?", command=self.olvide_contrasena
                    ).grid(row=0, column=1, sticky="e")

        # Botón
        self.boton = primary_button(card, "Iniciar sesión", command=self.iniciar_sesion, icon="")
        self.boton.grid(row=9, column=0, sticky="ew", padx=pad, pady=(16, 16))

        ctk.CTkLabel(card, text="¿Necesitas acceso? Contacta al administrador.",
                     font=Fonts.SMALL(), text_color=Colors.TEXT_MUTED
                     ).grid(row=10, column=0, pady=(0, 28))

        ctk.CTkLabel(center, text="🛡  Tu información, centralizada y protegida.",
                     font=Fonts.TINY(), text_color=Colors.TEXT_MUTED).pack(pady=(14, 0))

        # Enter también inicia sesión
        self.usuario.bind("<Return>", lambda e: self.password.focus())
        self.password.bind("<Return>", lambda e: self.iniciar_sesion())

    def _build_footer(self):
        footer = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        footer.grid(row=2, column=0, sticky="ew")
        footer.grid_columnconfigure(0, weight=1)

        ctk.CTkFrame(footer, height=1, fg_color=Colors.BORDER, corner_radius=0
                     ).grid(row=0, column=0, columnspan=2, sticky="ew")
        ctk.CTkLabel(footer, text="© 2026 Eclipcom. Todos los derechos reservados.",
                     font=Fonts.TINY(), text_color=Colors.TEXT_MUTED
                     ).grid(row=1, column=0, sticky="w", padx=32, pady=16)
        ctk.CTkLabel(footer, text=f"Versión {generalConfiguracion.GeneralConfig.version()}",
                     font=Fonts.TINY(), text_color=Colors.TEXT_MUTED
                     ).grid(row=1, column=1, sticky="e", padx=32, pady=16)

    # -------------------------------------------------------------------------------------------------------------------------
    #                         Acciones
    # -------------------------------------------------------------------------------------------------------------------------
    def mostrar_error(self, mensaje):
        # Mockup 01 Error: borde rojo en la contraseña y mensaje debajo
        self.lbl_error.configure(text=mensaje)
        self.password.con_error = bool(mensaje)
        self.password.configure(border_color=Colors.ERROR if mensaje else Colors.BORDER)

    def iniciar_sesion(self):
        if self.boton.cget("state") == "disabled":
            return
        usuario = self.usuario.get().strip()
        password = self.password.get()
        if not usuario or not password:
            self.mostrar_error("Escribe tu usuario y tu contraseña.")
            return

        if self.inicio_sesion(self.master, usuario, password, self.vista_menuPrincipal,
                              bool(self.recordar.get())):
            self.mostrar_error("")
            return

        self.intentos -= 1
        self.password.delete(0, "end")
        if self.intentos > 0:
            texto = "intento" if self.intentos == 1 else "intentos"
            self.mostrar_error(f"Usuario o contraseña incorrectos. Te quedan {self.intentos} {texto}.")
            self.password.focus()
        else:
            self.mostrar_error(f"Demasiados intentos. Espera {ESPERA_SEGUNDOS} segundos.")
            self.boton.configure(state="disabled")
            self.after(ESPERA_SEGUNDOS * 1000, self.desbloquear)

    def desbloquear(self):
        if not self.winfo_exists():
            return
        self.intentos = INTENTOS
        self.boton.configure(state="normal")
        self.mostrar_error("")

    def olvide_contrasena(self):
        dialogo(self, "¿Olvidaste tu contraseña?",
                "Por seguridad, solo el administrador puede restablecerla. "
                "Contáctalo para recuperar tu acceso.")
