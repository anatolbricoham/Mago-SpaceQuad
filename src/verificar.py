#!/usr/bin/env python3
"""Verifica la placa baja v3 y guarda resultados CAD en JSON.
Clips y radio son envolventes ESTIMADAS, no una validacion de ajuste real.
    python verificar.py stl/mango_spacequad_v3.stl [docs/cad_checks.json]
"""
import io
import json
from pathlib import Path
import subprocess
import sys
import numpy as np
import trimesh
from geom import *
import mango_v3 as mg

ROOT = Path(__file__).resolve().parent.parent
V1 = ROOT / "stl" / "mango_spacequad_tripode.stl"
BASE_REV = "35019cc"
DUP = (-33.4, -17.9, 118.0, 177.0, 28.0, 59.5)
R_W, R_T, R_L, R_ABOVE = 62.0, 40.0, 130.0, 25.0
CLIPS = (25.0, 30.0, 35.0, 40.0, 45.0)

def baseline():
    raw = subprocess.run(["git", "-C", str(ROOT), "show", f"{BASE_REV}:stl/mango_spacequad_v3.stl"],
                         capture_output=True, check=True).stdout
    return trimesh.load(io.BytesIO(raw), file_type="stl")

def walki(w=R_W):
    """Radio sobre la placa; misma transformacion que el clip, no traslacion independiente."""
    uc = mg.PLATE_U0 + mg.PLATE_W / 2
    s1 = mg.PLATE_L + R_ABOVE
    return mg.plate_box(uc - w/2, uc + w/2, s1 - R_L, s1,
                        mg.PLATE_T + 0.5, mg.PLATE_T + 0.5 + R_T)

def duplexor():
    return to_mf(trimesh.creation.box(bounds=[DUP[0::2], DUP[1::2]]))

def tongue(w, depth, offset=0.5):
    uc = mg.PLATE_U0 + mg.PLATE_W / 2
    s0 = mg.PLATE_L - depth
    return mg.plate_box(uc - w/2, uc + w/2, s0, s0 + mg.USABLE_L,
                        -mg.CLIP_T_MAX - offset, -offset)

def radio_clip(w=45.0):
    uc = mg.PLATE_U0 + mg.PLATE_W / 2
    bridge = mg.plate_box(uc - w/2, uc + w/2, mg.PLATE_L, mg.PLATE_L + 2,
                          -mg.CLIP_T_MAX - 0.5, mg.PLATE_T + 1)
    return tongue(w, mg.USABLE_L) + bridge

def use_box(u0, u1, v0, v1, h0, h1):
    return to_mf(trimesh.creation.box(bounds=[[-h1, v0, u0], [-h0, v1, u1]]))

def sdiff(a, b):
    return (a - b) + (b - a)

