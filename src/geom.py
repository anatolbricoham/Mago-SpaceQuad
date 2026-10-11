"""Utilidades geometricas compartidas (trimesh + manifold3d + shapely).
Sistema de coordenadas del mango: X hacia la empunadura, Y a lo largo del boom, Z hacia la torre.
La cara libre de la torre (la que queda ARRIBA al usar la antena con la empunadura hacia abajo) es X = FACE_X.
Para las piezas del soporte se usa u = distancia hacia fuera de esa cara (x = FACE_X - u)."""
import numpy as np, trimesh, manifold3d as mf
import shapely.geometry as sg
from shapely import affinity

FACE_X = -58.64          # cara -X de la torre
TY0, TY1 = 136.32, 158.82  # caras -Y / +Y de la torre
YC = (TY0 + TY1) / 2      # eje de la torre en Y

def to_mf(m):
    return mf.Manifold(mf.Mesh(vert_properties=np.asarray(m.vertices, np.float32),
                               tri_verts=np.asarray(m.faces, np.uint32)))

def to_tm(M):
    g = M.to_mesh()
    return trimesh.Trimesh(g.vert_properties[:, :3].copy(), g.tri_verts.copy(), process=False)

def box(u0, u1, y0, y1, z0, z1):
    """Caja en coordenadas (u,y,z) -> mango."""
    x0, x1 = FACE_X - u1, FACE_X - u0
    return to_mf(trimesh.creation.box(bounds=[[x0, y0, z0], [x1, y1, z1]]))

def prism_y(poly_uz, y0, y1):
    """Extruye un poligono definido en (u,z) a lo largo de Y entre y0 e y1."""
    poly = sg.Polygon([(FACE_X - u, z) for u, z in np.asarray(poly_uz.exterior.coords)])
    holes = [[(FACE_X - u, z) for u, z in np.asarray(r.coords)] for r in poly_uz.interiors]
    poly = sg.Polygon(poly.exterior.coords, holes)
    m = trimesh.creation.extrude_polygon(poly, y1 - y0)       # plano XY (x,z), altura = y
    v = m.vertices.copy()
    m = trimesh.Trimesh(np.c_[v[:, 0], y0 + v[:, 2], v[:, 1]], m.faces, process=True)
    if m.volume < 0: m.invert()
    return to_mf(m)

def prism_z(poly_uy, z0, z1):
    """Extruye un poligono (u,y) a lo largo de Z."""
    poly = sg.Polygon([(FACE_X - u, y) for u, y in np.asarray(poly_uy.exterior.coords)],
                      [[(FACE_X - u, y) for u, y in np.asarray(r.coords)] for r in poly_uy.interiors])
    m = trimesh.creation.extrude_polygon(poly, z1 - z0)
    m.apply_translation([0, 0, z0])
    if m.volume < 0: m.invert()
    return to_mf(m)

def cyl_y(u, z, r, y0, y1, n=48):
    return prism_y(sg.Point(u, z).buffer(r, n), y0, y1)

def cyl_u(y, z, r, u0, u1, n=48):
    """Cilindro con eje en la direccion u (normal a la cara)."""
    m = trimesh.creation.cylinder(radius=r, height=abs(u1 - u0), sections=n)
    m.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0]))
    m.apply_translation([FACE_X - (u0 + u1) / 2, y, z])
    return to_mf(m)

def hex_u(y, z, af, u0, u1, rot=0.0):
    """Prisma hexagonal (entre caras af) con eje en u."""
    R = af / np.sqrt(3)
    pts = [(y + R*np.cos(rot + k*np.pi/3), z + R*np.sin(rot + k*np.pi/3)) for k in range(6)]
    return prism_z_yz(pts, u0, u1)

def prism_z_yz(pts_yz, u0, u1):
    poly = sg.Polygon(pts_yz)
    m = trimesh.creation.extrude_polygon(poly, abs(u1 - u0))   # plano (y,z), altura = x
    v = m.vertices.copy()
    m = trimesh.Trimesh(np.c_[v[:, 2], v[:, 0], v[:, 1]], m.faces, process=True)
    m.apply_translation([FACE_X - u1, 0, 0])
    if m.volume < 0: m.invert()
    return to_mf(m)

def teardrop(u, z, r, apex=(-1, 0), n=48):
    """Circulo con punta (gota) para agujeros horizontales imprimibles. apex: direccion (du,dz) de la punta."""
    c = sg.Point(u, z).buffer(r, n)
    d = np.array(apex, float); d /= np.linalg.norm(d)
    p = np.array([u, z]) + d * r * np.sqrt(2)
    n1 = np.array([-d[1], d[0]])
    tri = sg.Polygon([tuple(p), tuple(np.array([u, z]) + n1*r/np.sqrt(2) + d*r/np.sqrt(2)),
                      tuple(np.array([u, z]) - n1*r/np.sqrt(2) + d*r/np.sqrt(2))])
    return c.union(tri)
