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

CHOOSE_TEAM, ADD_TO_TEAM = range(3,5)

def join_team(update, context):
    # global counter
    # global teams
    with open('teams.json') as json_file:
        teams = json.load(json_file)
    context.user_data['joiner_teams'] = teams
    # logger.info(f"{update.message.from_user.name} is joining team number "+ str(counter))
    team_names = "<u>Teams:</u> \n"
    reply_keyboard = []
    
    for i in range(1,1+len(teams["teams"])):
        team_names += f"  {i}: {teams['teams'][i-1]['group_name']}\n"
        reply_keyboard += [str(i)]
    update.message.reply_text(team_names)

    logger.info('user %s wants to join a teams', update.message.from_user.name)
    update.message.reply_text('which group would you like to join?', 
    reply_markup=ReplyKeyboardMarkup([reply_keyboard, ["Cancel"]], one_time_keyboard=True))

    return CHOOSE_TEAM
    
    
    

def choose_team(update, context):
    teams = context.user_data['joiner_teams']
    user = update.message.from_user
    team_no = update.message.text
    if team_no.lower() == 'cancel':
        update.message.reply_text('Cancelling transaction. Type /teamstart to try again.', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    try:
        team_no = int(team_no)-1
    except:
        update.message.reply_text('Not a number. Cancelling transaction. Type /teamstart to try again.', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    try:
        team_name = teams['teams'][team_no]['group_name']
    except:
        update.message.reply_text('Invalid team number. Cancelling transaction. Type /teamstart to try again.', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    logger.info(f"{update.message.from_user.name} is joining team "+ team_name)
    
    for j in range(len(teams["teams"])):
        try:
            teams["teams"][j]["group_members"].remove(user.name).remove(user.name)
        except:
            pass
    
    teams["teams"][team_no]["group_members"].append(user.name)
    #wacky temp way of removing dublicates
    teams["teams"][team_no]["group_members"] = list(set(teams["teams"][team_no]["group_members"]))
    

    with open('teams.json', 'w') as outfile:
        json.dump(teams, outfile, indent = 4)
    update.message.reply_text(user.name+" has been added to team: "+team_name)
    return ConversationHandler.END

    #teams["teams"][i]["group_members"].remove(user.name) 

    update.message.reply_text('No group with name: "'+ team_name + '"')
    return ConversationHandler.END 

