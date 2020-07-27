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
import open3d as o3d
from plyfile import PlyData, PlyElement
import os
from Modules.file_management import show_all_file_type
from pathlib import Path

files_dir = Path.cwd() / 'Files'

GET_IFC_RESPONSE, GET_STRETCH_PARAMETERS, GET_IFC_FILE, GET_STRETCHED_NAME, SAVE_STRETCHED = range(5)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

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

def rotate(vis, mesh, X, Y):
    ctr = vis.get_view_control()
    for x, y in zip(X, Y):
        ctr.rotate(x, y)
    vis.update_geometry(mesh)
    vis.poll_events()
    vis.update_renderer()
    return vis

def show_building(mesh):
    vis = o3d.visualization.Visualizer()
    vis.create_window()
    vis.add_geometry(mesh)
    vis = rotate(vis, mesh, [0, 200, 0], [-500, 0, 150])


    # ctr = vis.get_view_control()
    # ctr.rotate(0.0, -500.0)
    # ctr.rotate(200, 0)
    # ctr.rotate(0, 150)
    # vis.update_geometry(mesh)
    # vis.poll_events()
    # vis.update_renderer()

    logger.info('capturing screen images')
    vis.capture_screen_image('1.png')
    vis = rotate(vis, mesh, [0, -200, -200, 0], [-150, 0, 0, 150])
    vis.capture_screen_image('2.png')
    vis = rotate(vis, mesh, [0, 200, 900, 0], [-150, 0, 0, 150])
    vis.capture_screen_image('3.png')
    vis = rotate(vis, mesh, [0, -900, -900, 0], [-150, 0, 0, 150])
    vis.capture_screen_image('4.png')
    logger.info('Screen images captured')
    vis.destroy_window()

def show_wire_mesh(mesh):
    line_set = o3d.geometry.LineSet.create_from_triangle_mesh(mesh)
    show_building(line_set)
    
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

def save_to_new_ifc(new_all_points, old_file_name, new_file_name):
    counter = 0
    json_obj = getJson(files_dir / old_file_name)
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
    with Path(files_dir / f'{new_file_name}.json').open(mode = 'w') as outfile:
        json.dump(stretched_json_obj, outfile, indent=4)

