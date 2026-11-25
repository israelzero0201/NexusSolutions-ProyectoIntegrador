import datetime

from views.estilos import (enfocar_despues, Colors, Fonts, Sizes, primary_button, outline_button, link_button, text_input,
                           select_input, campo_formulario, campo_select, marcar_error, deshabilitar, form_card,
                           page_header, help_icon, confirmar, salir_sin_guardar, dialogo, dinero,
                           telefono_txt, iniciales, text_area, texto_de, danger_button, ctk, sidebar, header)
from configuraciones import sesion
from configuraciones.permisos import puede, rol_actual, campos_parciales_txt, CAMPOS_VENTA_PARCIAL, ESTADOS_SOLO_GESTION
from ordenes.ordenes import ordenTrabajo
from cliente.cliente import Clientes
from trabajadores.trabajadores import Trabajadores

IVA = 0.16
CON_IVA = "Con IVA"
SIN_IVA = "Sin IVA"
SIN_CLIENTES = "Sin clientes registrados"
SIN_TECNICO = "Sin asignar (después)"
TIPOS_PAGO = ("Anticipo", "Abono", "Liquidación")
SIN_NOTAS = "Aún no hay notas en la bitácora."
# Valor en la BD -> texto que ve el usuario
TIPOS = {"instalacion": "Instalación", "mantenimiento": "Mantenimiento"}
ESTADOS = {"pendiente": "Pendiente", "asignada": "Asignada", "en_proceso": "En proceso",
           "concluida": "Concluida", "cancelada": "Cancelada"}


def clave_de(diccionario, texto):
    # Busca la clave a partir del texto: clave_de(ESTADOS, "En proceso") -> "en_proceso"
    return next((clave for clave, valor in diccionario.items() if valor == texto), texto)


def hora_txt(hora):
    # MySQL regresa TIME como timedelta: 9 h 30 min -> "09:30"
    if hora is None or hora == "":
        return ""
    if isinstance(hora, datetime.timedelta):
        minutos = int(hora.total_seconds()) // 60
        return f"{minutos // 60:02d}:{minutos % 60:02d}"
    if isinstance(hora, datetime.time):
        return hora.strftime("%H:%M")
    return str(hora)[:5]


def leer_importe(texto):
    # "$1,500.50" -> 1500.5 ; "" -> 0.0 ; texto inválido -> None
    texto = str(texto).replace("$", "").replace(",", "").strip()
    if not texto:
        return 0.0
    try:
        return float(texto)
    except ValueError:
        return None


def estados_permitidos(actual):
    # Estados que el usuario puede elegir desde el estado actual (los técnicos no pueden cancelar)
    estados = ordenTrabajo.statusPermitidos(actual)
    if not puede("editar_ventas"):
        estados = [s for s in estados if s == actual or s not in ESTADOS_SOLO_GESTION]
    return estados


