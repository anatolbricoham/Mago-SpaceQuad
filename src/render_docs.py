#!/usr/bin/env python3
"""Genera las imagenes de docs/img (vista de uso y detalle del canal del clip). Requiere pyvista.
    python render_docs.py ../stl ../docs/img"""
import sys, os, numpy as np, trimesh, pyvista as pv
from geom import *
import verificar as vf
pv.OFF_SCREEN = True

def rot(m):   # (x,y,z)->(z,y,-x): empunadura hacia abajo, boom horizontal
    R = np.array([[0,0,1,0],[0,1,0,0],[-1,0,0,0],[0,0,0,1.0]]); m = m.copy(); m.apply_transform(R); return m

def bx(x0,x1,y0,y1,z0,z1): return trimesh.creation.box(bounds=[[x0,y0,z0],[x1,y1,z1]])

def main(stl_dir, out):
    os.makedirs(out, exist_ok=True)
    mango = trimesh.load(os.path.join(stl_dir, 'mango_spacequad_v4.stl'))
    radio, dup = to_tm(vf.walki()), to_tm(vf.duplexor())
    boom = bx(-7.5,7.5,60,300,8,23.1)
    parts = [(mango,'#8d9399',1),(radio,'#2e9e5b',0.6),(boom,'#c9ced3',1),(dup,'#c0392b',1)]
    # --- vista de uso
    pl = pv.Plotter(off_screen=True, shape=(1,2), window_size=(1600,760))
    c = np.array([60, 150, 40.0])
    for i, v in enumerate([(1,-1.6,0.55),(-1,-1.2,0.5)]):
        pl.subplot(0, i)
        for m,col,op in parts: pl.add_mesh(pv.wrap(rot(m)), color=col, opacity=op, smooth_shading=False)
        pl.camera_position = [tuple(c+np.array(v)*480), tuple(c), (0,0,1)]
        pl.set_background('white')
    pl.subplot(0,0); pl.add_text('Posicion de uso: empunadura abajo. Verde: walki colgado del clip   Rojo: duplexor', font_size=9, position='lower_left', color='black')
    pl.screenshot(os.path.join(out,'vista_uso.png'))
    # --- detalle del canal del clip (sin walki)
    pl = pv.Plotter(off_screen=True, window_size=(1100,900))
    pl.add_mesh(pv.wrap(rot(mango)), color='#8d9399')
    pl.add_mesh(pv.wrap(rot(dup)), color='#c0392b')
    pl.set_background('white')
    c = np.array([38, 113, -62.0])
    pl.camera_position = [tuple(c+np.array([1.0,-0.7,0.5])*230), tuple(c), (0,0,1)]
    pl.add_text('Mango v4: canal en V para el clip del walki en la empunadura', font_size=11, position='upper_left', color='black')
    pl.screenshot(os.path.join(out,'mango_detalles.png'))

if __name__ == '__main__':
    main(*sys.argv[1:3])
