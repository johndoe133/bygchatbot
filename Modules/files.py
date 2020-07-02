import logging
import json
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, File)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
from beats import token, getJson
import requests, urllib.request
import jsonschema
from jsonschema import validate
from datetime import datetime
from pathlib import Path

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

REQUEST_FILE, GET_IMAGE, GET_BEATS, GET_IFC, GET_NAME, GET_DESCRIPTION = range(6)

file_type = ""
file_id = ""
file_name = ""
files_dir = Path.cwd() / 'Files'

def ask_file_type(update, context):
    reply_keyboard = [['Image','Beats', 'IFC','Cancel']]
    update.message.reply_text("Please select which file type you'd like to send",
    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return REQUEST_FILE

def request_file(update, context):
    global file_type
    #logging
    user = update.message.from_user

    response = update.message.text
    chat_id = update.message.chat_id
    file_type = response.lower()
    if (file_type not in ['image','beats', 'ifc','cancel']):
        update.message.reply_text('Invalid input. Send file cancelled. Type /sendfile to try again.', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    elif (file_type == 'cancel'):
        update.message.reply_text('Send file cancelled. Type /sendfile to try again.', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    update.message.reply_text(f"Send a(n) {file_type} file to me, if you would like to cancel type 'cancel'")
    return GET_IMAGE

def get_a_file(update, context):
    if (file_type not in ['image', 'beats', 'ifc']):
        return ConversationHandler.END

    #logging
    user = update.message.from_user
    logger.info(f'User {user.first_name} is requested to send {file_type}')
    global file_id
    global file_name
    bot = context.bot

    chat_id = update.message.chat_id
    try:
        if (file_type == 'image'):
            file_id = update.message.photo[-1].file_id
        else:
            file_id =update.message.document.file_id
        gen_file = bot.get_file(file_id)
        gen_file.download()
        # Path(Path.cwd() / file_name).rename(files_dir / file_name)
        logger.info(f'{file_type} successfully downloaded')
        file_name = (str(gen_file.file_path).split('/'))[-1]
        if file_type == 'beats':
            temp_json = getJson(Path.cwd() / file_name)
            valid = (validate_beats(temp_json))
            if (valid != "valid"):
                logger.info('Beats acquired from %s were invalid. Reason %s', user.first_name, valid)
                update.message.reply_text("Invalid beats file due to " + valid + ", cancelling file upload. Type /sendfile to try again")
                return ConversationHandler.END
        Path(Path.cwd() / file_name).rename(files_dir / file_name)
        update.message.reply_text(f"{file_type[0].upper()}{file_type[1:]} acquired!")
        update.message.reply_text('Please enter a short title of the file')
        return GET_NAME
    except Exception as e:
        logger.info('Failed to acquire %s from %s', file_type, user.first_name)
        logger.info(e)
        update.message.reply_text(f"File was not a(n) {file_type}, cancelling file upload. Type /sendfile to try again")
        return ConversationHandler.END

def get_name(update, context):
    global file_type
    name = update.message.text
    user = update.message.from_user
    j = getJson(files_dir / 'files.json')
    if not (file_type in j.keys()):
        j[file_type] = []
    counter = 0
    duplicate = False
    for item in j[file_type]:
        if item['name'] == name:
            duplicate = True
            update.message.reply_text(f'The file name \'{name}\' is already in use')
        elif item['name'][:-4] == name:
            counter += 1
    if duplicate:
        update.message.reply_text(f'Uploading file as \'{name} ({counter})\'')
        name += f" ({counter})"

    j[file_type].append({"name":name, "uploaded_by":user.name, "date":str(datetime.now()), 'file_id':file_id, 'file_name':file_name})
    with Path(files_dir / 'files.json').open(mode='w') as outfile:
        json.dump(j, outfile, indent=4)

    update.message.reply_text('Enter a description: ')
    return GET_DESCRIPTION

def get_description(update, context):
    desc = update.message.text
    j = getJson(files_dir / 'files.json')
    j[file_type][-1]['description'] = desc
    with Path(files_dir / 'files.json').open(mode='w') as outfile:
        json.dump(j, outfile, indent=4)
    update.message.reply_text('File uploaded! View your files with /filemanage')
    return ConversationHandler.END
    

def validate_beats(obj):
    beats_schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "team": {"type": "string"},
                "segments": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id":{"type": "integer"},
                            "order":{"type": "string"},
                            "name": {"type": "string"},
                            "flrs": {"anyOf": [{"type": "integer"},{"type": "null"}]},
                            "gfa": {"anyOf": [{"type": "number"},{"type": "null"}]},
                            "f2f": {"anyOf": [{"type": "number"},{"type": "null"}]},
                        }
                    }
                },
                "min_off_hgt": {"anyOf": [{"type": "number"},{"type": "null"}]},
                "min_off_wid": {"anyOf": [{"type": "number"},{"type": "null"}]},
                "footprint": {"anyOf": [{"type": "number"},{"type": "null"}]},
                "shaft_area": {"anyOf": [{"type": "number"},{"type": "null"}]},
                "cars_required": {"anyOf": [{"type": "integer"},{"type": "null"}]},
                "cars_provided": {"anyOf": [{"type": "integer"},{"type": "null"}]},
                "perm_sing_off": {"anyOf": [{"type": "number"},{"type": "null"}]},
                "perm_open_off": {"anyOf": [{"type": "number"},{"type": "null"}]}
            }
        }
    }
    try:
        validate(instance=obj, schema=beats_schema)
    except jsonschema.exceptions.ValidationError as err:
        return "format/type error"
    if (check_team_duplicates(obj)):
        return "duplicate team"
    elif (check_id_duplicates(obj)):
        return "duplicate id"
    else:
        return "valid"

def check_team_duplicates(json_obj):
    for index, team in enumerate(json_obj):
        for i in range(index+1, len(json_obj)):
            if (team["team"] == json_obj[i]['team']):
                return True
    return False

def check_id_duplicates(json_obj):
    for team in json_obj:
        for index, segment in enumerate(team['segments']):
            for i in range(index+1, len(team['segments'])):
                if (segment['id'] == json_obj[index]['segments'][i]['id']):
                    return True
    return False
