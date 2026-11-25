import sys
import tkinter
from pathlib import Path
import customtkinter as ctk
from configuraciones import generalConfiguracion, sesion, permisos

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
ROLES = ("Tecnico", "Ingeniero", "Administrativo")

class Colors:
    PRIMARY_DARK = "#012F6B"      # Header y sidebar
    PRIMARY = "#0B4FB3"           # Botones y item activo del sidebar
    PRIMARY_HOVER = "#093F8F"
    SIDEBAR_HOVER = "#0A3E87"
    ACCENT_LIGHT = "#8BD0F0"      # Tarjetas de módulos
    BG = "#F3F7FC"                # Fondo del contenido
    SURFACE = "#FFFFFF"           # Tarjeta de tabla
    ROW_ALT = "#F7F9FC"
    BORDER = "#DCE3EE"
    TEXT_TITLE = "#0B2F6B"
    TEXT_BODY = "#1E2A3B"
    TEXT_MUTED = "#5F6F86"
    TEXT_ON_DARK = "#FFFFFF"
    TEXT_SIDEBAR_SECTION = "#A9BCDC"
    LINK = "#1558C0"
    AVATAR_BG = "#8BD0F0"
    AVATAR_TEXT = "#012F6B"
    ERROR = "#C0392B"
    ERROR_HOVER = "#A93226"
    SUCCESS_BG = "#EAF7EF"        # Aviso "Venta guardada correctamente"
    SUCCESS_BORDER = "#8FD3A8"
    SUCCESS_TEXT = "#1E7B45"
    INPUT_DISABLED = "#F1F4F8"

class Fonts:
    FAMILY = "Inter"

    @staticmethod
    def get(size=12, weight="normal"):
        return ctk.CTkFont(family=Fonts.FAMILY, size=size, weight=weight)

    H1 = staticmethod(lambda: Fonts.get(26, "bold"))
    H2 = staticmethod(lambda: Fonts.get(20, "bold"))
    H3 = staticmethod(lambda: Fonts.get(16, "bold"))
    BODY = staticmethod(lambda: Fonts.get(13))
    BODY_BOLD = staticmethod(lambda: Fonts.get(13, "bold"))
    SMALL = staticmethod(lambda: Fonts.get(11))
    TINY = staticmethod(lambda: Fonts.get(10))
    BUTTON = staticmethod(lambda: Fonts.get(13, "bold"))


class Sizes:
    # Tamaño inicial de la ventana (main.py la maximiza con el tamaño real de la pantalla)
    WINDOW = (1280, 760)

    HEADER_HEIGHT = 64
    SIDEBAR_WIDTH = 240
    CONTENT_PAD = 32
    CARD_RADIUS = 10
    BUTTON_RADIUS = 6
    BUTTON_HEIGHT = 36
    SIDEBAR_ITEM_HEIGHT = 40
    TABLE_ROW_HEIGHT = 44
    TABLE_HEADER_HEIGHT = 40
    INPUT_HEIGHT = 40
    FORM_CARD_WIDTH = 440


# ----------------------------------------------------------------------
# TEMAS (Configuración): modo claro/oscuro + color principal
# ----------------------------------------------------------------------
MODOS = {
    "Claro": {"BG": "#F3F7FC", "SURFACE": "#FFFFFF", "ROW_ALT": "#F7F9FC", "BORDER": "#DCE3EE",
              "TEXT_BODY": "#1E2A3B", "TEXT_MUTED": "#5F6F86", "INPUT_DISABLED": "#F1F4F8",
              "SUCCESS_BG": "#EAF7EF", "SUCCESS_BORDER": "#8FD3A8", "SUCCESS_TEXT": "#1E7B45"},
    "Oscuro": {"BG": "#0F1620", "SURFACE": "#18212D", "ROW_ALT": "#1D2735", "BORDER": "#2C3A4D",
               "TEXT_BODY": "#E3E9F2", "TEXT_MUTED": "#9AA8BC", "INPUT_DISABLED": "#222D3B",
               "SUCCESS_BG": "#12301F", "SUCCESS_BORDER": "#2F7A4D", "SUCCESS_TEXT": "#7DDBA3"},
}

