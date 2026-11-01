<p align="center">
  <img src="docs/img/bricohams_logo.png" alt="Bricohams" width="420">
</p>

# Mango SpaceQuad con trípode, soporte de walki por clip y duplexor

Mango imprimible en 3D para la antena de satélites **BIG SIGNAL SpaceQuad** (VHF/UHF, boom cuadrado de 15 mm).
Se puede llevar en la mano o montar en un trípode de fotografía. Lleva una **lengüeta ancha para el clip de cinturón del walki**
en la torre y una funda para el duplexor.

> **Ayuda y navegación:** [guía completa de uso, instalación y scripts](docs/AYUDA.md) ·
> [montaje](docs/MONTAJE.md) · [materiales](docs/MATERIALES.md) · [cambios](CHANGELOG.md).

<p align="center">
  <img src="docs/img/vista_uso.png" alt="Conjunto en posición de uso" width="90%">
</p>

## Novedades de esta revisión de la v3

Se vuelve a la v3 (lengüeta en la torre, la misma tuerca única de trípode a 1,2 mm de la cara) y **solo cambia el soporte del clip**:
una **placa baja a 20° sobre la horizontal**, con dos cartelas laterales de 4 mm, bajos abiertos y una **ventana rectangular** opcional.

- **Dimensiones estimadas** (no medidas, no verificadas con walkies reales): lenguas de clip de **25 a 45 mm** de ancho y hasta **6 mm** de grosor,
  Placa de 55 × 48 × 4 mm, 47 mm libres entre cartelas, recorrido de inserción de 40 mm y espacio libre de 7 mm bajo la placa.
  La cara inferior empieza en H=65 mm; las cartelas tienen pies planos V=140..154, H=54 mm, embebidos 4,64 mm en la torre.
