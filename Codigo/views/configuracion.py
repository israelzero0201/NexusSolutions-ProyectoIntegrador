from views.estilos import (Colors, Fonts, Sizes, MODOS, ACENTOS, MODO_DEFAULT, ACENTO_DEFAULT, outline_button,
                           form_card, page_header, tema_guardado, ctk, sidebar, header)
from configuraciones import generalConfiguracion, sesion
from configuraciones.permisos import rol_actual

class Configuracion(ctk.CTkFrame):
    # Apariencia de la app en esta computadora (se guarda en config.json)
    def __init__(self, master, on_logout, mainMenu, customers, orders, users, settings, cambiar_tema):
        super().__init__(master, fg_color=Colors.BG, corner_radius=0)
        master.title("Eclipcom - Configuración")
        self.cambiar_tema = cambiar_tema
        self.modo, self.acento = tema_guardado()
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        header(self)
        sidebar(self, on_logout, mainMenu, customers, orders, "configuracion", users=users, settings=settings)
        self._build_content()

    def _build_content(self):
        pad = Sizes.CONTENT_PAD
        content = ctk.CTkScrollableFrame(self, fg_color=Colors.BG, corner_radius=0)
        content.grid(row=1, column=1, sticky="nsew")
        content.grid_columnconfigure(0, weight=1)
        cuerpo = ctk.CTkFrame(content, fg_color="transparent")
        cuerpo.grid(row=0, column=0, sticky="nsew", padx=pad, pady=pad)
        cuerpo.grid_columnconfigure(0, weight=1)

        top = page_header(cuerpo, "Inicio / Configuración", "Configuración",
                          "Personaliza la apariencia de Eclipcom en esta computadora.")
        outline_button(top, "Restablecer", icon="↺", width=140,
                       command=lambda: self.cambiar_tema(MODO_DEFAULT, ACENTO_DEFAULT)
                       ).grid(row=0, column=1, rowspan=2, sticky="e")

        # Apariencia
        card, apariencia = form_card(cuerpo, "Apariencia", "Los cambios se aplican al instante", columnas=1)
        card.grid(row=2, column=0, sticky="ew")

        ctk.CTkLabel(apariencia, text="Modo", font=Fonts.SMALL(), text_color=Colors.TEXT_BODY,
                     anchor="w").grid(row=0, column=0, sticky="w")
        self.var_modo = ctk.StringVar(value=self.modo)
        ctk.CTkSegmentedButton(
            apariencia, values=list(MODOS), variable=self.var_modo, font=Fonts.SMALL(), height=34,
            selected_color=Colors.PRIMARY, selected_hover_color=Colors.PRIMARY_HOVER,
            unselected_color=Colors.ROW_ALT, unselected_hover_color=Colors.BORDER,
            fg_color=Colors.BORDER, text_color=Colors.TEXT_BODY,
            command=lambda modo: self.cambiar_tema(modo, self.acento),
        ).grid(row=1, column=0, sticky="w", pady=(6, 18))

        ctk.CTkLabel(apariencia, text="Color principal", font=Fonts.SMALL(), text_color=Colors.TEXT_BODY,
                     anchor="w").grid(row=2, column=0, sticky="w")
        colores = ctk.CTkFrame(apariencia, fg_color="transparent")
        colores.grid(row=3, column=0, sticky="w", pady=(6, 4))
        for i, (nombre, paleta) in enumerate(ACENTOS.items()):
            elegido = nombre == self.acento
            ctk.CTkButton(
                colores, text=f"✓  {nombre}" if elegido else nombre, width=150, height=56,
                corner_radius=Sizes.CARD_RADIUS, font=Fonts.BUTTON(), text_color="#FFFFFF",
                fg_color=paleta["principal"], hover_color=paleta["hover"],
                border_width=3 if elegido else 0, border_color=Colors.TEXT_BODY,
                command=lambda n=nombre: self.cambiar_tema(self.modo, n),
            ).grid(row=0, column=i, padx=(0, 12))

        ctk.CTkLabel(apariencia, text="Se guarda en esta computadora; cada integrante puede elegir el suyo.",
                     font=Fonts.TINY(), text_color=Colors.TEXT_MUTED, anchor="w"
                     ).grid(row=4, column=0, sticky="w", pady=(8, 0))

        # Acerca de
        card, acerca = form_card(cuerpo, "Acerca de", "", columnas=1)
        card.grid(row=3, column=0, sticky="ew", pady=(16, 0))
        datos = sesion.actual()
        for i, texto in enumerate((
                f"Eclipcom · versión {generalConfiguracion.GeneralConfig.version()}",
                f"Sesión: {datos.get('nombre') or datos.get('usuario') or '—'} ({rol_actual() or 'sin rol'})")):
            ctk.CTkLabel(acerca, text=texto, font=Fonts.SMALL(), text_color=Colors.TEXT_BODY,
                         anchor="w").grid(row=i, column=0, sticky="w", pady=2)
