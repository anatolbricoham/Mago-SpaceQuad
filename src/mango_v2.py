#!/usr/bin/env python3
"""
Mango SpaceQuad v2 (Bricohams): parte del STL v1 del repositorio.

    python mango_v2.py ../stl/mango_spacequad_tripode.stl ../stl/mango_spacequad_v2.stl

Cambios respecto a v1:
 1. Se rellena la rosca lateral 1/4" del movil (nicho de tuerca + taladro). La funcion del movil se retira.
 2. Se anade en la cara libre de la torre (la que queda ARRIBA en uso, lejos del duplexor) una base GoPro de
    3 dedos con el eje de giro paralelo al boom. El pivote queda a PIV_G mm de la cara.
    El dedo exterior (lado +Y) es mas grueso y lleva el nicho hexagonal de la tuerca M5.
La rosca 1/4" de arriba de la torre se mantiene por si quieres colgar algo extra.
"""
import sys
import numpy as np, trimesh
import shapely.geometry as sg
from geom import *

# ---------------------------------------------------------------- PARAMETROS (mm)
PIV_G   = 24.0        # distancia del eje del pivote a la cara de la torre
PIV_Z   = 48.0        # altura (Z) del pivote sobre el origen del STL
R_PRONG = 7.5         # radio del extremo de los dedos (estandar GoPro)
P_T, GAP = 3.0, 3.3   # grosor de dedo y hueco (holgura 0,15 por lado con el dedo macho de 3,0)
P_C     = 6.0         # grosor del dedo exterior (nicho de tuerca)
BOLT_D  = 5.4         # taladro M5
NUT_AF, NUT_DEPTH = 8.4, 4.0   # tuerca M5 (8 mm entre caras) y profundidad del nicho
POST_END = 13.0       # hasta aqui (u) el cuerpo es macizo; desde aqui se abren los huecos entre dedos
# nicho/taladro de la antigua rosca lateral (medidos en v1)
OLD_Z = 47.57

Y_TOT = P_T + GAP + P_T + GAP + P_C          # 18.6
Y0 = YC - Y_TOT / 2                           # lado -Y (dedo A)

def build(src, dst):
    m = trimesh.load(src); m.merge_vertices()
    body = to_mf(m)
    print("v1:", body.status(), round(body.volume()/1000, 1), "cm3")

    # 1) rellenar rosca lateral movil: nicho de tuerca abierto por la cara -Y + taladro hasta la torre
    fill = box(-9.2, -2.6, TY0, YC + 5.9, OLD_Z - 5.8, OLD_Z + 5.8)               # nicho de tuerca (x -55,6..-49,7)
    fill = fill + cyl_u(YC, OLD_Z, 3.45, -19.3, 0.2)                                # taladro Ø6,6 (x -58,6..-39,6)
    body = body + fill

    # 2) base GoPro: perfil (u,z) con cara inferior a 45 grados (sin soportes bajo los dedos)
    c = sg.Point(PIV_G, PIV_Z).buffer(R_PRONG, 64)
    k = PIV_G + R_PRONG*np.sqrt(2)               # recta z = u + (PIV_Z - k) tangente por debajo
    zlow = lambda u: (u - k) + PIV_Z
    prof = sg.MultiPoint([(-1.5, zlow(-1.5)), (-1.5, PIV_Z + 14), (PIV_G, PIV_Z + R_PRONG)]).convex_hull.union(c).convex_hull
    boss = prism_y(prof, Y0, Y0 + Y_TOT)
    # huecos entre dedos (desde POST_END hacia fuera)
    gaps = [(Y0 + P_T, Y0 + P_T + GAP), (Y0 + 2*P_T + GAP, Y0 + 2*P_T + 2*GAP)]
    cut = None
    for ya, yb in gaps:
        g = box(POST_END, PIV_G + R_PRONG + 2, ya, yb, PIV_Z - 40, PIV_Z + 40)
        cut = g if cut is None else cut + g
    # taladro M5 (gota para imprimir horizontal: punta hacia +Z)
    hole = prism_y(teardrop(PIV_G, PIV_Z, BOLT_D/2, apex=(0, 1)), Y0 - 1, Y0 + Y_TOT + 1)
    # nicho hexagonal de la tuerca M5 en el dedo exterior (+Y), abierto por fuera
    nut = prism_y(sg.Polygon([(PIV_G + NUT_AF/np.sqrt(3)*np.cos(a), PIV_Z + NUT_AF/np.sqrt(3)*np.sin(a))
                              for a in np.arange(6)*np.pi/3 + np.pi/6]), Y0 + Y_TOT - NUT_DEPTH, Y0 + Y_TOT + 1)
    boss = boss - cut - hole - nut
    body = body + boss
    out = to_tm(body)
    out.export(dst)
    print("OK ->", dst, np.round(out.extents, 1), "mm", round(body.volume()/1000, 1), "cm3", body.status())

if __name__ == "__main__":
    if len(sys.argv) != 3: sys.exit(__doc__)
    build(sys.argv[1], sys.argv[2])
