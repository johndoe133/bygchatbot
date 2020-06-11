from chatbot import (token, get, getBuildingFloorArea, getBuildingHeight, 
                    getBuildingVolume, getJson, getHeight, getVolume, getFloorArea)
import logging
import json
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode)
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
    json_formatted = json.dumps(json_obj, indent=0)
    formatted_str = "<code>----------</code>\n"
    for line in json_formatted.split("\n"):
        if (line == "{"):
            formatted_str += ""
        elif (line in ["},","}"]):
            formatted_str += "<code>----------</code>\n"
        elif (line in ["[","]"]):
            pass
        else:
            if ("name" in line or "team" in line):
                line = line.replace("\"", "")
                line = line.strip(",")
                line = line.split(": ")
                formatted_str += f'<code>{line[0]:5}: {line[1]:<20}</code>\n'
    update.message.reply_text(
        'Hi! I am the BygBot. I will hold a conversation with you. '
        'Send /cancel to stop talking to me.\n\n'
        'This is the information I found so far:\n' + formatted_str + 
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
    json_formatted = json.dumps(json_obj[TEAM_INDEX], indent=2)
    formatted_str = "==========================\n"
    for line in json_formatted.split("\n"):
        if (line == "{"):
            formatted_str += ""
        elif (line in ["    {"]):
            formatted_str += ""
        elif (line in ["},", "}"]):
            formatted_str += "==========================\n"
        elif (line in ["    },", "    }"]):
            formatted_str += "<code>    ---</code>\n"
        elif (line.strip() in ["[","]","],"]):
            pass
        else:
            line = line.replace("\"", "")
            line = line.strip(",")
            line = line.split(": ")
            if (line[1] == "["):
                line[1] = ""
            formatted_str += f'<code>{line[0][2:]:15}:{line[1]:>10}</code>\n'
    update.message.reply_text(
        "This is the information I found on team " + TEAM + "\n"
        +formatted_str+ "\n--------\n"

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
    for index, segment in enumerate(json_obj[TEAM_INDEX]['segments']):
        if segment['id'] == SEGMENT:
            SEGMENT_INDEX = index
    json_formatted = json.dumps(json_obj[TEAM_INDEX]['segments'][SEGMENT_INDEX], indent=0)
    formatted_str = "==========================\n"
    for line in json_formatted.split("\n"):
        if (line == "{"):
            formatted_str += ""
        elif (line in ["},","}"]):
            formatted_str += "==========================\n"
        elif (line in ["[","]"]):
            pass
        else:
            line = line.replace("\"", "")
            line = line.strip(",")
            line = line.split(": ")
            formatted_str += f'<code>{line[0]:15}: {line[1]:>10}</code>\n'
    update.message.reply_text(
        "This is the information I found on segment " + SEGMENT + "\n\n-------\n"
        +formatted_str+ "\n--------\n"
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
    logger.warning('Error %s', context.error)
    return ConversationHandler.END

