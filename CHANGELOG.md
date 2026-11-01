# Cambios

**Ayuda:** [guía del proyecto](docs/AYUDA.md) · [README](README.md) · [montaje](docs/MONTAJE.md) · [materiales](docs/MATERIALES.md).

## Ayuda, CLI e imágenes — 2026-11-01
- Índice de ayuda en español, navegación cruzada y opciones `-h`/`--help` sin dependencias CAD.
- Renders explicativos del STL v3 actual: conjunto estimado, acceso al duplexor y detalle de placa/cartelas; sin cambios de STL ni de resultados CAD.

## Revisión de placa baja v3 — 2026-11-01
- Sustituye la funda vertical por placa de 55 × 48 × 4 mm a 20°, 47 mm libres, recorrido de 40 mm, espacio de 7 mm y ventana opcional de 22 × 6 mm.
- Dos cartelas de 4 mm con pies V140..154 a H54, embebidos 4,64 mm en la torre existente; bajos abiertos, sin losa.
- Conserva empuñadura, boom y trípode. Verificación contra 35019cc, pies finitos y barridos continuos de clip y radio+clip.
- Corredores V del duplexor sin obstrucción nueva; colisión nominal heredada de v1 (462,2388 mm³) documentada, no ocultada.
- Renders CAD y resultados JSON actualizados. Dimensiones de clip/radio estimadas; sin prueba física ni certificación estructural.

## v3.1.0 — 2026-11-01 (diseño histórico, sustituido)
- En esa revisión se restaura la v3 (c77de14) como modelo activo: lengüeta del clip en la torre y tuerca única de trípode a 1,2 mm (ranura de 5,9 mm; rosca limitada por la tuerca real, 5,6 mm nominal).
- La descripción de esta versión (boca 50 mm, fondo 47 mm, 70 mm útiles y paredes en cuña) corresponde al diseño anterior; no describe el STL actual. La revisión vigente, arriba, usa una placa de 55 × 48 × 4 mm a 20°, 47 mm libres, 40 mm de inserción y dos cartelas.
  Dimensiones del clip (25–45 × 6 mm) estimadas, no verificadas; solo se conoce la separación de 26 mm entre tornillos del clip Retevis/TYT MD-380 (https://www.retevis.com/products/belt-clip-for-tyt-tytera-md-380-retevis-rt3-radio).
- La v4 (canal en V, dos tuercas) se archiva en legacy/mango_v4/.
- El verificador de aquel snapshot comparaba contra git c77de14; el script vigente compara contra 35019cc.
- Nueva imagen docs/img/clip_detalle.png.

## v4.0.0 — 2026-11-01 (diseño histórico, archivado)
- Canal universal en V para el clip del walki en la cara superior de la empuñadura (lenguas de 25 a 45 mm y hasta 6 mm de grosor).
  Labios en cola de milano a 45° (sin soportes); la lengua baja por la V hasta acuñarse. Sustituye a la lengüeta de la torre de la v3.
- Ranura del trípode para dos tuercas 1/4"-20 apiladas (rosca a 1,2 mm de la cara; 8,8 mm de rosca con un tornillo de 10 mm).
- `mango_v3.py` pasa a `mango_v4.py`; `verificar.py` comprueba el canal, los voladizos nuevos y la rosca del trípode.

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
