from beats import (token, getJson)
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

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


ADD_TASK, ADD_DESCRIPTION, TO_GROUP = range(11,14)



def assign_task(update,context):


    #setup for add task
    update.message.reply_text("What is the task that you want to add")
    return ADD_TASK

description = ""
def add_task(update,context):
    task = update.message.text
    context.user_data['task'] = task


    #setup for add description
    update.message.reply_text("Please write a short description")
    
    return ADD_DESCRIPTION


def add_description(update, context):
    
    description = update.message.text
    context.user_data['description'] = description
    
    #setup for choose group
    with open('teams.json') as json_file:
        teams = json.load(json_file)

    context.user_data['teams'] = teams

    team_names = "<u>Groups:</u> \n"
    reply_keyboard = []
    for i in range(len(teams["teams"])):
        team_names += f"  {i+1}: {teams['teams'][i]['group_name']}\n"
        reply_keyboard += [str(i+1)]
    update.message.reply_text(team_names)

    update.message.reply_text("Which group would you like to assign this task to? ",
    reply_markup=ReplyKeyboardMarkup([reply_keyboard], one_time_keyboard=True))


    return TO_GROUP


def to_group(update, context):
    teams = context.user_data['teams']

    group = update.message.text
    
    task = context.user_data['task']
    description = context.user_data['description']

    try:
        group = int(group)-1
    except:
        update.message.reply_text('Not a number. Cancelling transaction. Type /teamstart to try again.', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    try:
        teams["teams"][group]["tasks"].append(task)
        teams["teams"][group]["descriptions"].append(description)
    except:
        update.message.reply_text('Invalid group number. Cancelling transaction. Type /teamstart to try again.', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    with open('teams.json', 'w') as outfile:
        json.dump(teams, outfile, indent = 4)

    update.message.reply_text("Task has been added to group: " + teams["teams"][group]["group_name"])

    return ConversationHandler.END 