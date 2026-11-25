import sys
import datetime
import tkinter
from tkinter import messagebox

from views.estilos import Colors, Sizes, apply_theme, aplicar_tema, poner_icono, dinero, ctk, dialogo
from views.inicioSesion import View_inicioSesion
from views.menuPrincipal import MainMenu
from views.ventas import Ventas
from views.clientes import Customers
from views.formularioCliente import FormularioCliente
from views.formularioVenta import FormularioVenta
from views.usuarios import Usuarios
from views.formularioUsuario import FormularioUsuario
from views.configuracionInicial import ConfiguracionInicial
from views.configuracion import Configuracion
from views import impresion

from controladores.inicioSesion import controlador_iniciarSesion

from cliente.cliente import Clientes
from ordenes.ordenes import ordenTrabajo
from trabajadores.trabajadores import Trabajadores

from configuraciones import sesion, generalConfiguracion
from configuraciones.permisos import puede, rol_actual, rol_valido, CAMPOS_VENTA_PARCIAL, ESTADOS_SOLO_GESTION
from conexion import conexion, cursor
import migraciones


class App():
    def __init__(self, ventana):
        self.ventana = ventana
        apply_theme()
        w, h = Sizes.WINDOW
        self.ventana.geometry(f"{w}x{h}")
        self.ventana.minsize(960, 600)
        # Esto maximiza la ventana por defecto
        self.ventana.after(0, self.maximizar)
        self.ventana.configure(fg_color=Colors.BG)
        self.ventana.grid_columnconfigure(0, weight=1)
        self.ventana.grid_rowconfigure(1, weight=1)
        # Intercepta el botón cerrar
        self.ventana.protocol("WM_DELETE_WINDOW", self.cerrar)
        self.ventana.bind("<F11>", lambda event: self.ventana.attributes("-fullscreen", not self.ventana.attributes("-fullscreen")))
        self.ventana.bind("<Escape>", lambda event: self.ventana.attributes("-fullscreen", False))
        self.main()

