#!/usr/bin/env python3
"""
Soporte universal de walki para el mango v2 (enganche GoPro).

    python soporte_walki.py ../stl            # genera las STL de impresion
    python soporte_walki.py ../stl --montado  # ademas, el conjunto montado (para revisar)

Piezas:
  adaptador_gopro_walki   placa con 2 dedos GoPro (macho) + 4 ranuras con canal para tuerca M4.
                          Se imprime con la placa en la cama y los dedos hacia arriba (sin soportes).
  mordaza_walki  (x2)     mordaza en L que se atornilla a la placa por las ranuras; se desliza para
                          cerrar sobre el walki. Cubre de WMIN a WMAX de ancho y hasta TMAX de grosor.
Todo en el mismo sistema de coordenadas que el mango v2 (ver geom.py).
"""
import sys, os
import numpy as np, trimesh
import shapely.geometry as sg
from geom import *
import mango_v2 as mg

# ---------------------------------------------------------------- PARAMETROS (mm)
WMIN, WMAX = 50.0, 86.0      # anchos de walki admitidos (el mas estrecho / el mas ancho del mercado, con margen)
TMAX       = 54.0            # grosor maximo del walki (con bateria grande)
W_DEF      = 62.0            # ancho con el que se dibuja el montaje
PIV_G, PIV_Z, R_PRONG = mg.PIV_G, mg.PIV_Z, mg.R_PRONG
P_T, GAP, Y0 = mg.P_T, mg.GAP, mg.Y0
BOLT_D = mg.BOLT_D
PL_U0, PL_T = PIV_G + R_PRONG + 0.5, 6.5      # cara trasera de la placa (u) y grosor
PL_U1 = PL_U0 + PL_T
PL_LY, PL_LZ = 80.0, 136.0                    # placa: largo (Y) x ancho (Z)
SLOT_Y = 24.0                                 # ranuras a +-SLOT_Y del eje
WALL, FOOT_W, FOOT_T = 4.0, 16.0, 4.5         # mordaza: pared, ancho y grosor del pie
JAW_LY = 76.0                                 # largo de la mordaza en Y
BOLT_Z = WALL + FOOT_W/2                      # centro del tornillo respecto a la cara interior (+WALL+...)
M4_D, NUT4_AF, NUT4_T = 4.6, 7.3, 3.4         # holgura M4, tuerca M4 (7 mm) y su canal

def ztrav():
    """recorrido del centro del tornillo (distancia al eje Z del pivote) para WMIN..WMAX"""
    return WMIN/2 + BOLT_Z, WMAX/2 + BOLT_Z

def stadium(y, za, zb, w, u0, u1):
    """ranura (estadio) alargada en Z, con eje u"""
    r = w/2
    return box(u0, u1, y - r, y + r, za, zb) + cyl_u(y, za, r, u0, u1, 24) + cyl_u(y, zb, r, u0, u1, 24)

def adaptador():
    zc = PIV_Z
    plate = box(PL_U0, PL_U1, YC - PL_LY/2, YC + PL_LY/2, zc - PL_LZ/2, zc + PL_LZ/2)
    # esquinas redondeadas (R6) en el plano YZ
    rr = 6.0
    keep = sg.box(YC - PL_LY/2 + rr, zc - PL_LZ/2 + rr, YC + PL_LY/2 - rr, zc + PL_LZ/2 - rr).buffer(rr, 24)
    ouline = prism_u_yz(keep, PL_U0 - 1, PL_U1 + 1)
    plate = plate ^ ouline
    # dedos macho: perfil (u,z) con el extremo redondo R7,5 y el cuerpo hasta la placa
    c = sg.Point(PIV_G, zc).buffer(R_PRONG, 64)
    prof = sg.MultiPoint([(PL_U0 + 0.5, zc - R_PRONG), (PL_U0 + 0.5, zc + R_PRONG)]).convex_hull.union(c).convex_hull
    hole = teardrop(PIV_G, zc, BOLT_D/2, apex=(-1, 0))
    prof = prof.difference(hole)
    for ya in (Y0 + P_T + 0.15, Y0 + 2*P_T + GAP + 0.15):
        plate = plate + prism_y(prof, ya, ya + P_T)
    # ranuras (cuatro) con canal de tuerca M4 por la cara trasera
    za, zb = ztrav()
    for sy in (-SLOT_Y, SLOT_Y):
        for sz in (-1, 1):
            z0, z1 = sorted((zc + sz*za, zc + sz*zb))
            plate = plate - stadium(YC + sy, z0, z1, M4_D, PL_U0 - 0.5, PL_U1 + 0.5)
            plate = plate - box(PL_U0 - 0.5, PL_U0 + NUT4_T, YC + sy - NUT4_AF/2, YC + sy + NUT4_AF/2, z0 - NUT4_AF/2, z1 + NUT4_AF/2)
    return plate