# oscuro/tarjeta/enlace_oscuro se usan en modo oscuro
ACENTOS = {
    "Azul Eclipcom": {"barra": "#012F6B", "principal": "#0B4FB3", "hover": "#093F8F", "barra_hover": "#0A3E87",
                      "claro": "#8BD0F0", "enlace": "#1558C0", "titulo": "#0B2F6B", "seccion": "#A9BCDC",
                      "oscuro": "#0A1A33", "tarjeta": "#16314F", "enlace_oscuro": "#7DB3F7"},
    # Colores del logo de Eclipse Comunicaciones: rojo, negro y azul
    "Eclipse": {"barra": "#141414", "principal": "#E30A17", "hover": "#B80812", "barra_hover": "#2A2A2A",
                "claro": "#F8C9CC", "enlace": "#08009F", "titulo": "#111111", "seccion": "#B3B3B3",
                "oscuro": "#050505", "tarjeta": "#3A1215", "enlace_oscuro": "#9C99FF"},
    "Verde": {"barra": "#0F4D3A", "principal": "#16865F", "hover": "#11694A", "barra_hover": "#145E47",
              "claro": "#A6E3C8", "enlace": "#127A55", "titulo": "#0F3F30", "seccion": "#A9D8C4",
              "oscuro": "#0B1F19", "tarjeta": "#173A30", "enlace_oscuro": "#6ED6AA"},
    "Morado": {"barra": "#3B1D6E", "principal": "#6A3FC8", "hover": "#5531A3", "barra_hover": "#4A2785",
               "claro": "#CDB9F5", "enlace": "#6236C2", "titulo": "#33195F", "seccion": "#C4B3E6",
               "oscuro": "#1A1030", "tarjeta": "#2D2147", "enlace_oscuro": "#B9A0F7"},
    "Vino": {"barra": "#6B1530", "principal": "#B3264F", "hover": "#8F1E3F", "barra_hover": "#7E1B39",
             "claro": "#F4B6C6", "enlace": "#B0244C", "titulo": "#5A1229", "seccion": "#E3AFBE",
             "oscuro": "#2A0D17", "tarjeta": "#47202C", "enlace_oscuro": "#F294AD"},
    "Grafito": {"barra": "#1F2933", "principal": "#3E4C59", "hover": "#323F4B", "barra_hover": "#2B3640",
                "claro": "#CBD2D9", "enlace": "#334E68", "titulo": "#1F2933", "seccion": "#9AA5B1",
                "oscuro": "#111820", "tarjeta": "#2A3440", "enlace_oscuro": "#A9BCD0"},
}
MODO_DEFAULT = "Claro"
ACENTO_DEFAULT = "Azul Eclipcom"


def aplicar_tema(modo, acento):
    # Cambia los colores de la clase Colors. Las pantallas que se dibujen después ya salen con el tema nuevo
    modo = modo if modo in MODOS else MODO_DEFAULT
    acento = acento if acento in ACENTOS else ACENTO_DEFAULT
    for nombre, valor in MODOS[modo].items():
        setattr(Colors, nombre, valor)
    a = ACENTOS[acento]
    Colors.PRIMARY = a["principal"]
    Colors.PRIMARY_HOVER = a["hover"]
    Colors.TEXT_SIDEBAR_SECTION = a["seccion"]
    Colors.AVATAR_BG = a["claro"]
    Colors.AVATAR_TEXT = a["barra"]
    if modo == "Oscuro":
        Colors.PRIMARY_DARK = a["oscuro"]
        Colors.SIDEBAR_HOVER = a["barra"]
        Colors.ACCENT_LIGHT = a["tarjeta"]
        Colors.LINK = a["enlace_oscuro"]
        Colors.TEXT_TITLE = "#EAF1FB"
    else:
        Colors.PRIMARY_DARK = a["barra"]
        Colors.SIDEBAR_HOVER = a["barra_hover"]
        Colors.ACCENT_LIGHT = a["claro"]
        Colors.LINK = a["enlace"]
        Colors.TEXT_TITLE = a["titulo"]
    ctk.set_appearance_mode("dark" if modo == "Oscuro" else "light")
    return modo, acento


# Ícono de la app (la "E" del logo) para la ventana, los diálogos y la barra de tareas
ICONO_ICO = Path(__file__).resolve().parent.parent / "recursos" / "eclipcom.ico"
ICONO_PNG = Path(__file__).resolve().parent.parent / "recursos" / "eclipcom.png"


def poner_icono(ventana):
    try:
        if sys.platform.startswith("win"):
            ventana.iconbitmap(str(ICONO_ICO))      # en Windows también evita el ícono de CustomTkinter
        else:
            ventana.icono = tkinter.PhotoImage(file=str(ICONO_PNG))
            ventana.iconphoto(False, ventana.icono)
    except (tkinter.TclError, OSError) as e:
        print(f"No se pudo poner el ícono: {e}")


def tema_guardado():
    config = generalConfiguracion.GeneralConfig
    return config.get("modo", MODO_DEFAULT), config.get("color", ACENTO_DEFAULT)


def apply_theme():
    ctk.set_default_color_theme("blue")
    aplicar_tema(*tema_guardado())


# ----------------------------------------------------------------------
# FORMATOS
# ----------------------------------------------------------------------
def fecha_corta(fecha):
    # 2026-11-04 -> "04 nov 2026"
    if not fecha:
        return "Sin fecha"
    return f"{fecha.day:02d} {MESES[fecha.month - 1][:3]} {fecha.year}"


def fecha_larga(fecha):
    # 2026-11-04 -> "4 de noviembre de 2026"
    return f"{fecha.day} de {MESES[fecha.month - 1]} de {fecha.year}"


def dinero(valor):
    # 18560 -> "$18,560.00"
    return f"${float(valor or 0):,.2f}"


def telefono_txt(telefono):
    # "6185252789" -> "618 525 2789"
    digitos = "".join(c for c in str(telefono or "") if c.isdigit())
    if len(digitos) == 10:
        return f"{digitos[:3]} {digitos[3:6]} {digitos[6:]}"
    return str(telefono or "")


