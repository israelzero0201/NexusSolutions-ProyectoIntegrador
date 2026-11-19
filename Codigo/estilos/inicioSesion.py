from estilos.estilos import Colors, Fonts, Sizes, primary_button, brand_logo, text_input, ctk

class InicioSesion:
    def __init__(self, ventana, on_login):
        super().__init__()
        self.ventana = ventana
        self.on_login = on_login
        self._build_header()
        self._build_body()
        self._build_footer()
    # -------------------------------------------------------------------------------------------------------------------------
    #                         View Pestaña Inicio de Sesión
    # -------------------------------------------------------------------------------------------------------------------------
    def _build_header(self):
        header = ctk.CTkFrame(self.ventana, fg_color=Colors.PRIMARY_DARK, corner_radius=0,
                              height=Sizes.HEADER_HEIGHT)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(1, weight=1)
        header.grid_rowconfigure(0, weight=1)

        brand_logo(header).grid(row=0, column=0, padx=32, sticky="w")

    def _build_body(self):
        body = ctk.CTkFrame(self.ventana, fg_color="transparent", corner_radius=0)
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
        self.password.grid(row=6, column=0, sticky="ew", padx=pad, pady=(6, 14))

        # Mensaje de error (vacío hasta que haga falta)
        self.lbl_error = ctk.CTkLabel(card, text="", font=Fonts.SMALL(),
                                      text_color=Colors.ERROR, anchor="w")
        self.lbl_error.grid(row=8, column=0, sticky="w", padx=pad, pady=(8, 0))

        # Botón
        primary_button(card, "Iniciar sesión", command=self.iniciar_sesion, icon=""
                       ).grid(row=9, column=0, sticky="ew", padx=pad, pady=(8, 16))

        ctk.CTkLabel(card, text="¿Necesitas acceso? Contacta al administrador.",
                     font=Fonts.SMALL(), text_color=Colors.TEXT_MUTED
                     ).grid(row=10, column=0, pady=(0, 28))

    def _build_footer(self):
        footer = ctk.CTkFrame(self.ventana, fg_color="transparent", corner_radius=0)
        footer.grid(row=2, column=0, sticky="ew")
        footer.grid_columnconfigure(0, weight=1)

        ctk.CTkFrame(footer, height=1, fg_color=Colors.BORDER, corner_radius=0
                     ).grid(row=0, column=0, columnspan=2, sticky="ew")
        ctk.CTkLabel(footer, text="© 2026 Eclipcom. Todos los derechos reservados.",
                     font=Fonts.TINY(), text_color=Colors.TEXT_MUTED
                     ).grid(row=1, column=0, sticky="w", padx=32, pady=16)
        ctk.CTkLabel(footer, text="Versión 1.0", font=Fonts.TINY(),
                     text_color=Colors.TEXT_MUTED
                     ).grid(row=1, column=1, sticky="e", padx=32, pady=16)

    def iniciar_sesion(self):
        usuario = self.usuario.get().strip()
        password = self.password.get()
        if not self.on_login(usuario, password):
            self.lbl_error.configure(text="Usuario o contraseña incorrectos.")
            self.usuario.focus()