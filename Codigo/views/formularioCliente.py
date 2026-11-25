import re

from views.estilos import (enfocar_despues, Colors, Fonts, Sizes, primary_button, outline_button, campo_formulario,
                           marcar_error, form_card, page_header, confirmar, salir_sin_guardar, deshabilitar,
                           data_table, dialogo, telefono_txt, fecha_corta, dinero, ctk, sidebar, header)
from configuraciones.permisos import puede
from cliente.cliente import Clientes
from ordenes.ordenes import ordenTrabajo

PATRON_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")

class FormularioCliente(ctk.CTkFrame):
    # Sirve para Mockup 07 (Nuevo cliente) y Mockup 08 (Editar cliente).
    # cliente = None para uno nuevo, o la tupla (id, razon_social, persona_contacto, telefono, email)
    # Si el rol no puede editar clientes (técnico), se muestra en solo lectura.
    def __init__(self, master, on_logout, mainMenu, customers, orders, users, settings, guardar, cliente=None,
                 ver_venta=None):
        super().__init__(master, fg_color=Colors.BG, corner_radius=0)
        self.guardar = guardar
        self.cliente = cliente
        self.customers = customers
        self.ver_venta = ver_venta
        self.nuevo = cliente is None
        self.solo_lectura = not self.nuevo and not puede("editar_clientes")
        if self.nuevo:
            master.title("Eclipcom - Nuevo cliente")
        else:
            master.title("Eclipcom - Cliente" if self.solo_lectura else "Eclipcom - Editar cliente")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        header(self)
        # Si hay cambios sin guardar, el menú lateral también pregunta antes de salir
        sidebar(self, lambda: self._salir(on_logout), lambda: self._salir(mainMenu),
                lambda: self._salir(customers), lambda: self._salir(orders), "clientes", subpagina=True,
                users=lambda: self._salir(users), settings=lambda: self._salir(settings))
        self._build_content()
        self._llenar()
        self.inicial = self._valores()

    @staticmethod
    def separar_nombre(completo):
        # En la BD el nombre va junto (persona_contacto). Se toman los 2 últimos como apellidos:
        # "Mariana López Hernández" -> ("Mariana", "López Hernández")
        partes = str(completo or "").split()
        if len(partes) <= 1:
            return " ".join(partes), ""
        if len(partes) == 2:
            return partes[0], partes[1]
        return " ".join(partes[:-2]), " ".join(partes[-2:])

    def _build_content(self):
        pad = Sizes.CONTENT_PAD
        content = ctk.CTkScrollableFrame(self, fg_color=Colors.BG, corner_radius=0)
        content.grid(row=1, column=1, sticky="nsew")
        content.grid_columnconfigure(0, weight=1)
        cuerpo = ctk.CTkFrame(content, fg_color="transparent")
        cuerpo.grid(row=0, column=0, sticky="nsew", padx=pad, pady=pad)
        cuerpo.grid_columnconfigure(0, weight=1)

        if self.nuevo:
            top = page_header(cuerpo, "Inicio / Clientes / Nuevo cliente", "Nuevo cliente",
                              "Completa los datos para crear un nuevo registro en el directorio.")
        else:
            nombre = self.cliente[2] or self.cliente[1] or "este cliente"
            if self.solo_lectura:
                titulo, subtitulo = "Cliente", f"Consulta la información de {nombre}. Solo administración puede editarla."
            else:
                titulo, subtitulo = "Editar cliente", f"Actualiza la información de {nombre} y conserva sus datos al día."
            top = page_header(cuerpo, f"Inicio / Clientes / {Clientes.clave(self.cliente[0])}", titulo, subtitulo)
        outline_button(top, "Volver a clientes", command=lambda: self._salir(self.customers),
                       icon="←", width=160).grid(row=0, column=1, rowspan=2, sticky="e")

        # Datos de identificación
        detalle = "ID asignado al guardar" if self.nuevo else f"Cliente {Clientes.clave(self.cliente[0])}"
        card, datos = form_card(cuerpo, "Datos de identificación", detalle)
        card.grid(row=2, column=0, sticky="ew")
        marco, self.nombre = campo_formulario(datos, "Nombre(s) *", "Ingresa el nombre")
        marco.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        marco, self.apellidos = campo_formulario(datos, "Apellidos *", "Ingresa los apellidos")
        marco.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        marco, self.empresa = campo_formulario(datos, "Empresa", "Nombre comercial o razón social")
        marco.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(4, 0))

        # Datos de contacto
        card, contacto = form_card(cuerpo, "Datos de contacto", "Verifica los datos antes de guardar")
        card.grid(row=3, column=0, sticky="ew", pady=(16, 0))
        marco, self.email = campo_formulario(contacto, "Correo electrónico *", "nombre@empresa.mx")
        marco.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        marco, self.telefono = campo_formulario(contacto, "Teléfono *", "Ej. 618 414 1260")
        marco.grid(row=0, column=1, sticky="ew", padx=(10, 0))

        # Ventas del cliente (para consultar su historial y abrir cada venta)
        if not self.nuevo:
            self._build_historial(cuerpo)

        # Pie: * Campos obligatorios   [Cancelar] [Guardar]   (en solo lectura no hay pie)
        if self.solo_lectura:
            return
        pie = ctk.CTkFrame(cuerpo, fg_color="transparent")
        pie.grid(row=5, column=0, sticky="ew", pady=(16, 0))
        pie.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(pie, text="* Campos obligatorios", font=Fonts.TINY(),
                     text_color=Colors.TEXT_MUTED).grid(row=0, column=0, sticky="w")
        outline_button(pie, "Cancelar", command=lambda: self._salir(self.customers),
                       width=110).grid(row=0, column=1, padx=(0, 10))
        primary_button(pie, "Guardar cliente" if self.nuevo else "Guardar cambios",
                       command=self._guardar, icon="", width=150).grid(row=0, column=2)

    def _build_historial(self, cuerpo):
        ventas = [v for v in ordenTrabajo.consultar() if v["id_cliente"] == self.cliente[0]]
        ventas.sort(key=lambda v: v["id"], reverse=True)
        card, lista = form_card(cuerpo, "Ventas del cliente", f"{len(ventas)} venta(s)", columnas=1)
        card.grid(row=4, column=0, sticky="ew", pady=(16, 0))
        if not ventas:
            ctk.CTkLabel(lista, text="Este cliente todavía no tiene ventas registradas.", font=Fonts.SMALL(),
                         text_color=Colors.TEXT_MUTED, anchor="w").grid(row=0, column=0, sticky="w")
            return
        columnas = [("Folio / Fecha", 2), ("Proyecto", 3), ("Técnico", 2), ("Total (MXN)", 2),
                    ("Estado", 2), ("Acción", 2)]
        filas = [[f'{ordenTrabajo.folio(v["id"], v["fecha"])}\n{fecha_corta(v["fecha"])}', v["proyecto"] or "",
                  v["tecnicos"] or "Sin asignar", dinero(v["monto"]),
                  str(v["status"]).replace("_", " ").capitalize()] for v in ventas]
        self.ids_ventas = {fila[0]: v["id"] for fila, v in zip(filas, ventas)}
        data_table(lista, columnas, filas, action_text="Ver detalle",
                   on_action=self._abrir_venta if self.ver_venta else None).grid(row=0, column=0, sticky="ew")

    def _abrir_venta(self, fila):
        self._salir(lambda: self.ver_venta(self.ids_ventas[fila[0]]))

    def _llenar(self):
        if self.nuevo:
            enfocar_despues(self.nombre)
            return
        id_cliente, razon, contacto, telefono, email = self.cliente
        nombre, apellidos = self.separar_nombre(contacto)
        for entrada, valor in ((self.nombre, nombre), (self.apellidos, apellidos),
                               (self.empresa, razon), (self.email, email),
                               (self.telefono, telefono_txt(telefono))):
            if valor:
                entrada.insert(0, valor)
            if self.solo_lectura:
                deshabilitar(entrada)

    def _valores(self):
        return tuple(e.get().strip() for e in (self.nombre, self.apellidos, self.empresa,
                                               self.email, self.telefono))

    # -------------------------------------------------------------------------------------------------------------------------
    #                         Validación y guardado
    # -------------------------------------------------------------------------------------------------------------------------
    def _validar(self):
        nombre, apellidos, empresa, email, telefono = self._valores()
        digitos = "".join(c for c in telefono if c.isdigit())
        telefono_ok = len(digitos) == 10 and all(c.isdigit() or c in " -" for c in telefono)
        errores = [
            (self.nombre, "" if nombre else "Escribe el nombre del cliente."),
            (self.apellidos, "" if apellidos else "Escribe los apellidos del cliente."),
            (self.email, "" if PATRON_CORREO.match(email)
                         else "Escribe un correo válido, por ejemplo: nombre@empresa.mx"),
            (self.telefono, "" if telefono_ok else "El teléfono debe tener 10 dígitos."),
        ]
        primero = None
        for entrada, mensaje in errores:
            marcar_error(entrada, mensaje)
            if mensaje and primero is None:
                primero = entrada
        if primero is not None:
            primero.focus()
            return False
        return True

    def _guardar(self):
        if not self._validar():
            return
        nombre, apellidos, empresa, email, telefono = self._valores()
        contacto = f"{nombre} {apellidos}"
        telefono = "".join(c for c in telefono if c.isdigit())   # se guardan solo los 10 dígitos

        if self.nuevo:
            self.guardar(empresa, contacto, telefono, email)
        elif self._valores() == self.inicial:
            dialogo(self, "No hay cambios por guardar",
                    "Modifica algún dato del cliente o usa «Volver a clientes».")
        else:
            confirmar(self, "¿Estás seguro de hacer los cambios?",
                      lambda: self.guardar(empresa, contacto, telefono, email))

    def _salir(self, destino):
        if self._valores() != self.inicial:
            salir_sin_guardar(self, destino)
        else:
            destino()
