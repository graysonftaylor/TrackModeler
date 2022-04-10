import bpy
import bmesh
import math
import mathutils
import numpy as np
import requests

bm = bmesh.new()

# function to print output to console
def print(data):
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == 'CONSOLE':
                override = {'window': window, 'screen': screen, 'area': area}
                bpy.ops.console.scrollback_append(override, text=str(data), type="OUTPUT")

#testing print on a get
response = requests.get('https://google.com/')
print(response.status_code)

rStep = 6
maxR = 4.0
minR = 0.5
maxH = 1
bottomH = 0.3

segCount = 10

vertsList = []

thetaList = np.linspace(0, 2*np.pi, segCount)
rList = np.linspace(minR, maxR, rStep)
# hList = np.linspace(maxH, 0, rStep)
# hList = hList - hList ** 2 + bottomH

hArray = np.random.random((rStep, segCount)) * 0.4 + 0.2
scaleSeg = np.random.random((segCount, )) * 0.1 + 0.95

# Create circle verts
for i in range(rStep):
    tmpMesh = bmesh.ops.create_circle(bm, segments=segCount, radius=rList[i])
    for j in range(segCount):
        # Lift it up
        bmesh.ops.translate(
            bm, verts=[tmpMesh["verts"][j]], vec=(0.0, 0.0, hArray[i, j]))
    vertsList.append(tmpMesh["verts"])

# Scale it
for i in range(rStep):
    for j in range(segCount):
        bmesh.ops.scale(bm, verts=[vertsList[i][j]], vec=(scaleSeg[j], scaleSeg[j], 1))

# Up faces
for i in range(rStep-1):
    for j in range(segCount-1):
        bm.faces.new([vertsList[i][j], vertsList[i][j+1],
                     vertsList[i+1][j+1], vertsList[i+1][j]])
    bm.faces.new([vertsList[i][segCount-1], vertsList[i][0],
                  vertsList[i+1][0], vertsList[i+1][segCount-1]])

# Bottom verts
bottomInMesh = bmesh.ops.create_circle(bm, segments=segCount, radius=minR)
bottomOutMesh = bmesh.ops.create_circle(bm, segments=segCount, radius=maxR)
for i in range(segCount):
    bmesh.ops.scale(bm, verts=[bottomInMesh["verts"][i]], vec=(scaleSeg[i], scaleSeg[i], 1))
    bmesh.ops.scale(bm, verts=[bottomOutMesh["verts"][i]], vec=(scaleSeg[i], scaleSeg[i], 1))

bottomOutVerts = bottomOutMesh["verts"]
bottomInVerts = bottomInMesh["verts"]


# Outer face
outVerts = vertsList[rStep-1]

for i in range(segCount-1):
    bm.faces.new([outVerts[i], outVerts[i+1],
                 bottomOutVerts[i+1], bottomOutVerts[i]])
    bm.faces.new([bottomInVerts[i], bottomInVerts[i+1],
                 bottomOutVerts[i+1], bottomOutVerts[i]])

bm.faces.new([outVerts[segCount-1], outVerts[0],
             bottomOutVerts[0], bottomOutVerts[segCount-1]])
bm.faces.new([bottomInVerts[segCount-1], bottomInVerts[0],
              bottomOutVerts[0], bottomOutVerts[segCount-1]])

# Inner face
inVerts = vertsList[0]
for i in range(segCount-1):
    bm.faces.new([inVerts[i], inVerts[i+1],
                 bottomInVerts[i+1], bottomInVerts[i]])
bm.faces.new([inVerts[segCount-1], inVerts[0],
              bottomInVerts[0], bottomInVerts[segCount-1]])

me = bpy.data.meshes.new("Mesh")
bm.to_mesh(me)
bm.free()

obj = bpy.data.objects.new("Object", me)
bpy.context.collection.objects.link(obj)

# bpy.ops.mesh.primitive_cylinder_add(
#    vertices=segCount, radius=minR, depth=2)  # Bottom