#     # ------Utilidades-------

    def maximizar(self):
        try:
            self.ventana.state("zoomed")        # Windows
        except tkinter.TclError:
            self.ventana.attributes("-zoomed", True)    # Linux

    def borrarPantalla(self):
        for widget in self.ventana.winfo_children():
            widget.destroy()
        for i in range(5):
            self.ventana.grid_columnconfigure(i, weight=0)
            self.ventana.grid_rowconfigure(i, weight=0)

    def prepararPantalla(self):
        self.borrarPantalla()
        self.ventana.grid_columnconfigure(0, weight=1)
        self.ventana.grid_rowconfigure(0, weight=1)

    def navegacion(self):
        # Botones del menú lateral que reciben todas las vistas
        return {"on_logout": self.cerrar_sesion, "mainMenu": self.cambiar_menuPrincipal,
                "customers": self.cambiar_clientes, "orders": self.cambiar_ordenes,
                "users": self.cambiar_usuarios, "settings": self.cambiar_configuracion}

    def cerrar(self):
        # El archivo de sesión solo existe si marcó "Recordarme"; aquí solo se cierra la conexión
        if conexion is not None:
            try:
                cursor.close()
                conexion.close()
            except Exception as e:
                print(f"Error al cerrar la conexión: {e}")
        self.ventana.destroy()

    def cerrar_sesion(self):
        sesion.terminar()
        self.ventana.after(150, self.vista_inicioSesion)

    def cambiar_menuPrincipal(self):
        self.ventana.after(150, self.vista_menuPrincipal)

    def cambiar_clientes(self):
        self.ventana.after(150, self.vista_clientes)

    def cambiar_nuevo_cliente(self):
        self.ventana.after(150, self.vista_nuevo_cliente)

    def cambiar_editar_cliente(self, id):
        self.ventana.after(150, lambda: self.vista_editar_cliente(id))

    def cambiar_ordenes(self):
        self.ventana.after(150, self.vista_ordenes)

    def cambiar_nueva_venta(self):
        self.ventana.after(150, self.vista_nueva_venta)

    def cambiar_detalle_venta(self, id):
        self.ventana.after(150, lambda: self.vista_detalle_venta(id))

    def cambiar_usuarios(self):
        self.ventana.after(150, self.vista_usuarios)

    def cambiar_nuevo_usuario(self):
        self.ventana.after(150, self.vista_nuevo_usuario)

    def cambiar_editar_usuario(self, id):
        self.ventana.after(150, lambda: self.vista_editar_usuario(id))

    def cambiar_configuracion(self):
        self.ventana.after(150, self.vista_configuracion)

    def cambiar_tema(self, modo, acento):
        # Se guarda en config.json, se cambian los colores y se vuelve a dibujar la pantalla
        modo, acento = aplicar_tema(modo, acento)
        generalConfiguracion.GeneralConfig.guardar("modo", modo)
        generalConfiguracion.GeneralConfig.guardar("color", acento)
        self.ventana.configure(fg_color=Colors.BG)
        self.cambiar_configuracion()

    def respuesta_sql(self, respuesta, al_aceptar=None):
        # Mockup 08: "Acción realizada con éxito"  [ACEPTAR]
        if respuesta:
            dialogo(self.ventana, "Acción realizada con éxito", al_cerrar=al_aceptar)
        else:
            dialogo(self.ventana, "No se pudo realizar la acción",
                    "Verifica los datos e inténtalo de nuevo. Si el problema sigue, "
                    "revisa la conexión con la base de datos.")

    def autor(self):
        # "Luis Hernández (Tecnico)": se usa en la bitácora y en los pagos
        datos = sesion.actual()
        return f"{datos.get('nombre') or datos.get('usuario') or 'Usuario'} ({rol_actual() or 'sin rol'})"

    def tiene_permiso(self, permiso):
        # Segunda revisión de permisos: aunque la vista oculte un botón, el controlador vuelve a checar
        if puede(permiso):
            return True
        dialogo(self.ventana, "No tienes permiso para esta acción",
                f"Tu rol ({rol_actual() or 'sin rol'}) no puede hacerlo. Pide apoyo a administración.")
        return False

    # -------------------------------------------------------------------------------------------------------------------------
