from beats import (token, get, getBuildingFloorArea, getBuildingHeight, 
                    getBuildingVolume, getJson, getHeight, getVolume, getFloorArea)
import logging
import json
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

from info import *
from files import *
from agile_help import *
from define import *
from teamCreater import *
from viewTask import *

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


FROM_GROUP, CHOOSE_TASK, CONFIRM = range(14,17)


def remove_task(update, context):

    #setup for choose group
    global teams

    view_task(update, context)

    with open('teams.json') as json_file:
        teams = json.load(json_file)
    reply_keyboard = []
    for i in range(len(teams["teams"])):
        reply_keyboard += [str(i)]

    update.message.reply_text("From which group would you like to remove a task?",
    reply_markup=ReplyKeyboardMarkup([reply_keyboard], one_time_keyboard=True))
    

    return FROM_GROUP

group = 0
def from_group(update,context):
    global group
    global teams
    group = int(update.message.text)


    #setup for choose task
    if (teams["teams"][group]["tasks"]==[]):
        update.message.reply_text("This group does currently not have any assigned tasks")
        return ConversationHandler.END 

    
    with open('teams.json') as json_file:
        teams = json.load(json_file)
    tasks = "<u>Tasks:</u> \n"
    reply_keyboard = []
    for i in range(len(teams["teams"][group]["tasks"])):
        tasks += f"  {i}: {teams['teams'][group]['tasks'][i]}\n"
        reply_keyboard += [str(i)]
    update.message.reply_text(tasks, )

    
    update.message.reply_text("Which task would you like to remove?",
    reply_markup=ReplyKeyboardMarkup([reply_keyboard], one_time_keyboard=True))

    return CHOOSE_TASK

index = ""
def choose_task(update, context):
    global index
    index = int(update.message.text)
    task = teams['teams'][group]['tasks'][index]
    desc = teams['teams'][group]['descriptions'][index]
    #setup for confirm
    

    reply_keyboard = ["Yes", "No"]
    update.message.reply_text("Are you sure you would like to remove the task: \n" + task + "\n "+ desc, 
    reply_markup=ReplyKeyboardMarkup([reply_keyboard], one_time_keyboard=True))

    return CONFIRM

def confirm(update, context):
    global teams
    global index

    confirm = update.message.text

    if (confirm != "Yes"):
        update.message.reply_text("You have chosen to NOT remove the task")
        return ConversationHandler.END

    del teams["teams"][group]["tasks"][index]
    del teams["teams"][group]["descriptions"][index]


    with open('teams.json', 'w') as outfile:    
        json.dump(teams, outfile, indent = 4)

    update.message.reply_text("The task has been removed")

    return ConversationHandler.END