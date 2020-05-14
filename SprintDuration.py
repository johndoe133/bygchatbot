from chatbot import (token, get, getBuildingFloorArea, getBuildingHeight, 
                    getBuildingVolume, getJson, getHeight, getVolume, getFloorArea)
import logging
import json
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

from info import *
from files import *
from AgileHelp import *
from define import *
from teamCreater import *

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

EDIT_DURATION,CHOOSE_DURATION = range(2)

def set_duration(update, context):

    reply_keyboard = ["Yes", "No"]


    update.message.reply_text('would you like to edit the duration of the sprint? ', 
    reply_markup=ReplyKeyboardMarkup([reply_keyboard], one_time_keyboard=True))
    return EDIT_DURATION


def edit_duration(update,context):
    with open('teams.json') as json_file:
        teams = json.load(json_file)

    user = update.message.from_user
    confirm = update.message.text

    print(confirm)

    if (confirm == "Yes"):
        update.message.reply_text("Choose the length of the sprint (number of days)")
        return CHOOSE_DURATION
    else:
        update.message.reply_text('The duration of the sprint remains at: '+ str(teams["sprint_duration"]))
        return ConversationHandler.END 

def choose_duration(update,context):
    with open('teams.json') as json_file:
        teams = json.load(json_file)

    user = update.message.from_user 
    duration = update.message.text

    try:
        duration = int(duration)
    except:
        update.message.reply_text("The sprint duration must be an integer")
        update.message.reply_text('The duration of the sprint remains at: '+ str(teams["sprint_duration"]))
        return ConversationHandler.END 
    
    teams["sprint_duration"] = duration
    update.message.reply_text('The duration of the sprint has been set to: '+ str(teams["sprint_duration"]))
    
    
    with open('teams.json', 'w') as outfile:
        json.dump(teams, outfile, indent = 4)
    
    return ConversationHandler.END 

