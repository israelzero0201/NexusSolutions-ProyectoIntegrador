import datetime

from views.estilos import Colors, Fonts, Sizes, module_card, fecha_larga, ctk, sidebar, header
from configuraciones import permisos, sesion
from ordenes.ordenes import ordenTrabajo
from cliente.cliente import Clientes
from trabajadores.trabajadores import Trabajadores

class MainMenu(ctk.CTkFrame):
    def __init__(self, master, on_logout, mainMenu, customers, orders, users, settings):
        super().__init__(master, fg_color=Colors.BG, corner_radius=0)
        master.title("Eclipcom - Menú principal")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.customers = customers
        self.orders = orders
        self.users = users
        header(self)
        sidebar(self, on_logout, mainMenu, customers, orders, "menu_principal", users=users, settings=settings)
        self._build_content()

    def _tarjetas(self):
        # Solo se muestran los módulos que permite el rol
        tarjetas = []
        if permisos.puede("ver_ventas"):
            tarjetas.append(("🛍", "Ventas",
                             "Registra nuevas ventas, consulta sus detalles y mantén cada proyecto al día.",
                             f"{ordenTrabajo.cantidad_ventas()} ventas registradas", "Ir a ventas", self.orders))
        if permisos.puede("ver_clientes"):
            tarjetas.append(("👥", "Clientes",
                             "Centraliza la información de tus clientes y actualiza sus datos de contacto.",
                             f"{Clientes.cantidad_clientes()} clientes registrados", "Ir a clientes", self.customers))
        if permisos.puede("ver_usuarios"):
            tarjetas.append(("👤", "Usuarios",
                             "Da de alta a tu equipo y define qué puede hacer cada quien en Eclipcom.",
                             f"{len(Trabajadores.consultar())} usuarios registrados", "Ir a usuarios", self.users))
        return tarjetas
  
    def _build_content(self):
        pad = Sizes.CONTENT_PAD
        content = ctk.CTkFrame(self, fg_color=Colors.BG, corner_radius=0)
        content.grid(row=1, column=1, sticky="nsew", padx=pad, pady=pad)

        tarjetas = self._tarjetas()
        columnas = max(2, len(tarjetas))
        content.grid_columnconfigure(tuple(range(columnas)), weight=1, uniform="cards")

        nombre = (sesion.actual().get("nombre") or "").split(" ")[0]
        ctk.CTkLabel(content, text="Inicio / Menú principal", font=Fonts.TINY(),
                     text_color=Colors.TEXT_MUTED, anchor="w").grid(row=0, column=0, columnspan=columnas, sticky="w")
        ctk.CTkLabel(content, text="Menú principal", font=Fonts.H1(),
                     text_color=Colors.TEXT_TITLE, anchor="w").grid(row=1, column=0, columnspan=columnas, sticky="w", pady=(6, 0))
        ctk.CTkLabel(content, text=f"Hola{', ' + nombre if nombre else ''}. Elige un módulo para comenzar a trabajar.",
                     font=Fonts.BODY(), text_color=Colors.TEXT_MUTED, anchor="w"
                     ).grid(row=2, column=0, columnspan=columnas, sticky="w", pady=(0, 20))

        for i, (icono, titulo, descripcion, contador, boton, comando) in enumerate(tarjetas):
            izquierda = 0 if i == 0 else 10
            derecha = 0 if i == len(tarjetas) - 1 else 10
            module_card(content, icono, titulo, descripcion, contador, boton, comando,
                        wrap=380 if columnas == 2 else 260
                        ).grid(row=3, column=i, sticky="nsew", padx=(izquierda, derecha))

        # Mockup 02 V2: fecha de actualización debajo de las tarjetas + nivel de acceso
        ctk.CTkLabel(content, text=f"Información actualizada al {fecha_larga(datetime.date.today())}.",
                     font=Fonts.TINY(), text_color=Colors.TEXT_MUTED, anchor="w"
                     ).grid(row=4, column=0, columnspan=columnas, sticky="w", pady=(16, 0))
        ctk.CTkLabel(content, text=f"Tu rol: {permisos.rol_actual()} · {permisos.descripcion_rol()}",
                     font=Fonts.TINY(), text_color=Colors.TEXT_MUTED, anchor="w", justify="left", wraplength=700
                     ).grid(row=5, column=0, columnspan=columnas, sticky="w", pady=(4, 0))
