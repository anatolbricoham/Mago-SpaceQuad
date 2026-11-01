#!/usr/bin/env python3
"""
Mango SpaceQuad v3 (Bricohams): parte del STL v1 del repositorio.

    python mango_v3.py ../stl/mango_spacequad_tripode.stl ../stl/mango_spacequad_v3.stl

Cambios respecto a v1:
 1. Se rellena la rosca lateral 1/4" del movil (nicho de tuerca + taladro). La funcion del movil se retira.
 2. Soporte de walki integrado: lengueta para el clip de cinturon en la cara +Z de la torre (un lateral en uso),
    lejos del duplexor. El clip baja por arriba entre la lengueta y la torre; el walki cuelga por fuera.
    Funda abierta por arriba con paredes laterales (rigidez) y ventana para el saliente del clip.
 3. Tuerca 1/4"-20 del tripode mas cerca de la cara del culo (de 3,0 a TRIPOD_SKIN mm): con las placas
    rapidas de 5-6 mm de tornillo el v1 apenas cogia rosca.
La base GoPro de la v2 se retira (legacy/soporte_gopro).
"""
import sys
import numpy as np, trimesh
import shapely.geometry as sg
from shapely import affinity
from geom import *

# ---------------------------------------------------------------- PARAMETROS (mm)
# lengueta del clip (X hacia la empunadura = abajo en uso, Z = hacia fuera de la torre)
X_BOT   = -33.64      # extremo inferior (en uso) = cara +X de la torre
FLOOR   = 5.0         # fondo cerrado de la funda
USABLE_L = 70.0       # largo util de la lengua del clip (ESTIMADO, no medido)
CLIP_L  = USABLE_L + FLOOR   # largo total de la lengueta
BACK_T  = 3.0         # pared trasera sobre la cara de la torre
# Envolvente de ingenieria para clips de cinturon de walkies tipo Baofeng, Radtel, Anytone, Quansheng, Retevis RT3S.
# ESTIMADA (25-45 mm de ancho x hasta 6 mm de grueso); solo esta verificada la separacion de 26 mm entre tornillos
# del clip Retevis/TYT MD-380 (retevis.com). No es una validacion de ajuste universal.
CLIP_W_MIN, CLIP_W_MAX, CLIP_T_MAX = 25.0, 45.0, 6.0   # ancho min/max y grueso max estimados de la lengua del clip
MIN_CLEAR = 7.0       # holgura minima del canal (grueso max + 1 mm)
G_BOT, G_TOP = MIN_CLEAR, 10.0   # hueco para la lengua del clip en el fondo / en la boca (boca en cuna)
PLATE_T = 4.0         # grosor de la lengueta (lo que coge el clip, como un cinturon)
W_IN, W_NARROW = 50.0, 47.0   # ancho interior en la boca y en el fondo: cuna suave, el clip de 45 mm entra a fondo (>= 47 mm libres)
SIDE_T = 4.0          # paredes laterales; el exterior se estrecha igual que el interior (lados en cuna)
WIN_W, WIN_H, WIN_X = 22.0, 6.0, 10.0   # ventana rectangular para el saliente del clip (ancho, alto, distancia al fondo)
CHAMFER = 1.5         # chaflan de entrada en el borde superior
# tripode (medido en v1): centro del taladro, cara del culo, tuerca 1/4"-20
T_YC, T_ZC, BUTT_FACE = 115.2, 15.7, 110.0
NUT_AF, NUT_T, NUT_HOLE = 11.4, 5.9, 6.6   # NUT_T = ranura (holgura), no el grosor del metal
NUT_T_NOMINAL = 5.6   # grosor nominal de la tuerca 1/4"-20 (limita la rosca engranada)
OLD_SKIN, TRIPOD_SKIN = 3.0, 1.2
# nicho/taladro de la antigua rosca lateral (medidos en v1)
OLD_Z = 47.57

def xz(poly):
    """poligono (x,z) -> (u,z) para prism_y (u = FACE_X - x)"""
    return affinity.affine_transform(poly, [-1, 0, 0, 1, FACE_X, 0])

def z_in(x, fz):
    """cara interior de la lengueta (hueco en cuna de G_BOT a G_TOP)"""
    return fz + BACK_T + G_BOT + (G_TOP - G_BOT) * (X_BOT - x) / CLIP_L

def half_in(x):
    """semiancho interior de la funda en x: W_NARROW en el fondo y W_IN en la boca (lados en cuna)"""
    t = min(max((X_BOT - FLOOR - x) / (CLIP_L - FLOOR), 0.0), 1.0)
    return (W_NARROW + (W_IN - W_NARROW) * t) / 2

def plan(pad, x_end):
    """planta (x,y) de la funda, estrechada hacia el fondo, en coordenadas (u,y) para prism_z; pad = grosor extra"""
    xs = [X_BOT, X_BOT - FLOOR, X_BOT - CLIP_L, x_end]
    pts = [(x, YC - half_in(x) - pad) for x in xs] + [(x, YC + half_in(x) + pad) for x in reversed(xs)]
    return affinity.affine_transform(sg.Polygon(pts), [-1, 0, 0, 1, FACE_X, 0])

def clip_holder(fz):
    """lengueta + funda sobre la cara z = fz de la torre; lados y fondo interior en cuna"""
    x_t = X_BOT - CLIP_L
    zb, zt = fz + BACK_T, z_in(x_t, fz) + PLATE_T
    env = sg.Polygon([(X_BOT, fz - 2.5), (x_t, fz - 2.5), (x_t, zt), (X_BOT, z_in(X_BOT, fz) + PLATE_T)])
    env = env.difference(sg.Polygon([(x_t - 1, zt - CHAMFER - 1), (x_t + CHAMFER + 1, zt + 1), (x_t - 1, zt + 1)]))
    pocket = sg.Polygon([(X_BOT - FLOOR, zb), (x_t - 1, zb), (x_t - 1, z_in(x_t - 1, fz)), (X_BOT - FLOOR, z_in(X_BOT - FLOOR, fz))])
    wy = W_IN / 2 + SIDE_T
    h = prism_y(xz(env), YC - wy, YC + wy) ^ prism_z(plan(SIDE_T, x_t - 1), fz - 3, fz + 60)
    h = h - (prism_y(xz(pocket), YC - W_IN/2, YC + W_IN/2) ^ prism_z(plan(0, x_t - 1), fz - 3, fz + 60))
    xw = X_BOT - FLOOR - WIN_X                       # borde inferior de la ventana
    return h - box(FACE_X - xw, FACE_X - xw + WIN_H, YC - WIN_W/2, YC + WIN_W/2, zb, fz + 40)

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
    # 2) lengueta del clip en la cara +Z de la torre (la mas alta del STL)
    body = body + clip_holder(m.bounds[1][2])
    # 3) tuerca del tripode
    body = tripod_fix(body, m.vertices)
    out = to_tm(body)
    out.export(dst)
    print("OK ->", dst, np.round(out.extents, 1), "mm", round(body.volume()/1000, 1), "cm3", body.status())

if __name__ == "__main__":
    if len(sys.argv) != 3: sys.exit(__doc__)
    build(sys.argv[1], sys.argv[2])
