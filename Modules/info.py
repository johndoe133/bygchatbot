from beats import (token, getJson, getVolume, getVolume, getFloorArea, getHeight)
import logging
import json
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
from Modules.file_management import show_all_file_type
from pathlib import Path

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

OVERVIEW, TEAM_INFO, SEGMENT_INFO, GIVE_INFO = range(4)
TEAM = ""
TEAM_INDEX = None
SEGMENT = ""
SEGMENT_INDEX = None
METRIC = ""
beats_path = Path('.')
beats_file_name = ""

def view_beats(update, context):
    j = getJson(Path(Path.cwd()) / 'Files' / 'files.json')
    if len(j['beats']) == 0:
        update.message.reply_text('You have not uploaded any beats files yet!')
        return ConversationHandler.END
    update.message.reply_text(show_all_file_type(j, 'beats'))
    update.message.reply_text('To get an overview of the beats, first select a beats file to view')
    return OVERVIEW

def overview(update, context):
    global beats_path
    global beats_file_name
    reply_keyboard = [[]]
    file_title = update.message.text
    j = getJson(Path(Path.cwd()) / 'Files' / 'files.json')
    beats_file_name = [item['file_name'] for item in j['beats'] if item['name'] == file_title]
    if len(beats_file_name) == 0:
        update.message.reply_text('Invalid file title, cancelling action. Type /viewbeats to try again.')
        return ConversationHandler.END
    beats_file_name = beats_file_name[0]
    beats_path = Path(Path.cwd() / 'Files' / beats_file_name)
    json_obj = getJson(beats_path)
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
    json_obj = getJson(beats_path)
    user = update.message.from_user
    global TEAM_INDEX
    TEAM = update.message.text
    found = False
    for i in range(len(json_obj)):
        if json_obj[i]['team'] == TEAM:
            found = True
            TEAM_INDEX=i
            break
    if (not found):
        update.message.reply_text('Invalid team, cancelling action. Try /viewbeats to try again.',
        reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
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
    json_obj = getJson(beats_path)
    user = update.message.from_user
    SEGMENT = update.message.text
    try:
        SEGMENT = int(SEGMENT)
    except:
        update.message.reply_text('Invalid segment. It must be a number. Cancelling action, try /viewbeats to try again'
        , reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    global TEAM_INDEX
    global SEGMENT_INDEX
    reply_keyboard = [['Height','Volume','Floor Area', 'Cancel']]
    found = False
    for index, segment in enumerate(json_obj[TEAM_INDEX]['segments']):
        print(index)
        if segment['id'] == SEGMENT:
            found = True
            print('found it')
            SEGMENT_INDEX = index
    
    if (not found):
        update.message.reply_text('Invalid segment, cancelling action. Try /viewbeats to try again.',
        reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

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
        "This is the information I found on segment " + str(SEGMENT) + "\n\n-------\n"
        +formatted_str+ "\n--------\n"
        "What further information would you like on segment " + str(SEGMENT),
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return GIVE_INFO

def give_info(update, context):
    # get beats.json
    json_obj = getJson(beats_path)
    user = update.message.from_user

    # metric desired
    METRIC = update.message.text
    logger.info("Metric user %s desires: %s", user.first_name, METRIC)

    global TEAM_INDEX
    global SEGMENT_INDEX
    try:
        if (METRIC == 'Height'):
            update.message.reply_text('The height of the building is: ' + str(getHeight(json_obj, TEAM_INDEX, SEGMENT_INDEX)),
            reply_markup=ReplyKeyboardRemove())
        elif (METRIC == 'Volume'):
            update.message.reply_text('The volume of the building is: ' + str(getVolume(json_obj, TEAM_INDEX, SEGMENT_INDEX)),
            reply_markup=ReplyKeyboardRemove())
        elif (METRIC == 'Floor Area'):
            update.message.reply_text('The floor area is: ' + str(getFloorArea(json_obj, TEAM_INDEX, SEGMENT_INDEX)),
            reply_markup=ReplyKeyboardRemove())
        elif (METRIC == 'Cancel'):
            update.message.reply_text('Cancelling action, try /viewbeats to try again.',
            reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
        else:
            update.message.reply_text('Invalid input. Cancelling action, try /viewbeats to try again.',
            reply_markup=ReplyKeyboardRemove())
    except:
        update.message.reply_text('Invalid measurements. Cancelling action, try /viewbeats to try again',
            reply_markup=ReplyKeyboardRemove())
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