def iniciales(nombre):
    # "Antonio Manzano" -> "AM"
    partes = str(nombre or "").split()
    return "".join(p[0] for p in partes[:2]).upper() or "EC"


# ----------------------------------------------------------------------
# COMPONENTES ESTILIZADOS
# ----------------------------------------------------------------------
def primary_button(parent, text, command=None, icon="→", **kw):
    return ctk.CTkButton(
        parent, text=f"{icon}  {text}" if icon else text, command=command,
        fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_HOVER,
        text_color=Colors.TEXT_ON_DARK, font=Fonts.BUTTON(),
        corner_radius=Sizes.BUTTON_RADIUS, height=kw.pop("height", Sizes.BUTTON_HEIGHT),
        width=kw.pop("width", 130), **kw,
    )


def outline_button(parent, text, command=None, icon="", **kw):
    # Botón blanco con borde azul ("Volver a ventas", "Cancelar", "Editar concepto")
    return ctk.CTkButton(
        parent, text=f"{icon}  {text}" if icon else text, command=command,
        fg_color=Colors.SURFACE, hover_color=Colors.BG, border_width=1,
        border_color=Colors.LINK, text_color=Colors.LINK, font=Fonts.BUTTON(),
        corner_radius=Sizes.BUTTON_RADIUS, height=kw.pop("height", Sizes.BUTTON_HEIGHT),
        width=kw.pop("width", 130), **kw,
    )


def danger_button(parent, text, command=None, **kw):
    return ctk.CTkButton(
        parent, text=text, command=command,
        fg_color=Colors.ERROR, hover_color=Colors.ERROR_HOVER,
        text_color=Colors.TEXT_ON_DARK, font=Fonts.BUTTON(),
        corner_radius=Sizes.BUTTON_RADIUS, height=kw.pop("height", Sizes.BUTTON_HEIGHT),
        width=kw.pop("width", 110), **kw,
    )


def link_button(parent, text, command=None, **kw):
    return ctk.CTkButton(
        parent, text=text, command=command, fg_color="transparent",
        hover_color=Colors.BG, text_color=kw.pop("text_color", Colors.LINK), font=Fonts.SMALL(),
        corner_radius=4, height=24, width=kw.pop("width", 0), **kw,
    )


def sidebar_button(parent, text, command, icon="", active=False):
    return ctk.CTkButton(
        parent, text=f"{icon}   {text}", command=command, anchor="w",
        fg_color=Colors.PRIMARY if active else "transparent",
        hover_color=Colors.PRIMARY if active else Colors.SIDEBAR_HOVER,
        text_color=Colors.TEXT_ON_DARK, font=Fonts.BODY(),
        corner_radius=Sizes.BUTTON_RADIUS, height=Sizes.SIDEBAR_ITEM_HEIGHT,
    )


def module_card(parent, icon, title, description, counter_text, button_text, command, wrap=380):
    card = ctk.CTkFrame(parent, fg_color=Colors.ACCENT_LIGHT,
                        corner_radius=Sizes.CARD_RADIUS)
    card.grid_columnconfigure(0, weight=1)

    top = ctk.CTkFrame(card, fg_color="transparent")
    top.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 0))
    top.grid_columnconfigure(1, weight=1)
    ctk.CTkLabel(top, text=icon, font=Fonts.get(20), text_color=Colors.TEXT_TITLE
                 ).grid(row=0, column=0, sticky="w")
    ctk.CTkLabel(top, text=counter_text, font=Fonts.TINY(), text_color=Colors.TEXT_TITLE
                 ).grid(row=0, column=1, sticky="e")

    ctk.CTkLabel(card, text=title, font=Fonts.H2(), text_color=Colors.TEXT_TITLE,
                 anchor="w").grid(row=1, column=0, sticky="w", padx=20, pady=(10, 4))
    ctk.CTkLabel(card, text=description, font=Fonts.SMALL(), text_color=Colors.TEXT_TITLE,
                 anchor="w", justify="left", wraplength=wrap
                 ).grid(row=2, column=0, sticky="w", padx=20)
    primary_button(card, button_text, command=command).grid(
        row=3, column=0, sticky="w", padx=20, pady=(16, 20))
    return card


