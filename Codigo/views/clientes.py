from views.estilos import (Colors, Fonts, Sizes, primary_button, outline_button, search_input,
                           data_table, table_footer, telefono_txt, ctk, sidebar, header)
from configuraciones.permisos import puede
from cliente.cliente import Clientes

POR_PAGINA = 6

class Customers(ctk.CTkFrame):
    def __init__(self, master, on_logout, mainMenu, customers, orders, users, settings, nuevo_cliente, editar_cliente):
        super().__init__(master, fg_color=Colors.BG, corner_radius=0)
        master.title("Eclipcom - Clientes")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.customers = customers
        self.orders = orders
        self.nuevo_cliente = nuevo_cliente
        self.editar_cliente = editar_cliente

        self.pagina = 1
        self.paginas = 1
        self.por_nombre = False     # botón "Ordenar por nombre"
        self.filtrados = []
        self.clientes = self._cargar_clientes()

        header(self)
        sidebar(self, on_logout, mainMenu, customers, orders, "clientes", users=users, settings=settings)
        self._build_content()
        self._refrescar()

    def _cargar_clientes(self):
        lista = []
        for id_cliente, razon, contacto, telefono, email in Clientes.consultar():
            lista.append({
                "id": id_cliente,
                "clave": Clientes.clave(id_cliente),
                "nombre": contacto or razon or "",
                "empresa": razon or "",
                "email": email or "",
                "telefono": telefono_txt(telefono),
            })
        return lista

    def _build_content(self):
        pad = Sizes.CONTENT_PAD
        content = ctk.CTkFrame(self, fg_color=Colors.BG, corner_radius=0)
        content.grid(row=1, column=1, sticky="nsew", padx=pad, pady=pad)
        content.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(content, text="Inicio / Clientes", font=Fonts.TINY(),
                     text_color=Colors.TEXT_MUTED, anchor="w").grid(row=0, column=0, sticky="w")

        top = ctk.CTkFrame(content, fg_color="transparent")
        top.grid(row=1, column=0, sticky="ew", pady=(6, 20))
        top.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(top, text="Clientes", font=Fonts.H1(), text_color=Colors.TEXT_TITLE,
                     anchor="w").grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(top, text="Consulta y actualiza la información de tus clientes.",
                     font=Fonts.BODY(), text_color=Colors.TEXT_MUTED, anchor="w"
                     ).grid(row=1, column=0, sticky="w")
        if puede("editar_clientes"):
            primary_button(top, "Nuevo cliente", command=self.nuevo_cliente, icon="+",
                           width=140).grid(row=0, column=1, rowspan=2, sticky="e")

        # Directorio de clientes
        banner = ctk.CTkFrame(content, fg_color=Colors.ACCENT_LIGHT,
                              corner_radius=Sizes.CARD_RADIUS, height=58)
        banner.grid(row=2, column=0, sticky="ew")
        banner.grid_propagate(False)
        banner.grid_columnconfigure(0, weight=1)
        banner.grid_rowconfigure(0, weight=1)
        ctk.CTkLabel(banner, text="Directorio de clientes", font=Fonts.get(12, "bold"),
                     text_color=Colors.TEXT_TITLE, anchor="w").grid(row=0, column=0, sticky="w", padx=20)
        ctk.CTkLabel(banner, text=f"{len(self.clientes)} clientes · Información centralizada",
                     font=Fonts.SMALL(), text_color=Colors.TEXT_TITLE
                     ).grid(row=0, column=1, sticky="e", padx=20)

        # Buscador y orden
        filtros = ctk.CTkFrame(content, fg_color="transparent")
        filtros.grid(row=3, column=0, sticky="ew", pady=(18, 18))
        filtros.grid_columnconfigure(0, weight=1)

        self.buscar = search_input(filtros, "Buscar por nombre, empresa o correo electrónico",
                                   self._aplicar_filtros)
        self.buscar.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        self.btn_orden = outline_button(filtros, "Ordenar por nombre", command=self._cambiar_orden,
                                        icon="⇅", width=170, height=Sizes.INPUT_HEIGHT)
        self.btn_orden.grid(row=0, column=1)

        # Tabla (se vuelve a dibujar al buscar, ordenar o cambiar de página)
        self.tabla_holder = ctk.CTkFrame(content, fg_color="transparent")
        self.tabla_holder.grid(row=4, column=0, sticky="ew")
        self.tabla_holder.grid_columnconfigure(0, weight=1)

    def _cambiar_orden(self):
        self.por_nombre = not self.por_nombre
        self.btn_orden.configure(text="⇅  Ordenar por ID" if self.por_nombre else "⇅  Ordenar por nombre")
        self._refrescar()

    def _aplicar_filtros(self, _evento=None):
        self.pagina = 1
        self._refrescar()

    def _refrescar(self):
        texto = self.buscar.get().strip().lower()
        self.filtrados = [
            c for c in self.clientes
            if not texto or texto in f'{c["nombre"]} {c["empresa"]} {c["email"]}'.lower()
        ]
        if self.por_nombre:
            self.filtrados.sort(key=lambda c: c["nombre"].lower())
        else:
            self.filtrados.sort(key=lambda c: c["id"])
        self._dibujar_tabla()

    def _ir_a_pagina(self, numero):
        if 1 <= numero <= self.paginas:
            self.pagina = numero
            self._dibujar_tabla()

    def _dibujar_tabla(self):
        for widget in self.tabla_holder.winfo_children():
            widget.destroy()

        total = len(self.filtrados)
        self.paginas = max(1, -(-total // POR_PAGINA))
        self.pagina = min(self.pagina, self.paginas)
        inicio = (self.pagina - 1) * POR_PAGINA
        visibles = self.filtrados[inicio:inicio + POR_PAGINA]

        if not visibles:
            texto = ("No hay clientes que coincidan con la búsqueda." if self.clientes
                     else "Aún no hay clientes registrados. Usa «Nuevo cliente» para agregar el primero.")
            ctk.CTkLabel(self.tabla_holder, text=texto, font=Fonts.BODY(),
                         text_color=Colors.TEXT_MUTED).pack(pady=40)
            return

        columnas = [("ID", 1), ("Cliente", 2), ("Empresa", 2), ("Correo electrónico", 3),
                    ("Teléfono", 2), ("Acción", 1)]
        filas = [[c["clave"], c["nombre"], c["empresa"] or "—", c["email"], c["telefono"]]
                 for c in visibles]
        # El técnico solo consulta: "Ver" en lugar de "Editar"
        tabla = data_table(self.tabla_holder, columnas, filas,
                           action_text="Editar" if puede("editar_clientes") else "Ver",
                           on_action=self._abrir_edicion)
        tabla.pack(fill="x")
        table_footer(tabla, inicio, len(visibles), total, self.pagina, self.paginas, self._ir_a_pagina)

    def _abrir_edicion(self, fila):
        # fila[0] = "CL-001"
        self.editar_cliente(int(fila[0].split("-")[1]))
