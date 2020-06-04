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
from team_viewer import *
from teamJoiner import *
from SprintDuration import *
from assignTask import *
from removeTask import *
from viewTask import *


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


GET_RESPONSE,CHECK_OVERWRITE, EDIT_GROUPS = range(3)

def team_start(update, context):

    reply_keyboard = [["Create Groups", "View Groups", "Edit Groups", "Join Group"]]

    update.message.reply_text("What would you like to do?", 
    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))


    return GET_RESPONSE

def get_response(update, context):

    option = update.message.text
    print(option)


    if (option == "Create Groups"):
        reply_keyboard = [["Yes", "No"]]
        update.message.reply_text("Are you sure you want to overwrite the current Groups?", 
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

        return CHECK_OVERWRITE
    elif (option == "View Groups"):
        return view_team(update, context)
    elif (option == "Edit Groups"):
        return EDIT_GROUPS
    elif (option == "Join Group"):
        return join_team(update, context)

    update.message.reply_text("heyy whats up yo")

    return ConversationHandler.END  


def check_overwrite(update,context):

    confirm = update.message.text

    if (confirm != "Yes"):
        update.message.reply_text("You have cancelled the overwrite. Nothing has changed")
        return ConversationHandler.END  

    return create_team(update, context)