def data_table(parent, columns, rows, action_text="Ver detalle", on_action=None):
    wrapper = ctk.CTkFrame(parent, fg_color=Colors.SURFACE, corner_radius=Sizes.CARD_RADIUS,
                           border_width=1, border_color=Colors.BORDER)
    table = ctk.CTkFrame(wrapper, fg_color="transparent", corner_radius=0)
    table.pack(fill="x", padx=1, pady=1)
    for i, (_, weight) in enumerate(columns):
        table.grid_columnconfigure(i, weight=weight, uniform="col")

    for i, (title, _) in enumerate(columns):
        ctk.CTkLabel(table, text=title, font=Fonts.get(11, "bold"),
                     text_color=Colors.TEXT_ON_DARK, fg_color=Colors.PRIMARY_DARK,
                     height=Sizes.TABLE_HEADER_HEIGHT, anchor="w", corner_radius=0
                     ).grid(row=0, column=i, sticky="nsew", ipadx=8)

    for r, row in enumerate(rows, start=1):
        bg = Colors.SURFACE if r % 2 else Colors.ROW_ALT
        for c, value in enumerate(row):
            ctk.CTkLabel(table, text=value, font=Fonts.SMALL(), text_color=Colors.TEXT_BODY,
                         fg_color=bg, height=Sizes.TABLE_ROW_HEIGHT, anchor="w",
                         corner_radius=0).grid(row=r, column=c, sticky="nsew", ipadx=8)
        cell = ctk.CTkFrame(table, fg_color=bg, corner_radius=0, height=Sizes.TABLE_ROW_HEIGHT)
        cell.grid(row=r, column=len(row), sticky="nsew")
        link_button(cell, action_text,
                    command=(lambda v=row: on_action(v)) if on_action else None
                    ).place(x=4, rely=0.5, anchor="w")
    return wrapper


def table_footer(tabla, inicio, mostrados, total, pagina, paginas, ir_a_pagina):
    # Pie de tabla: "Mostrando 1–6 de 6 registros"  Anterior [1] Siguiente
    pie = ctk.CTkFrame(tabla, fg_color=Colors.SURFACE, corner_radius=0, height=52)
    pie.pack(fill="x", padx=1, pady=(0, 1))
    pie.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(pie, text=f"Mostrando {inicio + 1}–{inicio + mostrados} de {total} registros",
                 font=Fonts.SMALL(), text_color=Colors.TEXT_MUTED
                 ).grid(row=0, column=0, sticky="w", padx=16, pady=14)

    pager = ctk.CTkFrame(pie, fg_color="transparent")
    pager.grid(row=0, column=1, sticky="e", padx=16)
    link_button(pager, "Anterior", command=lambda: ir_a_pagina(pagina - 1),
                state="normal" if pagina > 1 else "disabled").pack(side="left")
    for n in range(1, paginas + 1):
        activa = n == pagina
        ctk.CTkButton(
            pager, text=str(n), width=28, height=28, corner_radius=4, font=Fonts.SMALL(),
            fg_color=Colors.PRIMARY if activa else "transparent",
            hover_color=Colors.PRIMARY_HOVER if activa else Colors.BG,
            text_color=Colors.TEXT_ON_DARK if activa else Colors.LINK,
            command=lambda n=n: ir_a_pagina(n),
        ).pack(side="left", padx=2)
    link_button(pager, "Siguiente", command=lambda: ir_a_pagina(pagina + 1),
                state="normal" if pagina < paginas else "disabled").pack(side="left")
    return pie


def brand_logo(parent):
    logo = ctk.CTkFrame(parent, fg_color="transparent")
    ctk.CTkLabel(logo, text="E", width=28, height=28, font=Fonts.get(16, "bold"),
                 text_color=Colors.PRIMARY_DARK, fg_color=Colors.TEXT_ON_DARK,
                 corner_radius=4).pack(side="left")
    ctk.CTkLabel(logo, text="eclipcom", font=Fonts.get(18, "bold"),
                 text_color=Colors.TEXT_ON_DARK).pack(side="left", padx=(8, 0))
    return logo


def text_input(parent, placeholder="", show=None, **kw):
    entry = ctk.CTkEntry(
        parent, placeholder_text=placeholder, show=show or "",
        height=Sizes.INPUT_HEIGHT, corner_radius=Sizes.BUTTON_RADIUS,
        border_width=1, border_color=Colors.BORDER, fg_color=Colors.SURFACE,
        text_color=Colors.TEXT_BODY, placeholder_text_color=Colors.TEXT_MUTED,
        font=Fonts.BODY(), **kw,
    )
    # Si el campo tiene error, el borde se queda rojo aunque cambie el foco
    entry.con_error = False
    entry.bind("<FocusIn>", lambda e: entry.configure(
        border_color=Colors.ERROR if entry.con_error else Colors.PRIMARY))
    entry.bind("<FocusOut>", lambda e: entry.configure(
        border_color=Colors.ERROR if entry.con_error else Colors.BORDER))
    return entry


def text_area(parent, height=120, **kw):
    # Caja de texto de varias líneas (bitácora / notas)
    return ctk.CTkTextbox(
        parent, height=height, wrap="word", corner_radius=Sizes.BUTTON_RADIUS,
        border_width=1, border_color=Colors.BORDER, fg_color=Colors.SURFACE,
        text_color=Colors.TEXT_BODY, font=Fonts.BODY(), **kw,
    )


def texto_de(caja):
    # Texto de un CTkTextbox sin el salto de línea final que agrega Tk
    return caja.get("1.0", "end-1c")


