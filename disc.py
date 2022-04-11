import bpy
import bpy.ops as o
import bmesh
import math
import mathutils
import numpy as np
import requests
# Authors: Eric, Taishan, Grayson

# prints output to console
def print(data):
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == 'CONSOLE':
                override = {'window': window, 'screen': screen, 'area': area}
                bpy.ops.console.scrollback_append(override, text=str(data), type="OUTPUT")
      
#random generators
def rand():
  return (np.random.rand()-0.5)*2
def randsq():
  return (np.random.rand()**2-0.5)*2
      
#cube creation
def cube(loc, resize):
  o.mesh.primitive_cube_add(location = loc)
  o.transform.resize(value = resize)

#prism creation
def prism(loc, resize, vert, angle, angle2):
  o.mesh.primitive_cylinder_add(vertices = vert, location = loc)
  ob = bpy.context.object
  ob.rotation_euler=(0, 0, angle)
  o.transform.resize(value = resize)
  ob.rotation_euler=(0, 0, angle2)
    
#creates platform with edge number = valence, text = title string
def createPlatform(valence):
    #round platform
    if valence > 0.8:
        bpy.ops.mesh.primitive_torus_add(location = (0,0,0), major_radius=5, minor_radius = 0.1, major_segments = 256)
        bpy.ops.mesh.primitive_cone_add(radius1 = 5.3, radius2 = 5, depth=0.5, location = (0,0,-0.2), vertices = 1000)
    #octagon platform
    elif valence > 0.6:
        prism((0,0, -0.2),(5.5,5.5,0.2), 8, 3, 1)
        prism((0,0, -0.2),(5.5,5.5,0.2), 8, 3, 1)
    #hexagon platform
    elif valence > 0.4:
        prism((0,0, -0.2),(5.5,5.5,0.2), 6, 3, 1)
    #pentagon platform
    elif valence > 0.2:
        prism((0,0, -0.2),(5.5,5.5,0.2), 5, 3, 1)
    #square platform
    else:
        prism((0,0, -0.2),(6.5,6.5,0.2), 4, 3, 1)
    bpy.ops.object.text_add(radius=1, location = (-1,-4.5,0),rotation=(1.5,0,0))
    ob=bpy.context.object
    ob.data.body = title
    bpy.context.object.data.extrude = 0.1

        
#testing print on a get
response = requests.get('https://google.com/')
print(response.status_code)


bm = bmesh.new()

rStep = 6
maxR = 4.0
minR = 0.5
maxH = 1
bottomH = 0.3
segCount = 10

#track values
valence = 0.9
energy = 0
tempo = 0
title = "title"

vertsList = []

thetaList = np.linspace(0, 2*np.pi, segCount)
rList = np.linspace(minR, maxR, rStep)
# hList = np.linspace(maxH, 0, rStep)
# hList = hList - hList ** 2 + bottomH

hArray = np.random.random((rStep, segCount)) * 0.4 + 0.2
scaleSeg = np.random.random((segCount, )) * 0.1 + 0.95

#creates platform with edge number determined by valence score
createPlatform(valence)

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
