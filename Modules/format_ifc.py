import numpy as np
import json
from beats import (getJson)
from plyfile import PlyData, PlyElement
import open3d as o3d

def format_faces_verts(shape_rep, counter):
    tuple_verts = shape_rep['Vertices']
    tuple_verts = [(x, y, z) for [x, y, z] in tuple_verts]
    faces = shape_rep['Faces']
    faces = [list(np.array(face)+counter) for face in faces]
    faces = [(f,0,0,0) for f in faces]
    counter += len(tuple_verts)
    return tuple_verts, faces, counter

def split_into_triangles_points(items, counter):
    lines = items[0].split('\n')
    points = []
    triangles = []
    for index, line in enumerate(lines):
        try:
            if line[0] == 'v':
                points += [tuple(line[2:].split(' '))]
            elif line[0] == 'f':
                triangle = line[2:].split(' ')
                triangle = list(np.array((list(map(int, triangle))))-1+counter)
                triangles += [triangle]
            else: 
                print(f'failed at index {index} for line {line}')
        except Exception as e:
            print(index, ' : ', repr(line))
            raise Exception(e)

        
    points = [(float(x), float(y), float(z)) for (x,y,z) in points]
    return points, triangles

def reformat():
    old_ifc = getJson('duplex_A.json')
    Objects = dict()
    Representations = dict()

    for item in old_ifc:
        id = item['GlobalId']
        if (item['Class'] != 'ShapeRepresentation'):
            Objects[id] = item
        else:
            new_item = item
            verts, faces = split_into_triangles_points(item['Items'], 0)
            for i in range(len(faces)):
                faces[i] = [int(j) for j in faces[i]]
            new_item['Vertices'] = verts
            new_item['Faces'] = faces
            del new_item['Items']
            Representations[id] = new_item

    new_ifc = dict()
    new_ifc['Objects'] = Objects
    new_ifc['ShapeRepresentations'] = Representations
    with open('duplex_A_reformat.json', 'w') as outfile:
        json.dump(new_ifc, outfile, indent=4)
    return Objects, Representations

def draw_building_colored(o, r, color_id):
    counter = 0
    all_verts = []
    all_faces = []
    color_verts = []
    color_faces = []
    for id in o:
        shape_id = o[id]['Representations'][0]['ref']
        shape_rep = r[shape_id]
        if (id == color_id):
            color_verts, color_faces, c = format_faces_verts(shape_rep, 0)
        tuple_verts, faces, counter = format_faces_verts(shape_rep, counter)
        all_verts += tuple_verts
        all_faces += faces

    # color_verts = np.array(color_verts, dtype=[('x', 'f4'), ('y', 'f4'),('z', 'f4')])
    # color_faces = np.array(color_faces, dtype=[('vertex_indices', 'i4', (3,)),('red', 'u1'), ('green', 'u1'),('blue', 'u1')])

    all_verts = np.array(all_verts, dtype=[('x', 'f4'), ('y', 'f4'),('z', 'f4')])
    all_faces = np.array(all_faces, dtype=[('vertex_indices', 'i4', (3,)),('red', 'u1'), ('green', 'u1'),('blue', 'u1')])

    color_verts = np.array(color_verts, dtype=[('x', 'f4'), ('y', 'f4'),('z', 'f4')])
    color_faces = np.array(color_faces, dtype=[('vertex_indices', 'i4', (3,)),('red', 'u1'), ('green', 'u1'),('blue', 'u1')])

    v = PlyElement.describe(all_verts, 'vertex')
    f = PlyElement.describe(all_faces, 'face')
    ply1 = PlyData([v, f])
    ply1.write('ply1.ply')
    mesh =  o3d.io.read_triangle_mesh("ply1.ply")
    mesh.compute_vertex_normals()

    v_color = PlyElement.describe(color_verts, 'vertex')
    f_color = PlyElement.describe(color_faces, 'face')
    ply_color = PlyData([v_color, f_color])
    ply_color.write('ply_color.ply')
    mesh_color =  o3d.io.read_triangle_mesh("ply_color.ply")
    mesh_color.compute_vertex_normals()
    mesh_color.paint_uniform_color([1, 0.706, 0])

    meshes = [mesh, mesh_color]

    # meshes = [mesh_color]

    
    o3d.visualization.draw_geometries(meshes)