def search_input(parent, placeholder, on_change):
    # Buscador con la "x" para limpiar el texto (como en los mockups de Ventas y Clientes)
    entry = text_input(parent, f"🔍  {placeholder}")
    entry.bind("<KeyRelease>", on_change)

    def limpiar():
        entry.delete(0, "end")
        parent.focus()          # quita el foco para que vuelva a verse el placeholder
        on_change()

    # Colores fijos: dentro de una caja de texto CTk no detecta bien el color de fondo
    ctk.CTkButton(entry, text="✕", command=limpiar, width=24, height=24, corner_radius=4,
                  fg_color=Colors.SURFACE, bg_color=Colors.SURFACE, hover_color=Colors.BG,
                  text_color=Colors.TEXT_MUTED, font=Fonts.SMALL()
                  ).place(relx=1.0, x=-8, rely=0.5, anchor="e")
    return entry


def select_input(parent, valores, inicial, command=None, border=None,
                 text_color=None, width=140, expandir=True):
    # Lista desplegable con borde. Regresa (caja, variable, menu)
    border = border or Colors.BORDER
    text_color = text_color or Colors.TEXT_BODY
    caja = ctk.CTkFrame(parent, fg_color=Colors.SURFACE, border_width=1,
                        border_color=border, corner_radius=Sizes.BUTTON_RADIUS)
    var = ctk.StringVar(value=inicial)
    menu = ctk.CTkOptionMenu(
        caja, values=valores, variable=var, command=command, width=width,
        fg_color=Colors.SURFACE, button_color=Colors.SURFACE,
        button_hover_color=Colors.BG, text_color=text_color,
        text_color_disabled=Colors.TEXT_MUTED,
        dropdown_fg_color=Colors.SURFACE, dropdown_text_color=Colors.TEXT_BODY,
        dropdown_hover_color=Colors.BG, font=Fonts.SMALL(), dropdown_font=Fonts.SMALL(),
        height=Sizes.INPUT_HEIGHT - 6, corner_radius=Sizes.BUTTON_RADIUS - 2,
        dynamic_resizing=not expandir,
    )
    if expandir:
        menu.pack(fill="x", padx=2, pady=2)
    else:
        menu.pack(padx=2, pady=2)
    return caja, var, menu


def checkbox(parent, text, **kw):
    return ctk.CTkCheckBox(
        parent, text=text, font=Fonts.SMALL(), text_color=Colors.TEXT_BODY,
        fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_HOVER,
        border_color=Colors.BORDER, border_width=1,
        checkbox_width=16, checkbox_height=16, corner_radius=3, **kw,
    )


def enfocar_despues(widget, ms=100):
    # Pone el cursor en un campo un momento después de dibujar la pantalla.
    # Se programa en la ventana principal y revisa que el campo siga existiendo (por si ya se cambió de pantalla)
    widget.winfo_toplevel().after(ms, lambda: widget.focus() if widget.winfo_exists() else None)


def campo_formulario(parent, texto, placeholder="", ayuda="", show=None):
    # Etiqueta + caja de texto + renglón para ayuda o error. Regresa (marco, entrada)
    marco = ctk.CTkFrame(parent, fg_color="transparent")
    marco.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(marco, text=texto, font=Fonts.SMALL(), text_color=Colors.TEXT_BODY,
                 anchor="w").grid(row=0, column=0, sticky="w")
    entrada = text_input(marco, placeholder, show=show)
    entrada.grid(row=1, column=0, sticky="ew", pady=(6, 0))
    entrada.ayuda = ayuda
    entrada.lbl_error = ctk.CTkLabel(marco, text=ayuda, font=Fonts.TINY(), height=18,
                                     text_color=Colors.TEXT_MUTED, anchor="w")
    entrada.lbl_error.grid(row=2, column=0, sticky="w")
    # En cuanto el usuario corrige el campo, se quita el error
    entrada.bind("<KeyRelease>", lambda e: marcar_error(entrada, "") if entrada.con_error else None)
    return marco, entrada


def marcar_error(entrada, mensaje):
    # Pone (o quita, si mensaje == "") el borde rojo y el texto de error debajo del campo
    entrada.con_error = bool(mensaje)
    entrada.configure(border_color=Colors.ERROR if mensaje else Colors.BORDER)
    lbl = getattr(entrada, "lbl_error", None)
    if lbl is not None:
        lbl.configure(text=mensaje or entrada.ayuda,
                      text_color=Colors.ERROR if mensaje else Colors.TEXT_MUTED)


def campo_select(parent, texto, valores, inicial, command=None, ayuda="", tooltip_texto=None):
    # Etiqueta (+ "?" opcional) + lista desplegable + renglón de ayuda. Regresa (marco, variable, menu, lbl_ayuda)
    marco = ctk.CTkFrame(parent, fg_color="transparent")
    marco.grid_columnconfigure(0, weight=1)
    titulo = ctk.CTkFrame(marco, fg_color="transparent")
    titulo.grid(row=0, column=0, sticky="w")
    ctk.CTkLabel(titulo, text=texto, font=Fonts.SMALL(), text_color=Colors.TEXT_BODY,
                 anchor="w").pack(side="left")
    if tooltip_texto:
        help_icon(titulo, tooltip_texto).pack(side="left", padx=(6, 0))
    caja, var, menu = select_input(marco, valores, inicial, command=command)
    caja.grid(row=1, column=0, sticky="ew", pady=(6, 0))
    lbl_ayuda = ctk.CTkLabel(marco, text=ayuda, font=Fonts.TINY(), height=18,
                             text_color=Colors.TEXT_MUTED, anchor="w", justify="left", wraplength=360)
    lbl_ayuda.grid(row=2, column=0, sticky="w")
    return marco, var, menu, lbl_ayuda


