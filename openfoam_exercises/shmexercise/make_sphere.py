import numpy as np

def make_sphere(radius=0.25, center=(1.0, 1.0, 1.0), n=24, filename='sphere.stl'):
    cx, cy, cz = center
    tris = []
    for i in range(n):
        lat0 = np.pi * (-0.5 + i/n)
        lat1 = np.pi * (-0.5 + (i+1)/n)
        z0, r0 = np.sin(lat0), np.cos(lat0)
        z1, r1 = np.sin(lat1), np.cos(lat1)
        for j in range(n):
            a0 = 2*np.pi * j/n
            a1 = 2*np.pi * (j+1)/n
            p0 = np.array([cx+radius*r0*np.cos(a0), cy+radius*r0*np.sin(a0), cz+radius*z0])
            p1 = np.array([cx+radius*r1*np.cos(a0), cy+radius*r1*np.sin(a0), cz+radius*z1])
            p2 = np.array([cx+radius*r1*np.cos(a1), cy+radius*r1*np.sin(a1), cz+radius*z1])
            p3 = np.array([cx+radius*r0*np.cos(a1), cy+radius*r0*np.sin(a1), cz+radius*z0])

            if i == 0:          # south pole: p0 == p3, emit one triangle
                tris.append([p0, p1, p2])
            elif i == n-1:      # north pole: p1 == p2, emit one triangle
                tris.append([p0, p1, p3])
            else:
                tris.append([p0, p1, p2])
                tris.append([p0, p2, p3])

    with open(filename, 'w') as f:
        f.write('solid sphere\n')
        for tri in tris:
            # Normal from centroid outward — always correct for a convex sphere
            centroid = (tri[0] + tri[1] + tri[2]) / 3.0
            nv = centroid - np.array([cx, cy, cz])
            nv /= np.linalg.norm(nv)
            f.write(f'facet normal {nv[0]:.6f} {nv[1]:.6f} {nv[2]:.6f}\n')
            f.write('  outer loop\n')
            for pt in tri:
                f.write(f'    vertex {pt[0]:.6f} {pt[1]:.6f} {pt[2]:.6f}\n')
            f.write('  endloop\nendfacet\n')
        f.write('endsolid sphere\n')
    print(f"Created {filename}: {len(tris)} triangles")

make_sphere()
