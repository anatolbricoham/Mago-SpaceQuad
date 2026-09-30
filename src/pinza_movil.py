#!/usr/bin/env python3
"""
Pinza ajustable para movil con tuerca 1/4"-20 (para brazo de rotula).

    python pinza_movil.py ../stl ../step

Genera pinza_movil_cuerpo y pinza_movil_mordaza en STL (orientados para
imprimir, cara trasera sobre la cama) y en STEP.
Rango: moviles de 58 a 92 mm de ancho y hasta 12 mm de grosor con funda.
"""
import os, sys
import numpy as np, trimesh
import cadquery as cq

# ------------------------------------------------------------------ PARAMETROS
BT, BH, BL = 10.0, 16.0, 116.0          # barra: grosor, alto, largo
JT, JD, LIP, JH = 4.0, 12.0, 3.0, 44.0  # mordaza: pared, fondo (movil+funda), pestana, alto
NX = 41.0                               # posicion de la tuerca 1/4"
NUT_AF = 11.4                           # tuerca 1/4"-20 entre caras (+holgura)
C, W, SL = 0.35, 3.0, 20.0              # corredera: holgura, pared, largo
M4_AF = 7.3                             # tuerca M4 entre caras (+holgura)

def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1-x0, y1-y0, z1-z0, centered=False).translate((x0, y0, z0))

Z0 = BH/2 - JH/2

def cuerpo():
    body = box(0, BL, 0, BT, 0, BH)
    body = body.union(box(0, JT, -JD, BT, Z0, Z0+JH)).union(box(0, JT+LIP, -JD-2.5, -JD, Z0, Z0+JH))
    nut = cq.Workplane("XZ").polygon(6, NUT_AF/np.cos(np.pi/6)).extrude(-(BT-3)).translate((NX, -0.01, BH/2))
    hole = cq.Workplane("XZ").circle(3.3).extrude(-(BT+2)).translate((NX, -1, BH/2))
    return body.cut(nut).cut(hole)

def mordaza(xi=4.0 + 75.0):
    sl = box(xi, xi+SL, -C-W, BT+C+W, -C-W, BH+C+W).cut(box(xi-1, xi+SL+1, -C, BT+C, -C, BH+C))
    sj = sl.union(box(xi, xi+JT, -JD, -C-W+0.01, Z0, Z0+JH)).union(box(xi-LIP, xi+JT, -JD-2.5, -JD, Z0, Z0+JH))
    top = BH+C+W
    sj = sj.union(box(xi+SL/2-6, xi+SL/2+6, BT/2-6, BT/2+6, top-0.01, top+5))            # refuerzo
    sj = sj.cut(cq.Workplane("XY").circle(1.7).extrude(20).translate((xi+SL/2, BT/2, BH)))  # M4
    sj = sj.cut(box(xi+SL/2-M4_AF/2, xi+SL/2+7, BT/2-M4_AF/2, BT/2+M4_AF/2, top+0.8, top+0.8+3.5))  # tuerca M4
    return sj

def export(wp, name, stl_dir, step_dir):
    cq.exporters.export(wp, os.path.join(step_dir, name + ".step"))
    tmp = os.path.join(stl_dir, name + ".stl")
    cq.exporters.export(wp, tmp, tolerance=0.01, angularTolerance=0.05)
    m = trimesh.load(tmp)
    m.apply_transform(trimesh.transformations.rotation_matrix(-np.pi/2, [1, 0, 0]))  # trasera abajo
    m.apply_translation(-m.bounds[0]); m.export(tmp)
    print(f"OK -> {name}: {np.round(m.extents,1)} mm, {wp.val().Volume()/1000:.1f} cm3")

if __name__ == "__main__":
    stl_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    step_dir = sys.argv[2] if len(sys.argv) > 2 else stl_dir
    os.makedirs(stl_dir, exist_ok=True); os.makedirs(step_dir, exist_ok=True)
    export(cuerpo(), "pinza_movil_cuerpo", stl_dir, step_dir)
    export(mordaza(), "pinza_movil_mordaza", stl_dir, step_dir)
