import base64
import datetime
import html
import tempfile
import webbrowser
from pathlib import Path

from views.estilos import dinero, telefono_txt
from ordenes.ordenes import ordenTrabajo

# Hoja para imprimir el detalle de una venta. Se genera un archivo HTML y se abre en el navegador,
# que muestra el cuadro de impresión (ahí también se puede elegir "Guardar como PDF").
# No necesita instalar nada extra.

RECURSOS = Path(__file__).resolve().parent.parent / "recursos"
LOGO_EMPRESA = RECURSOS / "logo_eclipse.png"     # Eclipse Comunicaciones (encabezado)
LOGO_APP = RECURSOS / "eclipcom.png"             # Eclipcom (pie de página, más pequeño)
ESTADOS = {"pendiente": "Pendiente", "asignada": "Asignada", "en_proceso": "En proceso",
           "concluida": "Concluida", "cancelada": "Cancelada"}
TIPOS = {"instalacion": "Instalación", "mantenimiento": "Mantenimiento"}

ESTILO = """
@page { size: letter; margin: 14mm; }
* { box-sizing: border-box; }
body { font-family: "Segoe UI", Inter, Arial, sans-serif; color: #1E2A3B; font-size: 10.5pt; margin: 0; }
.barra { background: #F3F7FC; padding: 10px; text-align: right; border-bottom: 1px solid #DCE3EE; }
.barra button { background: #0B4FB3; color: #fff; border: 0; border-radius: 6px; padding: 8px 18px;
                font-size: 11pt; cursor: pointer; }
.hoja { max-width: 820px; margin: 0 auto; padding: 18px; }
header { display: flex; justify-content: space-between; align-items: center;
         border-bottom: 3px solid #012F6B; padding-bottom: 10px; }
.empresa img { height: 66px; display: block; }
.empresa b { font-size: 20pt; color: #000; }
.folio { text-align: right; }
.folio h1 { margin: 0; font-size: 15pt; color: #012F6B; }
.folio span { color: #5F6F86; font-size: 9.5pt; }
h2 { font-size: 11.5pt; color: #012F6B; border-bottom: 1px solid #DCE3EE; padding-bottom: 3px; margin: 18px 0 8px; }
.datos { display: grid; grid-template-columns: 1fr 1fr; gap: 5px 28px; }
.datos div { display: grid; grid-template-columns: 130px 1fr; gap: 8px; }
.datos div span { color: #5F6F86; }
table { width: 100%; border-collapse: collapse; }
th { background: #012F6B; color: #fff; text-align: left; padding: 6px 8px; font-size: 9.5pt; }
td { padding: 6px 8px; border-bottom: 1px solid #DCE3EE; font-size: 9.5pt; vertical-align: top; }
.num { text-align: right; white-space: nowrap; }
.totales { width: 46%; margin: 8px 0 0 auto; }
.totales td { border: 0; padding: 3px 8px; }
.fuerte td { font-weight: 700; font-size: 11pt; border-top: 1px solid #1E2A3B; }
.bitacora { white-space: pre-wrap; border: 1px solid #DCE3EE; border-radius: 6px; padding: 10px;
            font-size: 9.5pt; line-height: 1.4; }
.vacio { color: #5F6F86; font-style: italic; }
.firmas { display: flex; gap: 48px; margin-top: 56px; }
.firmas div { flex: 1; border-top: 1px solid #1E2A3B; text-align: center; padding-top: 4px; font-size: 9pt; }
footer { margin-top: 24px; color: #5F6F86; font-size: 8.5pt; display: flex; align-items: center;
         justify-content: center; gap: 6px; }
footer img { width: 16px; height: 16px; }
footer b { color: #012F6B; }
th, header, .barra button { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
@media print { .barra { display: none; } .hoja { padding: 0; } }
"""


def _e(texto):
    return html.escape(str(texto if texto is not None else ""))


def _fecha(valor):
    if isinstance(valor, datetime.date):
        return valor.strftime("%d/%m/%Y")
    try:
        return datetime.date.fromisoformat(str(valor)).strftime("%d/%m/%Y")
    except ValueError:
        return str(valor or "—")


def _imagen(ruta):
    # Imagen incrustada en la hoja (así funciona aunque se mueva el archivo)
    return f"data:image/png;base64,{base64.b64encode(ruta.read_bytes()).decode()}"


def _hora(valor):
    if isinstance(valor, datetime.timedelta):
        minutos = int(valor.total_seconds()) // 60
        return f"{minutos // 60:02d}:{minutos % 60:02d}"
    return str(valor)[:5] if valor else "—"


