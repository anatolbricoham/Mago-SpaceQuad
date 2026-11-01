#!/usr/bin/env python3
"""Comprobaciones del mango v3 (soporte de clip revisado): pieza estanca y de un solo solido, cambios localizados
en el soporte del clip respecto a la v3 original (c77de14), recorrido de la lengua del clip, hueco de la empunadura,
duplexor, walki colgado y tuerca unica del tripode.
    python verificar.py ../stl/mango_spacequad_v3.stl
Las dimensiones del clip (CLIP_W_MIN..CLIP_W_MAX x CLIP_T_MAX) son ESTIMACIONES de ingenieria, no medidas verificadas."""
import sys, io, subprocess, numpy as np, trimesh
import shapely.geometry as sg
from geom import *
import mango_v3 as mg

# duplexor (el mismo bloque que se dibuja en render_docs.py) y walki tipo (ancho Y x grueso Z x alto X)
DUP = (-33.4, -17.9, 118.0, 177.0, 28.0, 59.5)
R_W, R_T, R_L, R_ABOVE = 62.0, 40.0, 130.0, 25.0   # R_ABOVE: lo que sobresale el walki por encima del clip
FZ = 78.32                                          # cara +Z de la torre en v1 (base de la lengueta)
ROOT = __file__.rsplit("src", 1)[0]
V1 = ROOT + "stl/mango_spacequad_tripode.stl"
BASE_REV = "c77de14"                                # v3 original (lengueta de 42 mm), sacada de git
CLIPS = (25.0, 30.0, 35.0, 40.0, 45.0)              # anchos de lengua probados (estimados)
SCREW = 10.0                                        # tornillo del tripode (estimado)

def baseline():
    raw = subprocess.run(["git", "-C", ROOT, "show", f"{BASE_REV}:stl/mango_spacequad_v3.stl"],
                         capture_output=True, check=True).stdout
    return trimesh.load(io.BytesIO(raw), file_type="stl")

def walki(fz=FZ, w=R_W):
    """walki apoyado en la cara exterior de la lengueta, con el clip hasta el borde superior"""
    x_t = mg.X_BOT - mg.CLIP_L
    zo = lambda x: mg.z_in(x, fz) + mg.PLATE_T
    xa, xb = x_t - R_ABOVE, x_t - R_ABOVE + R_L
    p = sg.Polygon([(xa, zo(xa)), (xb, zo(xb)), (xb, zo(xb) + R_T), (xa, zo(xa) + R_T)])
    return prism_y(mg.xz(p), YC - w/2, YC + w/2)

def duplexor():
    return to_mf(trimesh.creation.box(bounds=[DUP[0::2], DUP[1::2]]))

