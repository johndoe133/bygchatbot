from chatbot import (token)
import logging
import json
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
from telegram import ParseMode
from info import cancel
from chatbot import getJson
import re
from main import logger

def split_triangles_points(items):
    lines = items[0].split('\n')
    points = []
    triangles = []
    for index, line in enumerate(lines):
        if line[0] == 'v':
            points += [line[2:].split(' ')]
        elif line[0] == 'f':
            triangles += [line[2:].split(' ')]
        else: 
            logger.info(f'failed at index {index} for line {line}')
    print(points,"\n=============")
    return points, triangles

def find_min_dimension(points, dimension):
    minimum = points[0][dimension]
    for point in points:
        if minimum < point[dimension]:
            minimum = point[dimension]
    return minimum

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

def start_analysis(update, context):
    json_obj = getJson('duplex_A.json')
    classes = {}
    for item in json_obj:
        print(f'Mine height: {get_min_height(item)}')
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

