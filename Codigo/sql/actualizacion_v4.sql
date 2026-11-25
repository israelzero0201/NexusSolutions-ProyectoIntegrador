-- Eclipcom versión 4: columnas nuevas en ordenes_info.
-- NO hace falta correr este archivo: el programa las agrega solo al abrirse (migraciones.py).
-- Se deja como referencia para la documentación y el diagrama de clases.

ALTER TABLE ordenes_info
  ADD COLUMN concepto        VARCHAR(150)  NULL,                 -- concepto de venta escrito a mano
  ADD COLUMN cantidad        INT           NOT NULL DEFAULT 1,
  ADD COLUMN precio_unitario DECIMAL(10,2) NULL,
  ADD COLUMN con_iva         TINYINT(1)    NOT NULL DEFAULT 1,   -- 1 = total con 16 % de IVA, 0 = sin IVA
  ADD COLUMN monto_anticipo  DECIMAL(10,2) NOT NULL DEFAULT 0,   -- cuánto dejó el cliente de anticipo
  ADD COLUMN calle           VARCHAR(120)  NULL,
  ADD COLUMN numero          VARCHAR(20)   NULL,
  ADD COLUMN colonia         VARCHAR(80)   NULL,
  ADD COLUMN levantada_por   VARCHAR(100)  NULL;                 -- quién llenó el formulario de la venta

-- direccion_sitio se sigue llenando con la dirección completa ("Calle #número, Col. colonia")
-- y anticipo_pagado queda en 1 cuando monto_anticipo > 0, para que lo anterior siga funcionando.
