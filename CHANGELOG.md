# Cambios

## v3.0.0 — 2026-10-23
- Soporte de walki integrado: lengüeta para el clip de cinturón en el lateral de la torre (una sola pieza, sin tornillos).
  El walki queda a 28,6 mm del duplexor.
- Tuerca 1/4"-20 del trípode a 1,2 mm de la cara del culo (antes 3 mm): los tornillos cortos de las placas rápidas ya cogen rosca.
- Se retira la base GoPro con su adaptador y sus mordazas (movidos a `legacy/soporte_gopro/`; `soporte_walki.py` necesita el `mango_v2.py` de la v2.0.0).
- `mango_v2.py` pasa a `mango_v3.py`; `verificar.py` y `render_docs.py` se rehacen para la v3.

## v2.0.0 — 2026-10-11
- Soporte de walki nuevo con enganche tipo GoPro (base de 3 dedos en la cara libre de la torre). Ya no choca con el duplexor.
- Soporte **universal**: mordazas ajustables de 50 a 86 mm de ancho y hasta 54 mm de grosor.
- Se retira la función del móvil (rosca lateral 1/4" rellenada; pinza movida a `legacy/`).
- Nuevos scripts: `mango_v2.py`, `soporte_walki.py`, `verificar.py`, `render_docs.py`.
- Imágenes de la documentación actualizadas.

## v1.0.0 — 2026-09-30
- Mango nivelado sobre el eje del boom (el STL original estaba girado ~1°).
- Base plana en el culo de la empuñadura con tuerca 1/4"-20 para trípode.
- Dos roscas 1/4"-20 en la torre para brazos de rótula (walki arriba, móvil en el lateral).
- Funda para duplexor VHF/UHF entre la torre y el boom.
- Pinza de móvil imprimible (58–92 mm) con tuerca 1/4"-20.
- Scripts paramétricos de generación (`src/`).
