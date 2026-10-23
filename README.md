<p align="center">
  <img src="docs/img/bricohams_logo.png" alt="Bricohams" width="420">
</p>

# Mango SpaceQuad con trípode, soporte de walki por clip y duplexor

Mango imprimible en 3D para la antena de satélites **BIG SIGNAL SpaceQuad** (VHF/UHF, boom cuadrado de 15 mm).
Se puede llevar en la mano o montar en un trípode de fotografía. Lleva una **lengüeta para el clip de cinturón del walki**
y una funda para el duplexor.

<p align="center">
  <img src="docs/img/vista_uso.png" alt="Conjunto en posición de uso" width="90%">
</p>

## Novedades de la v3

- **Soporte de walki integrado en el mango**: una lengüeta en el lateral de la torre donde se engancha el **clip de cinturón**
  del propio walki, como si fuera un cinturón. Es una sola pieza, sin tornillos ni mordazas.
  El walki cuelga por el lateral, a casi 3 cm del duplexor, así que ya no choca con él.
- **Rosca del trípode corregida**: la tuerca 1/4"-20 queda a **1,2 mm** de la cara del culo (antes a 3 mm).
  Los tornillos de las placas rápidas son cortos (5–6 mm) y antes apenas cogían rosca.
- Se retira la base GoPro de la v2, con su adaptador y sus mordazas. Están en `legacy/soporte_gopro/`.

<p align="center">
  <img src="docs/img/mango_detalles.png" alt="Detalle de la lengüeta" width="70%">
</p>

## Características

- **Encaja en el boom de la SpaceQuad**: túnel de 15,5 × 15,5 mm para el boom cuadrado de 15 mm (0,5 mm de holgura).
- **Rosca de trípode en el culo de la empuñadura**: tuerca 1/4"-20 embutida en una base plana de 52 × 31 mm.
  La empuñadura queda hacia abajo y el boom horizontal, igual que al llevarla en la mano.
- **Lengüeta para el clip**: 4 mm de grosor y 70 mm de largo. Funda con hueco en cuña (de 4 mm abajo a 9 mm en la boca)
  y paredes laterales que dejan **42 mm** de ancho para la lengua del clip. Tiene una ventana para el saliente del clip.
- **Funda para el duplexor** VHF/UHF entre la torre y el boom: 16 × 32 mm por dentro, 48 mm de largo, abierta por los extremos.
- **Paramétrico**: todo se genera con scripts de Python (trimesh + manifold3d), así que las medidas se pueden adaptar.

## Contenido del repositorio

```
stl/    Piezas listas para imprimir (ya orientadas)
  mango_spacequad_v3.stl         Mango v3 (lengüeta para el clip + funda duplexor + base de trípode)
  mango_spacequad_tripode.stl    Mango v1 (se conserva: es la entrada de mango_v3.py)
src/    Scripts paramétricos que generan las piezas
docs/   Imágenes, montaje y lista de materiales
legacy/ Pinza del móvil (v1) y soporte GoPro con mordazas (v2), ya no se usan
```

## Materiales

Lista completa en [docs/MATERIALES.md](docs/MATERIALES.md). En resumen:

| Cantidad | Pieza |
|---|---|
| 1 | Tuerca hexagonal 1/4"-20 UNC (11,1 mm entre caras) para el trípode (opcional) |

El walki se sujeta con su propio clip de cinturón: no hace falta tornillería.

## Impresión

| Pieza | Material | Orientación | Soportes |
|---|---|---|---|
| Mango v3 | PETG o ASA (exterior, al sol) | La del STL | Sí, desde la cama (bajo la empuñadura, la torre y la lengüeta) |

0,2 mm de capa, 4 perímetros y 30–40 % de relleno. La lengüeta conviene que salga casi maciza (4 perímetros la llenan).
Limpia bien los soportes del interior de la funda del clip.

## Montaje

Pasos detallados en [docs/MONTAJE.md](docs/MONTAJE.md).

1. Mete la tuerca 1/4"-20 por su ranura del culo de la empuñadura.
2. Pasa el boom de la SpaceQuad por el túnel del mango y mete el duplexor en su funda.
3. Engancha el walki: mete su clip de cinturón por arriba, entre la lengüeta y la torre, y empújalo hasta el fondo.

## Compatibilidad del clip

| Dato | Valor |
|---|---|
| Ancho de la lengua del clip | hasta 42 mm |
| Largo de la lengua | hasta 65 mm |
| Abertura del clip | al menos 4 mm (lo que mide la lengüeta) |

Sirve para los clips de la mayoría de walkis (Baofeng, Yaesu, Kenwood, AnyTone, Retevis…). Las medidas se cambian en `src/mango_v3.py`.

## Regenerar las piezas

```bash
pip install -r src/requirements.txt
cd src
python mango_v3.py ../stl/mango_spacequad_tripode.stl ../stl/mango_spacequad_v3.stl
python verificar.py ../stl/mango_spacequad_v3.stl      # pieza estanca, choques, hueco del clip y tuerca del trípode
python render_docs.py ../stl ../docs/img                # imágenes
```

`mango_v3.py` parte del STL v1 incluido en el repositorio. `build_mango.py` (v1) parte del **STL original del mango**,
que no está incluido (ver *Créditos*) y necesita además `cadquery`.
Las medidas se cambian en la sección `PARAMETROS` de cada script.

## Estado

Diseño verificado en el ordenador: pieza estanca, walkis de 50, 62 y 70 mm sin tocar el mango ni el duplexor
(28,6 mm de separación) y 0 mm³ añadidos sobre el duplexor respecto a la v1.
**Aún sin probar impresa**: si algún ajuste no encaja, se abre un issue o se toca el parámetro correspondiente.

## Créditos y licencia

- Mango original de la SpaceQuad: **[AUTOR ORIGINAL — completar con nombre y enlace]**.
  Este proyecto es una modificación de su diseño y respeta su licencia original.
- Modificaciones, soporte de walki y scripts: **Bricohams**.
- BIG SIGNAL y SpaceQuad son marcas de sus respectivos propietarios. Este proyecto no está afiliado a ellos.

Licencia: [CC BY-SA 4.0](LICENSE) para los modelos y la documentación. Los scripts de `src/` también se
publican bajo CC BY-SA 4.0. Si la licencia del diseño original es distinta, **manda la del original**.

73 y buenas pasadas.