#                                                           Vistas
#       -----------------------------------------------------------------------------------------------------------------------
    def main(self):
        if conexion is None:
            messagebox.showerror(title="Eclipcom",
                                 message="No se pudo conectar con la base de datos eclipse_ordenes.\n"
                                         "Verifica que MySQL esté encendido (XAMPP) y vuelve a abrir el programa.")
            self.ventana.destroy()
            return
        # Agrega a la BD las columnas nuevas que necesite esta versión (si ya existen no hace nada)
        try:
            agregadas = migraciones.actualizar_bd()
            if agregadas:
                print("Columnas agregadas a la base de datos:", ", ".join(agregadas))
        except Exception as e:
            messagebox.showerror(title="Eclipcom",
                                 message=f"No se pudo actualizar la base de datos:\n{e}\n\n"
                                         "Revisa que el usuario de MySQL tenga permiso para modificar tablas.")
            self.ventana.destroy()
            return
        # Primera vez: si no hay ningún administrador, se pide crear uno (no hay que tocar la BD a mano)
        if not Trabajadores.hay_administrador():
            sesion.terminar()
            self.vista_configuracion_inicial()
            return
        # "Recordarme": el archivo solo trae id y usuario; el rol se vuelve a leer de la BD
        recordado = sesion.cargar()
        trabajador = Trabajadores.consultar_id(recordado.get("id")) if recordado.get("id") else None
        # trabajador = (id, nombre, usuario, rol, especialidad, status)
        if trabajador and trabajador[2] == recordado.get("usuario") and trabajador[5] == "activo":
            sesion.iniciar(trabajador[0], trabajador[2], trabajador[3], trabajador[1], recordar=True)
            self.vista_menuPrincipal()
        else:
            sesion.terminar()
            self.vista_inicioSesion()

    # ------Vista Configuración inicial (solo si no hay administrador)-------

    def vista_configuracion_inicial(self):
        self.prepararPantalla()
        vista = ConfiguracionInicial(self.ventana, self.crear_primer_admin_controller,
                                     lambda: self.ventana.after(150, self.vista_inicioSesion))
        vista.grid(row=0, column=0, sticky="nsew")

    def bienvenida_admin(self):
        self.vista_menuPrincipal()
        dialogo(self.ventana, "¡Listo! Ya eres administrador de Eclipcom",
                "Ahora da de alta a tu equipo (ingenieros, administrativos y técnicos) en el módulo Usuarios.",
                [("Después", None, "contorno"), ("Ir a Usuarios", self.cambiar_usuarios, "primario")], ancho=420)

    # ------Vistas Inicio de Sesion-------

    def vista_inicioSesion(self):
        self.prepararPantalla()
        vista = View_inicioSesion(self.ventana, controlador_iniciarSesion, self.vista_menuPrincipal)
        vista.grid(row=0, column=0, sticky="nsew")

    # ------Vistas Menu Principal-------

    def vista_menuPrincipal(self):
        self.prepararPantalla()
        vista = MainMenu(self.ventana, **self.navegacion())
        vista.grid(row=0, column=0, sticky="nsew")

    # ------Vistas Clientes (solo gestión)-------

    def vista_clientes(self):
        if not self.tiene_permiso("ver_clientes"):
            return
        self.prepararPantalla()
        vista = Customers(self.ventana, **self.navegacion(),
                          nuevo_cliente=self.cambiar_nuevo_cliente, editar_cliente=self.cambiar_editar_cliente)
        vista.grid(row=0, column=0, sticky="nsew")

    def vista_nuevo_cliente(self):
        if not self.tiene_permiso("editar_clientes"):
            return
        self.prepararPantalla()
        vista = FormularioCliente(self.ventana, **self.navegacion(), guardar=self.insertar_cliente_controller)
        vista.grid(row=0, column=0, sticky="nsew")

    def vista_editar_cliente(self, id):
        # Con "editar_clientes" se edita; con solo "ver_clientes" (técnico) se muestra en solo lectura
        if not self.tiene_permiso("ver_clientes"):
            return
        cliente = Clientes.consultar_id(id)
        if cliente is None:
            dialogo(self.ventana, "No se encontró el cliente", "Es posible que lo hayan eliminado.")
            return
        self.prepararPantalla()
        vista = FormularioCliente(self.ventana, **self.navegacion(),
                                  guardar=lambda razon, contacto, telefono, email:
                                      self.modificar_cliente_controller(id, razon, contacto, telefono, email),
                                  cliente=cliente, ver_venta=self.cambiar_detalle_venta)
        vista.grid(row=0, column=0, sticky="nsew")

    # ------Vistas Ventas (órdenes)-------

    def vista_ordenes(self, mensaje=None):
        if not self.tiene_permiso("ver_ventas"):
            return
        self.prepararPantalla()
        vista = Ventas(self.ventana, **self.navegacion(),
                       nueva_venta=self.cambiar_nueva_venta,
                       ver_detalle=lambda venta: self.cambiar_detalle_venta(venta["id"]),
                       mensaje=mensaje)
        vista.grid(row=0, column=0, sticky="nsew")

    def vista_nueva_venta(self):
        if not self.tiene_permiso("crear_ventas"):
            return
        self.prepararPantalla()
        vista = FormularioVenta(self.ventana, **self.navegacion(), guardar=self.insertar_venta_controller)
        vista.grid(row=0, column=0, sticky="nsew")

    def vista_detalle_venta(self, id):
        if not self.tiene_permiso("ver_ventas"):
            return
        venta = ordenTrabajo.consultar_id(id)
        if venta is None:
            dialogo(self.ventana, "No se encontró la venta", "Es posible que la hayan eliminado.")
            return
        self.prepararPantalla()
        vista = FormularioVenta(self.ventana, **self.navegacion(),
                                guardar=lambda datos: self.modificar_venta_controller(venta, datos),
                                venta=venta, cambiar_estado=self.cambiar_estado_controller,
                                asignar_tecnico=self.asignar_tecnico_controller,
                                quitar_tecnico=self.quitar_tecnico_controller,
                                registrar_pago=self.registrar_pago_controller,
                                quitar_pago=self.quitar_pago_controller,
                                agregar_nota=self.agregar_nota_controller,
                                borrar_bitacora=self.borrar_bitacora_controller,
                                imprimir=self.imprimir_venta_controller)
        vista.grid(row=0, column=0, sticky="nsew")

    # ------Vistas Usuarios (solo gestión)-------

    def vista_usuarios(self):
        if not self.tiene_permiso("ver_usuarios"):
            return
        self.prepararPantalla()
        vista = Usuarios(self.ventana, **self.navegacion(),
                         nuevo_usuario=self.cambiar_nuevo_usuario, editar_usuario=self.cambiar_editar_usuario)
        vista.grid(row=0, column=0, sticky="nsew")

    def vista_nuevo_usuario(self):
        if not self.tiene_permiso("editar_usuarios"):
            return
        self.prepararPantalla()
        vista = FormularioUsuario(self.ventana, **self.navegacion(), guardar=self.insertar_usuario_controller)
        vista.grid(row=0, column=0, sticky="nsew")

    def vista_editar_usuario(self, id):
        if not self.tiene_permiso("editar_usuarios"):
            return
        usuario = Trabajadores.consultar_id(id)
        if usuario is None:
            dialogo(self.ventana, "No se encontró el usuario", "Es posible que lo hayan eliminado.")
            return
        self.prepararPantalla()
        vista = FormularioUsuario(self.ventana, **self.navegacion(),
                                  guardar=lambda nombre, usuario_txt, contrasena, rol, especialidad, status:
                                      self.modificar_usuario_controller(id, nombre, usuario_txt, contrasena,
                                                                        rol, especialidad, status),
                                  usuario=usuario, eliminar=self.eliminar_usuario_controller)
        vista.grid(row=0, column=0, sticky="nsew")

    # ------Vista Configuración (todos los roles)-------

    def vista_configuracion(self):
        self.prepararPantalla()
        vista = Configuracion(self.ventana, **self.navegacion(), cambiar_tema=self.cambiar_tema)
        vista.grid(row=0, column=0, sticky="nsew")

