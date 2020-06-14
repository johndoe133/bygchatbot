# from beats import (token)
import logging
import json
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
from telegram import ParseMode
from info import cancel
from beats import getJson
import re
import numpy as np
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import open3d as o3d
from plyfile import PlyData, PlyElement

def split_triangles_points(items, counter):
    lines = items[0].split('\n')
    points = []
    triangles = []
    for index, line in enumerate(lines):
        if line[0] == 'v':
            points += [tuple(line[2:].split(' '))]
        elif line[0] == 'f':
            triangle = line[2:].split(' ')
            triangle = list(np.array((list(map(int, triangle))))-1+counter)
            triangles += [(triangle,0,0,0)]
        else: 
            logger.info(f'failed at index {index} for line {line}')
    points = [(float(x), float(y), float(z)) for (x,y,z) in points]
    return points, triangles

def find_min_dimension(points, dimension):
    points_dimension = [point[dimension] for point in points]
    return min(points_dimension)

def find_max_dimension(points, dimension):
    points_dimension = [point[dimension] for point in points]
    return max(points_dimension)

def get_min_height(obj):
    min_height = None
    building = getJson('duplex_A.json')
    points = []
    for representation in obj['Representations']:
        rep_id = representation['ref']
        for item in building:
            if item['GlobalId'] == rep_id:
                points,triangles = split_triangles_points(item['Items'])
                new_min_height = find_min_dimension(points, 2)
                if min_height is None:
                    min_height = new_min_height
                else:
                    if new_min_height < min_height:
                        min_height = new_min_height

    return min_height

def show_building(all_points, all_triangles):
        vertex = np.array(all_points, dtype=[('x', 'f4'), ('y', 'f4'),('z', 'f4')])
        face = np.array(all_triangles,
        dtype=[('vertex_indices', 'i4', (3,)),('red', 'u1'), ('green', 'u1'),('blue', 'u1')])
        verts = PlyElement.describe(vertex, 'vertex')
        faces = PlyElement.describe(face, 'face')
        ply0 = PlyData([verts, faces])
        ply0.write('ply0.ply')
        mesh = o3d.io.read_triangle_mesh("ply0.ply")
        mesh.compute_vertex_normals()
        o3d.visualization.draw_geometries([mesh])

def start_analysis(update, context):
    json_obj = getJson('duplex_A.json')
    classes = {}
    ax = plt.axes(projection='3d')
    all_points = []
    all_triangles = []
    counter = 0
    for item in json_obj:
        class_name = item['Class']
        if class_name == 'ShapeRepresentation':
            points, triangles = split_triangles_points(item['Items'], counter)
            counter += len(points)
            all_points += points
            all_triangles += triangles
        elif class_name in classes.keys():
            classes[class_name]['Count'] += 1
            if (class_name == 'Wall'):
                if 'Volume' in item.keys():
                    classes[class_name]['Volume'] += item['Volume']
        else:
            classes[class_name] = {}
            classes[class_name]['Count'] = 1
            if (class_name == 'Wall'):
                classes[class_name]['Volume'] = 0
                if 'Volume' in item.keys():
                    classes[class_name]['Volume'] += item['Volume']
    update.message.reply_text(classes)

    update.message.reply_text("Stretching everything by 10 along z axis")

    

    show_building(all_points, all_triangles)
    return all_points, all_triangles

    


if __name__ == "__main__":
    json_obj = getJson('duplex_A.json')
    classes = {}
    ax = plt.axes(projection='3d')
    
    counter = 0
    for item in json_obj:
        class_name = item['Class']
        if class_name == 'ShapeRepresentation':
            points, triangles = split_triangles_points(item['Items'], counter)
            counter += len(points)
            all_points += points
            all_triangles += triangles
        elif class_name in classes.keys():
            classes[class_name]['Count'] += 1
            if (class_name == 'Wall'):
                if 'Volume' in item.keys():
                    classes[class_name]['Volume'] += item['Volume']
        else:
            classes[class_name] = {}
            classes[class_name]['Count'] = 1
            if (class_name == 'Wall'):
                classes[class_name]['Volume'] = 0
                if 'Volume' in item.keys():
                    classes[class_name]['Volume'] += item['Volume']
    
    print(all_triangles[0:4])
    counter = 0
    vertex = np.array(all_points, dtype=[('x', 'f4'), ('y', 'f4'),('z', 'f4')])
    face = np.array(all_triangles,
    dtype=[('vertex_indices', 'i4', (3,)),('red', 'u1'), ('green', 'u1'),('blue', 'u1')])
    verts = PlyElement.describe(vertex, 'vertex')
    faces = PlyElement.describe(face, 'face')

    ply0 = PlyData([verts, faces])
    ply0.write('ply0.ply')



    mesh = o3d.io.read_triangle_mesh("ply0.ply")
    mesh.compute_vertex_normals()

    o3d.visualization.draw_geometries([mesh])

    # print(all_points[0])

    # x = [x for (x,y,z) in all_points]
    # y = [y for (x,y,z) in all_points]
    # z = [z for (x,y,z) in all_points]
    # ax.scatter3D(x, y, z, 'blue', s=0.5)
    # ax.set_xlim3d(-200, 200)
    # ax.set_ylim3d(-200,200)
    # ax.set_zlim3d(-200,200)

    # plt.show()
