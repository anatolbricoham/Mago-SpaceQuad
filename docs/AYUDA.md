# Ayuda del proyecto

Guía de entrada para elegir el archivo imprimible, preparar Python, usar los comandos y entender qué está comprobado. El modelo activo es **`stl/mango_spacequad_v3.stl`**; los demás diseños y generadores son históricos.

**Navegación:** [README](../README.md) · [montaje](MONTAJE.md) · [materiales](MATERIALES.md) · [cambios](../CHANGELOG.md).

## Qué archivo usar

- Imprime `stl/mango_spacequad_v3.stl`, ya orientado. No lo confundas con `stl/mango_spacequad_tripode.stl`: este último es la base v1 que consume el generador v3, no el modelo final actual.
- `legacy/mango_v4/mango_spacequad_v4.stl` es el antiguo canal en V; no es la revisión vigente.
- Los STL/STEP de `legacy/` son la pinza para móvil y el soporte GoPro antiguos. No se necesitan para montar la v3.
- Ver [materiales](MATERIALES.md) y [montaje](MONTAJE.md) para hardware y pasos de montaje.

## Preparación

Se necesita Python con `pip` y Git (el verificador consulta una revisión del repositorio). Desde la raíz del clon, crea y activa un entorno virtual e instala las dependencias:

**Windows PowerShell**

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r src/requirements.txt
```

**Linux/macOS (bash)**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r src/requirements.txt
```

Las dependencias comunes son NumPy, trimesh, manifold3d y Shapely; el render usa además PyVista. CadQuery se requiere únicamente para el generador v1, y no para los comandos de la v3. No hace falta instalar nada para consultar la ayuda de los scripts.

## Comandos actuales

Ejecuta desde la raíz del repositorio. `-h` y `--help` describen los argumentos y terminan sin cargar las bibliotecas CAD ni escribir archivos:

```powershell
python src/mango_v3.py --help
python src/verificar.py --help
python src/render_docs.py --help
```

```bash
python src/mango_v3.py --help
python src/verificar.py --help
python src/render_docs.py --help
```

Regenera el STL activo, verifica el sólido y actualiza el JSON de comprobaciones:

```text
python src/mango_v3.py stl/mango_spacequad_tripode.stl stl/mango_spacequad_v3.stl
python src/verificar.py stl/mango_spacequad_v3.stl docs/cad_checks.json
```

Genera las imágenes de documentación (sobrescribe los PNG correspondientes):

```text
python src/render_docs.py stl docs/img
```

`mango_v3.py` necesita el STL v1 de entrada del repositorio y un directorio de salida ya existente. `verificar.py` debe ejecutarse dentro del clon Git porque compara con `35019cc`; acepta un segundo argumento opcional para escribir el informe JSON. `render_docs.py` necesita el STL v3 y PyVista. Los argumentos desconocidos, faltantes o rutas inválidas se rechazan antes de escribir.

## Interpretar las comprobaciones CAD

El informe [docs/cad_checks.json](cad_checks.json) registra **45 comprobaciones CAD**. `passed` es el booleano global; cada entrada de `checks` contiene `name`, `passed` y campos con valores específicos (por ejemplo, `collision_mm3`); `limitations` enumera las salvedades. Si alguna comprobación falla, el verificador devuelve código 1; con comprobaciones superadas devuelve 0. Un error de argumentos devuelve 2. Ante un fallo, revisa el nombre y los valores de las entradas con `passed: false`, corrige la causa y vuelve a verificar antes de publicar. Sin ruta de informe, solo se muestran resultados en consola. El resultado no certifica el ajuste físico de radios o duplexores, ni resistencia o impresión.

## Otros puntos de entrada Python

Todos los scripts ejecutables ofrecen `-h`/`--help` incluso sin dependencias opcionales:

| Script | Uso / condición |
|---|---|
| `src/build_mango.py` | Generador histórico v1. Necesita un STL original externo no incluido y CadQuery. |
| `legacy/mango_v4/mango_v4.py` | Generador de la v4 archivada; requiere `src/geom.py` importable en el contexto histórico. |
| `legacy/soporte_gopro/soporte_walki.py` | Generador GoPro v2 archivado; requiere `mango_v2.py` y `geom.py` de su contexto histórico, que no están en esa carpeta. |
| `legacy/pinza_movil/pinza_movil.py` | Pinza de móvil archivada; requiere CadQuery. |
| `src/geom.py` | Biblioteca geométrica importable, no un comando generador. |

La ayuda de los scripts archivados solo documenta sus argumentos; no garantiza que sus dependencias o entradas históricas estén disponibles ni convierte esos modelos en diseños vigentes.

## Geometría y límites de compatibilidad

La placa actual mide **55 × 48 × 4 mm**, está inclinada **20°** y tiene dos cartelas laterales de 4 mm. El espacio libre entre ellas es **47 mm**, el recorrido modelado para la lengua del clip es **40 mm** y el espacio bajo la placa es **7 mm**. La cara inferior empieza a H=65 mm. Los pies de las cartelas están en V=140..154, H=54 mm, con 4,64 mm de inserción nominal en la torre.

