import bpy
import bmesh
import math
import mathutils
import numpy as np


MAX_DURATION = 360000

SEG_COUNT = 64

R0 = 0.2
R1 = 4.0
R2 = R1 + 0.2

H0 = 0.2
H1 = 0.2

rStep = 6

loudness = -4.843 # [-10, 0]
tempo = 180
duration = 189627 # < MAX_DURATION
energy = 0.6 # [0, 1]
valence = 0.567 # Not used now
danceability = 0.617 # Not used now
trackName = 'Track'


def outerRing(bm, ring1_d, ring1_u, ring2_d, ring2_u):
    # Outer circle: Duration

    seg = int(np.floor((duration / MAX_DURATION) * SEG_COUNT)) + 1

    print(seg)

    for i in range(seg):
        bm.faces.new([ring1_d[i], ring1_d[i+1], ring2_d[i+1], ring2_d[i]])
        bm.faces.new([ring1_u[i], ring1_u[i+1], ring2_u[i+1], ring2_u[i]])

        bm.faces.new([ring1_u[i], ring1_u[i+1], ring1_d[i+1], ring1_d[i]])
        bm.faces.new([ring2_u[i], ring2_u[i+1], ring2_d[i+1], ring2_d[i]])

    bm.faces.new([ring1_u[0], ring2_u[0], ring2_d[0], ring1_d[0]])
    bm.faces.new([ring1_u[seg], ring2_u[seg],
                 ring2_d[seg], ring1_d[seg]])


def disk(bm, ring0_d, ring0_u, ring1_d, ring1_u):
    for i in range(SEG_COUNT-1):
        bm.faces.new([ring0_d[i], ring0_d[i+1], ring1_d[i+1], ring1_d[i]])
        bm.faces.new([ring0_u[i], ring0_u[i+1], ring1_u[i+1], ring1_u[i]])

        bm.faces.new([ring0_u[i], ring0_u[i+1], ring0_d[i+1], ring0_d[i]])
        bm.faces.new([ring1_u[i], ring1_u[i+1], ring1_d[i+1], ring1_d[i]])

    bm.faces.new([ring0_d[SEG_COUNT-1], ring0_d[0],
                 ring1_d[0], ring1_d[SEG_COUNT-1]])
    bm.faces.new([ring0_u[SEG_COUNT-1], ring0_u[0],
                 ring1_u[0], ring1_u[SEG_COUNT-1]])

    bm.faces.new([ring0_u[SEG_COUNT-1], ring0_u[0],
                 ring0_d[0], ring0_d[SEG_COUNT-1]])
    bm.faces.new([ring1_u[SEG_COUNT-1], ring1_u[0],
                 ring1_d[0], ring1_d[SEG_COUNT-1]])


def waves(bm):
    maxAng = 2*np.pi * duration / MAX_DURATION

    pointCnt = int(np.ceil(tempo / 8))

    thetaList = np.linspace(0, maxAng, pointCnt)

    print(pointCnt)

    HList = np.zeros((rStep, pointCnt))

    # Energy - Amplifier of height
    baseH = H1 + (loudness + 10) / 20
    maxAmp = energy / 2

    for i in range(rStep):
        for j in range(pointCnt):
            HList[i, j] = baseH + (np.random.random() - 0.5) * maxAmp

    rList = np.linspace(R0+0.8, R1-0.2, rStep)
    fan = int(np.floor(pointCnt * (duration / MAX_DURATION)))

    print(fan, duration / MAX_DURATION)

    baseCircles = []

    for i in range(rStep):
        tBaseCircle = bmesh.ops.create_circle(
            bm, segments=pointCnt, radius=rList[i])['verts'][:fan+1]
        bmesh.ops.translate(bm, verts=tBaseCircle, vec=(0, 0, H1))
        baseCircles.append(tBaseCircle)

    baseCircleOut = bmesh.ops.create_circle(
        bm, segments=pointCnt, radius=R1)['verts'][:fan+1]

    bmesh.ops.translate(bm, verts=baseCircleOut, vec=(0, 0, H1))

    circles = []

    for i in range(rStep):
        tCircle = bmesh.ops.create_circle(
            bm, segments=pointCnt, radius=rList[i])['verts'][:fan+1]
        for j in range(fan+1):
            bmesh.ops.translate(
                bm, verts=[tCircle[j]], vec=(0, 0, HList[i, j]))
        # bmesh.ops.smooth_laplacian_vert(bm, verts=tCircle)
        circles.append(tCircle)

    for r in range(rStep-1):
        for i in range(fan):
            bm.faces.new([circles[r][i], circles[r][i+1],
                         circles[r+1][i+1], circles[r+1][i]])

    for i in range(fan):
        bm.faces.new([circles[0][i], circles[0][i+1],
                      baseCircles[0][i+1], baseCircles[0][i]])
        bm.faces.new([circles[rStep-1][i], circles[rStep-1][i+1],
                      baseCircleOut[i+1], baseCircleOut[i]])

    for i in range(rStep-1):
        bm.faces.new([circles[i][0], circles[i+1][0],
                      baseCircles[i+1][0], baseCircles[i][0]])
        bm.faces.new([circles[i][fan], circles[i+1][fan],
                      baseCircles[i+1][fan], baseCircles[i][fan]])
    bm.faces.new([circles[rStep-1][0], baseCircleOut[0], baseCircles[rStep-1][0]])    
    bm.faces.new([circles[rStep-1][fan], baseCircleOut[fan], baseCircles[rStep-1][fan]])


