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
import os

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
def get_mesh(all_points, all_triangles):
    vertex = np.array(all_points, dtype=[('x', 'f4'), ('y', 'f4'),('z', 'f4')])
    face = np.array(all_triangles,
    dtype=[('vertex_indices', 'i4', (3,)),('red', 'u1'), ('green', 'u1'),('blue', 'u1')])
    verts = PlyElement.describe(vertex, 'vertex')
    faces = PlyElement.describe(face, 'face')
    ply0 = PlyData([verts, faces])
    ply0.write('ply0.ply')

    mesh =  o3d.io.read_triangle_mesh("ply0.ply")
    mesh.compute_vertex_normals()
    return mesh

def show_building(mesh):
    o3d.visualization.draw_geometries([mesh])

def stretch(all_points, min_z, max_z, amt):
    for i, (x, y, z) in enumerate(all_points):
        (x, y, z) = all_points[i]
        if z >= min_z and z <= max_z:
            all_points[i] = (x, y, z*amt)
        elif z > max_z:
            all_points[i] = (x, y, z + max_z*amt)
    return all_points

def custom_draw_geometry_with_custom_fov(pcd, fov_step):
    vis = o3d.visualization.Visualizer()
    vis.create_window()
    vis.add_geometry(pcd)
    ctr = vis.get_view_control()
    image = vis.capture_screen_float_buffer()
    plt.imshow(np.asarray(image))
    plt.show()
    print("Field of view (before changing) %.2f" % ctr.get_field_of_view())
    ctr.change_field_of_view(step=fov_step)
    print("Field of view (after changing) %.2f" % ctr.get_field_of_view())
    vis.run()
    vis.destroy_window()

def custom_draw_geometry_with_camera_trajectory(pcd):
    custom_draw_geometry_with_camera_trajectory.index = -1
    custom_draw_geometry_with_camera_trajectory.trajectory =\
            o3d.io.read_pinhole_camera_trajectory(
                    "../../TestData/camera_trajectory.json")
    custom_draw_geometry_with_camera_trajectory.vis = o3d.visualization.Visualizer(
    )
    if not os.path.exists("../../TestData/image/"):
        os.makedirs("../../TestData/image/")
    if not os.path.exists("../../TestData/depth/"):
        os.makedirs("../../TestData/depth/")

    def move_forward(vis):
        # This function is called within the o3d.visualization.Visualizer::run() loop
        # The run loop calls the function, then re-render
        # So the sequence in this function is to:
        # 1. Capture frame
        # 2. index++, check ending criteria
        # 3. Set camera
        # 4. (Re-render)
        ctr = vis.get_view_control()
        glb = custom_draw_geometry_with_camera_trajectory
        if glb.index >= 0:
            print("Capture image {:05d}".format(glb.index))
            depth = vis.capture_depth_float_buffer(False)
            image = vis.capture_screen_float_buffer(False)
            plt.imsave("../../TestData/depth/{:05d}.png".format(glb.index),\
                    np.asarray(depth), dpi = 1)
            plt.imsave("../../TestData/image/{:05d}.png".format(glb.index),\
                    np.asarray(image), dpi = 1)
            vis.capture_depth_image("depth/{:05d}.png".format(glb.index), False)
            vis.capture_screen_image("image/{:05d}.png".format(glb.index), False)
        glb.index = glb.index + 1
        if glb.index < len(glb.trajectory.parameters):
            ctr.convert_from_pinhole_camera_parameters(
                glb.trajectory.parameters[glb.index])
        else:
            custom_draw_geometry_with_camera_trajectory.vis.\
                    register_animation_callback(None)
        return False

    vis = custom_draw_geometry_with_camera_trajectory.vis
    vis.create_window()
    vis.add_geometry(pcd)
    vis.get_render_option().load_from_json("../../TestData/renderoption.json")
    vis.register_animation_callback(move_forward)
    vis.run()
    vis.destroy_window()

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

    update.message.reply_text("Stretching everything by 2 along z axis")

    

    
    all_points_stretched = stretch(all_points, 100, 200, 20)
    mesh = get_mesh(all_points_stretched, all_triangles)
    # show_building(mesh)
    custom_draw_geometry_with_custom_fov(mesh, -30)
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
