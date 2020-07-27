from Modules.beats import (token, getJson)
import logging
import json
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

#probably wont need all the extensions..
from Modules.info import *
from Modules.files import *
from Modules.agile_help import *
from Modules.define import *


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# states:
#create team
#
NUMBER_GROUPS,NAME_GROUP,MAKE_GROUP = range(5,8)

def create_team(update, context):
    teams = {}
    teams['teams'] = []

    chat_id = update.message.chat_id

    user = update.message.from_user
    logger.info('user %s wants to update teams', update.message.from_user.name)
    
    #with open('testjson2.json', 'w') as outfile:
    #    json.dump(teams, outfile, indent = 4)
    
    update.message.reply_text('How many groups would you like to create?')
    context.user_data['creator_teams'] = teams
    context.user_data['creator_group_no'] = 1
    return NUMBER_GROUPS
    

def number_groups(update,context):    
    user = update.message.from_user
    group_no = context.user_data['creator_group_no']
    counter = update.message.text
    logger.info('user %s wants to create %s teams', user.name, counter)
    try: 
        counter = int(counter)-1
        update.message.reply_text(f'Write group {group_no}\'s group name. If you\'d like to cancel, text cancel instead.', reply_markup=ReplyKeyboardRemove())
        context.user_data['creator_counter'] = counter
        return NAME_GROUP
    except:
        update.message.reply_text('Not a valid number', reply_markup=ReplyKeyboardRemove())
        logger.info('not a number', user.name)
    
    return ConversationHandler.END 

    

        
def name_group(update,context):
    counter = context.user_data['creator_counter']
    group_no = context.user_data['creator_group_no']
    teams = context.user_data['creator_teams']
    #user = update.message.from_user
    #logger.info('user %s is now naming %s teams', user.name, number)
    
    group_name = update.message.text
    if (group_name.lower() == 'cancel'):
        update.message.reply_text('Cancelling transaction. Type /teamstart to try again. ', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    update.message.reply_text(f"Group {group_no}\'s name is {group_name}")
    teams['sprint_duration'] = 1
    teams['first_sprint'] = ""
    teams['teams'].append({
        "group_name": group_name,
        "group_id": (group_no),
        "group_members" : [],
        "tasks" : [],
        "descriptions": []

    })
    group_no += 1

    if (counter <= 0):
        with open('teams.json', 'w') as outfile:
            json.dump(teams, outfile, indent = 4)
        
        return ConversationHandler.END 
    else:
        counter-=1
        context.user_data['creator_counter'] = counter
        context.user_data['creator_group_no'] = group_no
        update.message.reply_text(f"Write group {group_no}\'s group name")

        return NAME_GROUP
        #name_group(update,context)



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