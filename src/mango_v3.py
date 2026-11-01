#!/usr/bin/env python3
"""
Mango SpaceQuad v3 (Bricohams): parte del STL v1 del repositorio.

    python mango_v3.py ../stl/mango_spacequad_tripode.stl ../stl/mango_spacequad_v3.stl

Cambios respecto a v1:
 1. Se rellena la rosca lateral 1/4" del movil (nicho de tuerca + taladro). La funcion del movil se retira.
 2. Placa baja a 20 grados sobre la torre, con dos cartelas triangulares y bajos abiertos.
    El clip entra paralelo a la placa desde el extremo +V; ventana de retencion opcional.
 3. Tuerca 1/4"-20 del tripode mas cerca de la cara del culo (de 3,0 a TRIPOD_SKIN mm): con las placas
    rapidas de 5-6 mm de tornillo el v1 apenas cogia rosca.
La base GoPro de la v2 se retira (legacy/soporte_gopro).
"""
import argparse
from pathlib import Path
import sys


def _input_file(value):
    path = Path(value)
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"no existe el archivo de entrada: {value}")
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
        description="Genera el mango SpaceQuad v3 revisado desde el STL v1 del repositorio.",
        epilog="Ejemplo: python src/mango_v3.py stl/mango_spacequad_tripode.stl stl/mango_spacequad_v3.stl",
    )
    parser.add_argument("source", type=_input_file, help="STL v1 de entrada")
    parser.add_argument("destination", type=_output_file, help="STL v3 de salida")
    args = parser.parse_args()
    if Path(args.source).resolve() == Path(args.destination).resolve():
        parser.error("la entrada y la salida no pueden ser el mismo archivo")
    return args


if __name__ == "__main__":
    _cli_args = _parse_cli()

import numpy as np, trimesh
import shapely.geometry as sg
from geom import *

# ---------------------------------------------------------------- PARAMETROS (mm)
# Coordenadas de uso (U,V,H) = (z,y,-x). s sigue la placa, n es su normal.
PLATE_U0, PLATE_W = 24.0, 55.0
PLATE_V0, PLATE_H0 = 130.0, 65.0
PLATE_L, PLATE_T, ANGLE = 48.0, 4.0, 20.0
USABLE_L = 40.0
SIDE_T, MIN_CLEAR = 4.0, 7.0
W_IN = PLATE_W - 2 * SIDE_T
TOWER_H = 58.64
ROOT_V0, ROOT_V1, ROOT_H0 = 140.0, 154.0, 54.0
WIN_W, WIN_H, WIN_S = 22.0, 6.0, 14.0
HOOK_WINDOW = True
# Envolvente de ingenieria para clips de cinturon de walkies tipo Baofeng, Radtel, Anytone, Quansheng, Retevis RT3S.
# ESTIMADA (25-45 mm de ancho x hasta 6 mm de grueso); solo esta verificada la separacion de 26 mm entre tornillos
# del clip Retevis/TYT MD-380 (retevis.com). No es una validacion de ajuste universal.
CLIP_W_MIN, CLIP_W_MAX, CLIP_T_MAX = 25.0, 45.0, 6.0   # ancho min/max y grueso max estimados de la lengua del clip
# tripode (medido en v1): centro del taladro, cara del culo, tuerca 1/4"-20
T_YC, T_ZC, BUTT_FACE = 115.2, 15.7, 110.0
NUT_AF, NUT_T, NUT_HOLE = 11.4, 5.9, 6.6   # NUT_T = ranura (holgura), no el grosor del metal
NUT_T_NOMINAL = 5.6   # grosor nominal de la tuerca 1/4"-20 (limita la rosca engranada)
OLD_SKIN, TRIPOD_SKIN = 3.0, 1.2
# nicho/taladro de la antigua rosca lateral (medidos en v1)
OLD_Z = 47.57

