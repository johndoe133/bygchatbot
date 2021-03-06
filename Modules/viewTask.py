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

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def view_task(update, context):
    with open('teams.json') as json_file:
        teams = json.load(json_file)
        
    # team_names = "<u>Teams:</u> \n"
    # tasks = "<u>Tasks:</u> \n"

    tasks_string = ""

    #reply_keyboard = []
    for i in range(len(teams["teams"])):
        tasks_string += f"<u>Group {i+1}: {teams['teams'][i]['group_name']}</u>\n"
        #reply_keyboard += [str(i)]
        for j in range(len(teams["teams"][i]["tasks"])):
            tasks_string += f"  {j+1}: {teams['teams'][i]['tasks'][j]}\n"
            tasks_string += "      "+teams['teams'][i]['descriptions'][j] +"\n"

            #reply_keyboard += [str(j)]
    update.message.reply_text(tasks_string)
    return ConversationHandler.END  