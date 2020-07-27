from telegram.ext import (Updater, CommandHandler)
import json
import re
from uuid import uuid4
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

def getArgs(update):
    key = str(uuid4())
    args = update.message.text.partition(' ')[2].split(' ')
    return args

def getInfo(json_obj, args):
    if args[0] == '':
        return json.dumps(json_obj, indent=2)
    prev = json_obj
    for item in args:
        try:
            prev = prev[int(item)]
        except:
            prev = prev[item]
    return json.dumps(prev, indent=2)


def getJson(filename):
    with open(filename) as json_file:
        json_obj = json.load(json_file)
    return json_obj

token = getJson('token.json')['token']

def getHeight(json_obj, team_index, segment_index):
    f2f = float(json_obj[team_index]['segments'][segment_index]['f2f'])
    flrs = int(json_obj[team_index]['segments'][segment_index]['flrs'])
    return f2f * flrs

def getFloorArea(json_obj, team_index, segment_index):
    flrs = int(json_obj[team_index]['segments'][segment_index]['flrs'])
    gfa = float(json_obj[team_index]['segments'][segment_index]['gfa'])
    return gfa / flrs

def getVolume(json_obj, team_index, segment_index):
    return getFloorArea(json_obj, team_index, segment_index) * getHeight(json_obj, team_index, segment_index)


def getBuildingHeight(bot, update):
    chat_id = update.message.chat_id
    args = getArgs(update)
    bot.send_message(chat_id=chat_id, text=getHeight(int(args[0])))

def getBuildingFloorArea(bot, update):
    chat_id = update.message.chat_id
    args = getArgs(update)
    bot.send_message(chat_id=chat_id, text=getFloorArea(int(args[0])))

#how to get this value in teamcreater?
def getNum (bot, update):
    chat_id = update.message.chat_id
    args = getArgs(update)
    number = bot.getChatMembersCount(chat_id)
    bot.send_message(chat_id=chat_id, text=number)
