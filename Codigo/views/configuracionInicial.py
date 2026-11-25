from views.estilos import (enfocar_despues, Colors, Fonts, Sizes, primary_button, link_button, brand_logo,
                           campo_formulario, campo_select, ctk)
from views.formularioUsuario import validar_campos_usuario
from configuraciones import generalConfiguracion
from configuraciones.permisos import GESTION, descripcion_rol

class ConfiguracionInicial(ctk.CTkFrame):
    # Aparece solo cuando en la BD no hay ningún usuario activo de Ingeniero, Administrativo o Dueño.
    # Sirve para crear la primera cuenta con acceso completo; después todo se hace desde Usuarios.
    def __init__(self, master, crear_administrador, ir_a_login):
        super().__init__(master, fg_color="transparent", corner_radius=0)
        self.crear_administrador = crear_administrador
        self.ir_a_login = ir_a_login
        master.title("Eclipcom - Configuración inicial")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build_header()
        self._build_body()
        self._build_footer()
        enfocar_despues(self.nombre)

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color=Colors.PRIMARY_DARK, corner_radius=0,
                              height=Sizes.HEADER_HEIGHT)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(1, weight=1)
        header.grid_rowconfigure(0, weight=1)
        brand_logo(header).grid(row=0, column=0, padx=32, sticky="w")
        ctk.CTkLabel(header, text="Configuración inicial", font=Fonts.SMALL(),
                     text_color=Colors.TEXT_ON_DARK).grid(row=0, column=2, padx=32, sticky="e")

    def _build_body(self):
        body = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(0, weight=1)

        card = ctk.CTkFrame(body, fg_color=Colors.SURFACE, corner_radius=Sizes.CARD_RADIUS,
                            border_width=1, border_color=Colors.BORDER)
        card.grid(row=0, column=0)
        card.grid_columnconfigure((0, 1), weight=1, uniform="campos", minsize=250)

        pad = 32
        ctk.CTkLabel(card, text="🛠", width=40, height=40, font=Fonts.get(16),
                     text_color=Colors.TEXT_TITLE, fg_color=Colors.ACCENT_LIGHT,
                     corner_radius=Sizes.BUTTON_RADIUS
                     ).grid(row=0, column=0, sticky="w", padx=pad, pady=(28, 0))
        ctk.CTkLabel(card, text="Bienvenido a Eclipcom", font=Fonts.H1(),
                     text_color=Colors.TEXT_TITLE, anchor="w"
                     ).grid(row=1, column=0, columnspan=2, sticky="w", padx=pad, pady=(14, 4))
        ctk.CTkLabel(card, text="Todavía no hay ningún administrador. Crea la primera cuenta con acceso completo;\n"
                                "después podrás dar de alta a ingenieros, administrativos y técnicos desde Usuarios.",
                     font=Fonts.SMALL(), text_color=Colors.TEXT_MUTED, anchor="w", justify="left"
                     ).grid(row=2, column=0, columnspan=2, sticky="w", padx=pad, pady=(0, 18))

        marco, self.nombre = campo_formulario(card, "Nombre completo *", "Ej. Antonio Manzano")
        marco.grid(row=3, column=0, sticky="new", padx=(pad, 8))
        marco, self.usuario = campo_formulario(card, "Usuario *", "Ej. admin",
                                               ayuda="Sin espacios. Con él inicia sesión.")
        marco.grid(row=3, column=1, sticky="new", padx=(8, pad))
        marco, self.contrasena = campo_formulario(card, "Contraseña *", "Mínimo 4 caracteres", show="•")
        marco.grid(row=4, column=0, sticky="new", padx=(pad, 8), pady=(4, 0))
        marco, self.confirmacion = campo_formulario(card, "Confirmar contraseña *", "Repite la contraseña", show="•")
        marco.grid(row=4, column=1, sticky="new", padx=(8, pad), pady=(4, 0))

        # Solo roles con acceso completo
        marco, self.var_rol, _, self.lbl_rol = campo_select(
            card, "Rol *", list(GESTION), "Administrativo", command=self._mostrar_rol,
            ayuda=descripcion_rol("Administrativo"))
        marco.grid(row=5, column=0, sticky="new", padx=(pad, 8), pady=(4, 0))

        primary_button(card, "Crear administrador", command=self.crear, icon=""
                       ).grid(row=6, column=0, columnspan=2, sticky="ew", padx=pad, pady=(16, 8))

        acceso = ctk.CTkFrame(card, fg_color="transparent")
        acceso.grid(row=7, column=0, columnspan=2, pady=(0, 24))
        ctk.CTkLabel(acceso, text="¿Ya tienes una cuenta de técnico?", font=Fonts.SMALL(),
                     text_color=Colors.TEXT_MUTED).pack(side="left")
        link_button(acceso, "Iniciar sesión", command=self.ir_a_login).pack(side="left", padx=(4, 0))

        for entrada in (self.nombre, self.usuario, self.contrasena, self.confirmacion):
            entrada.bind("<Return>", lambda e: self.crear())

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

    def _mostrar_rol(self, _valor=None):
        self.lbl_rol.configure(text=descripcion_rol(self.var_rol.get()))

    def crear(self):
        if not validar_campos_usuario(self.nombre, self.usuario, self.contrasena, self.confirmacion,
                                      pedir_contrasena=True):
            return
        self.crear_administrador(self.nombre.get().strip(), self.usuario.get().strip(),
                                 self.contrasena.get(), self.var_rol.get())
