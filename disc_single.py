import bpy
import bmesh
import math
import mathutils
import numpy as np


MAX_DURATION = 360000

SEG_COUNT = 64

R0 = 0.4
R1 = 4.0
R2 = R1 + 0.2

H0 = 0.2
H1 = 0.2

rStep = 6

loudness = -4.843  # [-10, 0], for wave base
tempo = 180  # [90, 360], for wave freq
duration = 200000  # < MAX_DURATION, for outer ring
energy = 0.6  # [0, 1], for wave amps
valence = 0.3  # For edge decoration

danceability = 0.617  # Not used now
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


def waves():
    bm = bmesh.new()

    pointCnt = int(np.ceil(tempo / 8))

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
        circles.append(tCircle)

    # Up and Down face
    for r in range(rStep-1):
        for i in range(fan):
            bm.faces.new([circles[r][i], circles[r][i+1],
                         circles[r+1][i+1], circles[r+1][i]])
            bm.faces.new([baseCircles[r][i], baseCircles[r][i+1],
                         baseCircles[r+1][i+1], baseCircles[r+1][i]])

    for i in range(fan):
        bm.faces.new([baseCircles[rStep-1][i], baseCircles[rStep-1][i+1],
                      baseCircleOut[i+1], baseCircleOut[i]])

    # Inner and Outer face
    for i in range(fan):
        bm.faces.new([circles[0][i], circles[0][i+1],
                      baseCircles[0][i+1], baseCircles[0][i]])
        bm.faces.new([circles[rStep-1][i], circles[rStep-1][i+1],
                      baseCircleOut[i+1], baseCircleOut[i]])

    # Two Ends
    for i in range(rStep-1):
        bm.faces.new([circles[i][0], circles[i+1][0],
                      baseCircles[i+1][0], baseCircles[i][0]])
        bm.faces.new([circles[i][fan], circles[i+1][fan],
                      baseCircles[i+1][fan], baseCircles[i][fan]])
    bm.faces.new([circles[rStep-1][0], baseCircleOut[0],
                 baseCircles[rStep-1][0]])
    bm.faces.new([circles[rStep-1][fan], baseCircleOut[fan],
                 baseCircles[rStep-1][fan]])

    me = bpy.data.meshes.new("Wave Mesh")
    bm.to_mesh(me)
    bm.free()

    obj = bpy.data.objects.new("Wave", me)
    bpy.context.collection.objects.link(obj)


def addTitle():
    # Text
    font_curve = bpy.data.curves.new(type="FONT", name="Font Curve")
    font_curve.body = trackName
    font_obj = bpy.data.objects.new(name="Track Title", object_data=font_curve)
    font_obj.data.extrude = 0.1

    fontAng = np.pi * (duration / MAX_DURATION - 1/2)
    font_obj.location = (np.cos(fontAng)*(R0+0.8),
                         np.sin(fontAng)*(R0+0.8), H0+0.05)
    font_obj.rotation_euler = (0, 0, fontAng)

    bpy.context.scene.collection.objects.link(font_obj)


def edgeDecor():

    bm = bmesh.new()

    # For valence
    startAng = 2*np.pi * duration / MAX_DURATION

    decorNum = int((1 - duration / MAX_DURATION) * 40)

    decL = np.linspace(startAng, 2*np.pi, decorNum+1, endpoint=True)

    N = 32

    amp = R2-R1

    verts_u = []
    verts_d = []
    cent_verts_u = []
    cent_verts_d = []

    for i in range(decorNum):
        theta1 = decL[i]
        theta2 = decL[i+1]
        for j in np.linspace(theta1, theta2, N):
            x = 2*(j-theta1)/(theta2-theta1)
            if x > 1:
                x = 2 - x
            f = x ** ((1-valence) * 2)
            r = R1+amp*f

            j += np.pi/2

            verts_d.append(bmesh.ops.create_vert(
                bm, co=[r*np.cos(j), r*np.sin(j), 0])['vert'][0])
            verts_u.append(bmesh.ops.create_vert(
                bm, co=[r*np.cos(j), r*np.sin(j), H1])['vert'][0])

            cent_verts_d.append(bmesh.ops.create_vert(
                bm, co=[R0*np.cos(j), R0*np.sin(j), 0])['vert'][0])
            cent_verts_u.append(bmesh.ops.create_vert(
                bm, co=[R0*np.cos(j), R0*np.sin(j), H1])['vert'][0])

    L = len(verts_u)
    for i in range(L-1):
        bm.faces.new([verts_u[i], verts_u[i+1],
                     cent_verts_u[i+1], cent_verts_u[i]])
        bm.faces.new([verts_d[i], verts_d[i+1],
                     cent_verts_d[i+1], cent_verts_d[i]])

        bm.faces.new([cent_verts_u[i], cent_verts_u[i+1],
                     cent_verts_d[i+1], cent_verts_d[i]])
        bm.faces.new([verts_u[i], verts_u[i+1], verts_d[i+1], verts_d[i]])

    bm.faces.new([verts_u[0], verts_d[0],
                  cent_verts_d[0], cent_verts_u[0]])
    bm.faces.new([verts_u[L-1], verts_d[L-1],
                  cent_verts_d[L-1], cent_verts_u[L-1]])

    me = bpy.data.meshes.new("Edge Decoration Mesh")
    bm.to_mesh(me)
    bm.free()

    obj = bpy.data.objects.new("Edge Decoration", me)
    bpy.context.collection.objects.link(obj)


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

    me = bpy.data.meshes.new("Disk Mesh")
    bm.to_mesh(me)
    bm.free()

    obj = bpy.data.objects.new("Disk", me)
    bpy.context.collection.objects.link(obj)

    waves()

    edgeDecor()

    addTitle()
