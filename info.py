from chatbot import (token, get, getBuildingFloorArea, getBuildingHeight, 
                    getBuildingVolume, getJson, getHeight, getVolume, getFloorArea)
import logging
import json
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

TEAM_INFO, SEGMENT_INFO, GIVE_INFO = range(3)
TEAM = ""
TEAM_INDEX = 0
SEGMENT = ""
SEGMENT_INDEX = 0
METRIC = ""


def start(update, context):
    reply_keyboard = [[]]
    json_obj = getJson('beats.json')
    json_str = ""
    for i, team in enumerate(json_obj):
        del json_obj[i]['segments']
        reply_keyboard[0].append(team['team'])
    
    update.message.reply_text(
        'Hi! I am the BygBot. I will hold a conversation with you. '
        'Send /cancel to stop talking to me.\n\n'
        'This is the information I found so far:\n' + json.dumps(json_obj, indent=2) + 
        '\nWhich team would you like to examine?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return TEAM_INFO


def team_info(update, context):
    json_obj = getJson('beats.json')
    user = update.message.from_user
    global TEAM_INDEX
    TEAM = update.message.text
    for i in range(len(json_obj)):
        if json_obj[i]['team'] == TEAM:
            TEAM_INDEX=i
            break
    logger.info("Team that %s wishes to examine: %s", user.first_name, TEAM)
    logger.info("Team index: %i", TEAM_INDEX)
    reply_keyboard = [[]]
    for segment in json_obj[TEAM_INDEX]["segments"]:
        reply_keyboard[0].append(str(segment["id"]))
    json_team = json_obj[TEAM_INDEX]
    update.message.reply_text(
        "This is the information I found on team " + TEAM + "\n\n-------\n"
        +json.dumps(json_obj[TEAM_INDEX], indent=2)+ "\n--------\n"

        "Which segment would you like to look at?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return SEGMENT_INFO

def segments_info(update, context):
    json_obj = getJson('beats.json')
    user = update.message.from_user
    SEGMENT = update.message.text
    global TEAM_INDEX
    global SEGMENT_INDEX
    reply_keyboard = [['Height','Volume','Floor Area', 'Cancel']]
    print(TEAM_INDEX)
    for index, segment in enumerate(json_obj[TEAM_INDEX]['segments']):
        if segment['id'] == SEGMENT:
            SEGMENT_INDEX = index
    print(SEGMENT_INDEX)
    update.message.reply_text(
        "This is the information I found on segment " + SEGMENT + "\n\n-------\n"
        +json.dumps(json_obj[TEAM_INDEX]['segments'][SEGMENT_INDEX], indent=2)+ "\n--------\n"
        "What further information would you like on segment " + SEGMENT,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return GIVE_INFO

def give_info(update, context):
    # get beats.json
    json_obj = getJson('beats.json')
    user = update.message.from_user

    # metric desired
    METRIC = update.message.text
    logger.info("Metric user %s desires: %s", user.first_name, METRIC)

    global TEAM_INDEX
    global SEGMENT_INDEX

    if (METRIC == 'Height'):
        update.message.reply_text('The height of the building is: ' + str(getHeight(TEAM_INDEX, SEGMENT_INDEX)),
        reply_markup=ReplyKeyboardRemove())
    elif (METRIC == 'Volume'):
        update.message.reply_text('The volume of the building is: ' + str(getVolume(TEAM_INDEX, SEGMENT_INDEX)),
        reply_markup=ReplyKeyboardRemove())
    elif (METRIC == 'Floor Area'):
        update.message.reply_text('The floor area is: ' + str(getFloorArea(TEAM_INDEX, SEGMENT_INDEX)),
        reply_markup=ReplyKeyboardRemove())
    elif (METRIC == 'Cancel'):
        return ConversationHandler.END
    print('ended conversation')
    return ConversationHandler.END

def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    update.message.reply_text('Oops! Looks like I ran into an error there.')
    logger.warning('Update "%s" caused error "%s"', update, context.error)

