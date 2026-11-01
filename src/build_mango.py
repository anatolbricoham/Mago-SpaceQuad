#!/usr/bin/env python3
"""
Genera el mango SpaceQuad modificado (Bricohams) a partir del STL original.

    python build_mango.py original.stl ../stl/mango_spacequad_tripode.stl

Pasos:
 1. Separa el cuerpo principal del STL original (descarta piezas sueltas).
 2. Lo nivela: alinea el tunel del boom (15,5 x 15,5 mm) con el eje Y y
    lo centra en el origen (X hacia la empunadura, Z hacia la torre).
 3. Anade la funda del duplexor entre la torre y el boom.
 4. Vacia dos alojamientos de tuerca 1/4"-20 en la torre (arriba y lateral -X).
 5. Recorta la punta biselada de la empunadura, la cierra con una base plana
    y mete una tuerca 1/4"-20 para el tripode.
Todas las cotas estan en mm y se pueden cambiar en la seccion PARAMETROS.
"""
import argparse
from pathlib import Path
import sys, collections


def _input_file(value):
    path = Path(value)
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"no existe el STL original: {value}")
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
        description="Generador histórico v1; requiere el STL original no incluido y CadQuery.",
        epilog="Ejemplo (si dispones del original): python src/build_mango.py original.stl stl/mango_spacequad_tripode.stl",
    )
    parser.add_argument("source", type=_input_file, help="STL original externo")
    parser.add_argument("destination", type=_output_file, help="STL v1 de salida")
    args = parser.parse_args()
    if Path(args.source).resolve() == Path(args.destination).resolve():
        parser.error("la entrada y la salida no pueden ser el mismo archivo")
    return args


if __name__ == "__main__":
    _cli_args = _parse_cli()

import numpy as np, trimesh, manifold3d as mf, shapely.geometry as sg
import cadquery as cq

# ------------------------------------------------------------------ PARAMETROS
NUT_AF, NUT_T, NUT_HOLE = 11.4, 5.9, 6.6   # tuerca 1/4"-20: entre caras, grosor, taladro paso
NUT_DEPTH = 3.0                            # plastico entre la cara y la tuerca
DUP_D, DUP_H, DUP_WALL, DUP_LIP = 16.0, 32.0, 3.0, 4.0   # funda duplexor (hueco interior D x H)
DUP_Y0, DUP_Y1 = 123.6, 171.6              # largo de la funda (48 mm)
BUTT_CUT, BUTT_FACE = 100.0, 110.0         # plano de corte y cara del culo (X)
PLUG_DEPTH = 12.0                          # tapon macizo dentro de la empunadura
# geometria del mango original ya nivelado (medida sobre el STL)
TX, TY0, TY1, TZ_TOP = -46.14, 136.32, 158.82, 62.72   # torre
TX_PLUS, TX_MINUS = -33.64, -58.64                    # caras +X / -X de la torre
BASE_TOP = 12.2                                         # cara superior de la base

# ------------------------------------------------------------------ utilidades
def M(m):  return mf.Manifold(mf.Mesh(vert_properties=np.asarray(m.vertices, np.float32),
                                      tri_verts=np.asarray(m.faces, np.uint32)))
def T(Mn): g = Mn.to_mesh(); return trimesh.Trimesh(g.vert_properties[:, :3], g.tri_verts)
def cqm(wp):
    v, f = wp.val().tessellate(0.02, 0.1)
    return trimesh.Trimesh([(p.x, p.y, p.z) for p in v], f)
def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1-x0, y1-y0, z1-z0, centered=False).translate((x0, y0, z0))

def tunnel_loops(m, ys):
    out = []
    for y in ys:
        s = m.section(plane_origin=[0, y, 0], plane_normal=[0, 1, 0])
        if s is None: continue
        for e in s.discrete:
            P = np.asarray(e)
            if 14 < np.ptp(P[:, 0]) < 17 and 14 < np.ptp(P[:, 2]) < 17: out.append((y, P))
    return out

def level(m):
    L = tunnel_loops(m, np.linspace(84, 172, 23))
    C = np.array([[(P[:, 0].min()+P[:, 0].max())/2, y, (P[:, 2].min()+P[:, 2].max())/2] for y, P in L])
    kx = np.polyfit(C[:, 1], C[:, 0], 1); kz = np.polyfit(C[:, 1], C[:, 2], 1)
    d = np.array([kx[0], 1, kz[0]]); d /= np.linalg.norm(d)
    m.apply_transform(trimesh.geometry.align_vectors(d, [0, 1, 0]))
    ang = []
    for y, P in tunnel_loops(m, np.linspace(90, 165, 8)):
        Q = P[:, [0, 2]]
        ang.append(min((np.ptp(Q @ np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]]), axis=0).sum(), t)
                       for t in np.radians(np.linspace(-3, 3, 241)))[1])
    a = np.median(ang); c, s = np.cos(a), np.sin(a)
    R = np.eye(4); R[0, 0] = c; R[0, 2] = s; R[2, 0] = -s; R[2, 2] = c
    m.apply_transform(R)
    # align_vectors puede dejarlo girado 180 grados: torre hacia +Z, empunadura hacia +X
    v = m.vertices
    if v[:, 2].max() - v[:, 2].mean() < v[:, 2].mean() - v[:, 2].min():
        m.apply_transform(np.diag([-1, 1, -1, 1.0]))
    y, P = tunnel_loops(m, [127])[0]
    m.apply_translation([-(P[:, 0].min()+P[:, 0].max())/2, 0, -(P[:, 2].min()+P[:, 2].max())/2])
    return m

