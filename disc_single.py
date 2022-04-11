import bpy
import bmesh
import math
import mathutils
import numpy as np


MAX_DURATION = 300

SEG_COUNT = 16


R0 = 0.5
R1 = 4.0
R2 = R1 + 0.2

H0 = 0.5
H1 = 0.5
H2 = H1 + 0.2

rStep = 6
maxH = 1
bottomH = 0.3


def outerRing(bm, duration, ring1_d, ring1_u, ring2_d, ring2_u):
    # Outer circle: Duration

    seg = int((duration / MAX_DURATION) * SEG_COUNT)

    for i in range(seg-1):
        bm.faces.new([ring1_d[i], ring1_d[i+1], ring2_d[i+1], ring2_d[i]])
        bm.faces.new([ring1_u[i], ring1_u[i+1], ring2_u[i+1], ring2_u[i]])

        bm.faces.new([ring1_u[i], ring1_u[i+1], ring1_d[i+1], ring1_d[i]])
        bm.faces.new([ring2_u[i], ring2_u[i+1], ring2_d[i+1], ring2_d[i]])

    bm.faces.new([ring1_u[0], ring2_u[0], ring2_d[0], ring1_d[0]])
    bm.faces.new([ring1_u[seg-1], ring2_u[seg-1],
                 ring2_d[seg-1], ring1_d[seg-1]])


def disk(bm, ring0_d, ring0_u, ring1_d, ring1_u):
    for i in range(SEG_COUNT-1):
        bm.faces.new([ring0_d[i], ring0_d[i+1], ring1_d[i+1], ring1_d[i]])
        bm.faces.new([ring0_u[i], ring0_u[i+1], ring1_u[i+1], ring1_u[i]])

        bm.faces.new([ring0_u[i], ring0_u[i+1], ring0_d[i+1], ring0_d[i]])
        bm.faces.new([ring1_u[i], ring1_u[i+1], ring1_d[i+1], ring1_d[i]])

    bm.faces.new([ring0_d[SEG_COUNT-1], ring0_d[0], ring1_d[0], ring1_d[SEG_COUNT-1]])
    bm.faces.new([ring0_u[SEG_COUNT-1], ring0_u[0], ring1_u[0], ring1_u[SEG_COUNT-1]])

    bm.faces.new([ring0_u[SEG_COUNT-1], ring0_u[0], ring0_d[0], ring0_d[SEG_COUNT-1]])
    bm.faces.new([ring1_u[SEG_COUNT-1], ring1_u[0], ring1_d[0], ring1_d[SEG_COUNT-1]])


if __name__ == '__main__':

    bm = bmesh.new()

    ring0_d = bmesh.ops.create_circle(
        bm, segments=SEG_COUNT, radius=R0)['verts']
    ring0_u = bmesh.ops.create_circle(
        bm, segments=SEG_COUNT, radius=R0)['verts']
    bmesh.ops.translate(bm, verts=ring0_u, vec=(0, 0, H0))

    ring1_d = bmesh.ops.create_circle(
        bm, segments=SEG_COUNT, radius=R1)['verts']
    ring1_u = bmesh.ops.create_circle(
        bm, segments=SEG_COUNT, radius=R1)['verts']
    bmesh.ops.translate(bm, verts=ring1_u, vec=(0, 0, H1))

    # For outer ring
    ring1_u2 = bmesh.ops.create_circle(
        bm, segments=SEG_COUNT, radius=R1)['verts']
    bmesh.ops.translate(bm, verts=ring1_u2, vec=(0, 0, H2))  # H2

    ring2_d = bmesh.ops.create_circle(
        bm, segments=SEG_COUNT, radius=R2)['verts']
    ring2_u = bmesh.ops.create_circle(
        bm, segments=SEG_COUNT, radius=R2)['verts']
    bmesh.ops.translate(bm, verts=ring2_u, vec=(0, 0, H2))

    outerRing(bm, 240, ring1_d, ring1_u2, ring2_d, ring2_u)

    disk(bm, ring0_d, ring0_u, ring1_d, ring1_u)

    me = bpy.data.meshes.new("Mesh")
    bm.to_mesh(me)
    bm.free()

    obj = bpy.data.objects.new("Object", me)
    bpy.context.collection.objects.link(obj)