def draw_building_no_windows():
    counter = 0
    ifc = getJson('duplex_A_reformat.json')
    o = ifc['Objects']
    r = ifc['ShapeRepresentations']
    all_verts = []
    all_faces = []
    for id in o:
        if o[id]['Class'] != 'Window':
            shape_id = o[id]['Representations'][0]['ref']
            shape_rep = r[shape_id]
            tuple_verts = shape_rep['Vertices']
            tuple_verts = [(x, y, z) for [x, y, z] in tuple_verts]
            all_verts += tuple_verts
            faces = shape_rep['Faces']
            faces = [list(np.array(face)+counter) for face in faces]
            counter += len(tuple_verts)
            faces = [(f,0,0,0) for f in faces]
            all_faces += faces
    all_verts = np.array(all_verts, dtype=[('x', 'f4'), ('y', 'f4'),('z', 'f4')])
    all_faces = np.array(all_faces, dtype=[('vertex_indices', 'i4', (3,)),('red', 'u1'), ('green', 'u1'),('blue', 'u1')])
    v = PlyElement.describe(all_verts, 'vertex')
    f = PlyElement.describe(all_faces, 'face')
    ply1 = PlyData([v, f])
    ply1.write('ply1.ply')
    mesh =  o3d.io.read_triangle_mesh("ply1.ply")
    mesh.compute_vertex_normals()
    o3d.visualization.draw_geometries([mesh])

def draw_building(o, r):
    counter = 0
    all_verts = []
    all_faces = []
    for id in o:
        shape_id = o[id]['Representations'][0]['ref']
        shape_rep = r[shape_id]
        verts, faces, counter = format_faces_verts(shape_rep, counter)
        all_verts += verts
        all_faces += faces
    all_verts = np.array(all_verts, dtype=[('x', 'f4'), ('y', 'f4'),('z', 'f4')])
    all_faces = np.array(all_faces, dtype=[('vertex_indices', 'i4', (3,)),('red', 'u1'), ('green', 'u1'),('blue', 'u1')])
    v = PlyElement.describe(all_verts, 'vertex')
    f = PlyElement.describe(all_faces, 'face')
    ply1 = PlyData([v, f])
    ply1.write('ply1.ply')
    mesh =  o3d.io.read_triangle_mesh("ply1.ply")
    mesh.compute_vertex_normals()
    o3d.visualization.draw_geometries([mesh])

def draw_item(o, r, id):
    new_o = dict()
    new_o[id] = o[id]
    new_r = dict()
    new_r[o[id]['Representations'][0]['ref']] = r[o[id]['Representations'][0]['ref']]
    draw_building(new_o, new_r)

def find_min_z(vertices):
    return min([z for [x,y,z] in vertices])

def find_max_z(vertices):
    return max([z for [x,y,z] in vertices])

def stretch_vertices(vertices, factor, min_z):
    new_vertices = []
    for [x, y, z] in vertices:
        new_vertices += [[x, y, (z-min_z)*factor + min_z]]
    return new_vertices

def move_vertices(vertices, amt):
    new_vertices = []
    for [x, y, z] in vertices:
        new_vertices += [[x, y, z+amt]]
    return new_vertices
    

def stretch_wall(o, r, key_wall, factor):
    shape_id = o[key_wall]['Representations'][0]['ref']
    shape_rep = r[shape_id]
    vertices = shape_rep['Vertices']
    min_z = find_min_z(vertices)
    max_z = find_max_z(vertices)
    amt = (max_z-min_z)*factor-(max_z-min_z)

    for key in r:
        vertices = r[key]['Vertices']
        current_min_z = find_min_z(vertices)
        current_max_z = find_max_z(vertices)
        if (current_min_z >= min_z and current_max_z <= max_z):
            shape_rep = r[key]
            vertices = shape_rep['Vertices']
            vertices = stretch_vertices(vertices, factor, min_z)
            r[key]['Vertices'] = vertices
        # elif (current_max_z <= max_z and current_min_z <= min_z):
        #     spec_factor = (1+amt)/(current_max_z-current_min_z)
        #     shape_rep = r[key]
        #     vertices = shape_rep['Vertices']
        #     vertices = stretch_vertices(vertices, spec_factor, current_min_z)
        #     r[key]['Vertices'] = vertices
        elif (current_max_z >= min_z):
            # Item is above wall, move upwards
            shape_rep = r[key]
            vertices = shape_rep['Vertices']
            vertices = move_vertices(vertices, amt)
            r[key]['Vertices'] = vertices
        else:
            # Assuming nothing with a lower z value that min_z and higher z value than max_z exists
            # It must be below the wall we want to stretch
            pass
    shape_id = o[key_wall]['Representations'][0]['ref']
    shape_rep = r[shape_id]
    vertices = shape_rep['Vertices']
    return r

if __name__ == "__main__":
    reformat()
    # draw_building_colored()
    ifc = getJson('duplex_A_reformat.json')
    o = ifc['Objects']
    r = ifc['ShapeRepresentations']
    for id in o:
        if (o[id]['Class'] == 'Wall'):
            print(f'id: {id}')
            print(f'type: {o[id]["ObjectType"]}')
            r_stretched = stretch_wall(o, r, id, 4)
            draw_building_colored(o, r_stretched, id)
    # draw_item(o, r, id)
    
    



