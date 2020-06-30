from beats import (token, getJson)
import logging
import json
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

from Modules.info import *
from Modules.files import *
from Modules.agile_help import *
from Modules.define import *

from Modules.teamCreater import *
from Modules.team_viewer import *
from Modules.teamJoiner import *

from Modules.SprintDuration import *
from Modules.assignTask import *
from Modules.removeTask import *
from Modules.viewTask import *


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


GET_RESPONSE,CHECK_OVERWRITE, EDIT_GROUPS = range(3)

def team_start(update, context):

    reply_keyboard = [["Create Groups", "View Groups", "Join Group", "Edit Groups"]]
    #Maybe make create groups also have to fix a sprint duration?
    
    #maybe turn sprint duration from days into date (based on the current date and number of days)
    
    #change 'edit groups' into 'edit tasks' (since thats what we do) - also implement it

    update.message.reply_text("What would you like to do?", 
    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))


    return GET_RESPONSE

def get_response(update, context):

    option = update.message.text


    if (option == "Create Groups"):
        reply_keyboard = [["Yes", "No"]]
        update.message.reply_text("Are you sure you want to overwrite the current Groups?", 
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

        return CHECK_OVERWRITE
    elif (option == "View Groups"):
        return view_team(update, context)
    elif (option == "Edit Groups"):
        reply_keyboard = [["Change Sprint Duration","View Tasks", "Assign Task", "Remove Task"]]
        update.message.reply_text("What would you like to do?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return EDIT_GROUPS
    elif (option == "Join Group"):
        return join_team(update, context)

    update.message.reply_text("Invalid Option")

    return ConversationHandler.END  


def check_overwrite(update,context):

    confirm = update.message.text

    if (confirm != "Yes"):
        update.message.reply_text("You have cancelled the overwrite. Nothing has changed")
        return ConversationHandler.END  

    return create_team(update, context)

def edit_groups(update, context):
    
    option = update.message.text
    
    if (option == "Change Sprint Duration"):
        return set_duration(update, context)
    elif (option == "View Tasks"):
        return view_task(update, context)
    elif (option == "Assign Task"):
        return assign_task(update,context)
    elif (option == "Remove Task"):
        return remove_task(update, context)

    update.message.reply_text("Invalid Option")

    return ConversationHandler.END  
    



