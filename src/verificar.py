#!/usr/bin/env python3
"""Comprobaciones del mango v4: pieza estanca, canal del clip libre, walki colgado sin tocar mango ni duplexor,
voladizos nuevos (sin soportes) y rosca del tripode.
    python verificar.py ../stl/mango_spacequad_v4.stl"""
import sys, numpy as np, trimesh
from geom import *
import mango_v4 as mg

# duplexor (el mismo bloque que se dibuja en render_docs.py) y walki tipo (ancho Y x grueso Z x alto X)
DUP = (-33.4, -17.9, 118.0, 177.0, 28.0, 59.5)
R_W, R_T, R_L, R_ABOVE = 62.0, 40.0, 130.0, 25.0   # R_ABOVE: lo que sobresale el walki por encima del clip
CLIP_PL = 55.0                                      # largo de la lengua del clip (de la bisagra a la punta)
CLIPS = (25.0, 30.0, 35.0, 40.0, 45.0)              # anchos de lengua probados
SCREW = 10.0                                        # tornillo del tripode
V1 = __file__.rsplit("src", 1)[0] + "stl/mango_spacequad_tripode.stl"

def stop(w):
    """x donde se acuna la punta de una lengua de ancho w"""
    return mg.X_TOP + (mg.W_TOP - w) * (mg.X_TIP - mg.X_TOP) / (mg.W_TOP - mg.W_TIP)

def walki(w=35.0):
    """walki con la espalda sobre los labios y la punta del clip acunada en el canal"""
    z0, x0 = mg.CH_ZF + mg.GAP + mg.LIP + mg.LIP_TIP, stop(w) - CLIP_PL - R_ABOVE
    return to_mf(trimesh.creation.box(bounds=[[x0, mg.CH_YC - R_W/2, z0 + 0.05], [x0 + R_L, mg.CH_YC + R_W/2, z0 + R_T]]))

def duplexor():
    return to_mf(trimesh.creation.box(bounds=[DUP[0::2], DUP[1::2]]))

def main(path):
    m = trimesh.load(path)
    mango, dup = to_mf(m), duplexor()
    def solid(pts):   # trimesh.contains falla con las caras degeneradas de la textura: se mira con manifold
        return np.array([(mango ^ to_mf(trimesh.creation.box(bounds=[np.subtract(p, 0.05), np.add(p, 0.05)]))).volume() > 1e-4
                         for p in pts])
    ok = True
    def check(name, cond, val=""):
        nonlocal ok; ok &= bool(cond)
        print(f"  [{'OK' if cond else 'FALLO'}] {name} {val}")
    print("pieza:")
    check("estanca (manifold)", mango.status().name == "NoError")
    vols = [c.volume() for c in mango.decompose()]     # el hueco interior de la empunadura sale con volumen < 0
    check("un solo solido", sum(v > 0 for v in vols) == 1, f"{mango.volume()/1000:.1f} cm3")
    print("canal del clip:")
    zf = mg.CH_ZF
    for w in CLIPS:
        x = stop(w)
        check(f"lengua {w:.0f} mm entra y se acuna", mg.X_TOP <= x <= mg.X_TIP, f"a {x - mg.X_TOP:.0f} mm de la boca")
        free = solid([[x - 1, mg.CH_YC + s * (w/2 - 0.5), zf + z] for s in (-1, 1) for z in (0.3, mg.GAP - 0.3)])
        lips = solid([[x - 1, mg.CH_YC + s * (mg.width(x - 1)/2 - mg.LIP + 0.3), zf + mg.GAP + mg.LIP + mg.LIP_TIP/2]
                           for s in (-1, 1)])
        check(f"  hueco libre de {mg.GAP:.0f} mm y labios encima", not free.any() and lips.all())
    check("tope cerrado en la punta", solid([[mg.X_TIP + mg.END_T/2, mg.CH_YC, zf + 2]])[0])
    print("walki:")
    for w in CLIPS:
        W = walki(w)
        check(f"walki con clip de {w:.0f} mm / mango", (W ^ mango).volume() < 0.01, f"{(W ^ mango).volume():.3f} mm3")
        d = trimesh.proximity.signed_distance(to_tm(W), to_tm(dup).vertices)
        check(f"walki con clip de {w:.0f} mm / duplexor > 2 mm", -d.max() > 2, f"{-d.max():.1f} mm")
    v1 = to_mf(trimesh.load(V1))
    extra = (dup ^ mango).volume() - (dup ^ v1).volume()
    check("duplexor: nada nuevo respecto a v1", abs(extra) < 0.01, f"{extra:.3f} mm3")
    print("impresion (orientacion del STL, cama en z = 0):")
    c, n = m.triangles_center, m.face_normals
    nut = (c[:, 0] > 94) & (abs(c[:, 1] - mg.T_YC) < 7) & (c[:, 2] < mg.T_ZC + 4)   # puente de la ranura y taladro
    steep = (c[:, 0] > mg.X_LEAD - 1) & (n[:, 2] < -0.72) & ~nut          # mas de 45 grados mirando abajo
    steep[steep] = trimesh.proximity.closest_point(trimesh.load(V1), c[steep])[1] > 0.05   # solo caras nuevas
    check("canal y zocalo sin voladizos de mas de 45 grados", m.area_faces[steep].sum() < 10.0,   # queda una astilla de ~5 mm2 en el techo del hueco interior
          f"{m.area_faces[steep].sum():.2f} mm2")
    print("tuerca del tripode:")
    face, sk, y, z = mg.BUTT_FACE, mg.TRIPOD_SKIN, mg.T_YC + 4.5, mg.T_ZC - 2
    depth = mg.NUT_N * mg.NUT_T
    inside = solid([[face - sk / 2, y, z], [face - sk - 0.5, y, z],
                         [face - sk - depth + 0.5, y, z], [face - sk - depth - 0.5, y, z]])
    check("piel delante de la tuerca", inside[0] and not inside[1], f"{sk} mm")
    check(f"ranura para {mg.NUT_N} tuercas", not inside[2] and inside[3], f"{depth:.1f} mm")
    check("la rosca empieza a menos de 2 mm de la cara", sk <= 2.0)
    eng = min(depth, SCREW - sk)
    check(f"tornillo de {SCREW:.0f} mm coge al menos 6 mm", eng >= 6.0, f"{eng:.1f} mm")
    print("TODO OK" if ok else "HAY FALLOS"); return ok

if __name__ == "__main__":
    sys.exit(0 if main(sys.argv[1]) else 1)