def plate_point(s, n=0.0):
    a = np.deg2rad(ANGLE)
    return (PLATE_V0 + s * np.cos(a) - n * np.sin(a),
            PLATE_H0 + s * np.sin(a) + n * np.cos(a))

def use_prism(poly_vh, u0, u1):
    """Poligono (V,H) extruido en U, devuelto en coordenadas originales del STL."""
    return prism_z(sg.Polygon([(FACE_X + h, v) for v, h in poly_vh]), u0, u1)

def plate_box(u0, u1, s0, s1, n0, n1):
    return use_prism([plate_point(s0, n0), plate_point(s1, n0),
                      plate_point(s1, n1), plate_point(s0, n1)], u0, u1)

def clip_holder():
    """Placa de 4 mm y dos cartelas: sin funda vertical ni suelo bajo el clip."""
    plate = plate_box(PLATE_U0, PLATE_U0 + PLATE_W, 0, PLATE_L, 0, PLATE_T)
    if HOOK_WINDOW:
        uc = PLATE_U0 + PLATE_W / 2
        plate -= plate_box(uc - WIN_W/2, uc + WIN_W/2, WIN_S, WIN_S + WIN_H, -1, PLATE_T + 1)
    gusset = [plate_point(0, 0.2), plate_point(PLATE_L, 0.2),
              (ROOT_V1, ROOT_H0), (ROOT_V0, ROOT_H0)]
    for u in (PLATE_U0, PLATE_U0 + PLATE_W - SIDE_T):
        plate += use_prism(gusset, u, u + SIDE_T)
    return plate

def tripod_fix(body, verts):
    """rellena el nicho v1 y lo vuelve a vaciar a TRIPOD_SKIN de la cara"""
    hull = to_mf(trimesh.convex.convex_hull(verts[verts[:, 0] > BUTT_FACE - 12]))
    x_old = BUTT_FACE - OLD_SKIN - NUT_T
    fill = to_mf(trimesh.creation.box(bounds=[[x_old - 0.1, T_YC - NUT_AF/2 - 0.1, -1],
                                              [BUTT_FACE - OLD_SKIN + 0.1, T_YC + NUT_AF/2 + 0.1, T_ZC + 0.1]]))
    body = body + (fill ^ hull)
    x1 = BUTT_FACE - TRIPOD_SKIN
    slot = to_mf(trimesh.creation.box(bounds=[[x1 - NUT_T, T_YC - NUT_AF/2, -1], [x1, T_YC + NUT_AF/2, T_ZC]]))
    hole = trimesh.creation.cylinder(radius=NUT_HOLE/2, height=BUTT_FACE + 1 - (x_old - 2), sections=48)
    hole.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0]))
    hole.apply_translation([(BUTT_FACE + 1 + x_old - 2) / 2, T_YC, T_ZC])
    return body - slot - to_mf(hole)

def build(src, dst):
    m = trimesh.load(src); m.merge_vertices()
    body = to_mf(m)
    print("v1:", body.status(), round(body.volume()/1000, 1), "cm3")

    # 1) rellenar rosca lateral movil: nicho de tuerca abierto por la cara -Y + taladro hasta la torre
    fill = box(-9.2, -2.6, TY0, YC + 5.9, OLD_Z - 5.8, OLD_Z + 5.8)               # nicho de tuerca (x -55,6..-49,7)
    fill = fill + cyl_u(YC, OLD_Z, 3.45, -19.3, 0.2)                                # taladro Ø6,6 (x -58,6..-39,6)
    body = body + fill
    # 2) placa baja sobre la cara superior de la torre (H = 58.64).
    body = body + clip_holder()
    # 3) tuerca del tripode
    body = tripod_fix(body, m.vertices)
    out = to_tm(body)
    out.export(dst)
    print("OK ->", dst, np.round(out.extents, 1), "mm", round(body.volume()/1000, 1), "cm3", body.status())

if __name__ == "__main__":
    build(_cli_args.source, _cli_args.destination)
