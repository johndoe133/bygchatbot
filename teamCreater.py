from chatbot import (token, get, getBuildingFloorArea, getBuildingHeight, 
                    getBuildingVolume, getJson, getHeight, getVolume, getFloorArea)
import logging
import json
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

#probably wont need all the extensions..
from info import *
from files import *
from AgileHelp import *
from define import *


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# states:
#create team
#
NUMBER_GROUPS,NAME_GROUP,MAKE_GROUP = range(5,8)

teams ={}
def create_team(update, context):
    global teams
    teams['teams'] = []

    chat_id = update.message.chat_id

    user = update.message.from_user
    print('You talk with user {} and his user ID: {} '.format(user['username'], user['id']))
    print(user)

    logger.info('user %s wants to update teams', update.message.from_user.name)
    
    #with open('testjson2.json', 'w') as outfile:
    #    json.dump(teams, outfile, indent = 4)
    
    update.message.reply_text('How many groups would you like to create?')
    return NUMBER_GROUPS
    

counter = 0
group_no = 1
def number_groups(update,context):    
    user = update.message.from_user
    global counter
    global group_no
    counter = update.message.text
    
    logger.info('user %s wants to create %s teams', user.name, counter)
    print(1)
    try: 
        counter = int(counter)-1
        update.message.reply_text(f'Write group {group_no}\'s group name')
        return NAME_GROUP
    except:
        update.message.reply_text('Not a valid number')
        logger.info('not a number', user.name)
    return ConversationHandler.END 

    

        
def name_group(update,context):
    print(4)
    global counter
    global teams
    global group_no
    #user = update.message.from_user
    #logger.info('user %s is now naming %s teams', user.name, number)
    
    print(5)
    groupName = update.message.text
    print(groupName)
    update.message.reply_text(f"Group {group_no}\'s name is {groupName}")
    teams['sprint_duration'] = 1
    teams['teams'].append({
        "group_name": groupName,
        "group_id": (group_no),
        "group_members" : [],
        "tasks" : [],
        "descriptions": []

    })
    group_no += 1

    if (counter <= 0):
        print(teams)
        with open('teams.json', 'w') as outfile:
            json.dump(teams, outfile, indent = 4)
        return ConversationHandler.END 
    else:
        counter-=1
        print(6)
        update.message.reply_text(f"Write group {group_no}\'s group name")
        return NAME_GROUP
        #name_group(update,context)
        print("we're done here")    



"""
list all groups

/join x to join group x


what about empty groups, what about non assigned people?
"""

def make_group(update, context):
    
    return ConversationHandler.END 



def getNum(bot, update):
    chat_id = update.message.chat_id
    #this is to get how many chat members are.. but i want it somewhere else
    number = bot.getChatMembersCount(chat_id)  
    return number


"""
import json
teams ={}
teams['people'] = []
teams['people'].append({
    'name': 'Scott',
    'website': 'stackabuse.com',
    'from': 'Nebraska'
})
teams['people'].append({
    'name': 'Larry',
    'website': 'google.com',
    'from': 'Michigan'
})
teams['people'].append({
    'name': 'Tim',
    'website': 'apple.com',
    'from': 'Alabama'
})
with open('testjson2.json', 'w') as outfile:
    json.dump(teams, outfile, indent = 4)
"""