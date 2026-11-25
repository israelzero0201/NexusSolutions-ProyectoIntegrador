import datetime

from views.estilos import (Colors, Fonts, Sizes, MESES, primary_button, search_input, select_input,
                           data_table, table_footer, success_banner, fecha_corta, dinero,
                           sidebar, ctk, header)
from ordenes.ordenes import ordenTrabajo
from cliente.cliente import Clientes

POR_PAGINA = 6
TODOS_ESTADOS = "Todos los estados"
TODOS_PERIODOS = "Todos los meses"

class Ventas(ctk.CTkFrame):
    def __init__(self, master, on_logout, mainMenu, customers, orders, users, settings, nueva_venta, ver_detalle, mensaje=None):
        super().__init__(master, fg_color=Colors.BG, corner_radius=0)
        self.nueva_venta = nueva_venta
        self.ver_detalle = ver_detalle
        self.mensaje = mensaje      # Mockup 03: "Venta V-2026-007 guardada correctamente."
        master.title("Eclipcom - Ventas")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.pagina = 1
        self.paginas = 1
        self.filtradas = []
        self.ventas = self._cargar_ventas()
        self.periodos = self._calcular_periodos()

        self.customers = customers
        self.orders = orders
        header(self)
        sidebar(self, on_logout, mainMenu, customers, orders, "ventas", users=users, settings=settings)
        self._build_content()
        self._refrescar()

    @staticmethod
    def _a_fecha(valor):
        if isinstance(valor, datetime.datetime):
            return valor.date()
        if isinstance(valor, datetime.date):
            return valor
        try:
            return datetime.date.fromisoformat(str(valor))
        except (TypeError, ValueError):
            return None

    def _cargar_ventas(self):
        # En la tabla se muestra el nombre de la persona de contacto (si no tiene, la empresa)
        clientes = {c[0]: (c[2] or c[1] or "", c[1] or "") for c in Clientes.consultar()}
        lista = []
        for venta in ordenTrabajo.consultar():
            fecha = self._a_fecha(venta["fecha"])
            nombre, empresa = clientes.get(venta["id_cliente"], (f"Cliente #{venta['id_cliente']}", ""))
            lista.append({
                "id": venta["id"],
                "folio": ordenTrabajo.folio(venta["id"], fecha),
                "fecha": fecha,
                "fecha_txt": fecha_corta(fecha),
                "cliente": nombre,
                "empresa": empresa,
                "proyecto": venta["proyecto"] or str(venta["tipo"]).capitalize(),
                "total": float(venta["monto"] or 0),
                "estado": str(venta["status"]).replace("_", " ").capitalize(),
                "tecnico": venta["tecnicos"] or "Sin asignar",
            })
        lista.sort(key=lambda v: v["id"], reverse=True)
        return lista

    def _calcular_periodos(self):
        """{'Todos los meses': None, 'Noviembre 2026': (2026, 11), ...}"""
        meses = sorted({(v["fecha"].year, v["fecha"].month)
                        for v in self.ventas if v["fecha"]}, reverse=True)
        periodos = {TODOS_PERIODOS: None}
        for anio, mes in meses:
            periodos[f"{MESES[mes - 1].capitalize()} {anio}"] = (anio, mes)
        return periodos

    def _periodo_inicial(self):
        hoy = datetime.date.today()
        etiqueta = f"{MESES[hoy.month - 1].capitalize()} {hoy.year}"
        return etiqueta if etiqueta in self.periodos else TODOS_PERIODOS

    def _build_content(self):
        pad = Sizes.CONTENT_PAD
        content = ctk.CTkFrame(self, fg_color=Colors.BG, corner_radius=0)
        content.grid(row=1, column=1, sticky="nsew", padx=pad, pady=pad)
        content.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(content, text="Inicio / Ventas", font=Fonts.TINY(),
                    text_color=Colors.TEXT_MUTED, anchor="w").grid(row=0, column=0, sticky="w")

        top = ctk.CTkFrame(content, fg_color="transparent")
        top.grid(row=1, column=0, sticky="ew", pady=(6, 20))
        top.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(top, text="Ventas", font=Fonts.H1(), text_color=Colors.TEXT_TITLE,
                    anchor="w").grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(top, text="Consulta tus ventas y accede a la información de cada proyecto.",
                    font=Fonts.BODY(), text_color=Colors.TEXT_MUTED, anchor="w"
                    ).grid(row=1, column=0, sticky="w")
        primary_button(top, "Nueva venta", command=self.nueva_venta, icon="+",
                    width=140).grid(row=0, column=1, rowspan=2, sticky="e")

        # Resumen del periodo
        banner = ctk.CTkFrame(content, fg_color=Colors.ACCENT_LIGHT,
                            corner_radius=Sizes.CARD_RADIUS, height=58)
        banner.grid(row=2, column=0, sticky="ew")
        banner.grid_propagate(False)
        banner.grid_columnconfigure((0, 1, 2), weight=1, uniform="banner")
        banner.grid_rowconfigure(0, weight=1)
        self.lbl_periodo = ctk.CTkLabel(banner, text="", font=Fonts.get(12, "bold"),
                                        text_color=Colors.TEXT_TITLE, anchor="w")
        self.lbl_periodo.grid(row=0, column=0, sticky="w", padx=20)
        self.lbl_conteo = ctk.CTkLabel(banner, text="", font=Fonts.SMALL(),
                                    text_color=Colors.TEXT_TITLE)
        self.lbl_conteo.grid(row=0, column=1)
        self.lbl_total = ctk.CTkLabel(banner, text="", font=Fonts.get(18, "bold"),
                                    text_color=Colors.TEXT_TITLE, anchor="e")
        self.lbl_total.grid(row=0, column=2, sticky="e", padx=20)

        # Aviso verde después de guardar una venta (Mockup 03 · Venta guardada)
        if self.mensaje:
            success_banner(content, self.mensaje).grid(row=3, column=0, sticky="ew", pady=(18, 0))

        # Filtros
        filtros = ctk.CTkFrame(content, fg_color="transparent")
        filtros.grid(row=4, column=0, sticky="ew", pady=(18, 18))
        filtros.grid_columnconfigure(0, weight=1)

        self.buscar = search_input(filtros, "Buscar por folio, cliente, proyecto o técnico", self._aplicar_filtros)
        self.buscar.grid(row=0, column=0, sticky="ew", padx=(0, 12))

        estados = [TODOS_ESTADOS] + sorted({v["estado"] for v in self.ventas})
        caja_estado, self.var_estado, _ = select_input(
            filtros, estados, TODOS_ESTADOS, command=self._aplicar_filtros,
            border=Colors.LINK, text_color=Colors.LINK, expandir=False)
        caja_estado.grid(row=0, column=1, padx=(0, 12))
        caja_mes, self.var_mes, _ = select_input(
            filtros, list(self.periodos), self._periodo_inicial(), command=self._aplicar_filtros,
            border=Colors.LINK, text_color=Colors.LINK, expandir=False)
        caja_mes.grid(row=0, column=2)

        # Tabla (se vuelve a dibujar al filtrar o cambiar de página)
        self.tabla_holder = ctk.CTkFrame(content, fg_color="transparent")
        self.tabla_holder.grid(row=5, column=0, sticky="ew")
        self.tabla_holder.grid_columnconfigure(0, weight=1)

    def _aplicar_filtros(self, _evento=None):
        self.pagina = 1
        self._refrescar()

    def _refrescar(self):
        texto = self.buscar.get().strip().lower()
        estado = self.var_estado.get()
        periodo = self.periodos.get(self.var_mes.get())

        def en_periodo(v):
            return periodo is None or (
                v["fecha"] is not None and (v["fecha"].year, v["fecha"].month) == periodo)

        del_periodo = [v for v in self.ventas if en_periodo(v)]
        self._actualizar_resumen(periodo, del_periodo)

        self.filtradas = [
            v for v in del_periodo
            if (estado == TODOS_ESTADOS or v["estado"] == estado)
            and (not texto or texto in f'{v["folio"]} {v["cliente"]} {v["empresa"]} {v["proyecto"]} {v["tecnico"]}'.lower())
        ]
        self._dibujar_tabla()

    def _actualizar_resumen(self, periodo, del_periodo):
        if periodo:
            etiqueta = f"{MESES[periodo[1] - 1].capitalize()} de {periodo[0]}"
        else:
            etiqueta = "Todos los periodos"
        total = sum(v["total"] for v in del_periodo)
        self.lbl_periodo.configure(text=etiqueta)
        self.lbl_conteo.configure(text=f"{len(del_periodo)} ventas registradas")
        self.lbl_total.configure(text=f"{dinero(total)} MXN")

    def _ir_a_pagina(self, numero):
        if 1 <= numero <= self.paginas:
            self.pagina = numero
            self._dibujar_tabla()

    def _dibujar_tabla(self):
        for widget in self.tabla_holder.winfo_children():
            widget.destroy()

        total = len(self.filtradas)
        self.paginas = max(1, -(-total // POR_PAGINA))
        self.pagina = min(self.pagina, self.paginas)
        inicio = (self.pagina - 1) * POR_PAGINA
        visibles = self.filtradas[inicio:inicio + POR_PAGINA]

        if not visibles:
            ctk.CTkLabel(self.tabla_holder, text="No hay ventas que coincidan con los filtros.",
                        font=Fonts.BODY(), text_color=Colors.TEXT_MUTED).pack(pady=40)
            return

        # Columna Técnico: todos los roles pueden ver a quién se asignó cada venta
        columnas = [("Folio / Fecha", 2), ("Cliente", 2), ("Proyecto", 3), ("Técnico", 2),
                    ("Total (MXN)", 2), ("Estado", 2), ("Acción", 2)]
        filas = [[f'{v["folio"]}\n{v["fecha_txt"]}', v["cliente"], v["proyecto"], v["tecnico"],
                dinero(v["total"]), v["estado"]] for v in visibles]
        tabla = data_table(self.tabla_holder, columnas, filas,
                        action_text="Ver detalle", on_action=self._abrir_detalle)
        tabla.pack(fill="x")
        table_footer(tabla, inicio, len(visibles), total, self.pagina, self.paginas, self._ir_a_pagina)

    def _abrir_detalle(self, fila):
        folio = fila[0].split("\n")[0]
        venta = next((v for v in self.ventas if v["folio"] == folio), None)
        if venta:
            self.ver_detalle(venta)
