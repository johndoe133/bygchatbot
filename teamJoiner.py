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

CHOOSE_TEAM, ADD_TO_TEAM = range(2)

def join_team(update, context):
    global number
    global teams
    with open('teams.json') as json_file:
        teams = json.load(json_file)
    print("joining team, testing number: "+ str(number))
    for i in range(len(teams["teams"])):
        update.message.reply_text(teams["teams"][i]["group_name"])
    

    logger.info('user %s wants to join a teams', update.message.from_user.name)
    update.message.reply_text('which team would you like to join?')

    return CHOOSE_TEAM
    
    
    

def choose_team(update, context):
    print(0)
    user = update.message.from_user
    team = update.message.text
    print(1)
    for i in range(len(teams["teams"])):
        print(teams["teams"][i]["group_name"]+"\n")

    for i in range(len(teams["teams"])):
        if (teams["teams"][i]["group_name"] == team):
            print("joining team "+ team)
            
            for j in range(len(teams["teams"])):
                try:
                    teams["teams"][i]["group_members"].remove(user.name).remove(user.name)
                except:
                    pass
            
            teams["teams"][i]["group_members"].append(user.name)
            #wacky temp way of removing dublicates
            teams["teams"][i]["group_members"] = list(set(teams["teams"][i]["group_members"]))
            

            with open('teams.json', 'w') as outfile:
                json.dump(teams, outfile, indent = 4)
            update.message.reply_text(user.name+" has been added to team: "+team)
            return ConversationHandler.END

    #teams["teams"][i]["group_members"].remove(user.name) 

    update.message.reply_text('No group with name: "'+ team + '"')
    return ConversationHandler.END 

    #if (user in teams["teams"]

def add_to_team(update,context):
    return ConversationHandler.END 
