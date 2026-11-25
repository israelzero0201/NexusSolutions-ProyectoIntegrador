-- Eclipcom versión 5: bitácora e historial de pagos en ordenes_info.
-- NO hace falta correr este archivo: el programa las agrega solo al abrirse (migraciones.py).
-- Se guardan como columnas (y no como tablas nuevas) para respetar el límite de 3 tablas del proyecto.

ALTER TABLE ordenes_info
  ADD COLUMN pagos    TEXT     NULL,   -- lista JSON: [{"fecha","monto","tipo","registro","nota"}, ...]
  ADD COLUMN bitacora LONGTEXT NULL;  -- notas con autor y fecha: "── 24/11/2026 10:26 · Nombre (Rol) ──"

-- monto_anticipo sigue guardando la suma de los pagos y anticipo_pagado queda en 1 si hay al menos uno.