def ifc_start(update, context):
    all_files = getJson(files_dir / 'files.json')
    try:
        ifc_file_name = context.user_data['ifc_file_name']
    except:
        try:
            ifc_files = show_all_file_type(all_files, 'ifc')
            if (ifc_files == ""):
                raise Exception('No ifc files uploaded')
            update.message.reply_text(ifc_files)
        except:
            update.message.reply_text('You have no files stored of type IFC. Try using /sendfile to store one. ')
            return ConversationHandler.END
        update.message.reply_text('Which IFC file would you like to load? Type the name of the file')
        return GET_IFC_FILE
    reply_keyboard = [['Load an IFC file', 'Get .ply file'], ['View', 'View wire frame'], ['Get analysis', 'Stretch']]
    update.message.reply_text('What would you like to do?',
    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    
    return GET_IFC_RESPONSE

def get_ifc_response(update, context):
    ifc_file_name = context.user_data['ifc_file_name']
    json_obj = getJson(files_dir / ifc_file_name)
    all_files = getJson(files_dir / 'files.json')
    option = update.message.text
    chat_id = update.message.chat_id
    if (option == 'Load an IFC file'):
        try:
            update.message.reply_text(show_all_file_type(all_files, 'ifc'))
        except:
            update.message.reply_text('You have no files stored of type IFC. Try using /sendfile to store one. ')
            return ConversationHandler.END
        update.message.reply_text('Which IFC file would you like to load? Type the name of the file')
        return GET_IFC_FILE
    elif (option == 'View'):
        all_points, all_triangles = get_all_triangles_points(files_dir / ifc_file_name)
        mesh = get_mesh(all_points, all_triangles)
        show_building(mesh)
        bot = context.bot
        [bot.send_photo(chat_id=chat_id, photo=open(f'{i}.png', 'rb')) for i in range(1, 5)]

        return ConversationHandler.END
    elif (option == 'Get analysis'):
        return start_analysis(update, context)
    elif (option == 'Stretch'):
        update.message.reply_text('Provide the range along the z axis you would like to stretch, '
        'and the amount you would like to stretch in the following format:\n'
        '<code>min_z, max_z, amount</code>')
        return GET_STRETCH_PARAMETERS
    elif (option == 'View stretched'):
        update.message.reply_text('Showing stretched building: ')
        all_points, all_triangles = get_all_triangles_points('duplex_A_stretched.json')
        mesh = get_mesh(all_points, all_triangles)
        show_building(mesh)
        bot = context.bot
        [bot.send_photo(chat_id=chat_id, photo=open(f'{i}.png', 'rb')) for i in range(1, 5)]
        return ConversationHandler.END
    elif (option == 'View wire frame'):
        all_points, all_triangles = get_all_triangles_points(files_dir / ifc_file_name)
        mesh = get_mesh(all_points, all_triangles)
        show_wire_mesh(mesh)
        bot = context.bot
        [bot.send_photo(chat_id=chat_id, photo=open(f'{i}.png', 'rb')) for i in range(1, 5)]
        return ConversationHandler.END
    elif (option == 'Get .ply file'):
        #send ply file
        bot = context.bot
        # try:
        #     bot.send_document(chat_id=chat_id, document=open("ply0.ply",'rb'))
        #     return ConversationHandler.END
        all_points, all_triangles = get_all_triangles_points(files_dir / ifc_file_name)
        get_mesh(all_points, all_triangles)
        
        bot.send_document(chat_id=chat_id, document=open("ply0.ply",'rb'))
        return ConversationHandler.END
       
    else:
        update.message.reply_text('Invalid option', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

def get_ifc_file(update, context):
    ifc_file_name = update.message.text
    ifc_file_name = ifc_file_name.lower()
    all_files = getJson(files_dir / 'files.json')
    all_ifc = all_files['ifc']
    try:
        index = [index for index, item in enumerate(all_ifc) if item['name'].lower() == ifc_file_name][0]
        ifc_file_name = all_ifc[index]['file_name']
        update.message.reply_text('Successfully loaded file!')
        context.user_data['ifc_file_name'] = ifc_file_name
        return ifc_start(update, context)
    except:
        update.message.reply_text('No file with this filename')
        ifc_file_name = None
        return ConversationHandler.END

def get_stretch_parameters(update, context):
    ifc_file_name = context.user_data['ifc_file_name']
    stretch_parameters = update.message.text
    try:
        parameters = stretch_parameters.split(',')
        if len(parameters) != 3:
            update.message.reply_text('Invalid format! Format must be <code>min_z, max_z, amount</code>. Cancelled transaction', reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
        
        all_points, all_triangles = get_all_triangles_points(files_dir / ifc_file_name)
        stretched_points = stretch_z(all_points, float(parameters[0]), float(parameters[1]), float(parameters[2]))
        context.user_data['stretched_points'] = stretched_points
        update.message.reply_text(f'Success! Stretched all points along the z axis from {float(parameters[0])} to {float(parameters[1])} by {float(parameters[2])}')
        update.message.reply_text(f'Showing preview of stretching:')
        show_building(get_mesh(stretched_points, all_triangles))
        bot = context.bot
        chat_id = update.message.chat_id
        [bot.send_photo(chat_id=chat_id, photo=open(f'{i}.png', 'rb')) for i in range(1, 5)]
        update.message.reply_text('Enter the name of the file you\'d like to save this as under IFC. If don\'t wish to save, type <code>cancel</code>')
        return GET_STRETCHED_NAME
    except Exception as e:
        update.message.reply_text(f'Failed! Error message:\n<code>{e}</code>')
        return ConversationHandler.END

def get_stretched_name(update, context):
    ifc_name = update.message.text
    context.user_data['ifc_name'] = ifc_name
    if ifc_name.lower() == 'cancel':
        update.message.reply_text('Let\'s forget that ever happened...')
        return ConversationHandler.END
    update.message.reply_text(f'Enter a description of the file:')
    return SAVE_STRETCHED

def save_stretched(update, context):
    ifc_file_name = context.user_data['ifc_file_name']
    ifc_name = context.user_data['ifc_name']
    stretched_points = context.user_data['stretched_points']

    user = update.message.from_user
    response = update.message.text
    from Modules.files import save_file_type
    import time
    file_title = 'stretched' + str(int(time.time()))
    # with Path(files_dir / file_title).open(mode='w') as outfile:
    #     json.dump(j, outfile, indent=4)
    
    save_to_new_ifc(stretched_points, ifc_file_name, file_title)
    save_file_type(update, context, ifc_name, file_title + '.json', response, 'ifc', user)
    update.message.reply_text('Successfully saved IFC file! To view, use /ifc')
    return ConversationHandler.END
    


def start_analysis(update, context):
    ifc_file_name = context.user_data['ifc_file_name']
    json_obj = getJson(files_dir / ifc_file_name)
    classes = {}
    for item in json_obj:
        class_name = item['Class']
        if class_name == 'ShapeRepresentation':
            pass
        elif class_name in classes.keys():
            classes[class_name]['Count'] += 1
            try:
                classes[class_name]['Sum of PSet_Revit_Dimensions'] += item['PSet_Revit_Dimensions']
            except:
                pass
            if (class_name == 'Wall'):
                if 'Volume' in item.keys():
                    classes[class_name]['Volume'] += item['Volume']
        else:
            classes[class_name] = {}
            classes[class_name]['Count'] = 1
            try:
                classes[class_name]['Sum of PSet_Revit_Dimensions'] = item['PSet_Revit_Dimensions']
            except:
                pass
            if (class_name == 'Wall'):
                classes[class_name]['Volume'] = 0
                if 'Volume' in item.keys():
                    classes[class_name]['Volume'] += item['Volume']

    output = "<code>"
    for class_key in classes.keys():
        item = classes[class_key]
        output += (f'\u2022 {class_key}\n')
        for key in item.keys():
            output += f'    {key:<32}: {item[key]}\n'
        output += "\n"
    output += "</code>"
    update.message.reply_text(classes)
    update.message.reply_text(output)
    return ConversationHandler.END