def prism_u_yz(poly_yz, u0, u1):
    pts = np.asarray(poly_yz.exterior.coords)
    return prism_z_yz([tuple(p) for p in pts[:-1]], u0, u1)

def mordaza(side, w=W_DEF):
    """side=+1 / -1 (lado +Z / -Z del eje del pivote). w = ancho del walki."""
    zc = PIV_Z
    zi = zc + side*w/2               # cara interior
    zo = zi + side*WALL              # cara exterior de la pared
    zf = zo + side*FOOT_W            # fin del pie
    zlo, zhi = sorted((zi, zo))
    h = PL_U1 + TMAX + 1.5           # altura de la pared (u)
    jaw = box(PL_U1, h, YC - JAW_LY/2, YC + JAW_LY/2, zlo, zhi)
    flo, fhi = sorted((zo, zf))
    jaw = jaw + box(PL_U1, PL_U1 + FOOT_T, YC - JAW_LY/2, YC + JAW_LY/2, flo, fhi)
    # cartelas triangulares (u,z) en los extremos de Y
    for yy in (YC - JAW_LY/2, YC + JAW_LY/2 - 3.0):
        tri = sg.Polygon([(PL_U1, zo), (PL_U1, zf), (PL_U1 + FOOT_T, zf), (PL_U1 + 34, zo)])
        # triangulo a partir del pie hasta 34 mm de altura en la pared
        tri = sg.Polygon([(PL_U1 + 0, zo), (PL_U1 + 0, zf), (PL_U1 + 34, zo)])
        jaw = jaw + prism_y(tri, yy, yy + 3.0)
    zb = zo + side*FOOT_W/2
    for sy in (-SLOT_Y, SLOT_Y):
        jaw = jaw - cyl_u(YC + sy, zb, M4_D/2, PL_U1 - 1, PL_U1 + FOOT_T + 1, 24)
        # avellanado para cabeza M4 (Ø7, 3,2 de alto) por la cara superior del pie
        jaw = jaw - cyl_u(YC + sy, zb, 3.8, PL_U1 + FOOT_T - 3.0, PL_U1 + FOOT_T + 1, 24)
    return jaw

def export_print(M, path, kind):
    m = to_tm(M)
    if kind == "adaptador":     # (x,y,z)->(y,z,x): placa en la cama, dedos arriba
        R = np.array([[0,1,0,0],[0,0,1,0],[1,0,0,0],[0,0,0,1.0]])
        m.apply_transform(R)
        m.apply_translation([-m.bounds[0,0] - m.extents[0]/2, -m.bounds[0,1] - m.extents[1]/2, -m.bounds[0,2]])
    else:                       # (x,y,z)->(z,y,-x): pie en la cama, pared hacia arriba
        R = np.array([[0,0,1,0],[0,1,0,0],[-1,0,0,0],[0,0,0,1.0]])
        m.apply_transform(R)
        m.apply_translation([-m.bounds[0,0], -m.bounds[0,1], -m.bounds[0,2]])
    m.export(path)
    print(f"OK -> {path} {np.round(m.extents,1)} mm {M.volume()/1000:.1f} cm3")

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out, exist_ok=True)
    A = adaptador(); J1 = mordaza(+1)
    export_print(A, os.path.join(out, "adaptador_gopro_walki.stl"), "adaptador")
    export_print(J1, os.path.join(out, "mordaza_walki.stl"), "mordaza")
