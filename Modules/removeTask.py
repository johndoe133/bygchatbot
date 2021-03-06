from Modules.beats import (token, getJson)
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
from Modules.viewTask import *

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


FROM_GROUP, CHOOSE_TASK, CONFIRM = range(14,17)


def remove_task(update, context):

    #setup for choose group

    view_task(update, context)

    with open('teams.json') as json_file:
        teams = json.load(json_file)
    context.user_data['teams'] = teams
    reply_keyboard = []
    for i in range(1,1+len(teams["teams"])):
        reply_keyboard += [str(i)]

    update.message.reply_text("From which group would you like to remove a task?",
    reply_markup=ReplyKeyboardMarkup([reply_keyboard], one_time_keyboard=True))
    

    return FROM_GROUP

def from_group(update,context):
    group = int(update.message.text)-1
    context.user_data['group'] = group
    teams = context.user_data['teams']

    #setup for choose task
    if (teams["teams"][group]["tasks"]==[]):
        update.message.reply_text("This group does currently not have any assigned tasks")
        return ConversationHandler.END 

    tasks = "<u>Tasks:</u> \n"
    reply_keyboard = []

    for i in range(1,1+len(teams["teams"][group]["tasks"])):
        tasks += f"  {i}: {teams['teams'][group]['tasks'][i-1]}\n"
        reply_keyboard += [str(i)]
    reply_keyboard += ["Cancel"]
    update.message.reply_text(tasks, )

    
    update.message.reply_text("Which task would you like to remove?",
    reply_markup=ReplyKeyboardMarkup([reply_keyboard], one_time_keyboard=True))

    return CHOOSE_TASK

def choose_task(update, context):
    teams = context.user_data['teams']
    group = context.user_data['group']
    index = update.message.text
    if (index.lower() == "cancel"):
        update.message.reply_text("No task has been removed")
        return ConversationHandler.END

    index = int(index)-1
    context.user_data['index'] = index

    task = teams['teams'][group]['tasks'][index]
    desc = teams['teams'][group]['descriptions'][index]
    #setup for confirm
    

    reply_keyboard = ["Yes", "No"]
    update.message.reply_text("Are you sure you would like to remove the task: \n" + task + "\n "+ desc, 
    reply_markup=ReplyKeyboardMarkup([reply_keyboard], one_time_keyboard=True))

    return CONFIRM

def confirm(update, context):
    teams = context.user_data['teams']
    group = context.user_data['group']
    index = context.user_data['index']

    confirm = update.message.text

    if (confirm.lower() != "yes"):
        update.message.reply_text("You have chosen to NOT remove the task")
        return ConversationHandler.END

    del teams["teams"][group]["tasks"][index]
    del teams["teams"][group]["descriptions"][index]
    context.user_data['teams'] = teams

    with open('teams.json', 'w') as outfile:    
        json.dump(teams, outfile, indent = 4)

    update.message.reply_text("The task has been removed")

    return ConversationHandler.END