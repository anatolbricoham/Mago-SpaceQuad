<p align="center">
  <img src="docs/img/bricohams_logo.png" alt="Bricohams" width="420">
</p>

# Mango SpaceQuad con trípode, soporte universal de walki y duplexor

Mango imprimible en 3D para la antena de satélites **BIG SIGNAL SpaceQuad** (VHF/UHF, boom cuadrado de 15 mm).
Se puede llevar en la mano o montar en un trípode de fotografía, y lleva un **soporte universal para el walki**
y una funda para el duplexor.

<p align="center">
  <img src="docs/img/vista_uso.png" alt="Conjunto en posición de uso" width="90%">
</p>

## Novedades de la v2

- **Soporte de walki nuevo, tipo GoPro** (el enganche más extendido en las webs de impresión 3D). Va en la cara libre de la torre,
  la que queda **arriba** al usar la antena, así que ya no choca con el duplexor y tiene sitio de sobra.
- **Universal**: dos mordazas ajustables que admiten walkis de **50 a 86 mm de ancho** y hasta **54 mm de grosor**
  (desde los Baofeng/AnyTone/Retevis hasta los más anchos del mercado, tipo Motorola APX/XTS).
- Se **retira la función del móvil** (la rosca lateral 1/4" y su brazo): por el ángulo no era útil. La pinza antigua queda en `legacy/`.
- El mango conserva la rosca 1/4" de arriba de la torre, la funda del duplexor y la base de trípode.

<p align="center">
  <img src="docs/img/mango_detalles.png" alt="Despiece" width="70%">
</p>

## Características

- **Encaja en el boom de la SpaceQuad**: túnel de 15,5 × 15,5 mm para el boom cuadrado de 15 mm (0,5 mm de holgura).
- **Rosca de trípode en el culo de la empuñadura**: tuerca 1/4"-20 embutida en una base plana de 52 × 31 mm.
  La empuñadura queda hacia abajo y el boom horizontal, igual que al llevarla en la mano.
- **Base GoPro de 3 dedos** integrada en la torre (pivote a 24 mm de la cara, eje paralelo al boom): el walki se puede
  inclinar unos grados hacia cada lado (ver *Margen de giro*).
- **Funda para el duplexor** VHF/UHF entre la torre y el boom: 16 × 32 mm por dentro, 48 mm de largo, abierta por los extremos.
- **Paramétrico**: todo se genera con scripts de Python (trimesh + manifold3d), así que las medidas se pueden adaptar.

## Contenido del repositorio

```
stl/    Piezas listas para imprimir (ya orientadas)
  mango_spacequad_v2.stl         Mango v2 (base GoPro + funda duplexor + base de trípode)
  adaptador_gopro_walki.stl      Placa con dedos GoPro y ranuras para las mordazas   (x1)
  mordaza_walki.stl              Mordaza ajustable                                   (x2, imprimir dos iguales)
  mango_spacequad_tripode.stl    Mango v1 (se conserva: es la entrada de mango_v2.py)
src/    Scripts paramétricos que generan las piezas
docs/   Imágenes, montaje y lista de materiales
legacy/ Pinza del móvil de la v1 (ya no se usa)
```

## Materiales

Lista completa en [docs/MATERIALES.md](docs/MATERIALES.md). En resumen:

| Cantidad | Pieza |
|---|---|
| 1 | Tornillo M5 × 20 + tuerca M5 (o un tornillo de pomo GoPro estándar) |
| 4 | Tornillo M4 × 12 (cabeza cilíndrica o allen, Ø máx. 7 mm) |
| 4 | Tuerca M4 |
| 2 | Tuerca hexagonal 1/4"-20 UNC (11,1 mm entre caras): trípode y rosca de arriba (opcional) |

## Impresión

| Pieza | Material | Orientación | Soportes |
|---|---|---|---|
| Mango v2 | PETG o ASA (exterior, al sol) | La del STL | Sí, desde la cama (bajo la empuñadura y la torre) |
| Adaptador | PETG | Placa en la cama, dedos hacia arriba | No |
| Mordazas (x2) | PETG | Pie en la cama, pared hacia arriba | No |

0,2 mm de capa, 4 perímetros, 30–40 % de relleno (los dedos GoPro y las paredes de las mordazas conviene que sean casi macizos).
Si el dedo macho no entra en los huecos de la base, repasa los huecos con una cuchilla; la holgura de diseño es de 0,15 mm por lado.

## Montaje

Pasos detallados en [docs/MONTAJE.md](docs/MONTAJE.md).

1. Mete las tuercas 1/4"-20 por sus ranuras (culo de la empuñadura y, si quieres, arriba de la torre).
2. Pasa el boom de la SpaceQuad por el túnel del mango y mete el duplexor en su funda.
3. Mete 4 tuercas M4 en los canales de la parte trasera del adaptador y atornilla las dos mordazas por las ranuras
   (tornillo desde arriba) dejándolas flojas.
4. Cierra las mordazas sobre el walki y aprieta los 4 tornillos.
5. Encaja los dedos del adaptador entre los de la torre y pasa el tornillo M5 (cabeza por el lado de la rosca de trípode, tuerca en el nicho del dedo grueso).

## Margen de giro

Con el walki montado se puede girar el soporte unos **+52° / −38°** alrededor del eje del pivote antes de tocar la torre
(calculado con `src/verificar.py`, igual para 50, 62 y 86 mm de ancho de walki).

## Regenerar las piezas

```bash
pip install -r src/requirements.txt
cd src
python mango_v2.py ../stl/mango_spacequad_tripode.stl ../stl/mango_spacequad_v2.stl
python soporte_walki.py ../stl
python verificar.py ../stl/mango_spacequad_v2.stl      # choques, holguras y margen de giro
python render_docs.py ../stl ../docs/img                # imágenes
```

`mango_v2.py` parte del STL v1 incluido en el repositorio. `build_mango.py` (v1) parte del **STL original del mango**,
que no está incluido (ver *Créditos*) y necesita además `cadquery`.
Las medidas (anchos de walki, pivote, tornillería) se cambian en la sección `PARAMETROS` de cada script.

## Estado

Diseño verificado en el ordenador (piezas estancas, 0 mm³ de interferencias con el mango, el duplexor y walkis de 50/62/86 mm).
**Aún sin probar impresa**: si algún ajuste no encaja, se abre un issue o se toca el parámetro correspondiente.

## Créditos y licencia

- Mango original de la SpaceQuad: **[AUTOR ORIGINAL — completar con nombre y enlace]**.
  Este proyecto es una modificación de su diseño y respeta su licencia original.
- Modificaciones, soporte de walki y scripts: **Bricohams**.
- BIG SIGNAL y SpaceQuad son marcas de sus respectivos propietarios. Este proyecto no está afiliado a ellos.
- GoPro es una marca de GoPro, Inc.; el interfaz de 3 dedos se usa solo por compatibilidad.

Licencia: [CC BY-SA 4.0](LICENSE) para los modelos y la documentación. Los scripts de `src/` también se
publican bajo CC BY-SA 4.0. Si la licencia del diseño original es distinta, **manda la del original**.

73 y buenas pasadas.
