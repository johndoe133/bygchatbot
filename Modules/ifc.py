from beats import (token)
import logging
import json
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
from telegram import ParseMode
from info import cancel
from beats import getJson

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

