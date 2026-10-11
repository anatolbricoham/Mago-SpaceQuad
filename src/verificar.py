#!/usr/bin/env python3
"""Comprobaciones: choques, holguras y margen de giro del soporte de walki contra el mango v2.
    python verificar.py ../stl/mango_spacequad_v2.stl"""
import sys, numpy as np, trimesh, manifold3d as mf
from scipy.spatial import cKDTree
from geom import *
import mango_v2 as mg, soporte_walki as sw

def rot_y(M, deg, cx, cz):
    """gira la pieza alrededor del eje paralelo a Y por (x=cx, z=cz)"""
    t = np.radians(deg); c, s = np.cos(t), np.sin(t)
    # matriz 4x4 de manifold (3x4 por columnas)
    R = [c, 0, -s, 0, 1, 0, s, 0, c, 0, 0, 0]
    M = M.translate((-cx, 0, -cz)).transform(np.array([[c,0,s,0],[0,1,0,0],[-s,0,c,0]])).translate((cx, 0, cz))
    return M

def vol_int(a, b):
    return (a ^ b).volume()

def main(mango_path):
    mango = to_mf(trimesh.load(mango_path))
    xp = FACE_X - sw.PIV_G
    A = sw.adaptador()
    for W in (sw.WMIN, sw.W_DEF, sw.WMAX):
        J = sw.mordaza(+1, W) + sw.mordaza(-1, W)
        radio = box(sw.PL_U1, sw.PL_U1 + 50.0, YC - 70, YC + 70, sw.PIV_Z - W/2, sw.PIV_Z + W/2)
        cj = A + J
        print(f"--- walki de {W:.0f} mm ---")
        print("  adaptador/mango  :", round(vol_int(A, mango), 3), "mm3")
        print("  mordazas/mango   :", round(vol_int(J, mango), 3), "mm3")
        print("  mordazas/adapt.  :", round(vol_int(J, A), 3), "mm3  (0 = solo apoyan)")
        print("  walki/mango      :", round(vol_int(radio, mango), 3), "mm3")
        # holgura minima (aprox por vertices) entre el conjunto y el mango
        mm = trimesh.load(mango_path); tree = cKDTree(mm.vertices)
        cv = to_tm(cj + radio).vertices
        d, _ = tree.query(cv)
        print("  holgura minima   :", round(d.min(), 2), "mm (aprox.)")
        lim = []
        for sgn in (+1, -1):
            ok = 0
            for deg in range(0, 61, 2):
                if vol_int(rot_y(cj + radio, sgn*deg, xp, sw.PIV_Z), mango) > 0.5: break
                ok = deg
            lim.append(ok)
        print(f"  giro libre alrededor del pivote: +{lim[0]} / -{lim[1]} grados")
    # dedos macho/hembra
    m = to_tm(mango); 
    print("dedos: interseccion macho/hembra =", round(vol_int(A, mango), 3))

if __name__ == "__main__":
    main(sys.argv[1])
