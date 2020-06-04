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


temp = range(1)

def view_task(update, context):

    global teams
    with open('teams.json') as json_file:
        teams = json.load(json_file)
        
    team_names = "<u>Teams:</u> \n"
    tasks = "<u>Tasks:</u> \n"

    reply_keyboard = []
    for i in range(len(teams["teams"])):
        team_names += f"  {i}: {teams['teams'][i]['group_name']}\n"
        reply_keyboard += [str(i)]
        for j in range(len(teams["teams"][i]["tasks"])):
            tasks += f"  {j}: {teams['teams'][i]['tasks'][j]}\n"
            reply_keyboard += [str(j)]
    update.message.reply_text(team_names, )


    print(team_names,tasks)

    tasks = "<u>Tasks:</u> \n"
    reply_keyboard = []
    for j in range(len(teams["teams"][i]["tasks"])):
        tasks += f"  {j}: {teams['teams'][i]['tasks'][j]}\n"
        reply_keyboard += [str(j)]
    update.message.reply_text(tasks, )

    return ""    