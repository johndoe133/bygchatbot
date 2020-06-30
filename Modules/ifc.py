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
import open3d as o3d
from plyfile import PlyData, PlyElement
import os

GET_IFC_RESPONSE, GET_STRETCH_PARAMETERS = range(2)

def split_triangles_points(items, counter):
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
                triangles += [(triangle,155,155,0)]
            else: 
                logger.info(f'failed at index {index} for line {line}')
        except Exception as e:
            print(index, ' : ', repr(line))
            raise Exception(e)

        
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
    vertices = np.array(all_points, dtype=[('x', 'f4'), ('y', 'f4'),('z', 'f4')])
    faces = np.array(all_triangles,
    dtype=[('vertex_indices', 'i4', (3,)),('red', 'u1'), ('green', 'u1'),('blue', 'u1')])

    verts = PlyElement.describe(vertices, 'vertex')
    faces = PlyElement.describe(faces, 'face')
    ply0 = PlyData([verts, faces])
    ply0.write('ply0.ply')
    mesh =  o3d.io.read_triangle_mesh("ply0.ply")
    mesh.paint_uniform_color([0.1, 0.706, 0])
    mesh.compute_vertex_normals()
    return mesh

def show_building(mesh):
    # o3d.visualization.draw_geometries([pcd])
    vis = o3d.visualization.Visualizer()
    vis.create_window()
    vis.add_geometry(mesh)
    ctr = vis.get_view_control()
    ctr.rotate(0.0, -500.0)
    ctr.rotate(200, 0)
    ctr.rotate(0, 150)
    vis.update_geometry(mesh)
    vis.poll_events()
    vis.update_renderer()
    print('capturing screen image')
    vis.capture_screen_image('wow.png')
    print('Screen image captured')
    vis.destroy_window()

def show_wire_mesh(mesh):
    line_set = o3d.geometry.LineSet.create_from_triangle_mesh(mesh)
    o3d.visualization.draw_geometries([line_set])
    
def stretch_z(all_points, min_z, max_z, amt):
    for i, (x, y, z) in enumerate(all_points):
        (x, y, z) = all_points[i]
        if z >= min_z and z <= max_z:
            all_points[i] = (x, y, z*amt)
        elif z > max_z:
            all_points[i] = (x, y, z + max_z*amt)
    return all_points

def get_all_triangles_points(file_name):
    json_obj = getJson(file_name)
    all_points = []
    all_triangles = []
    counter = 0
    for item in json_obj:
        class_name = item['Class']
        if class_name == 'ShapeRepresentation':
            # points, triangles = split_triangles_points(item['Items'], counter)
            try:
                points, triangles = split_triangles_points(item['Items'], counter)
            except Exception as e:
                print(item)
                print(e)
            counter += len(points)
            all_points += points
            all_triangles += triangles
    return all_points, all_triangles

def find_parent(json_obj, id):
    for item in json_obj:
        if item['Class'] != 'ShapeRepresentation' and item['GlobalId'] == id:
            return item
    else:
        return {}

def save_to_new_ifc(new_all_points):
    counter = 0
    json_obj = getJson('duplex_A.json')
    stretched_json_obj = []
    for item in json_obj:
        class_name = item['Class']
        if class_name == 'ShapeRepresentation':
            points_triangles_str = ""
            points, triangles = split_triangles_points(item['Items'], 1)
            for point in points:
                (x, y, z) = new_all_points[counter]
                counter += 1
                points_triangles_str += f"v {x} {y} {z}\n"
            for index, ([a, b, c], _, _, _) in enumerate(triangles):
                if (index == len(triangles)-1):
                    points_triangles_str += f"f {a} {b} {c}"
                else:
                    points_triangles_str += f"f {a} {b} {c}\n"
            item['Items'] = [points_triangles_str]
        stretched_json_obj += [item]
    with open('duplex_A_stretched.json', 'w') as outfile:
        json.dump(stretched_json_obj, outfile, indent=4)

def ifc_start(update, context):
    reply_keyboard = [['View', 'View wire frame'], ['Get analysis'], ['Stretch', 'View stretched']]
    update.message.reply_text('What would you like to do?',
    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    
    return GET_IFC_RESPONSE

def get_ifc_response(update, context):
    json_obj = getJson('duplex_A.json')
    option = update.message.text
    chat_id = update.message.chat_id
    if (option == 'View'):
        all_points, all_triangles = get_all_triangles_points('duplex_A.json')
        mesh = get_mesh(all_points, all_triangles)
        show_building(mesh)
        bot = context.bot
        bot.send_photo(chat_id=chat_id, photo=open('wow.png', 'rb'))
        return ConversationHandler.END
    elif (option == 'Get analysis'):
        return start_analysis(update, context)
    elif (option == 'S T R E T C H'):
        update.message.reply_text('Provide the range along the z axis you would like to stretch, '
        'and the amount you would like to stretch in the following format:\n'
        '<code>min_z, max_z, amount</code>')
        return GET_STRETCH_PARAMETERS
    elif (option == 'View stretched'):
        update.message.reply_text('Showing stretched building: ')
        all_points, all_triangles = get_all_triangles_points('duplex_A_stretched.json')
        mesh = get_mesh(all_points, all_triangles)
        show_building(mesh)
        return ConversationHandler.END
    elif (option == 'View wire frame'):
        update.message.reply_text('Showing wire frame of building: ')
        all_points, all_triangles = get_all_triangles_points('duplex_A.json')
        mesh = get_mesh(all_points, all_triangles)
        show_wire_mesh(mesh)
        return ConversationHandler.END
    else:
        update.message.reply_text('Invalid option')
        return ConversationHandler.END

def get_stretch_parameters(update, context):
    stretch_parameters = update.message.text
    try:
        parameters = stretch_parameters.split(',')
        if len(parameters) != 3:
            update.message.reply_text('Invalid format! Format must be <code>min_z, max_z, amount</code>. Cancelled transaction')
            return ConversationHandler.END
        
        all_points, all_triangles = get_all_triangles_points('duplex_A.json')
        stretched_points = stretch_z(all_points, float(parameters[0]), float(parameters[1]), float(parameters[2]))

        update.message.reply_text(f'Success! Stretched all points along the z axis from {float(parameters[0])} to {float(parameters[1])} by {float(parameters[2])}')
        save_to_new_ifc(stretched_points)
        return ConversationHandler.END
    except Exception as e:
        update.message.reply_text(f'Failed! Error message:\n<code>{e}</code>')
        return ConversationHandler.END
    return ConversationHandler.END

def start_analysis(update, context):
    json_obj = getJson('duplex_A.json')
    classes = {}
    for item in json_obj:
        class_name = item['Class']
        if class_name == 'ShapeRepresentation':
            pass
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
    return ConversationHandler.END