class FormularioVenta(ctk.CTkFrame):
    # Sirve para Mockup 04 (Nueva venta) y Mockup 05 (Detalle de venta).
    # venta = None para una venta nueva, o el diccionario de ordenTrabajo.consultar_id()
    def __init__(self, master, on_logout, mainMenu, customers, orders, users, settings, guardar, venta=None,
                 cambiar_estado=None, asignar_tecnico=None, quitar_tecnico=None, registrar_pago=None,
                 quitar_pago=None, agregar_nota=None, borrar_bitacora=None, imprimir=None):
        super().__init__(master, fg_color=Colors.BG, corner_radius=0)
        self.guardar = guardar
        self.cambiar_estado = cambiar_estado
        self.asignar_tecnico = asignar_tecnico
        self.quitar_tecnico = quitar_tecnico
        self.registrar_pago = registrar_pago
        self.quitar_pago = quitar_pago
        self.agregar_nota = agregar_nota
        self.borrar_bitacora = borrar_bitacora
        self.imprimir = imprimir
        self.venta = venta
        self.orders = orders
        self.nueva = venta is None
        # Edición completa: venta nueva o rol con "editar_ventas". Si no, solo CAMPOS_VENTA_PARCIAL
        self.completo = self.nueva or puede("editar_ventas")
        self.editando_concepto = self.nueva     # en el detalle el concepto se edita con "Editar concepto"
        self.monto_original = 0.0
        self.subtotal_original = 0.0
        self.con_iva_original = True
        self.clientes = self._cargar_clientes()
        self.tecnicos_libres = {}
        self.anticipo = self.fecha_anticipo = None     # solo en venta nueva (anticipo inicial)
        if self.nueva:
            self.folio = ordenTrabajo.folio(ordenTrabajo.siguiente_id())
            self.tecnicos = []
            self.cuenta = None
        else:
            self.folio = ordenTrabajo.folio(venta["id"], venta["fecha"])
            self.tecnicos = ordenTrabajo.tecnicosDeOrden(venta["id"])
            self.cuenta = ordenTrabajo.estadoDeCuenta(venta)   # precio inicial, pagos y saldo

        master.title("Eclipcom - Nueva venta" if self.nueva else "Eclipcom - Detalle de venta")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        header(self)
        # Si hay cambios sin guardar, el menú lateral también pregunta antes de salir
        sidebar(self, lambda: self._salir(on_logout), lambda: self._salir(mainMenu),
                lambda: self._salir(customers), lambda: self._salir(orders), "ventas", subpagina=True,
                users=lambda: self._salir(users), settings=lambda: self._salir(settings))
        self._build_content()
        self._llenar()
        self._aplicar_permisos()
        self._recalcular()
        self.inicial = self._valores()

    def _cargar_clientes(self):
        # {"Mariana López": (1, "Estudio Aurora", "Mariana López", "6185252789", "mariana@aurora.mx"), ...}
        clientes = {}
        for fila in Clientes.consultar():
            etiqueta = fila[2] or fila[1] or Clientes.clave(fila[0])
            if etiqueta in clientes:        # dos clientes con el mismo nombre
                etiqueta = f"{etiqueta} ({Clientes.clave(fila[0])})"
            clientes[etiqueta] = fila
        return clientes

    def _puede_editar(self, campo):
        if campo == "anticipo":
            # El anticipo inicial (venta nueva) y los pagos los registra administración
            return puede("registrar_pagos")
        return self.completo or campo in CAMPOS_VENTA_PARCIAL

    # -------------------------------------------------------------------------------------------------------------------------
    #                         Construcción de la pantalla
    # -------------------------------------------------------------------------------------------------------------------------
    def _build_content(self):
        pad = Sizes.CONTENT_PAD
        content = ctk.CTkScrollableFrame(self, fg_color=Colors.BG, corner_radius=0)
        content.grid(row=1, column=1, sticky="nsew")
        content.grid_columnconfigure(0, weight=1)
        cuerpo = ctk.CTkFrame(content, fg_color="transparent")
        cuerpo.grid(row=0, column=0, sticky="nsew", padx=pad, pady=pad)
        cuerpo.grid_columnconfigure(0, weight=1)

        if self.nueva:
            top = page_header(cuerpo, "Inicio / Ventas / Nueva venta", "Nueva venta",
                              "Registra una venta y vincúlala con un cliente y su proyecto. "
                              "Los campos con * son obligatorios.")
        else:
            if self.completo:
                subtitulo = f"Editando {self.folio} · Los cambios se aplicarán al guardar."
            else:
                subtitulo = f"Editando {self.folio} · Con tu rol puedes actualizar {campos_parciales_txt()}."
            top = page_header(cuerpo, f"Inicio / Ventas / {self.folio}", "Detalle de venta", subtitulo)
            if self._puede_editar("estado"):
                primary_button(top, "Cambiar estado", command=self._dialogo_estado, icon="",
                               width=140).grid(row=0, column=1, rowspan=2, sticky="e", padx=(0, 10))
            if puede("imprimir_ventas"):
                outline_button(top, "Imprimir", command=self._imprimir, icon="🖨",
                               width=120).grid(row=0, column=2, rowspan=2, sticky="e", padx=(0, 10))
        outline_button(top, "Volver a ventas", command=lambda: self._salir(self.orders),
                       icon="←", width=160).grid(row=0, column=3, rowspan=2, sticky="e")

        self._build_datos(cuerpo)          # fila 2
        self._build_conceptos(cuerpo)      # fila 3
        self._build_pagos(cuerpo)          # fila 4
        self._build_tecnicos(cuerpo)       # fila 5
        self._build_bitacora(cuerpo)       # fila 6

        # Pie: * Campos obligatorios   [Cancelar] [Guardar]
        pie = ctk.CTkFrame(cuerpo, fg_color="transparent")
        pie.grid(row=7, column=0, sticky="ew", pady=(16, 0))
        pie.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(pie, text="* Campos obligatorios", font=Fonts.TINY(),
                     text_color=Colors.TEXT_MUTED).grid(row=0, column=0, sticky="w")
        outline_button(pie, "Cancelar", command=lambda: self._salir(self.orders),
                       width=110).grid(row=0, column=1, padx=(0, 10))
        primary_button(pie, "Guardar venta" if self.nueva else "Guardar cambios",
                       command=self._guardar, icon="", width=150).grid(row=0, column=2)

    def _build_datos(self, cuerpo):
        if self.nueva:
            detalle = f"Folio automático: {self.folio}"
        else:
            detalle = f"Registrada por {self.venta['levantada_por'] or '(sin registro)'}"
        card, datos = form_card(cuerpo, "Datos de la venta", detalle, columnas=3)
        card.grid(row=2, column=0, sticky="ew")

        # Cliente (lista desplegable)
        marco = ctk.CTkFrame(datos, fg_color="transparent")
        marco.grid(row=0, column=0, sticky="new", padx=(0, 10))
        marco.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(marco, text="Cliente *", font=Fonts.SMALL(), text_color=Colors.TEXT_BODY,
                     anchor="w").grid(row=0, column=0, sticky="w")
        opciones = list(self.clientes) or [SIN_CLIENTES]
        caja, self.var_cliente, self.menu_cliente = select_input(marco, opciones, opciones[0],
                                                                 command=self._mostrar_cliente)
        caja.grid(row=1, column=0, sticky="ew", pady=(6, 0))

        marco, self.proyecto = campo_formulario(datos, "Nombre del proyecto *",
                                                "Ej. Instalación de cámaras en oficina")
        marco.grid(row=0, column=1, sticky="new", padx=10)
        marco, self.fecha = campo_formulario(datos, "Fecha de venta *", "dd/mm/aaaa",
                                             ayuda="Fecha en que se acordó la venta.")
        marco.grid(row=0, column=2, sticky="new", padx=(10, 0))

        # Debajo del cliente: CL-001 · Estudio Aurora · mariana@aurora.mx · 618 525 2789
        self.lbl_cliente = ctk.CTkLabel(datos, text="", font=Fonts.TINY(), height=18,
                                        text_color=Colors.TEXT_MUTED, anchor="w")
        self.lbl_cliente.grid(row=1, column=0, columnspan=2, sticky="w")

        marco, self.var_tipo, self.menu_tipo, _ = campo_select(datos, "Tipo de servicio", list(TIPOS.values()),
                                                               TIPOS["instalacion"])
        marco.grid(row=2, column=0, sticky="new", padx=(0, 10), pady=(4, 0))
        marco, self.hora = campo_formulario(datos, "Hora de inicio", "hh:mm", ayuda="Formato 24 h. Opcional.")
        marco.grid(row=2, column=1, sticky="new", padx=10, pady=(4, 0))
        marco, self.levantada = campo_formulario(datos, "Levantada por *", "Nombre de quien llena la venta",
                                                 ayuda="Quién llenó este formulario.")
        marco.grid(row=2, column=2, sticky="new", padx=(10, 0), pady=(4, 0))

        # Dirección del sitio en campos separados
        ctk.CTkLabel(datos, text="Dirección del sitio", font=Fonts.BODY_BOLD(), text_color=Colors.TEXT_TITLE,
                     anchor="w").grid(row=3, column=0, columnspan=3, sticky="w", pady=(8, 6))
        marco, self.calle = campo_formulario(datos, "Calle", "Ej. Av. 20 de Noviembre")
        marco.grid(row=4, column=0, sticky="new", padx=(0, 10))
        marco, self.numero = campo_formulario(datos, "Número", "Ej. 1205 o 12-B")
        marco.grid(row=4, column=1, sticky="new", padx=10)
        marco, self.colonia = campo_formulario(datos, "Colonia", "Ej. Centro")
        marco.grid(row=4, column=2, sticky="new", padx=(10, 0))

        # Técnico desde el registro (opcional): solo quien puede asignar técnicos
        self.var_tecnico = None
        if self.nueva and puede("asignar_tecnicos"):
            for id_tecnico, nombre, especialidad in Trabajadores.consultar_tecnicos():
                etiqueta = f"{nombre} · {especialidad}" if especialidad else nombre
                if etiqueta in self.tecnicos_libres:
                    etiqueta = f"{etiqueta} ({Trabajadores.clave(id_tecnico)})"
                self.tecnicos_libres[etiqueta] = id_tecnico
            marco, self.var_tecnico, _, _ = campo_select(
                datos, "Técnico asignado", [SIN_TECNICO] + list(self.tecnicos_libres), SIN_TECNICO,
                ayuda="Opcional. También puedes asignarlo después desde el detalle.")
            marco.grid(row=5, column=0, sticky="new", padx=(0, 10), pady=(4, 0))

    def _build_conceptos(self, cuerpo):
        titulo = "Conceptos de venta" if self.nueva else "Conceptos y estado"
        card, conceptos = form_card(cuerpo, titulo, "Moneda: MXN", columnas=1)
        card.grid(row=3, column=0, sticky="ew", pady=(16, 0))

        # Tabla de un concepto: Concepto | Cantidad | Precio unitario | Importe
        marco_tabla = ctk.CTkFrame(conceptos, fg_color=Colors.SURFACE, corner_radius=0,
                                   border_width=1, border_color=Colors.BORDER)
        marco_tabla.grid(row=0, column=0, sticky="ew")
        tabla = ctk.CTkFrame(marco_tabla, fg_color="transparent", corner_radius=0)
        tabla.pack(fill="x", padx=1, pady=1)
        for i, peso in enumerate((4, 1, 2, 2)):
            tabla.grid_columnconfigure(i, weight=peso, uniform="concepto")
        for i, titulo in enumerate(("Concepto *", "Cantidad", "Precio unitario", "Importe")):
            ctk.CTkLabel(tabla, text=titulo, font=Fonts.get(11, "bold"),
                         text_color=Colors.TEXT_ON_DARK, fg_color=Colors.PRIMARY_DARK,
                         height=Sizes.TABLE_HEADER_HEIGHT, anchor="w", corner_radius=0
                         ).grid(row=0, column=i, sticky="nsew", ipadx=8)

        # El concepto se escribe a mano: el que sea
        self.concepto = text_input(tabla, "Ej. Instalación de 4 cámaras IP con grabador")
        self.concepto.grid(row=1, column=0, sticky="ew", padx=8, pady=8)
        self.cantidad = text_input(tabla, "1", width=60)
        self.cantidad.grid(row=1, column=1, sticky="ew", padx=8, pady=8)
        self.precio = text_input(tabla, "0.00", width=90)
        self.precio.grid(row=1, column=2, sticky="ew", padx=8, pady=8)
        self.lbl_importe = ctk.CTkLabel(tabla, text="$0.00", font=Fonts.SMALL(),
                                        text_color=Colors.TEXT_BODY, anchor="w")
        self.lbl_importe.grid(row=1, column=3, sticky="ew", padx=16)
        for entrada in (self.cantidad, self.precio):
            entrada.bind("<KeyRelease>", self._recalcular)

        self.lbl_error_concepto = ctk.CTkLabel(conceptos, text="", font=Fonts.TINY(), height=18,
                                               text_color=Colors.ERROR, anchor="w")
        self.lbl_error_concepto.grid(row=1, column=0, sticky="w")

        abajo = ctk.CTkFrame(conceptos, fg_color="transparent")
        abajo.grid(row=2, column=0, sticky="ew")
        abajo.grid_columnconfigure(0, weight=1)

        # Izquierda: aviso (nueva) o estado + "Editar concepto" (detalle), y el anticipo
        izquierda = ctk.CTkFrame(abajo, fg_color="transparent")
        izquierda.grid(row=0, column=0, sticky="nw")
        self.btn_concepto = None
        self.menu_estado = None
        if self.nueva:
            ctk.CTkLabel(izquierda, text="La venta se registrará con estado Pendiente.",
                         font=Fonts.TINY(), text_color=Colors.TEXT_MUTED).pack(anchor="w")
        else:
            fila_estado = ctk.CTkFrame(izquierda, fg_color="transparent")
            fila_estado.pack(anchor="w")
            ctk.CTkLabel(fila_estado, text="Estado de la venta *", font=Fonts.SMALL(),
                         text_color=Colors.TEXT_BODY).pack(side="left")
            help_icon(fila_estado, "El estado indica en qué etapa va la venta. Solo se puede concluir "
                                   "si está asignada o en proceso; concluida o cancelada ya no cambia. "
                                   "Solo administración puede cancelar."
                      ).pack(side="left", padx=(6, 0))

            controles = ctk.CTkFrame(izquierda, fg_color="transparent")
            controles.pack(anchor="w", pady=(6, 0))
            actual = self.venta["status"]
            permitidos = [ESTADOS.get(s, s) for s in estados_permitidos(actual)]
            caja, self.var_estado, self.menu_estado = select_input(
                controles, permitidos, ESTADOS.get(actual, actual), width=220)
            caja.pack(side="left")
            if self._puede_editar("concepto"):
                self.btn_concepto = outline_button(controles, "Editar concepto", command=self._editar_concepto,
                                                   width=140, height=Sizes.INPUT_HEIGHT)
                self.btn_concepto.pack(side="left", padx=(10, 0))

        # Anticipo inicial (venta nueva). En el detalle los pagos van en la tarjeta "Pagos y saldo"
        if self.nueva:
            fila_anticipo = ctk.CTkFrame(izquierda, fg_color="transparent")
            fila_anticipo.pack(anchor="w", pady=(14, 0))
            marco, self.anticipo = campo_formulario(fila_anticipo, "Anticipo inicial", "$0.00",
                                                    ayuda="Opcional. Máximo el total.")
            marco.grid(row=0, column=0, sticky="nw", padx=(0, 12))
            self.anticipo.configure(width=170)
            self.anticipo.bind("<KeyRelease>", self._recalcular)
            marco, self.fecha_anticipo = campo_formulario(fila_anticipo, "Fecha del anticipo", "dd/mm/aaaa")
            marco.grid(row=0, column=1, sticky="nw")
            self.fecha_anticipo.configure(width=150)

        # Derecha: Con IVA / Sin IVA y los totales
        totales = ctk.CTkFrame(abajo, fg_color="transparent")
        totales.grid(row=0, column=1, sticky="ne")
        self.var_iva = ctk.StringVar(value=CON_IVA)
        self.seg_iva = ctk.CTkSegmentedButton(
            totales, values=[CON_IVA, SIN_IVA], variable=self.var_iva, font=Fonts.SMALL(), height=30,
            selected_color=Colors.PRIMARY, selected_hover_color=Colors.PRIMARY_HOVER,
            unselected_color=Colors.ROW_ALT, unselected_hover_color=Colors.BORDER,
            fg_color=Colors.BORDER, text_color=Colors.TEXT_BODY, command=self._recalcular)
        self.seg_iva.grid(row=0, column=0, columnspan=2, sticky="e", pady=(0, 8))
        self.lbl_subtotal = self._fila_total(totales, 1, "Subtotal")
        self.lbl_iva = self._fila_total(totales, 2, "IVA (16 %)",
                                        ayuda="Elige arriba si el total lleva IVA. Con IVA se suma el 16 % del subtotal.")
        self.lbl_total = self._fila_total(totales, 3, "Total", grande=True)
        ctk.CTkFrame(totales, height=1, fg_color=Colors.BORDER, corner_radius=0
                     ).grid(row=4, column=0, columnspan=2, sticky="ew", pady=6)
        self.lbl_anticipo = self._fila_total(totales, 5, "Anticipo" if self.nueva else "Pagado")
        self.lbl_saldo = self._fila_total(totales, 6, "Saldo pendiente", grande=True)

    def _fila_total(self, parent, fila, texto, ayuda=None, grande=False):
        etiqueta = ctk.CTkFrame(parent, fg_color="transparent")
        etiqueta.grid(row=fila, column=0, sticky="w", pady=1)
        ctk.CTkLabel(etiqueta, text=texto, font=Fonts.BODY_BOLD() if grande else Fonts.SMALL(),
                     text_color=Colors.TEXT_BODY).pack(side="left")
        if ayuda:
            help_icon(etiqueta, ayuda).pack(side="left", padx=(6, 0))
        valor = ctk.CTkLabel(parent, text="$0.00", anchor="e",
                             font=Fonts.get(16, "bold") if grande else Fonts.SMALL(),
                             text_color=Colors.TEXT_TITLE if grande else Colors.TEXT_BODY)
        valor.grid(row=fila, column=1, sticky="e", padx=(60, 0), pady=1)
        return valor

    def _build_tecnicos(self, cuerpo):
        # Todos ven a quién se asignó; solo quien tiene "asignar_tecnicos" puede asignar o quitar
        puede_asignar = puede("asignar_tecnicos")
        if self.nueva:
            return

        cerrada = self.venta["status"] in ordenTrabajo.CERRADOS
        card, lista = form_card(cuerpo, "Técnicos asignados", f"{len(self.tecnicos)} asignado(s)", columnas=1)
        card.grid(row=5, column=0, sticky="ew", pady=(16, 0))

        if not self.tecnicos:
            ctk.CTkLabel(lista, text="Esta venta aún no tiene técnico asignado.", font=Fonts.SMALL(),
                         text_color=Colors.TEXT_MUTED, anchor="w").grid(row=0, column=0, sticky="w")
        for i, (id_tecnico, nombre, especialidad) in enumerate(self.tecnicos):
            fila = ctk.CTkFrame(lista, fg_color=Colors.ROW_ALT, corner_radius=Sizes.BUTTON_RADIUS)
            fila.grid(row=i, column=0, sticky="ew", pady=3)
            fila.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(fila, text=iniciales(nombre), width=30, height=30, corner_radius=15,
                         fg_color=Colors.AVATAR_BG, text_color=Colors.AVATAR_TEXT, font=Fonts.get(10, "bold")
                         ).grid(row=0, column=0, padx=(10, 10), pady=8)
            ctk.CTkLabel(fila, text=f"{nombre}  ·  {especialidad or 'Sin especialidad'}", font=Fonts.SMALL(),
                         text_color=Colors.TEXT_BODY, anchor="w").grid(row=0, column=1, sticky="w")
            if puede_asignar and not cerrada:
                link_button(fila, "Quitar", command=lambda t=id_tecnico, n=nombre: self._quitar(t, n)
                            ).grid(row=0, column=2, padx=10)

        abajo = ctk.CTkFrame(lista, fg_color="transparent")
        abajo.grid(row=len(self.tecnicos) + 1, column=0, sticky="ew", pady=(8, 0))
        if not puede_asignar:
            ctk.CTkLabel(abajo, text="Solo administración, ingeniería o dirección pueden asignar técnicos.",
                         font=Fonts.TINY(), text_color=Colors.TEXT_MUTED).pack(anchor="w")
        elif cerrada:
            ctk.CTkLabel(abajo, text="La venta está cerrada; ya no se pueden cambiar sus técnicos.",
                         font=Fonts.TINY(), text_color=Colors.TEXT_MUTED).pack(anchor="w")
        else:
            primary_button(abajo, "Asignar técnico", command=self._dialogo_asignar, icon="+",
                           width=160).pack(anchor="w")

    def _build_pagos(self, cuerpo):
        # Precio inicial y cada anticipo/abono con su fecha y lo que resta después
        if self.nueva:
            return
        cuenta = self.cuenta
        card, cuerpo_pagos = form_card(cuerpo, "Pagos y saldo", f"Precio inicial: {dinero(cuenta['total'])}", columnas=3)
        card.grid(row=4, column=0, sticky="ew", pady=(16, 0))

        # Resumen
        for i, (titulo, valor) in enumerate((("Precio inicial", cuenta["total"]), ("Pagado", cuenta["pagado"]),
                                             ("Saldo pendiente", cuenta["saldo"]))):
            caja = ctk.CTkFrame(cuerpo_pagos, fg_color=Colors.ROW_ALT, corner_radius=Sizes.BUTTON_RADIUS)
            caja.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 6, 0 if i == 2 else 6))
            ctk.CTkLabel(caja, text=titulo, font=Fonts.TINY(), text_color=Colors.TEXT_MUTED).pack(anchor="w", padx=14, pady=(10, 0))
            ctk.CTkLabel(caja, text=dinero(valor), font=Fonts.H3(),
                         text_color=Colors.TEXT_TITLE).pack(anchor="w", padx=14, pady=(0, 10))

        # Tabla: Fecha | Movimiento | Monto | Registró | Nota | Saldo restante | (Quitar)
        puede_quitar = puede("eliminar_pagos")
        marco = ctk.CTkFrame(cuerpo_pagos, fg_color=Colors.SURFACE, border_width=1, border_color=Colors.BORDER,
                             corner_radius=0)
        marco.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(14, 0))
        tabla = ctk.CTkFrame(marco, fg_color="transparent", corner_radius=0)
        tabla.pack(fill="x", padx=1, pady=1)
        titulos = ["Fecha", "Movimiento", "Monto", "Registró", "Nota", "Saldo restante"] + (["Acción"] if puede_quitar else [])
        pesos = [2, 2, 2, 3, 3, 2] + ([1] if puede_quitar else [])
        for i, (titulo, peso) in enumerate(zip(titulos, pesos)):
            tabla.grid_columnconfigure(i, weight=peso, uniform="pagos")
            ctk.CTkLabel(tabla, text=titulo, font=Fonts.get(11, "bold"), text_color=Colors.TEXT_ON_DARK,
                         fg_color=Colors.PRIMARY_DARK, height=Sizes.TABLE_HEADER_HEIGHT, anchor="w",
                         corner_radius=0).grid(row=0, column=i, sticky="nsew", ipadx=8)
        filas = [[self._fecha_txt(self.venta["fecha"]), "Precio inicial", "", "", "", dinero(cuenta["total"])]]
        for mov in cuenta["movimientos"]:
            filas.append([self._fecha_txt(mov.get("fecha")), mov.get("tipo", "Pago"), f"- {dinero(mov['monto'])}",
                          mov.get("registro", ""), mov.get("nota", ""), dinero(mov["saldo"])])
        for r, fila in enumerate(filas, start=1):
            fondo = Colors.SURFACE if r % 2 else Colors.ROW_ALT
            for c, valor in enumerate(fila):
                ctk.CTkLabel(tabla, text=valor, font=Fonts.SMALL(), text_color=Colors.TEXT_BODY, fg_color=fondo,
                             height=36, anchor="w", corner_radius=0, wraplength=220, justify="left"
                             ).grid(row=r, column=c, sticky="nsew", ipadx=8)
            if puede_quitar:
                celda = ctk.CTkFrame(tabla, fg_color=fondo, corner_radius=0, height=36)
                celda.grid(row=r, column=len(fila), sticky="nsew")
                if r > 1:
                    mov = cuenta["movimientos"][r - 2]
                    link_button(celda, "Quitar", command=lambda m=mov: self._dialogo_quitar_pago(m)
                                ).place(x=4, rely=0.5, anchor="w")

        abajo = ctk.CTkFrame(cuerpo_pagos, fg_color="transparent")
        abajo.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        if not puede("registrar_pagos"):
            aviso = "Solo administración registra anticipos y abonos."
        elif self.venta["status"] == "cancelada":
            aviso = "La venta está cancelada; ya no se registran pagos."
        elif cuenta["saldo"] <= 0:
            aviso = "✓ La venta está liquidada."
        else:
            aviso = ""
            primary_button(abajo, "Registrar pago", command=self._dialogo_pago, icon="+", width=160).pack(side="left")
        if aviso:
            ctk.CTkLabel(abajo, text=aviso, font=Fonts.TINY(), text_color=Colors.TEXT_MUTED).pack(side="left")

    def _build_bitacora(self, cuerpo):
        # Un solo bloque tipo bloc de notas: avances, material pedido, problemas, pendientes...
        card, cuerpo_notas = form_card(cuerpo, "Bitácora", "Avances, material, problemas y pendientes", columnas=1)
        card.grid(row=6, column=0, sticky="ew", pady=(16, 0))
        yo = f"{sesion.actual().get('nombre') or sesion.actual().get('usuario', '')} ({rol_actual()})"
        self.txt_bitacora = None
        self.lbl_nota = None
        if self.nueva:
            ctk.CTkLabel(cuerpo_notas, text="Notas iniciales", font=Fonts.SMALL(), text_color=Colors.TEXT_BODY,
                         anchor="w").grid(row=0, column=0, sticky="w")
            self.nota_nueva = text_area(cuerpo_notas, height=140)
            self.nota_nueva.grid(row=1, column=0, sticky="ew", pady=(6, 4))
            ctk.CTkLabel(cuerpo_notas, text=f"Opcional. Se guardará a nombre de {yo} con la fecha al registrar la venta.",
                         font=Fonts.TINY(), text_color=Colors.TEXT_MUTED, anchor="w").grid(row=2, column=0, sticky="w")
            return

        # Bitácora guardada (solo lectura): cada nota con autor y fecha
        self.txt_bitacora = text_area(cuerpo_notas, height=280)
        self.txt_bitacora.grid(row=0, column=0, sticky="ew")

        ctk.CTkLabel(cuerpo_notas, text="Agregar nota", font=Fonts.SMALL(), text_color=Colors.TEXT_BODY,
                     anchor="w").grid(row=1, column=0, sticky="w", pady=(14, 0))
        self.nota_nueva = text_area(cuerpo_notas, height=110)
        self.nota_nueva.grid(row=2, column=0, sticky="ew", pady=(6, 6))

        fila = ctk.CTkFrame(cuerpo_notas, fg_color="transparent")
        fila.grid(row=3, column=0, sticky="ew")
        fila.grid_columnconfigure(0, weight=1)
        self.lbl_nota = ctk.CTkLabel(fila, text=f"Se guardará a nombre de {yo} con la fecha y hora.",
                                     font=Fonts.TINY(), text_color=Colors.TEXT_MUTED, anchor="w")
        self.lbl_nota.grid(row=0, column=0, sticky="w")
        if puede("eliminar_bitacora"):
            danger_button(fila, "Eliminar bitácora", command=self._dialogo_borrar_bitacora, width=150
                          ).grid(row=0, column=1, padx=(0, 10))
        if puede("escribir_bitacora"):
            primary_button(fila, "Agregar a la bitácora", command=self._agregar_nota, icon="+",
                           width=190).grid(row=0, column=2)

    def _mostrar_bitacora(self, texto):
        if self.txt_bitacora is None:
            return
        self.txt_bitacora.configure(state="normal")
        self.txt_bitacora.delete("1.0", "end")
        self.txt_bitacora.insert("1.0", (texto or "").strip() or SIN_NOTAS)
        self.txt_bitacora.configure(state="disabled")
        self.txt_bitacora.see("end")

    @staticmethod
    def _fecha_txt(fecha):
        # date o "2026-11-24" -> "24/11/2026"
        if isinstance(fecha, datetime.date):
            return fecha.strftime("%d/%m/%Y")
        try:
            return datetime.date.fromisoformat(str(fecha)).strftime("%d/%m/%Y")
        except ValueError:
            return str(fecha or "")

    # -------------------------------------------------------------------------------------------------------------------------
    #                         Datos
    # -------------------------------------------------------------------------------------------------------------------------
    def _llenar(self):
        if self.nueva:
            self.fecha.insert(0, datetime.date.today().strftime("%d/%m/%Y"))
            self.fecha_anticipo.insert(0, datetime.date.today().strftime("%d/%m/%Y"))
            self.cantidad.insert(0, "1")
            # Se propone el nombre de quien tiene la sesión abierta (se puede cambiar)
            nombre = sesion.actual().get("nombre") or ""
            if nombre:
                self.levantada.insert(0, nombre)
            self._mostrar_cliente()
            enfocar_despues(self.proyecto)
            return

        v = self.venta
        etiqueta = next((e for e, fila in self.clientes.items() if fila[0] == v["id_cliente"]), None)
        self.var_cliente.set(etiqueta or f"Cliente #{v['id_cliente']}")
        self._mostrar_cliente()
        for entrada, valor in ((self.proyecto, v["proyecto"]), (self.hora, hora_txt(v["hora"])),
                               (self.levantada, v["levantada_por"]), (self.numero, v["numero"]),
                               (self.colonia, v["colonia"])):
            if valor:
                entrada.insert(0, valor)
        if isinstance(v["fecha"], datetime.date):
            self.fecha.insert(0, v["fecha"].strftime("%d/%m/%Y"))
        # Ventas anteriores a la v4 solo tienen direccion_sitio: se muestra completa en Calle
        calle = v["calle"] if (v["calle"] or v["numero"] or v["colonia"]) else v["direccion"]
        if calle:
            self.calle.insert(0, calle)
        self.var_tipo.set(TIPOS.get(v["tipo"], TIPOS["instalacion"]))

        # Concepto, cantidad, precio e IVA guardados (las ventas viejas solo tenían el total con IVA)
        self.monto_original = float(v["monto"] or 0)
        if v["precio_unitario"] is not None:
            cantidad = int(v["cantidad"] or 1)
            precio = float(v["precio_unitario"])
            self.con_iva_original = bool(v["con_iva"])
            self.subtotal_original = round(cantidad * precio, 2)
        else:
            cantidad = 1
            self.con_iva_original = True
            precio = self.monto_original / (1 + IVA)
            self.subtotal_original = round(precio, 2)
        self.concepto.insert(0, v["concepto"] or TIPOS.get(v["tipo"], ""))
        self.cantidad.insert(0, str(cantidad))
        self.precio.insert(0, f"{precio:.2f}")
        self.var_iva.set(CON_IVA if self.con_iva_original else SIN_IVA)

        self._mostrar_bitacora(v["bitacora"])
        self._bloquear_concepto(True)

    def _aplicar_permisos(self):
        # Deja en gris lo que el rol no puede cambiar
        if self.anticipo is not None and not self._puede_editar("anticipo"):
            deshabilitar(self.anticipo)
            deshabilitar(self.fecha_anticipo)
        if not puede("escribir_bitacora"):
            deshabilitar(self.nota_nueva)
        if not self.nueva and (self.venta["levantada_por"] or not self.completo):
            deshabilitar(self.levantada)    # quién la levantó no cambia una vez registrado
        if self.completo:
            return
        campos = {"cliente": [self.menu_cliente], "proyecto": [self.proyecto, self.menu_tipo],
                  "fecha": [self.fecha], "hora": [self.hora],
                  "direccion": [self.calle, self.numero, self.colonia], "estado": [self.menu_estado]}
        for campo, widgets in campos.items():
            if not self._puede_editar(campo):
                for widget in widgets:
                    if widget is not None:
                        deshabilitar(widget)

    def _mostrar_cliente(self, _valor=None):
        fila = self.clientes.get(self.var_cliente.get())
        if fila is None:
            if puede("editar_clientes"):
                texto = "Primero registra un cliente en el módulo Clientes."
            else:
                texto = "El cliente no está registrado. Pide a administración que lo dé de alta."
        else:
            partes = [Clientes.clave(fila[0]), fila[1], fila[4], telefono_txt(fila[3])]
            texto = " · ".join(p for p in partes if p)
        self.lbl_cliente.configure(text=texto, text_color=Colors.TEXT_MUTED)

    def _bloquear_concepto(self, bloquear):
        estado = "disabled" if bloquear else "normal"
        fondo = Colors.INPUT_DISABLED if bloquear else Colors.SURFACE
        for entrada in (self.concepto, self.cantidad, self.precio):
            entrada.configure(state=estado, fg_color=fondo)
        self.seg_iva.configure(state=estado)

    def _editar_concepto(self):
        self.editando_concepto = True
        self._bloquear_concepto(False)
        self.btn_concepto.configure(state="disabled")
        self._recalcular()
        self.concepto.focus()

    def _leer_concepto(self):
        try:
            cantidad = int(self.cantidad.get().strip())
        except ValueError:
            cantidad = None
        precio = leer_importe(self.precio.get())
        return cantidad, precio

    def _leer_fecha(self, caja=None):
        texto = (caja or self.fecha).get().replace(" ", "")
        for formato in ("%d/%m/%Y", "%Y-%m-%d"):
            try:
                return datetime.datetime.strptime(texto, formato).date()
            except ValueError:
                pass
        return None

    def _leer_hora(self):
        # "" -> "" (sin hora) ; "9:30" -> "09:30:00" ; texto inválido -> None
        texto = self.hora.get().replace(" ", "")
        if not texto:
            return ""
        try:
            return datetime.datetime.strptime(texto, "%H:%M").strftime("%H:%M:00")
        except ValueError:
            return None

    def _calcular(self):
        # Regresa (subtotal, iva, total, con_iva)
        if self.editando_concepto:
            cantidad, precio = self._leer_concepto()
            subtotal = round(cantidad * precio, 2) if cantidad and precio else 0.0
            con_iva = self.var_iva.get() == CON_IVA
            iva = round(subtotal * IVA, 2) if con_iva else 0.0
            return subtotal, iva, round(subtotal + iva, 2), con_iva
        # Sin editar el concepto se respeta lo guardado
        total = self.monto_original
        return self.subtotal_original, round(total - self.subtotal_original, 2), total, self.con_iva_original

    def _recalcular(self, _evento=None):
        subtotal, iva, total, con_iva = self._calcular()
        if self.nueva:
            anticipo = leer_importe(self.anticipo.get()) or 0.0
        else:
            anticipo = self.cuenta["pagado"]
        self.lbl_importe.configure(text=dinero(subtotal))
        self.lbl_subtotal.configure(text=dinero(subtotal))
        self.lbl_iva.configure(text=dinero(iva) if con_iva else "No aplica")
        self.lbl_total.configure(text=dinero(total))
        self.lbl_anticipo.configure(text=f"- {dinero(anticipo)}")
        self.lbl_saldo.configure(text=dinero(total - anticipo))
        return total

    def _valores(self):
        estado = "" if self.nueva else self.var_estado.get()
        tecnico = self.var_tecnico.get() if self.var_tecnico is not None else ""
        cajas = [self.proyecto, self.fecha, self.hora, self.levantada, self.calle, self.numero, self.colonia,
                 self.concepto, self.cantidad, self.precio]
        if self.nueva:
            cajas += [self.anticipo, self.fecha_anticipo]
        return (self.var_cliente.get(), self.var_tipo.get(), self.var_iva.get(), estado, tecnico,
                texto_de(self.nota_nueva).strip()) + tuple(c.get().strip() for c in cajas)

    # -------------------------------------------------------------------------------------------------------------------------
    #                         Validación y guardado
    # -------------------------------------------------------------------------------------------------------------------------
    def _validar(self):
        valido = True
        if self.completo and self.var_cliente.get() not in self.clientes:
            self.lbl_cliente.configure(text="Selecciona un cliente. Si no existe, hay que registrarlo en Clientes.",
                                       text_color=Colors.ERROR)
            valido = False

        # Solo se validan los campos que el rol puede modificar
        revisiones = [
            ("proyecto", self.proyecto, bool(self.proyecto.get().strip()), "Escribe el nombre del proyecto."),
            ("fecha", self.fecha, self._leer_fecha() is not None, "Usa el formato dd/mm/aaaa, por ejemplo 04/11/2026."),
            ("hora", self.hora, self._leer_hora() is not None, "Usa el formato hh:mm, por ejemplo 09:30."),
        ]
        if self.nueva:
            revisiones.append(("levantada", self.levantada, bool(self.levantada.get().strip()),
                               "Escribe quién llenó esta venta."))
        for campo, entrada, correcto, mensaje in revisiones:
            if campo != "levantada" and not self._puede_editar(campo):
                continue
            marcar_error(entrada, "" if correcto else mensaje)
            valido = valido and correcto

        total = self._calcular()[2]
        if self.editando_concepto:
            cantidad, precio = self._leer_concepto()
            sin_concepto = not self.concepto.get().strip()
            mala_cantidad = cantidad is None or cantidad < 1
            mal_precio = precio is None or precio <= 0
            marcar_error(self.concepto, "x" if sin_concepto else "")
            marcar_error(self.cantidad, "x" if mala_cantidad else "")
            marcar_error(self.precio, "x" if mal_precio else "")
            if sin_concepto:
                self.lbl_error_concepto.configure(text="Escribe el concepto de la venta.")
                valido = False
            elif mala_cantidad or mal_precio:
                self.lbl_error_concepto.configure(
                    text="La cantidad debe ser un número entero mayor a 0 y el precio un importe mayor a 0.")
                valido = False
            else:
                self.lbl_error_concepto.configure(text="")

        if self.nueva and self._puede_editar("anticipo"):
            anticipo = leer_importe(self.anticipo.get())
            if anticipo is None or anticipo < 0:
                mensaje = "Escribe un importe válido, por ejemplo 1500."
            elif anticipo > total:
                mensaje = f"Máximo el total ({dinero(total)})."
            else:
                mensaje = ""
            marcar_error(self.anticipo, mensaje)
            valido = valido and not mensaje
            fecha_ok = not anticipo or self._leer_fecha(self.fecha_anticipo) is not None
            marcar_error(self.fecha_anticipo, "" if fecha_ok else "Usa dd/mm/aaaa.")
            valido = valido and fecha_ok
        elif not self.nueva and self.editando_concepto and total < self.cuenta["pagado"]:
            # Al editar el concepto, el total no puede quedar por debajo de lo ya pagado
            self.lbl_error_concepto.configure(
                text=f"El total no puede ser menor que lo ya pagado ({dinero(self.cuenta['pagado'])}).")
            valido = False
        return valido

    def _datos(self):
        # Todo lo que se manda al controlador en un diccionario
        fila = self.clientes.get(self.var_cliente.get())
        subtotal, iva, total, con_iva = self._calcular()
        datos = {
            "id_cliente": fila[0] if fila else self.venta["id_cliente"],
            "tipo": clave_de(TIPOS, self.var_tipo.get()),
            "proyecto": self.proyecto.get().strip(),
            "fecha": self._leer_fecha(),
            "hora": self._leer_hora() or None,
            "calle": self.calle.get().strip(),
            "numero": self.numero.get().strip(),
            "colonia": self.colonia.get().strip(),
            "levantada_por": self.levantada.get().strip(),
            "monto_anticipo": (leer_importe(self.anticipo.get()) or 0.0) if self.nueva else self.venta["monto_anticipo"],
            "fecha_anticipo": self._leer_fecha(self.fecha_anticipo) if self.nueva else None,
            "notas": texto_de(self.nota_nueva).strip() if self.nueva else "",
            "status": "pendiente" if self.nueva else clave_de(ESTADOS, self.var_estado.get()),
            "id_tecnico": self.tecnicos_libres.get(self.var_tecnico.get()) if self.var_tecnico else None,
        }
        if self.editando_concepto:
            cantidad, precio = self._leer_concepto()
            datos.update(concepto=self.concepto.get().strip(), cantidad=cantidad, precio_unitario=precio,
                         con_iva=con_iva, monto=total)
        else:
            v = self.venta
            datos.update(concepto=v["concepto"], cantidad=v["cantidad"], precio_unitario=v["precio_unitario"],
                         con_iva=v["con_iva"], monto=v["monto"])
        return datos

    def _guardar(self):
        if not self._validar():
            return
        datos = self._datos()
        if self.nueva:
            self.guardar(datos)
        elif self._valores() == self.inicial:
            dialogo(self, "No hay cambios por guardar",
                    "Modifica algún dato de la venta o usa «Volver a ventas».")
        else:
            confirmar(self, "¿Estás seguro de hacer los cambios?", lambda: self.guardar(datos))

    def _hay_cambios(self, accion):
        if self._valores() != self.inicial:
            dialogo(self, "Tienes cambios sin guardar",
                    f"Guarda o cancela tus cambios antes de {accion}.")
            return True
        return False

    def _dialogo_estado(self):
        if self._hay_cambios("cambiar el estado de la venta"):
            return
        actual = self.venta["status"]
        opciones = [ESTADOS.get(s, s) for s in estados_permitidos(actual) if s != actual]
        if not opciones:
            dialogo(self, "Esta venta ya está cerrada",
                    f"La venta está {ESTADOS.get(actual, actual).lower()} y ya no puede cambiar de estado.")
            return

        seleccion = {}

        def construir(marco):
            caja, seleccion["var"], _ = select_input(marco, opciones, opciones[0])
            caja.pack(fill="x")

        dialogo(self, f"Cambiar estado de {self.folio}",
                f"Estado actual: {ESTADOS.get(actual, actual)}. Elige el nuevo estado:",
                [("Cancelar", None, "contorno"),
                 ("Aplicar", lambda: self.cambiar_estado(self.venta["id"], clave_de(ESTADOS, seleccion["var"].get())),
                  "primario")],
                construir=construir)

    def _dialogo_asignar(self):
        if self._hay_cambios("asignar un técnico"):
            return
        asignados = {t[0] for t in self.tecnicos}
        disponibles = {}
        for id_tecnico, nombre, especialidad in Trabajadores.consultar_tecnicos():
            if id_tecnico in asignados:
                continue
            etiqueta = f"{nombre} · {especialidad}" if especialidad else nombre
            if etiqueta in disponibles:
                etiqueta = f"{etiqueta} ({Trabajadores.clave(id_tecnico)})"
            disponibles[etiqueta] = id_tecnico
        if not disponibles:
            dialogo(self, "No hay técnicos disponibles",
                    "Todos los técnicos activos ya están en esta venta, o todavía no hay técnicos. "
                    "Puedes darlos de alta en el módulo Usuarios.", ancho=400)
            return

        seleccion = {}
        opciones = list(disponibles)

        def construir(marco):
            caja, seleccion["var"], _ = select_input(marco, opciones, opciones[0])
            caja.pack(fill="x")

        dialogo(self, f"Asignar técnico a {self.folio}",
                "Elige al técnico. Si la venta está pendiente pasará a Asignada.",
                [("Cancelar", None, "contorno"),
                 ("Asignar", lambda: self.asignar_tecnico(self.venta["id"], disponibles[seleccion["var"].get()]),
                  "primario")],
                construir=construir, ancho=400)

    def _quitar(self, id_tecnico, nombre):
        if self._hay_cambios("quitar un técnico"):
            return
        confirmar(self, f"¿Quitar a {nombre} de esta venta?",
                  lambda: self.quitar_tecnico(self.venta["id"], id_tecnico),
                  "Si ya no queda ningún técnico, la venta vuelve a Pendiente.")

    # -------------------------------------------------------------------------------------------------------------------------
    #                         Pagos, bitácora e impresión
    # -------------------------------------------------------------------------------------------------------------------------
    def _dialogo_pago(self):
        if self._hay_cambios("registrar un pago"):
            return
        saldo = self.cuenta["saldo"]
        campos = {}
        tipo_inicial = "Abono" if self.cuenta["movimientos"] else "Anticipo"

        def construir(marco):
            marco.grid_columnconfigure((0, 1), weight=1, uniform="pago")
            m, campos["var_tipo"], _, _ = campo_select(marco, "Tipo", list(TIPOS_PAGO), tipo_inicial,
                                                       command=lambda t: liquidar(t))
            m.grid(row=0, column=0, sticky="new", padx=(0, 6))
            m, campos["monto"] = campo_formulario(marco, "Monto *", "$0.00", ayuda=f"Máximo {dinero(saldo)}")
            m.grid(row=0, column=1, sticky="new", padx=(6, 0))
            m, campos["fecha"] = campo_formulario(marco, "Fecha *", "dd/mm/aaaa")
            m.grid(row=1, column=0, sticky="new", padx=(0, 6))
            campos["fecha"].insert(0, datetime.date.today().strftime("%d/%m/%Y"))
            m, campos["nota"] = campo_formulario(marco, "Nota", "Ej. transferencia, efectivo")
            m.grid(row=1, column=1, sticky="new", padx=(6, 0))

        def liquidar(tipo):
            # "Liquidación" llena el monto con todo lo que falta
            if tipo == "Liquidación":
                campos["monto"].delete(0, "end")
                campos["monto"].insert(0, f"{saldo:.2f}")

        def registrar():
            monto = leer_importe(campos["monto"].get())
            fecha = self._leer_fecha(campos["fecha"])
            error_monto = ""
            if monto is None or monto <= 0:
                error_monto = "Escribe un importe mayor a 0."
            elif monto > saldo + 0.001:
                error_monto = f"No puede ser mayor que el saldo ({dinero(saldo)})."
            marcar_error(campos["monto"], error_monto)
            marcar_error(campos["fecha"], "" if fecha else "Usa dd/mm/aaaa.")
            if error_monto or not fecha:
                return False        # el diálogo sigue abierto
            pago = {"fecha": fecha.isoformat(), "monto": round(monto, 2), "tipo": campos["var_tipo"].get(),
                    "nota": campos["nota"].get().strip()}
            self.after(10, lambda: self.registrar_pago(self.venta["id"], pago))
            return True

        dialogo(self, f"Registrar pago en {self.folio}", f"Saldo pendiente: {dinero(saldo)}",
                [("Cancelar", None, "contorno"), ("Registrar", registrar, "primario", True)],
                construir=construir, ancho=460)

    def _dialogo_quitar_pago(self, movimiento):
        if self._hay_cambios("quitar un pago"):
            return
        confirmar(self, f"¿Quitar el {movimiento.get('tipo', 'pago').lower()} de {dinero(movimiento['monto'])} "
                        f"del {self._fecha_txt(movimiento.get('fecha'))}?",
                  lambda: self.quitar_pago(self.venta["id"], movimiento["indice"]),
                  "El saldo se vuelve a calcular y quedará anotado en la bitácora.")

    def _agregar_nota(self):
        texto = texto_de(self.nota_nueva).strip()
        if not texto:
            self.lbl_nota.configure(text="Escribe la nota primero.", text_color=Colors.ERROR)
            return
        bitacora = self.agregar_nota(self.venta["id"], texto)
        if bitacora is None:
            return
        # Se actualiza solo la bitácora (no se pierde lo que estés editando arriba)
        self._mostrar_bitacora(bitacora)
        self.nota_nueva.delete("1.0", "end")
        self.lbl_nota.configure(text=f"✓ Nota agregada el {datetime.datetime.now():%d/%m/%Y a las %H:%M}.",
                                text_color=Colors.SUCCESS_TEXT)

    def _dialogo_borrar_bitacora(self):
        def borrar():
            bitacora = self.borrar_bitacora(self.venta["id"])
            if bitacora is not None:
                self._mostrar_bitacora(bitacora)
                self.lbl_nota.configure(text="Se eliminó la bitácora.", text_color=Colors.TEXT_MUTED)

        confirmar(self, f"¿Eliminar toda la bitácora de {self.folio}?", borrar,
                  "Se borrarán todas las notas. Quedará anotado quién la eliminó y cuándo.")

    def _imprimir(self):
        if self._hay_cambios("imprimir (se imprime lo que está guardado)"):
            return
        self.imprimir(self.venta["id"])

    def _salir(self, destino):
        if self._valores() != self.inicial:
            salir_sin_guardar(self, destino)
        else:
            destino()