# -------------------------------------------------------------------------------------------------------------------------
#                                           Controlador
# -------------------------------------------------------------------------------------------------------------------------

# ------ Controladores Clientes -------

    def insertar_cliente_controller(self, razon, contacto, telefono, email):
        if not self.tiene_permiso("editar_clientes"):
            return
        nuevo = Clientes(razon, contacto, telefono, email)
        respuesta = nuevo.insertar()
        self.respuesta_sql(respuesta, self.cambiar_clientes)

    def modificar_cliente_controller(self, id, razon, contacto, telefono, email):
        if not self.tiene_permiso("editar_clientes"):
            return
        modificado = Clientes(razon, contacto, telefono, email)
        respuesta = modificado.actualizar(id)
        self.respuesta_sql(respuesta, self.cambiar_clientes)
        del modificado

# ------ Controladores Ventas (órdenes) -------

    # Grupo de permiso de cada dato de la venta (ver CAMPOS_VENTA_PARCIAL en permisos.py)
    GRUPOS_VENTA = {"id_cliente": "cliente", "proyecto": "proyecto", "tipo": "proyecto", "fecha": "fecha",
                    "hora": "hora", "calle": "direccion", "numero": "direccion", "colonia": "direccion",
                    "concepto": "concepto", "cantidad": "concepto", "precio_unitario": "concepto",
                    "con_iva": "concepto", "monto": "concepto", "monto_anticipo": "anticipo", "status": "estado"}

    def orden_desde(self, datos, anticipo_pagado, pagos=None, bitacora=None):
        return ordenTrabajo(datos["id_cliente"], datos["tipo"],
                            ordenTrabajo.componer_direccion(datos["calle"], datos["numero"], datos["colonia"]),
                            datos["proyecto"], datos["fecha"], datos["hora"], datos["status"], datos["monto"],
                            anticipo_pagado,
                            concepto=datos["concepto"], cantidad=datos["cantidad"],
                            precioUnitario=datos["precio_unitario"], conIva=datos["con_iva"],
                            montoAnticipo=datos["monto_anticipo"], calle=datos["calle"], numero=datos["numero"],
                            colonia=datos["colonia"], levantadaPor=datos["levantada_por"],
                            pagos=pagos, bitacora=bitacora)

    def insertar_venta_controller(self, datos):
        if not self.tiene_permiso("crear_ventas"):
            return
        if not puede("registrar_pagos"):
            datos["monto_anticipo"] = 0     # el anticipo solo lo registra administración
        if not puede("asignar_tecnicos"):
            datos["id_tecnico"] = None
        if not (datos.get("levantada_por") or "").strip() or datos["monto_anticipo"] > datos["monto"]:
            self.respuesta_sql(False)
            return
        datos["status"] = "pendiente"
        # El anticipo inicial es el primer pago del historial, con su fecha
        pagos = []
        if datos["monto_anticipo"] > 0:
            fecha_pago = datos.get("fecha_anticipo") or datos["fecha"]
            pagos.append({"fecha": fecha_pago.isoformat(), "monto": round(float(datos["monto_anticipo"]), 2),
                          "tipo": "Anticipo", "registro": self.autor(), "nota": ""})
        # Notas iniciales: primera entrada de la bitácora con autor y fecha
        bitacora = ordenTrabajo.entradaBitacora(self.autor(), datos["notas"]) if datos.get("notas") else None
        nueva = self.orden_desde(datos, 1 if pagos else 0, pagos, bitacora)
        if not nueva.crearOrden():
            self.respuesta_sql(False)
            return
        folio = ordenTrabajo.folio(nueva.idOrden, datos["fecha"])
        mensaje = f"Venta {folio} guardada correctamente."
        # Técnico desde el registro (opcional; también se puede asignar después en el detalle)
        if datos.get("id_tecnico"):
            tecnico = Trabajadores.consultar_id(datos["id_tecnico"])
            if tecnico and ordenTrabajo.asignarTecnico(nueva.idOrden, datos["id_tecnico"]):
                mensaje = f"Venta {folio} guardada y asignada a {tecnico[1]}."
            else:
                mensaje = f"Venta {folio} guardada. No se pudo asignar el técnico; asígnalo desde el detalle."
        self.ventana.after(150, lambda: self.vista_ordenes(mensaje))

    def modificar_venta_controller(self, venta, datos):
        if not self.tiene_permiso("editar_ventas_parcial"):
            return
        # Los pagos se manejan aparte (Registrar pago); aquí no se cambian
        datos["monto_anticipo"] = venta["monto_anticipo"]
        # venta = diccionario de ordenTrabajo.consultar_id(); datos = lo que manda el formulario
        if not puede("editar_ventas"):
            # Edición parcial: lo que no está en CAMPOS_VENTA_PARCIAL se queda como estaba en la BD
            for campo, grupo in self.GRUPOS_VENTA.items():
                if grupo not in CAMPOS_VENTA_PARCIAL:
                    datos[campo] = venta[campo]
            if datos["status"] != venta["status"] and datos["status"] in ESTADOS_SOLO_GESTION:
                self.tiene_permiso("editar_ventas")     # muestra el aviso de sin permiso
                return
        # Quién levantó la venta no cambia; solo se puede llenar si estaba vacío
        if venta["levantada_por"]:
            datos["levantada_por"] = venta["levantada_por"]
        if datos["status"] not in ordenTrabajo.statusPermitidos(venta["status"]) \
                or float(datos["monto_anticipo"] or 0) > float(datos["monto"] or 0):
            self.respuesta_sql(False)
            return
        # anticipo_pagado: 1 si dejó anticipo; si no se tocó el anticipo se respeta lo que había
        if float(datos["monto_anticipo"] or 0) == float(venta["monto_anticipo"] or 0):
            anticipo_pagado = venta["anticipo_pagado"]
        else:
            anticipo_pagado = 1 if float(datos["monto_anticipo"]) > 0 else 0
        modificada = self.orden_desde(datos, anticipo_pagado)
        respuesta = modificada.actualizarOrden(venta["id"])
        self.respuesta_sql(respuesta, self.cambiar_ordenes)
        del modificada

    def cambiar_estado_controller(self, id, status):
        if not self.tiene_permiso("editar_ventas_parcial"):
            return
        if status in ESTADOS_SOLO_GESTION and not self.tiene_permiso("editar_ventas"):
            return
        respuesta = ordenTrabajo.cambiarStatus(id, status)
        self.respuesta_sql(respuesta, lambda: self.cambiar_detalle_venta(id))

    def asignar_tecnico_controller(self, id_orden, id_trabajador):
        if not self.tiene_permiso("asignar_tecnicos"):
            return
        respuesta = ordenTrabajo.asignarTecnico(id_orden, id_trabajador)
        self.respuesta_sql(respuesta, lambda: self.cambiar_detalle_venta(id_orden))

    def quitar_tecnico_controller(self, id_orden, id_trabajador):
        if not self.tiene_permiso("asignar_tecnicos"):
            return
        respuesta = ordenTrabajo.quitarTecnico(id_orden, id_trabajador)
        self.respuesta_sql(respuesta, lambda: self.cambiar_detalle_venta(id_orden))