def deshabilitar(widget):
    # Deja un campo en solo lectura (gris) según el nivel de acceso
    if isinstance(widget, ctk.CTkEntry):
        widget.configure(state="disabled", fg_color=Colors.INPUT_DISABLED)
    else:
        widget.configure(state="disabled")


def form_card(parent, titulo, detalle="", columnas=2):
    # Tarjeta blanca con título a la izquierda y un texto gris a la derecha
    card = ctk.CTkFrame(parent, fg_color=Colors.SURFACE, corner_radius=Sizes.CARD_RADIUS,
                        border_width=1, border_color=Colors.BORDER)
    card.grid_columnconfigure(0, weight=1)

    top = ctk.CTkFrame(card, fg_color="transparent")
    top.grid(row=0, column=0, sticky="ew", padx=20, pady=(14, 12))
    top.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(top, text=titulo, font=Fonts.BODY_BOLD(), text_color=Colors.TEXT_TITLE,
                 anchor="w").grid(row=0, column=0, sticky="w")
    card.lbl_detalle = ctk.CTkLabel(top, text=detalle, font=Fonts.TINY(),
                                    text_color=Colors.TEXT_MUTED, anchor="e")
    card.lbl_detalle.grid(row=0, column=1, sticky="e")

    ctk.CTkFrame(card, height=1, fg_color=Colors.BORDER, corner_radius=0
                 ).grid(row=1, column=0, sticky="ew", padx=1)

    cuerpo = ctk.CTkFrame(card, fg_color="transparent")
    cuerpo.grid(row=2, column=0, sticky="ew", padx=20, pady=(16, 12))
    cuerpo.grid_columnconfigure(tuple(range(columnas)), weight=1, uniform="form")
    return card, cuerpo


def page_header(parent, ruta, titulo, subtitulo):
    # Migas de pan + título + subtítulo. Los botones se ponen en la columna 1 del frame que regresa
    ctk.CTkLabel(parent, text=ruta, font=Fonts.TINY(),
                 text_color=Colors.TEXT_MUTED, anchor="w").grid(row=0, column=0, sticky="w")
    top = ctk.CTkFrame(parent, fg_color="transparent")
    top.grid(row=1, column=0, sticky="ew", pady=(6, 20))
    top.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(top, text=titulo, font=Fonts.H1(), text_color=Colors.TEXT_TITLE,
                 anchor="w").grid(row=0, column=0, sticky="w")
    ctk.CTkLabel(top, text=subtitulo, font=Fonts.BODY(), text_color=Colors.TEXT_MUTED,
                 anchor="w").grid(row=1, column=0, sticky="w")
    return top


def success_banner(parent, texto):
    banner = ctk.CTkFrame(parent, fg_color=Colors.SUCCESS_BG, border_width=1,
                          border_color=Colors.SUCCESS_BORDER, corner_radius=Sizes.BUTTON_RADIUS)
    ctk.CTkLabel(banner, text=f"✓  {texto}", font=Fonts.SMALL(), text_color=Colors.SUCCESS_TEXT
                 ).pack(pady=10)
    return banner


def tooltip(widget, texto):
    # Muestra un recuadro azul con ayuda cuando el cursor pasa sobre el widget
    tip = {"ventana": None}

    def mostrar(_e=None):
        if tip["ventana"] is not None:
            return
        ventana = tkinter.Toplevel(widget)
        ventana.wm_overrideredirect(True)
        ventana.configure(bg=Colors.PRIMARY_DARK)
        tkinter.Label(ventana, text=texto, bg=Colors.PRIMARY_DARK, fg=Colors.TEXT_ON_DARK,
                      font=(Fonts.FAMILY, 9), justify="left", wraplength=240,
                      padx=10, pady=6).pack()
        x = widget.winfo_rootx() + 18
        y = widget.winfo_rooty() + widget.winfo_height() + 4
        ventana.wm_geometry(f"+{x}+{y}")
        tip["ventana"] = ventana

    def ocultar(_e=None):
        # El widget de CTk tiene widgets internos: si el cursor sigue encima no se oculta
        x, y = widget.winfo_pointerxy()
        try:
            debajo = str(widget.winfo_containing(x, y))
        except (KeyError, tkinter.TclError):
            debajo = ""
        if debajo == str(widget) or debajo.startswith(str(widget) + "."):
            return
        if tip["ventana"] is not None:
            tip["ventana"].destroy()
            tip["ventana"] = None

    widget.bind("<Enter>", mostrar)
    widget.bind("<Leave>", ocultar)
    return widget


