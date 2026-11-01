#!/usr/bin/env python3
"""Genera renders CAD de la placa baja, cartelas y conjunto radio+clip estimado. Requiere pyvista.
    python render_docs.py ../stl ../docs/img"""
import argparse
from pathlib import Path
import sys, os


def _stl_directory(value):
    path = Path(value)
    if not path.is_dir() or not (path / "mango_spacequad_v3.stl").is_file():
        raise argparse.ArgumentTypeError(f"debe ser un directorio con mango_spacequad_v3.stl: {value}")
    return str(path)


def _output_directory(value):
    path = Path(value)
    if path.exists() and not path.is_dir():
        raise argparse.ArgumentTypeError(f"la salida debe ser un directorio: {value}")
    return str(path)


def _parse_cli():
    parser = argparse.ArgumentParser(
        description="Genera imágenes CAD documentales; requiere PyVista y sobrescribe las imágenes destino.",
        epilog="Ejemplo: python src/render_docs.py stl docs/img",
    )
    parser.add_argument("stl_dir", type=_stl_directory, help="directorio que contiene el STL v3")
    parser.add_argument("output_dir", type=_output_directory, help="directorio donde guardar los PNG")
    return parser.parse_args()


if __name__ == "__main__":
    _cli_args = _parse_cli()

import numpy as np, trimesh, pyvista as pv
from geom import *
import verificar as vf
pv.OFF_SCREEN = True

def rot(m):   # (x,y,z)->(z,y,-x): empunadura hacia abajo, boom horizontal
    R = np.array([[0,0,1,0],[0,1,0,0],[-1,0,0,0],[0,0,0,1.0]]); m = m.copy(); m.apply_transform(R); return m

def bx(x0,x1,y0,y1,z0,z1): return trimesh.creation.box(bounds=[[x0,y0,z0],[x1,y1,z1]])

def main(stl_dir, out):
    os.makedirs(out, exist_ok=True)
    mango = trimesh.load(os.path.join(stl_dir, 'mango_spacequad_v3.stl'))
    radio, dup = to_tm(vf.walki()), to_tm(vf.duplexor())
    clip = to_tm(vf.radio_clip())
    boom = bx(-7.5,7.5,60,300,8,23.1)
    parts = [(mango,'#8d9399',1),(radio,'#2e9e5b',0.35),(clip,'#244a85',1),(boom,'#c9ced3',1),(dup,'#c0392b',0.7)]
    # --- vista de uso
    pl = pv.Plotter(off_screen=True, shape=(1,2), window_size=(1600,1000))
    c = np.array([45, 175, 0.0])
    for i, v in enumerate([(1,-1.6,0.55),(-1,-1.2,0.5)]):
        pl.subplot(0, i)
        for m,col,op in parts: pl.add_mesh(pv.wrap(rot(m)), color=col, opacity=op, smooth_shading=False)
        pl.camera_position = [tuple(c+np.array(v)*480), tuple(c), (0,0,1)]
        pl.camera.parallel_projection = True
        pl.camera.parallel_scale = 180
        pl.set_background('white')
        pl.add_text('Conjunto v3 / empunadura abajo', font_size=17, position=(20,950), color='black')
        pl.add_text('Verde: radio estimada / azul: clip estimado', font_size=13, position=(20,85), color='black')
        pl.add_text('Rojo: duplexor estimado / gris claro: boom', font_size=13, position=(20,55), color='black')
        pl.add_text('CAD ilustrativo: no certifica ajuste ni resistencia', font_size=12, position=(20,25), color='black')
    pl.screenshot(os.path.join(out,'vista_uso.png')); pl.close()
    # --- acceso al duplexor sin la envolvente de radio
    pl = pv.Plotter(off_screen=True, window_size=(1400,1000))
    pl.add_mesh(pv.wrap(rot(mango)), color='#8d9399')
    pl.add_mesh(pv.wrap(rot(dup)), color='#c0392b', opacity=0.7)
    pl.set_background('white')
    c = np.array([42, 145, -15.0])
    pl.camera_position = [tuple(c+np.array([1.0,-1.1,0.65])*300), tuple(c), (0,0,1)]
    pl.camera.parallel_projection = True
    pl.camera.parallel_scale = 130
    pl.add_arrows(np.array([[65,115,27],[65,181,27]]),
                  np.array([[0,-24,0],[0,24,0]]), color='#c0392b', mag=1)
    pl.add_text('Placa baja a 20 grados / duplexor y acceso por ambos extremos V', font_size=18, position=(25,945), color='black')
    pl.add_text('Rojo: envolvente estimada del duplexor / flechas: sentido de acceso', font_size=14, position=(25,65), color='black')
    pl.add_text('La caja de prueba roza la funda v1: conservar el paso no demuestra ajuste fisico', font_size=13, position=(25,30), color='black')
    pl.screenshot(os.path.join(out,'mango_detalles.png')); pl.close()
    # Recorte visual del STL real: omite la empunadura, no genera geometria nueva.
    detail = pv.wrap(rot(mango)).clip(normal=(0,0,1), origin=(0,0,50), invert=False)
    pl = pv.Plotter(off_screen=True, shape=(1,2), window_size=(1600,900))
    c = np.array([51.5, 152, 66.0])
    for i, v in enumerate([(1,1.2,1.4),(-0.7,1.3,-0.3)]):
        pl.subplot(0,i)
        pl.add_mesh(detail, color='#bdb98c', show_edges=False)
        pl.set_background('white')
        pl.camera_position = [tuple(c+np.array(v)*220), tuple(c), (0,0,1)]
        pl.camera.parallel_projection = True
        pl.camera.parallel_scale = 66
        title = 'Placa 55 x 48 x 4 mm / inclinacion 20 grados' if i == 0 else 'Dos cartelas de 4 mm / bajos abiertos'
        pl.add_text(title, font_size=16, position=(20,850), color='black')
        caption = 'Ventana opcional 22 x 6 mm' if i == 0 else '47 mm libres / insercion 40 mm / hueco 7 mm'
        pl.add_text(caption, font_size=14, position=(20,75), color='black')
        pl.add_text('Detalle del STL: empunadura y funda omitidas', font_size=12, position=(20,45), color='black')
        pl.add_text('Dimensiones CAD: sin prueba fisica ni certificacion', font_size=12, position=(20,20), color='black')
    pl.screenshot(os.path.join(out,'clip_detalle.png')); pl.close()

if __name__ == '__main__':
    main(_cli_args.stl_dir, _cli_args.output_dir)