def generar_html(venta, cliente, tecnicos, impreso_por):
    # venta = diccionario de ordenTrabajo.consultar_id(); cliente = tupla de Clientes.consultar_id()
    folio = ordenTrabajo.folio(venta["id"], venta["fecha"])
    desglose = ordenTrabajo.desglose(venta)
    cuenta = ordenTrabajo.estadoDeCuenta(venta)
    if LOGO_EMPRESA.exists():
        logo_empresa = f'<img src="{_imagen(LOGO_EMPRESA)}" alt="Eclipse Comunicaciones">'
    else:
        logo_empresa = "<b>Eclipse Comunicaciones</b>"
    logo_app = f'<img src="{_imagen(LOGO_APP)}" alt="E">' if LOGO_APP.exists() else ""

    if cliente:
        id_cliente, empresa, contacto, telefono, email = cliente
        cliente_html = (f"<div><span>Cliente</span>{_e(contacto)}</div><div><span>Empresa</span>{_e(empresa or '—')}</div>"
                        f"<div><span>Correo</span>{_e(email or '—')}</div><div><span>Teléfono</span>{_e(telefono_txt(telefono))}</div>")
    else:
        cliente_html = f"<div><span>Cliente</span>#{_e(venta['id_cliente'])}</div>"

    direccion = ordenTrabajo.componer_direccion(venta["calle"], venta["numero"], venta["colonia"]) or venta["direccion"]
    tecnicos_txt = ", ".join(f"{nombre}{f' ({esp})' if esp else ''}" for _, nombre, esp in tecnicos) or "Sin asignar"

    iva_txt = dinero(desglose["iva"]) if desglose["con_iva"] else "No aplica"
    filas_pagos = f"<tr><td>{_fecha(venta['fecha'])}</td><td>Precio inicial</td><td class='num'></td><td></td><td></td><td class='num'>{dinero(cuenta['total'])}</td></tr>"
    for mov in cuenta["movimientos"]:
        filas_pagos += (f"<tr><td>{_fecha(mov.get('fecha'))}</td><td>{_e(mov.get('tipo', 'Pago'))}</td>"
                        f"<td class='num'>- {dinero(mov['monto'])}</td><td>{_e(mov.get('registro', ''))}</td>"
                        f"<td>{_e(mov.get('nota', ''))}</td><td class='num'>{dinero(mov['saldo'])}</td></tr>")

    bitacora = (venta["bitacora"] or "").strip()
    bitacora_html = (f"<div class='bitacora'>{_e(bitacora)}</div>" if bitacora
                     else "<div class='bitacora vacio'>Sin notas en la bitácora.</div>")

    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"><title>{folio} · Eclipcom</title><style>{ESTILO}</style></head>
<body>
<div class="barra"><button onclick="window.print()">🖨 Imprimir</button></div>
<div class="hoja">
<header>
  <div class="empresa">{logo_empresa}</div>
  <div class="folio"><h1>Venta {folio}</h1><span>Estado: {_e(ESTADOS.get(venta['status'], venta['status']))}</span></div>
</header>

<h2>Datos de la venta</h2>
<div class="datos">
  {cliente_html}
  <div><span>Proyecto</span>{_e(venta['proyecto'])}</div><div><span>Tipo de servicio</span>{_e(TIPOS.get(venta['tipo'], venta['tipo']))}</div>
  <div><span>Fecha de venta</span>{_fecha(venta['fecha'])}</div><div><span>Hora de inicio</span>{_hora(venta['hora'])}</div>
  <div><span>Dirección del sitio</span>{_e(direccion or '—')}</div><div><span>Levantada por</span>{_e(venta['levantada_por'] or '—')}</div>
  <div><span>Técnicos</span>{_e(tecnicos_txt)}</div>
</div>

<h2>Concepto</h2>
<table>
  <tr><th>Concepto</th><th class="num">Cantidad</th><th class="num">Precio unitario</th><th class="num">Importe</th></tr>
  <tr><td>{_e(desglose['concepto'])}</td><td class="num">{desglose['cantidad']}</td>
      <td class="num">{dinero(desglose['precio'])}</td><td class="num">{dinero(desglose['subtotal'])}</td></tr>
</table>
<table class="totales">
  <tr><td>Subtotal</td><td class="num">{dinero(desglose['subtotal'])}</td></tr>
  <tr><td>IVA (16 %)</td><td class="num">{iva_txt}</td></tr>
  <tr class="fuerte"><td>Total</td><td class="num">{dinero(desglose['total'])}</td></tr>
</table>

<h2>Pagos y saldo</h2>
<table>
  <tr><th>Fecha</th><th>Movimiento</th><th class="num">Monto</th><th>Registró</th><th>Nota</th><th class="num">Saldo restante</th></tr>
  {filas_pagos}
</table>
<table class="totales">
  <tr><td>Pagado</td><td class="num">{dinero(cuenta['pagado'])}</td></tr>
  <tr class="fuerte"><td>Saldo pendiente</td><td class="num">{dinero(cuenta['saldo'])}</td></tr>
</table>

<h2>Bitácora</h2>
{bitacora_html}

<div class="firmas"><div>Firma del cliente</div><div>Firma de quien entrega</div></div>
<footer>{logo_app}<b>eclipcom</b> · Impreso el {datetime.datetime.now():%d/%m/%Y a las %H:%M} por {_e(impreso_por)}</footer>
</div>
<script>window.addEventListener("load", function () {{ setTimeout(function () {{ window.print(); }}, 400); }});</script>
</body></html>"""


def imprimir_venta(venta, cliente, tecnicos, impreso_por):
    # Guarda la hoja en la carpeta temporal y la abre en el navegador. Regresa la ruta del archivo
    carpeta = Path(tempfile.gettempdir()) / "Eclipcom"
    carpeta.mkdir(parents=True, exist_ok=True)
    archivo = carpeta / f"{ordenTrabajo.folio(venta['id'], venta['fecha'])}.html"
    archivo.write_text(generar_html(venta, cliente, tecnicos, impreso_por), encoding="utf-8")
    webbrowser.open(archivo.resolve().as_uri())
    return archivo