def help_icon(parent, texto):
    # Circulito "?" con tooltip
    icono = ctk.CTkLabel(parent, text="?", width=18, height=18, corner_radius=9,
                         fg_color=Colors.PRIMARY, text_color=Colors.TEXT_ON_DARK,
                         font=Fonts.get(10, "bold"))
    return tooltip(icono, texto)


# ----------------------------------------------------------------------
# VENTANAS EMERGENTES
# ----------------------------------------------------------------------
def dialogo(parent, titulo, mensaje="", botones=None, al_cerrar=None, construir=None, ancho=360):
    # Ventana modal con el estilo de los mockups.
    # botones: lista de (texto, comando, estilo) con estilo "primario", "contorno" o "peligro"
    #          y opcionalmente un 4.º valor True para validar antes de cerrar
    # al_cerrar: lo que se hace si cierran con la X o con Esc
    # construir: función opcional que recibe un frame para agregar más widgets (ej. una lista)
    botones = botones or [("ACEPTAR", al_cerrar, "primario")]
    raiz = parent.winfo_toplevel()
    dlg = ctk.CTkToplevel(raiz)
    dlg.title("Eclipcom")
    poner_icono(dlg)
    dlg.resizable(False, False)
    dlg.configure(fg_color=Colors.SURFACE)
    dlg.transient(raiz)

    ctk.CTkLabel(dlg, text=titulo, font=Fonts.BODY_BOLD(), text_color=Colors.TEXT_TITLE,
                 anchor="w", justify="left", width=ancho - 40, wraplength=ancho - 40
                 ).pack(fill="x", padx=20, pady=(16, 12))
    ctk.CTkFrame(dlg, height=1, fg_color=Colors.BORDER, corner_radius=0).pack(fill="x")
    if mensaje:
        ctk.CTkLabel(dlg, text=mensaje, font=Fonts.SMALL(), text_color=Colors.TEXT_MUTED,
                     anchor="w", justify="left", wraplength=ancho - 40
                     ).pack(fill="x", padx=20, pady=(14, 0))
    if construir:
        extra = ctk.CTkFrame(dlg, fg_color="transparent")
        extra.pack(fill="x", padx=20, pady=(12, 0))
        construir(extra)

    espera = {}

    def cerrar(comando=None):
        try:
            if "id" in espera:
                dlg.after_cancel(espera["id"])
            dlg.grab_release()
        except tkinter.TclError:
            pass
        dlg.destroy()
        if comando:
            comando()

    fila = ctk.CTkFrame(dlg, fg_color="transparent")
    fila.pack(padx=20, pady=18, anchor="e" if len(botones) > 1 else "center")
    estilos = {"primario": primary_button, "contorno": outline_button, "peligro": danger_button}
    def presionar(comando, validar):
        # validar=True: primero se ejecuta el comando; si regresa False el diálogo se queda abierto
        # (por ejemplo, cuando la contraseña es incorrecta)
        if validar:
            if comando and comando() is False:
                return
            cerrar()
        else:
            cerrar(comando)

    for boton in botones:
        texto, comando, estilo = boton[:3]
        validar = len(boton) > 3 and boton[3]
        crear = estilos.get(estilo, primary_button)
        opciones = {"icon": ""} if crear is not danger_button else {}
        crear(fila, texto, command=lambda c=comando, v=validar: presionar(c, v), width=110, **opciones
              ).pack(side="left", padx=(8, 0))

    dlg.protocol("WM_DELETE_WINDOW", lambda: cerrar(al_cerrar))
    dlg.bind("<Escape>", lambda e: cerrar(al_cerrar))

    # Centrar sobre la ventana principal y bloquearla mientras el diálogo esté abierto
    dlg.update_idletasks()
    x = raiz.winfo_rootx() + (raiz.winfo_width() - dlg.winfo_reqwidth()) // 2
    y = raiz.winfo_rooty() + (raiz.winfo_height() - dlg.winfo_reqheight()) // 3
    dlg.geometry(f"+{max(x, 0)}+{max(y, 0)}")
    dlg.lift()
    dlg.focus_force()

    def bloquear():
        try:
            dlg.grab_set()
        except tkinter.TclError:
            pass
    espera["id"] = dlg.after(150, bloquear)
    return dlg


def confirmar(parent, titulo, al_aceptar, mensaje=""):
    # Mockup 08: "¿Estás seguro de hacer los cambios?"  [CANCELAR] [ACEPTAR]
    return dialogo(parent, titulo, mensaje, [("CANCELAR", None, "peligro"),
                                             ("ACEPTAR", al_aceptar, "primario")])


def salir_sin_guardar(parent, al_salir):
    # Mockup 03: "¿Salir sin guardar?"
    return dialogo(parent, "¿Salir sin guardar?",
                   "Se perderán los datos que capturaste en este formulario.",
                   [("Seguir editando", None, "contorno"),
                    ("Salir sin guardar", al_salir, "primario")], ancho=420)