# ------ Controladores Pagos, bitácora e impresión -------

    def registrar_pago_controller(self, id_orden, pago):
        if not self.tiene_permiso("registrar_pagos"):
            return
        pago = dict(pago, registro=self.autor())
        respuesta = ordenTrabajo.agregarPago(id_orden, pago)
        if respuesta:
            # Queda anotado en la bitácora junto con lo que resta
            saldo = ordenTrabajo.estadoDeCuenta(ordenTrabajo.consultar_id(id_orden))["saldo"]
            fecha = datetime.date.fromisoformat(pago["fecha"]).strftime("%d/%m/%Y")
            ordenTrabajo.agregarNota(id_orden, self.autor(),
                                     f"Registró {pago['tipo'].lower()} de {dinero(pago['monto'])} con fecha {fecha}. "
                                     f"Saldo pendiente: {dinero(saldo)}.")
        self.respuesta_sql(respuesta, lambda: self.cambiar_detalle_venta(id_orden))

    def quitar_pago_controller(self, id_orden, indice):
        if not self.tiene_permiso("eliminar_pagos"):
            return
        quitado = ordenTrabajo.quitarPago(id_orden, indice)
        if quitado:
            try:
                fecha = datetime.date.fromisoformat(quitado.get("fecha", "")).strftime("%d/%m/%Y")
            except ValueError:
                fecha = quitado.get("fecha", "")
            ordenTrabajo.agregarNota(id_orden, self.autor(),
                                     f"Quitó el {quitado.get('tipo', 'pago').lower()} de {dinero(quitado['monto'])} "
                                     f"del {fecha}.")
        self.respuesta_sql(quitado is not None, lambda: self.cambiar_detalle_venta(id_orden))

    def agregar_nota_controller(self, id_orden, texto):
        # Regresa la bitácora actualizada (o None si no se pudo) para mostrarla sin recargar la pantalla
        if not self.tiene_permiso("escribir_bitacora") or not texto.strip():
            return None
        if not ordenTrabajo.agregarNota(id_orden, self.autor(), texto):
            self.respuesta_sql(False)
            return None
        return ordenTrabajo.bitacoraDe(id_orden)

    def borrar_bitacora_controller(self, id_orden):
        if not self.tiene_permiso("eliminar_bitacora"):
            return None
        if not ordenTrabajo.borrarBitacora(id_orden, self.autor()):
            self.respuesta_sql(False)
            return None
        return ordenTrabajo.bitacoraDe(id_orden)

    def imprimir_venta_controller(self, id_orden):
        if not self.tiene_permiso("imprimir_ventas"):
            return
        venta = ordenTrabajo.consultar_id(id_orden)
        if venta is None:
            self.respuesta_sql(False)
            return
        try:
            impresion.imprimir_venta(venta, Clientes.consultar_id(venta["id_cliente"]),
                                     ordenTrabajo.tecnicosDeOrden(id_orden), self.autor())
        except Exception as e:
            dialogo(self.ventana, "No se pudo preparar la impresión", str(e))