def waves2(bm):
    maxAng = 2*np.pi * duration / MAX_DURATION

    pointCnt = int(np.floor(tempo / 8))

    thetaList = np.linspace(0, maxAng, pointCnt)

    HList = np.zeros((rStep, pointCnt))

    # Energy - Amplifier of height
    baseH = H1 + (loudness + 10) / 30
    maxAmp = energy / 4

    for i in range(rStep):
        for j in range(pointCnt):
            HList[i, j] = baseH + (np.random.random() - 0.5) * maxAmp

    rList = np.linspace(R0+0.1, R1-0.2, rStep)
    fan = int(pointCnt * (duration / MAX_DURATION))

    circles = []

    for i in range(rStep):
        tCircle = bmesh.ops.create_circle(
            bm, segments=pointCnt, radius=rList[i])['verts'][:fan]
        for j in range(fan):
            bmesh.ops.translate(
                bm, verts=[tCircle[j]], vec=(0, 0, HList[i, j]))
        # bmesh.ops.smooth_laplacian_vert(bm, verts=tCircle)
        circles.append(tCircle)

    for r in range(rStep-1):
        for i in range(fan-1):
            bm.faces.new([circles[r][i], circles[r][i+1],
                         circles[r+1][i+1], circles[r+1][i]])

def addTitle():
    # Text
    font_curve = bpy.data.curves.new(type="FONT", name="Font Curve")
    font_curve.body = trackName
    font_obj = bpy.data.objects.new(name="Font Object", object_data=font_curve)
    font_obj.data.extrude = 0.1
    
    fontAng = np.pi * (duration / MAX_DURATION - 1/2)
    font_obj.location = (np.cos(fontAng)*(R0+0.4), np.sin(fontAng)*(R0+0.1), H0+0.05)
    font_obj.rotation_euler = (0, 0, fontAng)

    
    bpy.context.scene.collection.objects.link(font_obj)


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

    # Loudness - outer ring height

    if loudness < -10:
        loudness = -10
    H2 = H1 + (loudness + 10) / 40

    # For outer ring
    ring1_u2 = bmesh.ops.create_circle(
        bm, segments=SEG_COUNT, radius=R1)['verts']
    bmesh.ops.translate(bm, verts=ring1_u2, vec=(0, 0, H2))  # H2

    ring2_d = bmesh.ops.create_circle(
        bm, segments=SEG_COUNT, radius=R2)['verts']
    ring2_u = bmesh.ops.create_circle(
        bm, segments=SEG_COUNT, radius=R2)['verts']
    bmesh.ops.translate(bm, verts=ring2_u, vec=(0, 0, H2))

    outerRing(bm, ring1_d, ring1_u2, ring2_d, ring2_u)

    disk(bm, ring0_d, ring0_u, ring1_d, ring1_u)

    waves(bm)

    # for f in bm.faces:
    #     f.smooth = True

    me = bpy.data.meshes.new("Mesh")
    bm.to_mesh(me)
    bm.free()

    obj = bpy.data.objects.new("Object", me)
    bpy.context.collection.objects.link(obj)

    addTitle()
