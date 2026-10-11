#!/usr/bin/env python3
"""Genera las imagenes de docs/img (vista de uso y despiece). Requiere pyvista.
    python render_docs.py ../stl ../docs/img"""
import sys, os, numpy as np, trimesh, pyvista as pv
from geom import *
import soporte_walki as sw
pv.OFF_SCREEN = True

def rot(m):   # (x,y,z)->(z,y,-x): empunadura hacia abajo, boom horizontal
    R = np.array([[0,0,1,0],[0,1,0,0],[-1,0,0,0],[0,0,0,1.0]]); m = m.copy(); m.apply_transform(R); return m

def bx(x0,x1,y0,y1,z0,z1): return trimesh.creation.box(bounds=[[x0,y0,z0],[x1,y1,z1]])

def scene(stl_dir, W=62):
    mango = trimesh.load(os.path.join(stl_dir, 'mango_spacequad_v2.stl'))
    A = to_tm(sw.adaptador()); J = to_tm(sw.mordaza(1,W)+sw.mordaza(-1,W))
    radio = to_tm(box(sw.PL_U1, sw.PL_U1+35, YC-55, YC+55, sw.PIV_Z-W/2, sw.PIV_Z+W/2))
    boom = bx(-7.5,7.5,60,300,8,23.1)
    dup = bx(-33.4,-17.9,118,177,28,59.5)
    return mango, A, J, radio, boom, dup

def main(stl_dir, out):
    os.makedirs(out, exist_ok=True)
    mango, A, J, radio, boom, dup = scene(stl_dir)
    parts = [(mango,'#8d9399',1),(A,'#e07a1f',1),(J,'#2b6cc4',1),(radio,'#2e9e5b',0.9),(boom,'#c9ced3',1),(dup,'#c0392b',1)]
    # --- vista de uso
    pl = pv.Plotter(off_screen=True, shape=(1,2), window_size=(1600,760))
    c = np.array([40, 150, 15.0])
    for i, v in enumerate([(1,-1.6,0.55),(-1,-1.2,0.5)]):
        pl.subplot(0, i)
        for m,col,op in parts: pl.add_mesh(pv.wrap(rot(m)), color=col, opacity=op, smooth_shading=False)
        pl.camera_position = [tuple(c+np.array(v)*420), tuple(c), (0,0,1)]
        pl.set_background('white')
    pl.subplot(0,0); pl.add_text('Posicion de uso: empunadura abajo. Verde: walki   Azul: mordazas   Naranja: adaptador GoPro   Rojo: duplexor', font_size=9, position='lower_left', color='black')
    pl.screenshot(os.path.join(out,'vista_uso.png'))
    # --- despiece
    pl = pv.Plotter(off_screen=True, window_size=(1100,900))
    sh = lambda m,d: (lambda t:(t.apply_translation(d),t)[1])(rot(m))
    items = [(mango,'#8d9399',(0,0,0),'Mango v2 (base GoPro 3 dedos)'),
             (A,'#e07a1f',(70,0,0),'Adaptador GoPro + placa con ranuras'),
             (J,'#2b6cc4',(130,0,0),'2 mordazas ajustables 50-86 mm')]
    for m,col,d,lab in items:
        t = rot(m); t.apply_translation(d); pl.add_mesh(pv.wrap(t), color=col)
    pl.set_background('white')
    pl.camera_position = [(110,-480,260),(40,150,-10),(0,0,1)]
    pl.add_text('Despiece: mango v2 - adaptador - mordazas (x2)', font_size=11, position='upper_left', color='black')
    pl.screenshot(os.path.join(out,'mango_detalles.png'))

if __name__ == '__main__':
    main(*sys.argv[1:3])