# ------ Controladores Usuarios (trabajadores) -------

    def crear_primer_admin_controller(self, nombre, usuario, contrasena, rol):
        # Solo funciona mientras NO exista ningún administrador; después ya no se puede usar
        if Trabajadores.hay_administrador() or not puede("editar_usuarios", rol):
            dialogo(self.ventana, "Ya existe un administrador",
                    "Inicia sesión y pide a administración que te dé de alta en Usuarios.",
                    al_cerrar=lambda: self.ventana.after(150, self.vista_inicioSesion))
            return
        if Trabajadores.existeUsuario(usuario):
            self.respuesta_sql(False)
            return
        nuevo = Trabajadores(nombre, usuario, contrasena, rol, None, "activo")
        if not nuevo.insertar():
            self.respuesta_sql(False)
            return
        # Se inicia sesión directo con la cuenta recién creada
        datos = Trabajadores.iniciarSesion(usuario, contrasena)
        sesion.iniciar(datos[0], datos[1], datos[2], datos[3])
        self.ventana.after(150, self.bienvenida_admin)

    def insertar_usuario_controller(self, nombre, usuario, contrasena, rol, especialidad, status):
        if not self.tiene_permiso("editar_usuarios"):
            return
        if not rol_valido(rol) or not contrasena or Trabajadores.existeUsuario(usuario):
            self.respuesta_sql(False)
            return
        nuevo = Trabajadores(nombre, usuario, contrasena, rol, especialidad, status)
        respuesta = nuevo.insertar()
        self.respuesta_sql(respuesta, self.cambiar_usuarios)

    def eliminar_usuario_controller(self, id, contrasena):
        if not self.tiene_permiso("eliminar_usuarios"):
            return
        yo = sesion.actual().get("id")
        if id == yo:
            dialogo(self.ventana, "No puedes eliminar tu propia cuenta",
                    "Pide a otro administrador que lo haga si de verdad hace falta.")
            return
        # Se vuelve a pedir la contraseña de quien tiene la sesión abierta
        if not Trabajadores.verificarContrasena(yo, contrasena):
            dialogo(self.ventana, "Contraseña incorrecta", "No se eliminó al usuario.")
            return
        respuesta = Trabajadores.eliminar(id)
        self.respuesta_sql(respuesta, self.cambiar_usuarios)

    def modificar_usuario_controller(self, id, nombre, usuario, contrasena, rol, especialidad, status):
        if not self.tiene_permiso("editar_usuarios"):
            return
        if not rol_valido(rol) or Trabajadores.existeUsuario(usuario, id):
            self.respuesta_sql(False)
            return
        propio = id == sesion.actual().get("id")
        if propio:
            # Nadie cambia su propio rol ni se desactiva: se conservan los de la BD
            actual = Trabajadores.consultar_id(id)
            rol, status = actual[3], actual[5]
        modificado = Trabajadores(nombre, usuario, contrasena, rol, especialidad, status)
        respuesta = modificado.actualizar(id)
        if respuesta and propio:
            sesion.actualizar(nombre=nombre, usuario=usuario)
        self.respuesta_sql(respuesta, self.cambiar_usuarios)
        del modificado

if __name__ == "__main__":
    if sys.platform.startswith("win"):
        # Le dice a Windows que Eclipcom es su propia app: así la barra de tareas
        # muestra el ícono de la "E" y no el de Python
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Eclipcom.GestionComercial")
        except Exception as e:
            print(f"No se pudo registrar el ícono en la barra de tareas: {e}")
    ventana = ctk.CTk()
    poner_icono(ventana)
    app = App(ventana)
    ventana.mainloop()