def tongue(w, depth, on_plate=False, fz=FZ):
    """lengua del clip (ancho w, grueso CLIP_T_MAX, largo USABLE_L) con la punta a `depth` mm de la boca, pegada a la
    pared trasera o (on_plate) a la cara interior de la lengueta, siguiendo su pendiente"""
    x_tip = mg.X_BOT - mg.CLIP_L + depth
    x_end = x_tip - mg.USABLE_L
    if on_plate:
        top = lambda x: mg.z_in(x, fz) - 0.05
        p = sg.Polygon([(x_tip, top(x_tip) - mg.CLIP_T_MAX), (x_end, top(x_end) - mg.CLIP_T_MAX), (x_end, top(x_end)), (x_tip, top(x_tip))])
    else:
        zb = fz + mg.BACK_T + 0.05
        p = sg.Polygon([(x_tip, zb), (x_end, zb), (x_end, zb + mg.CLIP_T_MAX), (x_tip, zb + mg.CLIP_T_MAX)])
    return prism_y(mg.xz(p), YC - w/2, YC + w/2)
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
    def sdiff(a, b): return (a - b) + (b - a)
    x_t, x_f, zb = mg.X_BOT - mg.CLIP_L, mg.X_BOT - mg.FLOOR, FZ + mg.BACK_T
    print("pieza:")
    check("estanca (manifold)", mango.status().name == "NoError")
    vols = [c.volume() for c in mango.decompose()]     # el hueco interior de la empunadura sale con volumen < 0
    check("un solo solido", sum(v > 0 for v in vols) == 1, f"{mango.volume()/1000:.1f} cm3")

    print("localidad frente a la v3 original (%s):" % BASE_REV)
    base = to_mf(baseline())
    sd = sdiff(mango, base)
    wy = mg.W_IN / 2 + mg.SIDE_T
    env = box(-(mg.X_BOT + 1 - FACE_X), -(x_t - 2 - FACE_X) , YC - wy - 1, YC + wy + 1, FZ - 3.5, FZ + 60)
    outside = sd - env
    check("hay cambio en el soporte", sd.volume() > 100, f"{sd.volume():.0f} mm3 de diferencia simetrica")
    check("diferencia simetrica fuera del soporte ~ 0 (ruido float32)", outside.volume() < 1e-3, f"{outside.volume():.6f} mm3")
    bvols = sorted(round(c.volume(), 1) for c in base.decompose() if c.volume() < 0)
    nvols = sorted(round(c.volume(), 1) for c in mango.decompose() if c.volume() < 0)
    check("hueco de la empunadura intacto", bvols == nvols, f"{nvols} mm3")
    v1 = to_mf(trimesh.load(V1))
    extra = (dup ^ mango).volume() - (dup ^ v1).volume()
    check("duplexor: nada nuevo respecto a v1", abs(extra) < 0.01, f"{extra:.3f} mm3")
    check("duplexor: igual que en la v3 original", abs((dup ^ mango).volume() - (dup ^ base).volume()) < 0.01)

    print("recorrido del clip (anchos y grueso ESTIMADOS):")
    depths = [d for d in np.arange(0.0, mg.USABLE_L + 0.1, 5.0)]
    for w in CLIPS:
        for plate in (False, True):
            hits = [(tongue(w, d, plate) ^ mango).volume() for d in depths]
            full = max((d for d, h in zip(depths, hits) if h < 0.01), default=0.0) if all(h < 0.01 for h in hits[:1]) else 0.0
            check(f"lengua {w:.0f} x {mg.CLIP_T_MAX:.0f} mm barrida de la boca a {full:.0f} mm, {'sobre la lengueta' if plate else 'sobre la pared'}",
                  all(h < 0.01 for h in hits) and full >= 40.0, f"max choque {max(hits):.3f} mm3")
    check("45 x 6 mm a fondo: holgura lateral a cada lado >= 1 mm", (mg.W_NARROW - 45.0) / 2 >= 1.0 - 1e-9,
          f"{(mg.W_NARROW - 45.0) / 2:.1f} mm")
    check("lengua > boca (W_IN + 1) no cabe", (tongue(mg.W_IN + 1, 40.0) ^ mango).volume() > 1.0)
    print("  NOTA: lengua estrecha (25-30 mm) queda holgada lateralmente; la sujeta el muelle del propio clip, sin centrado")
    gap_min = min(mg.z_in(x, FZ) - zb for x in (x_f, x_t))
    check(f"holgura minima del canal >= {mg.MIN_CLEAR:.0f} mm", gap_min >= mg.MIN_CLEAR - 1e-6, f"{gap_min:.1f} mm")
    xm = x_f - 20
    ym = lambda s: YC + s * (mg.half_in(xm) + 1.0)
    check("paredes laterales macizas en cuna", solid([[xm, ym(-1), zb + 8], [xm, ym(1), zb + 8]]).all())
    check("canal abierto entre paredes", not solid([[xm, YC + 0.0, zb + 2], [xm, YC + mg.half_in(xm) - 0.5, zb + 2]]).any())
    check("fondo cerrado", solid([[mg.X_BOT - mg.FLOOR / 2, YC, zb + 2]])[0])
    check("boca abierta (sin pared en el extremo superior)", not solid([[x_t + 0.5, YC, zb + 2]])[0])
    zi = mg.z_in(xm, FZ)
    check("lengueta maciza", solid([[xm, YC + mg.WIN_W / 2 + 2, zi + mg.PLATE_T / 2]])[0], f"{mg.PLATE_T} mm")
    xw = mg.X_BOT - mg.FLOOR - mg.WIN_X            # la ventana ocupa x en [xw - WIN_H, xw] (como en la v3 original)
    xwc = xw - mg.WIN_H / 2
    zi = mg.z_in(xwc, FZ)
    win = [[xwc, YC + dy, zi + mg.PLATE_T / 2] for dy in (-mg.WIN_W/2 + 1, 0, mg.WIN_W/2 - 1)]
    check("ventana rectangular de retencion abierta", not solid(win).any(), f"{mg.WIN_W:.0f} x {mg.WIN_H:.0f} mm")
    frame = [[xwc, YC + s * (mg.WIN_W/2 + 1), zi + mg.PLATE_T / 2] for s in (-1, 1)] \
          + [[xw + 1, YC, zi + mg.PLATE_T / 2], [xw - mg.WIN_H - 1, YC, zi + mg.PLATE_T / 2]]
    check("marco macizo alrededor de la ventana", solid(frame).all())

    print("walki:")
    for w in (50.0, R_W, 70.0):
        W = walki(w=w)
        check(f"walki {w:.0f} mm / mango", (W ^ mango).volume() < 0.01, f"{(W ^ mango).volume():.3f} mm3")
        check(f"walki {w:.0f} mm / duplexor", (W ^ dup).volume() < 0.01)
    d = trimesh.proximity.signed_distance(to_tm(walki()), to_tm(dup).vertices)
    check("separacion walki-duplexor > 10 mm", -d.max() > 10, f"{-d.max():.1f} mm")

    print("tuerca del tripode (una sola):")
    face, sk, y = mg.BUTT_FACE, mg.TRIPOD_SKIN, mg.T_YC + 4.5
    z = mg.T_ZC - 2
    inside = solid([[face - sk / 2, y, z], [face - sk - 0.5, y, z],
                    [face - sk - mg.NUT_T + 0.5, y, z], [face - sk - mg.NUT_T - 0.5, y, z]])
    check("piel delante de la tuerca", inside[0] and not inside[1], f"{sk} mm (v1: {mg.OLD_SKIN} mm)")
    check("ranura para UNA tuerca", not inside[2] and inside[3], f"{mg.NUT_T} mm")
    check("la rosca empieza a menos de 2 mm de la cara", sk <= 2.0)
    check("grosor nominal de la tuerca <= ranura", mg.NUT_T_NOMINAL <= mg.NUT_T, f"{mg.NUT_T_NOMINAL} <= {mg.NUT_T} mm")
    eng = min(mg.NUT_T_NOMINAL, SCREW - sk)
    print(f"  SUPUESTO: rosca engranada = {eng:.1f} mm, limitada por la tuerca nominal ({mg.NUT_T_NOMINAL} mm); la ranura vacia ({mg.NUT_T} mm) no demuestra rosca")
    check(f"tornillo de {SCREW:.0f} mm: rosca nominal >= 5 mm", eng >= 5.0, f"{eng:.1f} mm")
    print("TODO OK" if ok else "HAY FALLOS"); return ok

if __name__ == "__main__":
    sys.exit(0 if main(sys.argv[1]) else 1)