Las dimensiones de lengua de **25–45 mm de ancho y hasta 6 mm de grosor son estimaciones de diseño**, no medidas de una familia de radios ni una garantía de ajuste. Los clips estrechos pueden quedar holgados lateralmente; la ventana de 22 × 6 mm es opcional y no engancha todos los modelos. El barrido CAD de inserción no es una prueba con un clip real. La única referencia pública indicada en el proyecto es la separación de 26 mm entre tornillos del clip Retevis/TYT MD-380; no se conoce allí el ancho ni el grosor de la lengua.

La envolvente ilustrativa de radio usada por el verificador/render es de **62 × 40 × 130 mm**, con su extremo +s situado 25 mm más allá del extremo de la placa; son dimensiones supuestas para el modelo CAD, no una medición de una radio concreta. La funda se diseñó para una sección de hasta 16 × 32 mm y 48 mm de largo. Para las comprobaciones de colisión, `verificar.py` usa una caja de **15,5 × 59 × 31,5 mm**; esta envolvente de prueba es más larga que la funda y no debe interpretarse como una dimensión física medida del duplexor.

La caja de prueba del duplexor ya intersecta la funda original v1 en **462,2388 mm³**; la revisión no añade obstrucción en los corredores de inserción desde ambos extremos del eje V que se comprobaron en CAD. Esto no demuestra ajuste físico del duplexor ni holgura suficiente para insertarlo. La conectividad y el anclaje geométrico de las cartelas tampoco certifican resistencia. No se han documentado pruebas físicas de impresión, carga ni compatibilidad de clips.

## Vistas de ayuda

![Conjunto v3 con radio, clip y duplexor estimados](img/vista_uso.png)

Vista de uso: empuñadura abajo. Verde: radio estimada; azul: clip estimado; rojo: duplexor estimado. Son envolventes CAD, no piezas medidas ni pruebas de montaje.

![Placa baja y acceso a la funda del duplexor](img/mango_detalles.png)

La placa queda sobre la torre; las flechas indican acceso por ambos extremos V. El paso conservado no garantiza que el duplexor real encaje: la caja de prueba ya intersecta la funda original.

![Detalle de placa, ventana opcional y cartelas con bajos abiertos](img/clip_detalle.png)

Detalle del STL actual, con empuñadura y funda omitidas visualmente: placa de 55 × 48 × 4 mm a 20°, dos cartelas de 4 mm y ventana opcional de 22 × 6 mm. El hueco de 7 mm y la inserción CAD de 40 mm no certifican compatibilidad ni resistencia.

## Impresión, orientación y montaje

- Usa PETG o ASA; el STL actual está orientado para imprimir.
- Ajuste de partida documentado: capa de 0,2 mm, 4 perímetros y 30–40 % de relleno.
- Usa soportes desde la cama bajo la empuñadura/torre y bajo la placa y las cartelas, según la vista del laminador. Retíralos del paso del clip y conserva los bajos abiertos; no rellenes el hueco entre cartelas.
- Revisa el laminado, la holgura real del clip y la rótula. Ensaya la carga de forma prudente y usa retención secundaria; no hay certificación estructural.
- El mango se instala sobre el boom cuadrado nominal de 15 mm; la funda está diseñada para una sección de duplexor de hasta 16 × 32 mm. Comprueba las dimensiones reales antes del montaje.

Los pasos y advertencias ampliados están en [Montaje](MONTAJE.md).

## Parámetros y mapa de archivos

- `src/mango_v3.py`: dimensiones de la placa, cartelas, ventana, ángulo, hueco de clip y tuerca de trípode (`PARAMETROS`).
- `src/geom.py`: primitivas geométricas compartidas y conversión local `u = FACE_X - x`; no define el sistema de coordenadas de uso completo.
- `src/mango_v3.py`: transforma coordenadas de uso `(U,V,H) = (z,y,-x)` mediante `plate_point()` y `use_prism()`.
- `src/verificar.py`: dimensiones de las envolventes CAD estimadas, criterios de comprobación y escritura de `docs/cad_checks.json`.
- `src/render_docs.py`: vistas e imágenes documentales.
- `src/build_mango.py`: parámetros del generador v1 histórico.
- `stl/`: STL v1 de entrada y STL v3 actual. `docs/`: esta guía, montaje, materiales, imágenes y resultados CAD. `legacy/`: diseños antiguos; `CHANGELOG.md`: historial de revisión.

## Problemas habituales

- **El verificador no encuentra una revisión Git:** ejecútalo desde un clon Git completo, no desde una copia suelta de los archivos.
- **Falta `manifold3d`, `trimesh`, etc.:** activa `.venv` y vuelve a instalar `src/requirements.txt`.
- **Falla el render por PyVista:** revisa la instalación de esa dependencia, incluida en `requirements.txt`.
- **No aparece el archivo de entrada:** ejecuta desde la raíz y respeta las rutas relativas de los ejemplos; comprueba que la entrada existe antes de regenerar.
- **El soporte no se ajusta o el laminado muestra interferencia:** revisa y mide tu clip/duplexor real. Las cotas del soporte de radio son estimaciones, no una promesa de compatibilidad.
