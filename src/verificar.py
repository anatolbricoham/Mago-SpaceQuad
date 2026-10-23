#!/usr/bin/env python3
"""Comprobaciones del mango v3: pieza estanca, walki colgado de la lengueta sin tocar mango ni duplexor,
hueco del clip y piel de la tuerca del tripode.
    python verificar.py ../stl/mango_spacequad_v3.stl"""
import sys, numpy as np, trimesh
import shapely.geometry as sg
from geom import *
import mango_v3 as mg

# duplexor (el mismo bloque que se dibuja en render_docs.py) y walki tipo (ancho Y x grueso Z x alto X)
DUP = (-33.4, -17.9, 118.0, 177.0, 28.0, 59.5)
R_W, R_T, R_L, R_ABOVE = 62.0, 40.0, 130.0, 25.0   # R_ABOVE: lo que sobresale el walki por encima del clip
FZ = 78.32                                          # cara +Z de la torre en v1 (base de la lengueta)
V1 = __file__.rsplit("src", 1)[0] + "stl/mango_spacequad_tripode.stl"

def walki(fz=FZ, w=R_W):
    """walki apoyado en la cara exterior de la lengueta, con el clip hasta el borde superior"""
    x_t = mg.X_BOT - mg.CLIP_L
    zo = lambda x: mg.z_in(x, fz) + mg.PLATE_T
    xa, xb = x_t - R_ABOVE, x_t - R_ABOVE + R_L
    p = sg.Polygon([(xa, zo(xa)), (xb, zo(xb)), (xb, zo(xb) + R_T), (xa, zo(xa) + R_T)])
    return prism_y(mg.xz(p), YC - w/2, YC + w/2)

def duplexor():
    return to_mf(trimesh.creation.box(bounds=[DUP[0::2], DUP[1::2]]))

def main(path):
    m = trimesh.load(path)
    mango, dup = to_mf(m), duplexor()
    ok = True
    def check(name, cond, val=""):
        nonlocal ok; ok &= bool(cond)
        print(f"  [{'OK' if cond else 'FALLO'}] {name} {val}")
    print("pieza:")
    check("estanca (manifold)", mango.status().name == "NoError")
    vols = [c.volume() for c in mango.decompose()]     # el hueco interior de la empunadura sale con volumen < 0
    check("un solo solido", sum(v > 0 for v in vols) == 1, f"{mango.volume()/1000:.1f} cm3")
    print("walki:")
    for w in (50.0, R_W, 70.0):
        W = walki(w=w)
        check(f"walki {w:.0f} mm / mango", (W ^ mango).volume() < 0.01, f"{(W ^ mango).volume():.3f} mm3")
        check(f"walki {w:.0f} mm / duplexor", (W ^ dup).volume() < 0.01)
    d = trimesh.proximity.signed_distance(to_tm(walki()), to_tm(dup).vertices)
    check("separacion walki-duplexor > 10 mm", -d.max() > 10, f"{-d.max():.1f} mm")
    # el bloque del duplexor es aproximado y ya roza la funda del v1: se exige no anadir nada
    v1 = to_mf(trimesh.load(V1))
    extra = (dup ^ mango).volume() - (dup ^ v1).volume()
    check("duplexor: nada nuevo respecto a v1", abs(extra) < 0.01, f"{extra:.3f} mm3")
    print("funda del clip:")
    x_mid = mg.X_BOT - mg.CLIP_L / 2
    zb, zi = FZ + mg.BACK_T, mg.z_in(x_mid, FZ)
    inside = m.contains([[x_mid, YC, zb + 0.5], [x_mid, YC + mg.W_IN/2 - 0.5, (zb + zi) / 2],
                         [x_mid, YC, zi + mg.PLATE_T / 2]])
    check("hueco libre para la lengua del clip", not inside[0] and not inside[1],
          f"{zi - zb:.1f} mm a media altura ({mg.G_BOT}-{mg.G_TOP})")
    check("lengueta maciza", inside[2], f"{mg.PLATE_T} mm")
    print("tuerca del tripode:")
    face, sk, y = mg.BUTT_FACE, mg.TRIPOD_SKIN, mg.T_YC + 4.5
    inside = m.contains([[face - sk / 2, y, mg.T_ZC], [face - sk - 1, y, mg.T_ZC], [face - sk - mg.NUT_T - 0.5, y, mg.T_ZC]])
    check("piel delante de la tuerca", inside[0] and not inside[1], f"{sk} mm (v1: {mg.OLD_SKIN} mm)")
    check("nicho viejo relleno", inside[2])
    print("TODO OK" if ok else "HAY FALLOS"); return ok

if __name__ == "__main__":
    sys.exit(0 if main(sys.argv[1]) else 1)