def guia_rapida(parent):
    # Mockup 04 V2: Guía rápida
    pasos = ("1. Elige un módulo en el menú lateral.\n"
             "2. Usa el buscador para encontrar un registro.\n"
             "3. Los campos con * son obligatorios.\n"
             "4. Pasa el cursor sobre el (?) para ver ayuda.\n\n"
             f"Tu rol: {permisos.rol_actual() or 'sin rol'}. {permisos.descripcion_rol()}")
    return dialogo(parent, "Guía rápida", pasos, [("Entendido", None, "contorno")], ancho=420)


# ----------------------------------------------------------------------
# HEADER Y SIDEBAR
# ----------------------------------------------------------------------
def header(ventana):
    datos = sesion.actual()
    nombre = datos.get("nombre") or datos.get("usuario") or "Usuario"
    rol = datos.get("rol") or ""

    header = ctk.CTkFrame(ventana, fg_color=Colors.PRIMARY_DARK, corner_radius=0,
                          height=Sizes.HEADER_HEIGHT)
    header.grid(row=0, column=0, columnspan=2, sticky="ew")
    header.grid_propagate(False)
    header.grid_columnconfigure(1, weight=1)
    header.grid_rowconfigure(0, weight=1)

    brand_logo(header).grid(row=0, column=0, padx=24, sticky="w")

    right = ctk.CTkFrame(header, fg_color="transparent")
    right.grid(row=0, column=2, padx=24, sticky="e")
    ctk.CTkLabel(right, text="GESTIÓN COMERCIAL", font=Fonts.TINY(),
                 text_color=Colors.TEXT_ON_DARK).pack(side="left", padx=(0, 20))
    ctk.CTkFrame(right, width=1, height=32, fg_color=Colors.TEXT_SIDEBAR_SECTION,
                 corner_radius=0).pack(side="left", padx=(0, 20))
    ctk.CTkLabel(right, text=iniciales(nombre), width=32, height=32, font=Fonts.get(11, "bold"),
                 text_color=Colors.AVATAR_TEXT, fg_color=Colors.AVATAR_BG,
                 corner_radius=16).pack(side="left")
    user = ctk.CTkFrame(right, fg_color="transparent")
    user.pack(side="left", padx=(10, 0))
    ctk.CTkLabel(user, text=nombre, font=Fonts.SMALL(),
                 text_color=Colors.TEXT_ON_DARK, anchor="w").pack(anchor="w")
    ctk.CTkLabel(user, text=rol, font=Fonts.TINY(),
                 text_color=Colors.TEXT_SIDEBAR_SECTION, anchor="w").pack(anchor="w")
    return header


def sidebar(parent, on_logout, mainMenu, customers, orders, pestaña, subpagina=False, users=None, settings=None):
    # subpagina=True en formularios (Nueva venta, Editar cliente...): el botón activo sí regresa a la lista
    # Solo aparecen los módulos que el rol del usuario puede ver
    side = ctk.CTkFrame(parent, fg_color=Colors.PRIMARY_DARK, corner_radius=0,
                        width=Sizes.SIDEBAR_WIDTH)
    side.grid(row=1, column=0, sticky="ns")
    side.grid_propagate(False)
    side.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(side, text="ESPACIO DE TRABAJO", font=Fonts.TINY(),
                 text_color=Colors.TEXT_SIDEBAR_SECTION, anchor="w"
                 ).grid(row=0, column=0, sticky="w", padx=20, pady=(24, 8))

    pestañas = [("menu_principal", "▦", "Menú principal", mainMenu)]
    if permisos.puede("ver_ventas"):
        pestañas.append(("ventas", "🛍", "Ventas", orders))
    if permisos.puede("ver_clientes"):
        pestañas.append(("clientes", "👥", "Clientes", customers))
    if permisos.puede("ver_usuarios") and users is not None:
        pestañas.append(("usuarios", "👤", "Usuarios", users))

    fila = 1
    for clave, icon, text, command in pestañas:
        active = clave == pestaña
        if active and not subpagina:
            command = None
        sidebar_button(side, text, command, icon, active).grid(
            row=fila, column=0, sticky="ew", padx=12, pady=2)
        fila += 1
    sidebar_button(side, "Guía rápida", lambda: guia_rapida(parent), "ⓘ").grid(
        row=fila, column=0, sticky="ew", padx=12, pady=2)
    if settings is not None:
        # Configuración (tema y color): disponible para todos los roles
        activa = pestaña == "configuracion"
        fila += 1
        sidebar_button(side, "Configuración", None if activa and not subpagina else settings, "⚙", activa).grid(
            row=fila, column=0, sticky="ew", padx=12, pady=2)

    side.grid_rowconfigure(fila + 1, weight=1)
    bottom = ctk.CTkFrame(side, fg_color="transparent")
    bottom.grid(row=fila + 2, column=0, sticky="ew", padx=12, pady=(0, 16))
    sidebar_button(bottom, "Cerrar sesión", on_logout, "⇦").pack(fill="x")
    ctk.CTkLabel(bottom, text=f"Eclipcom · {generalConfiguracion.GeneralConfig.version()}",
                 font=Fonts.TINY(), text_color=Colors.TEXT_ON_DARK, anchor="w"
                 ).pack(anchor="w", padx=8, pady=(10, 0))
    return side