def duplexer_sleeve():
    xf0 = TX_PLUS + DUP_D; xf1 = xf0 + DUP_WALL; zt = BASE_TOP + DUP_H; t = DUP_WALL
    c = box(TX_PLUS-0.6, xf1, DUP_Y0, DUP_Y1, BASE_TOP-t, BASE_TOP+0.5)            # suelo
    c = c.union(box(xf0, xf1, DUP_Y0, DUP_Y1, BASE_TOP-t, zt+t))                    # pared frontal
    c = c.union(box(xf0-DUP_LIP, xf1, DUP_Y0, DUP_Y1, zt, zt+t))                    # pestana frontal
    c = c.union(box(TX_PLUS-t, TX_PLUS+0.6, DUP_Y0, TY0+0.5, BASE_TOP-t, zt+t))     # trasera (-Y)
    c = c.union(box(TX_PLUS-t, TX_PLUS+0.6, TY1-0.5, DUP_Y1, BASE_TOP-t, 21.0))     # trasera (+Y)
    c = c.union(box(TX_PLUS-t, TX_PLUS+0.6+DUP_LIP, DUP_Y0, TY0+0.5, zt, zt+t))     # pestana trasera
    return c

def tower_nut_cuts():
    tyc = (TY0+TY1)/2
    z1 = TZ_TOP - NUT_DEPTH - NUT_T                     # rosca superior (walki)
    c = cq.Workplane("XY").circle(NUT_HOLE/2).extrude(TZ_TOP+1-(z1-7)).translate((TX, tyc, z1-7))
    c = c.union(box(TX-NUT_AF/2, TX+NUT_AF/2, TY0-1, tyc+NUT_AF/2, z1, z1+NUT_T))
    zs = 32.0                                           # rosca lateral -X (movil)
    c = c.union(cq.Workplane("YZ").circle(NUT_HOLE/2).extrude(20).translate((TX_MINUS-1, tyc, zs)))
    c = c.union(box(TX_MINUS+NUT_DEPTH, TX_MINUS+NUT_DEPTH+NUT_T, TY0-1, tyc+NUT_AF/2, zs-NUT_AF/2, zs+NUT_AF/2))
    return c

def ext(poly, x0, x1):
    m = trimesh.creation.extrude_polygon(poly.simplify(0.05), x1-x0)
    v = m.vertices.copy(); m.vertices = np.c_[v[:, 2]+x0, v[:, 0], v[:, 1]]
    if m.volume < 0: m.invert()
    return m

def build(src, dst):
    raw = trimesh.load(src)
    body = max(raw.split(only_watertight=False), key=lambda p: len(p.faces))
    h = level(body)
    # culo de la empunadura
    s = h.section(plane_origin=[BUTT_CUT, 0, 0], plane_normal=[1, 0, 0])
    loops = sorted([np.asarray(e)[:, 1:] for e in s.discrete if len(e) > 20], key=lambda P: -sg.Polygon(P).area)
    outer, inner = sg.Polygon(loops[0]).buffer(0), sg.Polygon(loops[1]).buffer(0)
    cap = M(ext(outer, BUTT_CUT-0.5, BUTT_FACE-1.0)) + M(ext(outer.buffer(-1.0), BUTT_FACE-1.01, BUTT_FACE))
    plug = M(ext(inner.buffer(0.3), BUTT_CUT-PLUG_DEPTH, BUTT_CUT))
    yc = (outer.bounds[0]+outer.bounds[2])/2; zc = (outer.bounds[1]+outer.bounds[3])/2
    slot = trimesh.creation.box(bounds=[[BUTT_FACE-NUT_DEPTH-NUT_T, yc-NUT_AF/2, zc-40], [BUTT_FACE-NUT_DEPTH, yc+NUT_AF/2, zc]])
    hole = trimesh.creation.cylinder(radius=NUT_HOLE/2, height=18, sections=48)
    hole.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0])); hole.apply_translation([BUTT_FACE-8, yc, zc])
    half = M(trimesh.creation.box(bounds=[[-500, -500, -500], [BUTT_CUT, 500, 500]]))
    R = ((M(h) ^ half) + cap + plug + M(cqm(duplexer_sleeve()))) - M(cqm(tower_nut_cuts())) - M(slot) - M(hole)
    out = T(R)
    out = trimesh.util.concatenate([p for p in out.split(only_watertight=False) if abs(p.volume) > 10])
    out.apply_translation([0, 0, -out.bounds[0, 2]])
    out.export(dst)
    print(f"OK -> {dst}  medidas {np.round(out.extents,1)} mm  volumen {R.volume()/1000:.0f} cm3")

if __name__ == "__main__":
    build(_cli_args.source, _cli_args.destination)
