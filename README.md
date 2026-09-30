<p align="center">
  <img src="docs/img/bricohams_logo.png" alt="Bricohams" width="420">
</p>

# Mango SpaceQuad con trípode, walki, móvil y duplexor

Mango imprimible en 3D para la antena de satélites **BIG SIGNAL SpaceQuad** (VHF/UHF, boom cuadrado de 15 mm).
Se puede llevar en la mano o montar en un trípode de fotografía, y lleva puntos de anclaje para el walki,
el móvil (para la app de seguimiento de satélites) y el duplexor.

<p align="center">
  <img src="docs/img/vista_uso.png" alt="Conjunto en posición de uso sobre trípode" width="90%">
</p>

## Características

- **Encaja en el boom de la SpaceQuad**: túnel de 15,5 × 15,5 mm para el boom cuadrado de 15 mm (0,5 mm de holgura).
- **Rosca de trípode en el culo de la empuñadura**: tuerca 1/4"-20 embutida en una base plana de 52 × 31 mm.
  La empuñadura queda hacia abajo y el boom horizontal, igual que al llevarla en la mano.
  Es compatible con cualquier placa de liberación rápida de rótula.
- **Dos roscas 1/4"-20 en la torre** para brazos de rótula comerciales ("magic arm"):
  - **arriba**, para el walki (con una pinza de cinturón o un soporte de walki);
  - **en el lateral**, para el móvil.
- **Funda para el duplexor** VHF/UHF entre la torre y el boom. Mide 16 × 32 mm por dentro y 48 mm de largo, y
  está abierta por los extremos para los conectores SMA/BNC.
- **Pinza de móvil imprimible** (2 piezas) con tuerca 1/4"-20. Admite móviles de 58 a 92 mm de ancho y hasta 12 mm de grosor con funda.
- **Paramétrico**: todo se genera con scripts de Python (CadQuery + manifold3d), así que las medidas se pueden adaptar.

<p align="center">
  <img src="docs/img/mango_detalles.png" alt="Detalle de roscas y funda" width="70%">
</p>

## Contenido del repositorio

```
stl/    Piezas listas para imprimir (ya orientadas)
  mango_spacequad_tripode.stl   Mango con roscas, funda de duplexor y base de trípode
  pinza_movil_cuerpo.stl        Barra + mordaza fija de la pinza del móvil
  pinza_movil_mordaza.stl       Mordaza deslizante
step/   Pinza del móvil en STEP para editarla en cualquier CAD
src/    Scripts paramétricos que generan las piezas
docs/   Imágenes, montaje y lista de materiales
```

## Materiales

Lista completa en [docs/MATERIALES.md](docs/MATERIALES.md). En resumen:

| Cantidad | Pieza |
|---|---|
| 4 | Tuerca hexagonal 1/4"-20 UNC (11,1 mm entre caras) |
| 1 | Tornillo M4 × 16–20 mm (mejor si es de cabeza moleteada o mariposa) |
| 1 | Tuerca M4 |
| 2 | Brazo de rótula con rosca 1/4" (tipo "magic arm") |
| 1 | Soporte o pinza para walki con rosca 1/4" |

## Impresión

| Parámetro | Mango | Pinza del móvil |
|---|---|---|
| Material | PETG o ASA (exterior, al sol); PLA solo para pruebas | PETG / PLA |
| Capa | 0,2 mm | 0,2 mm |
| Paredes | 4 perímetros | 3 perímetros |
| Relleno | 30–40 % giroide | 25 % |
| Soportes | **Sí**, desde la cama (bajo la empuñadura y la torre) | No |
| Orientación | La del STL | La del STL (cara trasera sobre la cama) |

Si las tuercas no entran, sube un poco la expansión horizontal de agujeros o repasa la ranura con una lima.

## Montaje

Los pasos detallados están en [docs/MONTAJE.md](docs/MONTAJE.md).

1. Mete las 3 tuercas 1/4"-20 del mango por sus ranuras: dos en la cara delantera de la torre y una en el lateral del culo de la empuñadura.
   Una gota de pegamento evita que se salgan.
2. Pasa el boom de la SpaceQuad por el túnel del mango.
3. Rosca los brazos de rótula: el del walki en la rosca de arriba y el del móvil en la lateral.
4. Mete el duplexor en su funda deslizándolo por un extremo.
5. Para usarlo en trípode, enrosca la placa rápida de la rótula en el culo de la empuñadura.

## Regenerar las piezas

```bash
pip install -r src/requirements.txt
cd src
python build_mango.py "BIG SIGNAL SpaceQuad.stl" ../stl/mango_spacequad_tripode.stl
python pinza_movil.py ../stl ../step
```

`build_mango.py` parte del **STL original del mango** (no está incluido en este repositorio, ver *Créditos*).
Las medidas (tuercas, funda del duplexor, posición de la base) se cambian en la sección `PARAMETROS` de cada script.

## Créditos y licencia

- Mango original de la SpaceQuad: **[AUTOR ORIGINAL — completar con nombre y enlace]**.
  Este proyecto es una modificación de su diseño y respeta su licencia original.
- Modificaciones, pinza del móvil y scripts: **Bricohams**.
- BIG SIGNAL y SpaceQuad son marcas de sus respectivos propietarios. Este proyecto no está afiliado a ellos.

Licencia: [CC BY-SA 4.0](LICENSE) para los modelos y la documentación. Los scripts de `src/` también se
publican bajo CC BY-SA 4.0. Si la licencia del diseño original es distinta, **manda la del original**.

73 y buenas pasadas.
