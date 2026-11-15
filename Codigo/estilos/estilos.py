import customtkinter as ctk

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

class Fonts:
    FAMILY = "Inter"

    @staticmethod
    def get(size=12, weight="normal"):
        # Se crea bajo demanda: CTkFont necesita que exista la ventana raíz
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
    # Obtiene el tamaño de la pantalla
    _tmp = ctk.CTk()
    _tmp.withdraw() 
    WINDOW = (_tmp.winfo_screenwidth(), _tmp.winfo_screenheight())
    _tmp.destroy()
    del _tmp

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


def apply_theme():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")


# ----------------------------------------------------------------------
# COMPONENTES ESTILIZADOS
# ----------------------------------------------------------------------
def primary_button(parent, text, command=None, icon="→", **kw):
    return ctk.CTkButton(
        parent, text=f"{icon}  {text}" if icon else text, command=command,
        fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_HOVER,
        text_color=Colors.TEXT_ON_DARK, font=Fonts.BUTTON(),
        corner_radius=Sizes.BUTTON_RADIUS, height=Sizes.BUTTON_HEIGHT,
        width=kw.pop("width", 130), **kw,
    )


def link_button(parent, text, command=None, **kw):
    return ctk.CTkButton(
        parent, text=text, command=command, fg_color="transparent",
        hover_color=Colors.BG, text_color=Colors.LINK, font=Fonts.SMALL(),
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


def module_card(parent, icon, title, description, counter_text, button_text, command):
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
                 anchor="w", justify="left", wraplength=380
                 ).grid(row=2, column=0, sticky="w", padx=20)
    primary_button(card, button_text, command=command).grid(
        row=3, column=0, sticky="w", padx=20, pady=(16, 20))
    return card


def data_table(parent, columns, rows, action_text="Ver detalle", on_action=None):
    """columns: lista de (titulo, peso). rows: lista de listas (sin la columna Acción)."""
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
    entry.bind("<FocusIn>", lambda e: entry.configure(border_color=Colors.PRIMARY))
    entry.bind("<FocusOut>", lambda e: entry.configure(border_color=Colors.BORDER))
    return entry
 
 
def checkbox(parent, text, **kw):
    return ctk.CTkCheckBox(
        parent, text=text, font=Fonts.SMALL(), text_color=Colors.TEXT_BODY,
        fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_HOVER,
        border_color=Colors.BORDER, border_width=1,
        checkbox_width=16, checkbox_height=16, corner_radius=3, **kw,
    )