from views.estilos import (Colors, Fonts, Sizes, primary_button, search_input, select_input,
                           data_table, table_footer, ctk, sidebar, header)
from configuraciones import sesion
from configuraciones.permisos import ROLES, normalizar
from trabajadores.trabajadores import Trabajadores

POR_PAGINA = 6
TODOS_ROLES = "Todos los roles"

class Usuarios(ctk.CTkFrame):
    def __init__(self, master, on_logout, mainMenu, customers, orders, users, settings, nuevo_usuario, editar_usuario):
        super().__init__(master, fg_color=Colors.BG, corner_radius=0)
        master.title("Eclipcom - Usuarios")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.nuevo_usuario = nuevo_usuario
        self.editar_usuario = editar_usuario

        self.pagina = 1
        self.paginas = 1
        self.filtrados = []
        self.usuarios = self._cargar_usuarios()

        header(self)
        sidebar(self, on_logout, mainMenu, customers, orders, "usuarios", users=users, settings=settings)
        self._build_content()
        self._refrescar()

    def _cargar_usuarios(self):
        yo = sesion.actual().get("id")
        lista = []
        for id_trabajador, nombre, usuario, rol, especialidad, status in Trabajadores.consultar():
            lista.append({
                "id": id_trabajador,
                "clave": Trabajadores.clave(id_trabajador),
                "nombre": f"{nombre} (tú)" if id_trabajador == yo else (nombre or ""),
                "usuario": usuario or "",
                "rol": rol or "",
                "especialidad": especialidad or "—",
                "estado": str(status or "").capitalize(),
            })
        return lista

    def _build_content(self):
        pad = Sizes.CONTENT_PAD
        content = ctk.CTkFrame(self, fg_color=Colors.BG, corner_radius=0)
        content.grid(row=1, column=1, sticky="nsew", padx=pad, pady=pad)
        content.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(content, text="Inicio / Usuarios", font=Fonts.TINY(),
                     text_color=Colors.TEXT_MUTED, anchor="w").grid(row=0, column=0, sticky="w")

        top = ctk.CTkFrame(content, fg_color="transparent")
        top.grid(row=1, column=0, sticky="ew", pady=(6, 20))
        top.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(top, text="Usuarios", font=Fonts.H1(), text_color=Colors.TEXT_TITLE,
                     anchor="w").grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(top, text="Da de alta a tu equipo y define el nivel de acceso de cada quien.",
                     font=Fonts.BODY(), text_color=Colors.TEXT_MUTED, anchor="w"
                     ).grid(row=1, column=0, sticky="w")
        primary_button(top, "Nuevo usuario", command=self.nuevo_usuario, icon="+",
                       width=150).grid(row=0, column=1, rowspan=2, sticky="e")

        # Equipo de trabajo
        activos = sum(1 for u in self.usuarios if u["estado"].lower() == "activo")
        banner = ctk.CTkFrame(content, fg_color=Colors.ACCENT_LIGHT,
                              corner_radius=Sizes.CARD_RADIUS, height=58)
        banner.grid(row=2, column=0, sticky="ew")
        banner.grid_propagate(False)
        banner.grid_columnconfigure(0, weight=1)
        banner.grid_rowconfigure(0, weight=1)
        ctk.CTkLabel(banner, text="Equipo de trabajo", font=Fonts.get(12, "bold"),
                     text_color=Colors.TEXT_TITLE, anchor="w").grid(row=0, column=0, sticky="w", padx=20)
        ctk.CTkLabel(banner, text=f"{len(self.usuarios)} usuarios · {activos} activos",
                     font=Fonts.SMALL(), text_color=Colors.TEXT_TITLE
                     ).grid(row=0, column=1, sticky="e", padx=20)

        # Buscador y filtro por rol
        filtros = ctk.CTkFrame(content, fg_color="transparent")
        filtros.grid(row=3, column=0, sticky="ew", pady=(18, 18))
        filtros.grid_columnconfigure(0, weight=1)
        self.buscar = search_input(filtros, "Buscar por nombre, usuario o especialidad", self._aplicar_filtros)
        self.buscar.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        caja, self.var_rol, _ = select_input(filtros, [TODOS_ROLES] + list(ROLES), TODOS_ROLES,
                                             command=self._aplicar_filtros, border=Colors.LINK,
                                             text_color=Colors.LINK, expandir=False)
        caja.grid(row=0, column=1)

        self.tabla_holder = ctk.CTkFrame(content, fg_color="transparent")
        self.tabla_holder.grid(row=4, column=0, sticky="ew")
        self.tabla_holder.grid_columnconfigure(0, weight=1)

    def _aplicar_filtros(self, _evento=None):
        self.pagina = 1
        self._refrescar()

    def _refrescar(self):
        texto = self.buscar.get().strip().lower()
        rol = self.var_rol.get()
        self.filtrados = [
            u for u in self.usuarios
            if (rol == TODOS_ROLES or normalizar(u["rol"]) == normalizar(rol))
            and (not texto or texto in f'{u["nombre"]} {u["usuario"]} {u["especialidad"]}'.lower())
        ]
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
            ctk.CTkLabel(self.tabla_holder, text="No hay usuarios que coincidan con la búsqueda.",
                         font=Fonts.BODY(), text_color=Colors.TEXT_MUTED).pack(pady=40)
            return

        columnas = [("ID", 1), ("Nombre", 3), ("Usuario", 2), ("Rol", 2), ("Especialidad", 2),
                    ("Estado", 1), ("Acción", 1)]
        filas = [[u["clave"], u["nombre"], u["usuario"], u["rol"], u["especialidad"], u["estado"]]
                 for u in visibles]
        tabla = data_table(self.tabla_holder, columnas, filas,
                           action_text="Editar", on_action=self._abrir_edicion)
        tabla.pack(fill="x")
        table_footer(tabla, inicio, len(visibles), total, self.pagina, self.paginas, self._ir_a_pagina)

    def _abrir_edicion(self, fila):
        # fila[0] = "US-003"
        self.editar_usuario(int(fila[0].split("-")[1]))
