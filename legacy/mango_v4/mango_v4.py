#!/usr/bin/env python3
"""
Mango SpaceQuad v4 (Bricohams): parte del STL v1 del repositorio.

    python mango_v4.py ../stl/mango_spacequad_tripode.stl ../stl/mango_spacequad_v4.stl

Cambios respecto a v1:
 1. Se rellena la rosca lateral 1/4" del movil (nicho de tuerca + taladro). La funcion del movil se retira.
 2. Canal universal para el clip del walki en la cara +Z de la empunadura (la de arriba al imprimir).
    En planta es una V: ancho arriba (junto al boom) y estrecho en la punta, cerrado en la punta.
    La lengua del clip entra por arriba bajo dos labios en cola de milano y baja hasta que su ancho
    coincide con el del canal: queda acunada por su propio peso. Los labios hacen de cinturon.
    Sustituye a la lengueta de la torre de la v3.
 3. Tuerca 1/4"-20 del tripode a TRIPOD_SKIN de la cara del culo y ranura para NUT_N tuercas apiladas:
    la rosca empieza a 1,2 mm y un tornillo de 10 mm coge 8,8 mm (con una sola tuerca, 5,9 mm).
"""
import argparse
from pathlib import Path
import sys


def _input_file(value):
    path = Path(value)
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"no existe el STL v1 de entrada: {value}")
    return str(path)


def _output_file(value):
    path = Path(value)
    if path.exists() and path.is_dir():
        raise argparse.ArgumentTypeError(f"la salida debe ser un archivo: {value}")
    if not path.parent.is_dir():
        raise argparse.ArgumentTypeError(f"no existe el directorio de salida: {path.parent}")
    return str(path)


def _parse_cli():
    parser = argparse.ArgumentParser(
        description="Generador histórico de la v4 con canal en V; requiere src/geom.py importable y no es el diseño STL actual.",
        epilog="Ejemplo histórico: python legacy/mango_v4/mango_v4.py stl/mango_spacequad_tripode.stl legacy/mango_v4/mango_spacequad_v4.stl",
    )
    parser.add_argument("source", type=_input_file, help="STL v1 de entrada")
    parser.add_argument("destination", type=_output_file, help="STL v4 histórico de salida")
    args = parser.parse_args()
    if Path(args.source).resolve() == Path(args.destination).resolve():
        parser.error("la entrada y la salida no pueden ser el mismo archivo")
    return args


if __name__ == "__main__":
    _cli_args = _parse_cli()

import numpy as np, trimesh
from geom import *

# ---------------------------------------------------------------- PARAMETROS (mm)
# canal del clip. X = hacia la punta de la empunadura (abajo en uso), Y = a lo largo del boom, Z = altura al imprimir.
# Lenguas de clip estimadas (ancho x grueso): Yaesu FT-60/65 (metal) 25-28 x 1,5; Baofeng UV-5R / UV-82 30-34 x 3-4;
# Quansheng UV-K5 33-35 x 4; TYT MD-380 33-36 x 4; Kenwood/Motorola profesionales 40-45 x 5-6.
CH_YC   = 113.0       # eje del canal en Y (centro de la cara superior de la empunadura)
CH_ZF   = 32.0        # suelo del canal (justo por encima de lo mas alto de la empunadura, 31,4)
X_LEAD  = 15.0        # comienzo de la rampa de entrada (sale del bloque del boom)
X_TOP, X_TIP = 60.0, 106.0   # tramo con labios: boca (ancho) y punta (estrecho, cerrada); con un clip de 45 mm
                             # el walki queda a 3 mm de la funda del duplexor
W_TOP, W_TIP = 50.0, 24.0    # ancho del suelo entre paredes: clip de 45 mm + holgura / tope de los mas estrechos
GAP     = 7.0         # altura libre bajo el labio junto a la pared (lengua de 6 mm + 1)
LIP     = 3.0         # vuelo de cada labio, con la cara inferior a 45 grados (sin soportes)
LIP_TIP = 1.5         # grosor en la punta del labio: el clip abraza de 1,5 a 4,5 mm, como un cinturon
RAIL    = 4.0         # ancho de cada pared
END_T   = 3.0         # tope de la punta
PAD_D   = 18.0        # el zocalo baja a 45 grados hasta CH_ZF - PAD_D dentro de la empunadura
# tripode (medido en v1): centro del taladro, cara del culo, tuerca 1/4"-20
T_YC, T_ZC, BUTT_FACE = 115.2, 15.7, 110.0
NUT_AF, NUT_T, NUT_HOLE, NUT_N = 11.4, 5.9, 6.6, 2
OLD_SKIN, TRIPOD_SKIN = 3.0, 1.2
# nicho/taladro de la antigua rosca lateral (medidos en v1)
OLD_Z = 47.57

def width(x):
    """ancho del suelo del canal en x (lineal entre la boca y la punta)"""
    return W_TOP + (W_TIP - W_TOP) * (x - X_TOP) / (X_TIP - X_TOP)