- Lo único verificado en una fuente pública es la separación de **26 mm entre tornillos** del clip Retevis/TYT MD-380 ([retevis.com](https://www.retevis.com/products/belt-clip-for-tyt-tytera-md-380-retevis-rt3-radio));
  no se conoce el grosor ni el ancho de su lengua.
- Los clips estrechos no se centran: quedan holgados lateralmente y se sujetan solo por el muelle del propio clip contra la lengüeta.
  La ventana no engancha todos los clips; es una ayuda opcional.
- Se conserva la v4 (canal en V sobre la empuñadura) en `legacy/mango_v4/`.

<p align="center">
  <img src="docs/img/mango_detalles.png" alt="Detalle de la lengüeta del clip" width="70%">
</p>
<p align="center">
  <img src="docs/img/clip_detalle.png" alt="Primer plano de la lengüeta con ventana" width="70%">
</p>
## Características

- **Encaja en el boom de la SpaceQuad**: túnel de 15,5 × 15,5 mm para el boom cuadrado de 15 mm (0,5 mm de holgura).
- **Rosca de trípode en el culo de la empuñadura**: **una** tuerca 1/4"-20 embutida en una base plana de 52 × 31 mm, a 1,2 mm de la cara.
  La ranura mide 5,9 mm (holgura de diseño); la rosca engranada está limitada por el grosor real de la tuerca (5,6 mm nominal), no por la cavidad.
  La empuñadura queda hacia abajo y el boom horizontal, igual que al llevarla en la mano.
- **Soporte del clip**: placa baja de 55 × 48 × 4 mm a 20°, 47 mm de ancho libre y 40 mm de inserción,
  espacio de 7 mm y bajos abiertos, dos cartelas con pies finitos y ventana opcional de 22 × 6 mm.
- **Funda para el duplexor** VHF/UHF entre la torre y el boom: 16 × 32 mm por dentro, 48 mm de largo, abierta por los extremos.
- **Paramétrico**: todo se genera con scripts de Python (trimesh + manifold3d), así que las medidas se pueden adaptar.

## Contenido del repositorio

```
stl/    Piezas listas para imprimir (ya orientadas)
  mango_spacequad_v3.stl         Mango v3 revisado (soporte del clip + funda duplexor + base de trípode)
  mango_spacequad_tripode.stl    Mango v1 (se conserva sin cambios: es la entrada de mango_v3.py)
src/    Scripts paramétricos que generan las piezas
docs/   Imágenes, montaje y lista de materiales
legacy/ Pinza del móvil (v1), soporte GoPro (v2) y mango v4 (canal en V), ya no se usan
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
| Mango v3 | PETG o ASA (exterior, al sol) | La del STL | Sí, desde la cama (bajo la empuñadura y la torre) y bajo la placa/cartelas |

0,2 mm de capa, 4 perímetros y 30–40 % de relleno.

## Montaje

Pasos detallados en [docs/MONTAJE.md](docs/MONTAJE.md).

1. Mete la tuerca 1/4"-20 por su ranura del culo de la empuñadura.
2. Pasa el boom de la SpaceQuad por el túnel del mango y mete el duplexor en su funda.
3. Abre el clip y deslízalo desde el extremo alto (+V), paralelo a la placa; la lengua queda debajo y el walki encima.
## Compatibilidad del clip (estimada)

| Dato | Valor (estimación de diseño, no medida) |
|---|---|
| Ancho de la lengua del clip | de 25 a 45 mm; 47 mm libres entre cartelas |
| Grosor de la lengua | hasta 6 mm (holgura mínima del canal 7 mm) |
| Recorrido útil | 40 mm; barrido continuo de lengua de 45 × 6 mm |
| Clips estrechos | quedan holgados en el ancho; el muelle del clip los sujeta, sin centrado |
| Ventana de 22 × 6 mm | retención opcional; no engancha todos los clips |

Familias pensadas: clips de cinturón de Baofeng, Radtel, Anytone, Quansheng y Retevis RT3S (sin atornillar al mango).
**No se ha medido ninguno**; solo está verificada en [retevis.com](https://www.retevis.com/products/belt-clip-for-tyt-tytera-md-380-retevis-rt3-radio) la separación de 26 mm entre tornillos del clip del MD-380/RT3.
No se garantiza ajuste universal: comprueba el clip de tu walki. Las medidas se cambian en `src/mango_v3.py`.

## Regenerar las piezas

```bash
python -m pip install -r src/requirements.txt
python src/mango_v3.py stl/mango_spacequad_tripode.stl stl/mango_spacequad_v3.stl
python src/verificar.py stl/mango_spacequad_v3.stl docs/cad_checks.json
python src/render_docs.py stl docs/img
```

`mango_v3.py` parte del STL v1 incluido en el repositorio. `verificar.py` compara con la revisión anterior leyéndola de git (`35019cc`),
así que hay que ejecutarlo dentro del clon. `build_mango.py` (v1) parte del **STL original del mango**,
que no está incluido (ver *Créditos*) y necesita además `cadquery`.
Consulta las opciones y advertencias antes de regenerar en [docs/AYUDA.md](docs/AYUDA.md); las medidas se cambian en la sección `PARAMETROS` de cada script.

## Estado

Resultados reproducibles en [docs/cad_checks.json](docs/cad_checks.json): sólido único manifold; cambios localizados;
empuñadura, boom y trípode conservados; barrido continuo de 40 mm del clip y del conjunto radio+clip en la misma transformación.
La radio estimada de 62 × 40 × 130 mm queda sobre la placa inclinada: no se presupone que cuelgue vertical.
La caja nominal del duplexor ya intersecta la funda v1 en 462,2388 mm³; se verifica igualdad con la base y ningún obstáculo nuevo
en ambos corredores de inserción V. Esto **no demuestra ajuste físico** de esa caja.
La textura original presenta degeneraciones al soldar vértices con trimesh; la malla canónica manifold es estanca.
Cada pie tiene al menos 3 mm de profundidad y 10 mm de tramo comprobados dentro de la torre; conectividad y volumen de anclaje
**no certifican resistencia**. Se requieren soportes bajo la placa/cartelas según orientación, revisión en el laminador y prueba de carga.
**Ningún clip real ha sido medido ni probado, y el modelo no está probado impreso.**
## Créditos y licencia

- Mango original de la SpaceQuad: **[AUTOR ORIGINAL — completar con nombre y enlace]**.
  Este proyecto es una modificación de su diseño y respeta su licencia original.
- Modificaciones, soporte de walki y scripts: **Bricohams**.
- BIG SIGNAL y SpaceQuad son marcas de sus respectivos propietarios. Este proyecto no está afiliado a ellos.

Licencia: [CC BY-SA 4.0](LICENSE) para los modelos y la documentación. Los scripts de `src/` también se
publican bajo CC BY-SA 4.0. Si la licencia del diseño original es distinta, **manda la del original**.

73 y buenas pasadas.