def main(path, report=None):
    mesh = trimesh.load(path)
    base_mesh = baseline()
    mango, base, v1 = to_mf(mesh), to_mf(base_mesh), to_mf(trimesh.load(V1))
    mount, dup = mg.clip_holder(), duplexor()
    results = []
    def check(name, passed, **values):
        results.append(dict(name=name, passed=bool(passed), **values))
        print(f"[{'OK' if passed else 'FALLO'}] {name} {values}", flush=True)
    canonical = to_tm(mango)
    check("manifold", mango.status().name == "NoError" and canonical.is_watertight and canonical.is_winding_consistent,
          canonical_watertight=canonical.is_watertight, raw_trimesh_watertight=mesh.is_watertight,
          baseline_raw_trimesh_watertight=base_mesh.is_watertight,
          status=mango.status().name)
    positive = [c for c in mango.decompose() if c.volume() > 0]
    check("one_solid", len(positive) == 1, solids=len(positive), volume_mm3=mango.volume())
    # Envolvente antigua + nueva; el resto debe ser identico, no solo sus cotas.
    old_env = use_box(74, 100, 117, 178, 32, 111)
    new_env = use_box(23, 80, 128, 176, 53, 87)
    difference = sdiff(mango, base)
    outside = abs((difference - old_env - new_env).volume())
    check("mount_changes_localized", outside < 0.001 and difference.volume() > 100,
          outside_mm3=outside, changed_mm3=difference.volume(), baseline=BASE_REV)
    for name, region in (
        ("grip_exact", use_box(-1, 80, 70, 180, -111, 0)),
        ("boom_exact", use_box(-1, 28, 70, 180, -1, 34)),
        ("tripod_exact", use_box(-1, 80, 70, 180, -111, -95)),
    ):
        delta = abs((difference ^ region).volume())
        check(name, delta < 0.001, symmetric_difference_mm3=delta)
    cavities = lambda m: sorted(round(c.volume(), 1) for c in m.decompose() if c.volume() < 0)
    check("grip_cavity_exact", cavities(mango) == cavities(base), cavities_mm3=cavities(mango))
    check("plate_dimensions", mg.PLATE_T == 4 and mg.ANGLE == 20 and mg.W_IN >= 47 and mg.USABLE_L >= 40,
          thickness_mm=mg.PLATE_T, angle_deg=mg.ANGLE, width_mm=mg.PLATE_W,
          clear_width_mm=mg.W_IN, insertion_mm=mg.USABLE_L)
    check("plate_above_duplexor", mg.PLATE_H0 >= 65, underside_min_h=mg.PLATE_H0)
    check("gussets_above_36", mg.ROOT_H0 > 36, minimum_h=mg.ROOT_H0)
    for i, u in enumerate((mg.PLATE_U0, mg.PLATE_U0 + mg.PLATE_W - mg.SIDE_T)):
        root = mount ^ base ^ use_box(u, u + mg.SIDE_T, 136, 159, mg.ROOT_H0, mg.TOWER_H)
        foot = use_box(u+0.5, min(u+mg.SIDE_T-0.5, 77.8),
                       mg.ROOT_V0+2, mg.ROOT_V1-2, mg.ROOT_H0+0.5, mg.ROOT_H0+3.5)
        missing = (foot - base).volume() + (foot - mount).volume()
        check(f"gusset_{i+1}_anchored", root.volume() > 100 and missing < 0.001,
              anchor_overlap_mm3=root.volume(), minimum_verified_embed_mm=3,
              minimum_verified_span_mm=mg.ROOT_V1-mg.ROOT_V0-4,
              verified_foot_volume_mm3=foot.volume(), missing_foot_mm3=missing,
              nominal_embed_mm=mg.TOWER_H-mg.ROOT_H0)
    # Barrido continuo: union exacta de todas las posiciones de un prisma trasladado.
    uc = mg.PLATE_U0 + mg.PLATE_W/2
    for w in CLIPS:
        for offset in (0.05, 0.5, 0.95):
            sweep = mg.plate_box(uc-w/2, uc+w/2, mg.PLATE_L-mg.USABLE_L,
                                 mg.PLATE_L+mg.USABLE_L, -mg.CLIP_T_MAX-offset, -offset)
            collision = (sweep ^ mango).volume()
            check(f"continuous_clip_{w:g}_{offset:g}", collision < 0.001,
                  sweep_mm=mg.USABLE_L, collision_mm3=collision)
    # El espacio de 7 mm se comprueba como volumen, no como resta de parametros.
    gap = mg.plate_box(uc-mg.W_IN/2, uc+mg.W_IN/2, mg.PLATE_L-mg.USABLE_L,
                       mg.PLATE_L, -mg.MIN_CLEAR, -0.001)
    check("seven_mm_gap", (gap ^ mango).volume() < 0.001, collision_mm3=(gap ^ mango).volume())
    open_under = use_box(uc-10, uc+10, 160, 170, 36, 64)
    check("open_underside", (mount ^ open_under).volume() < 0.001)
    window = mg.plate_box(uc-mg.WIN_W/2+0.1, uc+mg.WIN_W/2-0.1,
                          mg.WIN_S+0.1, mg.WIN_S+mg.WIN_H-0.1, 0.1, mg.PLATE_T-0.1)
    check("optional_hook_window", (window ^ mango).volume() < 0.001 if mg.HOOK_WINDOW else (window ^ mango).volume() > 1)
    plate_sample = mg.plate_box(uc+mg.WIN_W/2+1, uc+mg.WIN_W/2+2, 14, 15, 0.1, 3.9)
    check("plate_solid_around_window", (plate_sample - mango).volume() < 0.001)
    outside_faces = mg.plate_box(uc+12, uc+13, 14, 15, 4.01, 4.11) + \
                    mg.plate_box(uc+12, uc+13, 14, 15, -0.11, -0.01)
    check("actual_plate_four_mm_faces", abs((outside_faces ^ mango).volume()) < 0.001 and
          abs((plate_sample - mango).volume()) < 0.001)
    # La caja nominal del duplexor ya roza el STL v1. Separar ese defecto del soporte nuevo.
    delta_dup = abs((mango ^ dup).volume() - (base ^ dup).volume())
    check("duplexor_no_new_collision", (mount ^ dup).volume() < 0.001 and delta_dup < 0.001,
          new_collision_mm3=(mount ^ dup).volume(), inherited_v1_collision_mm3=(v1 ^ dup).volume(),
          baseline_delta_mm3=delta_dup)
    for direction, v0, v2 in (("minus_v", -100, 177), ("plus_v", 118, 400)):
        corridor = use_box(28, 59.5, v0, v2, 17.9, 33.4)
        added = ((mango - v1) ^ corridor).volume()
        changed = ((sdiff(mango, v1)) ^ corridor).volume()
        check(f"duplexor_corridor_{direction}", added < 0.001 and changed < 0.001,
              added_collision_mm3=added, changed_mm3=changed,
              inherited_collision_mm3=(v1 ^ corridor).volume())
        check(f"radio_clear_of_{direction}_corridor", ((walki()+radio_clip()) ^ corridor).volume() < 0.001)
    for w in (50.0, R_W, 70.0):
        radio, clip = walki(w), radio_clip()
        check(f"radio_{w:g}_clear", (radio ^ mango).volume() < 0.001 and (radio ^ dup).volume() < 0.001,
              mango_collision_mm3=(radio ^ mango).volume(), duplexor_collision_mm3=(radio ^ dup).volume())
        check(f"radio_{w:g}_clip_connected", (radio ^ clip).volume() > 1 and
              sum(c.volume() > 0 for c in (radio+clip).decompose()) == 1)
    check("clip_clear", (radio_clip() ^ mango).volume() < 0.001 and (radio_clip() ^ dup).volume() < 0.001,
          mango_collision_mm3=(radio_clip() ^ mango).volume())
    s1 = mg.PLATE_L + R_ABOVE
    swept_radio = mg.plate_box(uc-R_W/2, uc+R_W/2, s1-R_L, s1+mg.USABLE_L,
                               mg.PLATE_T+0.5, mg.PLATE_T+0.5+R_T)
    swept_bridge = mg.plate_box(uc-22.5, uc+22.5, mg.PLATE_L, mg.PLATE_L+2+mg.USABLE_L,
                                -mg.CLIP_T_MAX-0.5, mg.PLATE_T+1)
    swept_tongue = mg.plate_box(uc-22.5, uc+22.5, mg.PLATE_L-mg.USABLE_L,
                                mg.PLATE_L+mg.USABLE_L, -mg.CLIP_T_MAX-0.5, -0.5)
    assembly_sweep = swept_radio + swept_bridge + swept_tongue
    check("continuous_full_assembly_sweep", (assembly_sweep ^ mango).volume() < 0.001 and
          (assembly_sweep ^ dup).volume() < 0.001, sweep_mm=mg.USABLE_L,
          mango_collision_mm3=(assembly_sweep ^ mango).volume(),
          duplexor_collision_mm3=(assembly_sweep ^ dup).volume())
    passed = all(r["passed"] for r in results)
    data = dict(passed=passed, checks=results,
                limitations=["Estimated clips/radio; not physically tested.",
                             "Nominal duplexor box intersects original v1 housing; no new obstruction allowed.",
                             "Raw trimesh welding reports non-watertight texture degeneracies also present in baseline; canonical manifold mesh is watertight.",
                             "Finite gusset attachment is not a strength certification." ])
    if report:
        Path(report).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return passed

if __name__ == "__main__":
    sys.exit(0 if main(*sys.argv[1:]) else 1)
