# Versión 5.1 (Alpha 0.6.1)

- **Hoja de impresión**: el encabezado ahora lleva el logo real de **Eclipse Comunicaciones** (`recursos/logo_eclipse.png`). El logo de Eclipcom no se quitó: pasó al pie de página, más pequeño, junto a "Impreso el … por …".
- **Configuración**: nuevo tema de color **Eclipse** con los colores del logo de la empresa: menú lateral y encabezado negros, botones rojos (#E30A17) y enlaces azules (#08009F). Funciona en modo Claro y Oscuro.

---

# Versión 5 (Alpha 0.6)

## Base de datos (se actualiza sola al abrir)
Se agregan dos columnas a `ordenes_info`. Para respetar el límite de 3 tablas no se crean tablas nuevas (ver `sql/actualizacion_v5.sql`):
- `bitacora` (LONGTEXT): todas las notas en un solo bloque. Cada nota lleva `── fecha hora · Nombre (Rol) ──`.
- `pagos` (TEXT con una lista JSON): cada anticipo o abono con fecha, monto, tipo, quién lo registró y una nota. `monto_anticipo` sigue guardando la suma.

> Si el profe permitiera una tabla más, lo "de libro" sería una tabla `pagos` aparte. Con el límite de 3 tablas, esta es la forma de guardarlo.

## Ventas
- **Bitácora** (nueva venta y detalle): bloque grande para avances, material pedido, problemas y pendientes.
  - Cualquier rol puede escribir. Cada nota queda con su nombre, fecha y hora, y aparece al instante.
  - Solo **Ingeniero y Dueño** pueden *Eliminar bitácora*; queda anotado quién la eliminó y cuándo.
- **Pagos y saldo** (detalle): precio inicial y cada anticipo/abono con su fecha, quién lo registró, la nota y **lo que resta después de cada pago**.
  - *Registrar pago*: tipo Anticipo, Abono o Liquidación (Liquidación llena sola lo que falta). No deja pagar más que el saldo.
  - Cada pago se anota también en la bitácora.
  - Registran pagos: Ingeniero, Administrativo y Dueño. Quitar un pago: solo Ingeniero y Dueño.
  - Al editar el concepto, el total no puede quedar por debajo de lo ya pagado.
- **Nueva venta**: *Anticipo inicial* con su fecha (se vuelve el primer pago) y *Notas iniciales* (primera entrada de la bitácora).
- **Imprimir** (detalle, todos los roles): abre una hoja en el navegador con los datos, el concepto, los totales, los pagos con su saldo, la bitácora y las líneas de firma. Ahí mismo se puede elegir "Guardar como PDF". No hay que instalar nada.

## Permisos
- **Administrativo**: ya **no** puede eliminar usuarios (tampoco pagos ni la bitácora). Todo lo demás queda igual.
- **Técnico**: ahora ve el módulo **Clientes en solo lectura** (sin *Nuevo cliente* ni *Guardar*), con las ventas de cada cliente, y escribe en la bitácora.

## Archivos nuevos
`views/impresion.py`, `sql/actualizacion_v5.sql`

---

# Versión 4 (Alpha 0.5)

## Base de datos: se actualiza sola
Al abrir el programa, `migraciones.py` revisa `ordenes_info` y agrega **solo las columnas que falten**. No borra ni cambia nada de lo que ya existe, y siguen siendo las mismas tablas. Así nadie del equipo tiene que entrar a phpMyAdmin. El mismo cambio está en `sql/actualizacion_v4.sql`, por si lo necesitas para la documentación o el diagrama.

| Columna nueva | Para qué |
|---|---|
| `concepto` | Concepto de venta escrito a mano |
| `cantidad`, `precio_unitario` | Se guardan tal cual se capturan |
| `con_iva` | 1 = el total lleva 16 % de IVA, 0 = sin IVA |
| `monto_anticipo` | Cuánto dejó el cliente (`anticipo_pagado` queda en 1 si es mayor a 0) |
| `calle`, `numero`, `colonia` | Dirección separada (`direccion_sitio` se sigue llenando con la dirección completa) |
| `levantada_por` | Quién llenó el formulario de la venta (obligatorio al registrar) |

Las ventas que ya existían se siguen viendo igual. Su dirección aparece completa en *Calle* y su concepto es el tipo de servicio.

## Ventas
- **Concepto libre**: lo que quieras escribir. El tipo de servicio (Instalación/Mantenimiento) pasó a *Datos de la venta*.
- **Con IVA / Sin IVA**: botón junto a los totales; el usuario elige.
- **Anticipo en pesos**: muestra *Anticipo* y *Saldo pendiente*, y no deja capturar más que el total. Solo administración lo registra.
- **Calle, Número y Colonia** por separado.
- **Levantada por \***: obligatorio. Se propone el nombre de quien tiene la sesión abierta y se puede cambiar. Ya registrado no se modifica, y en el detalle aparece como "Registrada por …".
- **Técnico al registrar** (opcional): en *Nueva venta* se puede elegir el técnico. Si no, se asigna después desde el detalle, como antes.

## Usuarios
- **Eliminar usuario** (botón rojo en *Editar usuario*): pide **tu contraseña** para confirmar. Si te equivocas, el diálogo sigue abierto y no borra nada. Quita al usuario de sus ventas, y las que se quedan sin técnico vuelven a Pendiente. Nadie puede eliminarse a sí mismo.

## Configuración (menú lateral, todos los roles)
- **Modo** Claro / Oscuro y **color principal**: Azul Eclipcom, Verde, Morado, Vino o Grafito. Se aplica al instante, se guarda en `config.json` y tiene botón *Restablecer*.

## Ícono
- La ventana, los diálogos y la **barra de tareas de Windows** muestran la "E" de Eclipcom (`recursos/eclipcom.ico`) en lugar del logo de Python.

---

# Versión 3.1 (Alpha 0.4.1): configuración inicial

- Si en la BD no hay ningún usuario **activo** con rol Ingeniero, Administrativo o Dueño, al abrir el programa aparece la pantalla **"Bienvenido a Eclipcom"** en lugar del login. Ahí se crea la primera cuenta con acceso completo, sin tocar phpMyAdmin.
- Al crearla, la sesión se inicia sola y el programa ofrece ir directo a **Usuarios** para dar de alta al resto del equipo.
- Esa pantalla solo existe mientras no haya administrador. Cuando ya hay uno, deja de aparecer, y el controlador también rechaza crear otro por esa vía.
- Si ya había técnicos registrados, pueden entrar desde el enlace **"Iniciar sesión"** de esa pantalla.
- Archivo nuevo: `views/configuracionInicial.py`. La validación de usuario y contraseña ahora es una sola función (`validar_campos_usuario` en `views/formularioUsuario.py`), que usan las dos pantallas.

---

# Versión 3 (Alpha 0.4): acceso por niveles

No hay que cambiar nada en la base de datos. Se usan las mismas tablas y la columna `rol` de `trabajadores`.

## Quién puede hacer qué
| Acción | Técnico | Ingeniero / Administrativo / Dueño (ejecutivo) |
|---|---|---|
| Ver ventas, sus datos y a quién están asignadas | ✓ | ✓ |
| Registrar ventas nuevas | ✓ (sin anticipo) | ✓ |
| Modificar una venta | Solo dirección, fecha, hora y estado (no puede cancelar) | Todo |
| Asignar y quitar técnicos | ✗ | ✓ |
| Clientes | ✗ (no ve el módulo) | ✓ |
| Usuarios (alta, edición, activar/desactivar) | ✗ (no ve el módulo) | ✓ |

Todo esto se configura en **`configuraciones/permisos.py`**. Por ejemplo, para que el técnico también pueda cambiar el nombre del proyecto, agrega `"proyecto"` a `CAMPOS_VENTA_PARCIAL`.

## Cómo se protege
- **En la vista**: el menú lateral y el menú principal solo muestran los módulos permitidos, y los campos que no puedes cambiar aparecen en gris.
- **En el controlador** (`main.py`): cada acción vuelve a revisar el permiso. Si un técnico manda un cambio de cliente, proyecto o monto, se ignora y se conserva lo que estaba en la BD.
- **Sesión**: el rol vive en memoria y se lee de la BD. El archivo de "Recordarme" solo guarda id y usuario, así que editar `sesion.json` no sube de nivel. Si desactivan al usuario, su sesión recordada deja de funcionar.
- Nadie puede cambiar su propio rol ni desactivarse, para que no se quede sin acceso.

## Nuevo
- Módulo **Usuarios**: lista con buscador y filtro por rol, alta y edición. Valida usuario repetido o con espacios, contraseña de mínimo 4 caracteres y la confirmación. Al editar, si la contraseña se deja vacía se conserva la actual.
- **Detalle de venta**: tarjeta "Técnicos asignados" con *Asignar técnico* y *Quitar*. Al asignar, una venta Pendiente pasa a Asignada. Si se quita el último técnico, vuelve a Pendiente.
- **Ventas**: columna *Técnico* y búsqueda por técnico.
- **Formulario de venta**: campos *Hora de inicio* (hh:mm) y *Anticipo pagado*.
- **Menú principal y Guía rápida**: muestran tu rol y lo que puedes hacer.
- Archivos nuevos: `configuraciones/permisos.py`, `views/usuarios.py`, `views/formularioUsuario.py`.

---

# Versión 2: pantallas de los mockups y correcciones

## Errores corregidos
- **trabajadores.py**: usaba `cursor.commit()`, pero `commit()` es de la conexión. Ahora usa `conexion.commit()`, así que guardar, editar o borrar trabajadores ya funciona.
- **menuPrincipal.py / modelos**: `cantidad_ventas()` y `cantidad_clientes()` regresaban `0` cuando había un error y luego se hacía `[0]`, lo que tronaba. Ahora regresan directamente un número.
- **ordenes.py**: si una orden tenía 2 técnicos, salía repetida en Ventas. Ahora los técnicos se juntan en un solo texto.
- **cliente.py**: `select *` e `insert ... values(null, ...)` dependían del orden de las columnas. Ahora se nombran las columnas.
- **sesion.py**: `borrar()` tronaba si no existía `APPDATA`. Ahora usa la misma ruta que `guardar()`.
- **main.py**: las vistas viejas llamaban métodos que no existen (`menu_acciones`, `menu_clientes`, `menu_ordenes`) y mezclaban `pack` con `grid` en la misma ventana, lo cual Tk no permite. Se quitaron y las reemplazan las pantallas nuevas.
- **main.py**: `cerrar()` tronaba si no había conexión. Ahora, si no hay base de datos al iniciar, aparece un mensaje claro.
- **conexion.py**: sin `autocommit`, los SELECT podían mostrar datos viejos. Se activó, y `asignarTecnico` usa una transacción explícita.
- **estilos.py**: se quitaron los `print("menu")` de depuración del sidebar, la función `app_header` (estaba duplicada) y la ventana Tk temporal que se creaba solo para medir la pantalla.
- **ventas.py**: el título decía "Menú principal" y el botón "Nueva venta" no hacía nada.

## Pantallas según los mockups
| Mockup | Archivo |
|---|---|
| 01 Inicio de sesión + Error (intentos, Recordarme, ¿Olvidaste tu contraseña?) | `views/inicioSesion.py` |
| 02 V2 Menú principal | `views/menuPrincipal.py` |
| 03 Ventas + Venta guardada + Confirmar salida | `views/ventas.py` |
| 04 V2 Nueva venta + Guía rápida + Tooltip IVA | `views/formularioVenta.py` |
| 05 V2 Detalle de venta + Tooltip Estado | `views/formularioVenta.py` |
| 06 Clientes | `views/clientes.py` |
| 07 V3 Nuevo cliente (mensajes de error) | `views/formularioCliente.py` |
| 08 Editar cliente + confirmación + éxito | `views/formularioCliente.py` |

Los componentes nuevos (diálogos, tooltip, campos con error, botón con borde, etc.) están en `views/estilos.py`.

## Decisiones para respetar la base de datos actual
- **Cliente**: Nombre(s) + Apellidos se guardan juntos en `persona_contacto`, y Empresa en `razon_social`. Al editar, las 2 últimas palabras se toman como apellidos. RFC, Dirección y Ciudad no se incluyen porque no hay columnas para ellos.
- **Venta**: tiene un concepto, que es el tipo de servicio (Instalación/Mantenimiento). `monto_total` guarda el total con IVA (16 %). Al abrir el detalle, el concepto se muestra como 1 × subtotal.
- **Dirección del sitio** se agregó a la venta porque `ordenes_info` la tiene.
- **Estado**: solo se puede pasar a *Concluida* si la venta está asignada o en proceso, y una venta concluida o cancelada ya no cambia de estado.
- **Recordarme**: si no se marca, la sesión se borra al cerrar el programa.