def ring(x, half):
    """contorno cerrado en el plano x a partir de la mitad izquierda [(a, z)...] (simetrico respecto a CH_YC)"""
    return [(x, CH_YC - a, z) for a, z in half] + [(x, CH_YC + a, z) for a, z in reversed(half)]

def section(x, w, ztop):
    """seccion del zocalo en x: tapa de ancho w hasta ztop y bajada a 45 grados (o mas vertical) hacia dentro"""
    h = w / 2
    return ring(x, [(h, ztop), (h, CH_ZF), (max(h - PAD_D, 0.5), CH_ZF - PAD_D)])

def groove(x, w):
    """seccion del hueco: paredes verticales hasta GAP, labios a 45 grados y boca abierta hacia arriba"""
    h = w / 2
    return ring(x, [(h - LIP, CH_ZF + GAP + LIP + LIP_TIP + 5), (h - LIP, CH_ZF + GAP + LIP), (h, CH_ZF + GAP), (h, CH_ZF)])

def loft(a, b):
    """solido reglado entre dos contornos convexos con el mismo numero de vertices (la envolvente convexa
    no vale: al estrecharse la V uniria esquinas que no se corresponden)"""
    n = len(a)
    f = [(0, i, i + 1) for i in range(1, n - 1)] + [(n, n + i + 1, n + i) for i in range(1, n - 1)]
    for i in range(n):
        j = (i + 1) % n
        f += [(i, n + i, n + j), (i, n + j, j)]
    m = trimesh.Trimesh(np.array(a + b, float), f, process=False)
    if m.volume < 0: m.invert()
    return to_mf(m)

def clip_channel():
    ztop = CH_ZF + GAP + LIP + LIP_TIP
    x_end = X_TIP + END_T
    rails = loft(section(X_TOP, W_TOP + 2*RAIL, ztop), section(x_end, width(x_end) + 2*RAIL, ztop))
    lead = loft(section(X_LEAD, W_TOP + 2*RAIL, CH_ZF), section(X_TOP + 0.1, W_TOP + 2*RAIL, CH_ZF))
    cut = loft(groove(X_TOP - 5, width(X_TOP - 5)), groove(X_TIP, W_TIP))
    return rails + lead - cut

def tripod_fix(body, verts):
    """rellena el nicho v1 y lo vuelve a vaciar a TRIPOD_SKIN de la cara, con sitio para NUT_N tuercas"""
    hull_ = to_mf(trimesh.convex.convex_hull(verts[verts[:, 0] > BUTT_FACE - 12]))
    x_old = BUTT_FACE - OLD_SKIN - NUT_T
    fill = to_mf(trimesh.creation.box(bounds=[[x_old - 0.1, T_YC - NUT_AF/2 - 0.1, -1],
                                              [BUTT_FACE - OLD_SKIN + 0.1, T_YC + NUT_AF/2 + 0.1, T_ZC + 0.1]]))
    body = body + (fill ^ hull_)
    x1 = BUTT_FACE - TRIPOD_SKIN
    x0 = x1 - NUT_N * NUT_T
    slot = to_mf(trimesh.creation.box(bounds=[[x0, T_YC - NUT_AF/2, -1], [x1, T_YC + NUT_AF/2, T_ZC]]))
    hole = trimesh.creation.cylinder(radius=NUT_HOLE/2, height=BUTT_FACE + 1 - (x0 - 2), sections=48)
    hole.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0]))
    hole.apply_translation([(BUTT_FACE + 1 + x0 - 2) / 2, T_YC, T_ZC])
    return body - slot - to_mf(hole)

def build(src, dst):
    m = trimesh.load(src); m.merge_vertices()
    body = to_mf(m)
    print("v1:", body.status(), round(body.volume()/1000, 1), "cm3")

    # 1) rellenar rosca lateral movil: nicho de tuerca abierto por la cara -Y + taladro hasta la torre
    fill = box(-9.2, -2.6, TY0, YC + 5.9, OLD_Z - 5.8, OLD_Z + 5.8)               # nicho de tuerca (x -55,6..-49,7)
    fill = fill + cyl_u(YC, OLD_Z, 3.45, -19.3, 0.2)                                # taladro Ø6,6 (x -58,6..-39,6)
    body = body + fill
    # 2) canal del clip en la cara +Z de la empunadura; el zocalo no se mete en el hueco interior
    #    de la empunadura (su techo plano no se podria imprimir)
    channel = clip_channel()
    for p in body.decompose():
        if p.volume() < 0:                       # el hueco sale como cascara invertida
            c = to_tm(p); c.invert(); channel = channel - to_mf(c)
    body = body + channel
    # 3) tuerca del tripode
    body = tripod_fix(body, m.vertices)
    out = to_tm(body)
    out.export(dst)
    print("OK ->", dst, np.round(out.extents, 1), "mm", round(body.volume()/1000, 1), "cm3", body.status())

if __name__ == "__main__":
    build(_cli_args.source, _cli_args.destination)
