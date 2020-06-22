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

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

REQUEST_FILE, GET_IMAGE, GET_BEATS, GET_IFC, GET_NAME, GET_DESCRIPTION = range(6)

file_type = ""
file_id = ""

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
    if (response.lower() == 'image'):
        logger.info("User %s wishes to upload an image", user.first_name)
        update.message.reply_text("Send an image file to me, if you would like to cancel type 'cancel'")
        file_type = 'image'
        return GET_IMAGE
    elif (response.lower() == 'beats'):
        logger.info("User %s wishes to upload beats", user.first_name)
        update.message.reply_text("Send a .json file to me, if you would like to cancel type 'cancel'")
        file_type = 'beats'
        return GET_BEATS
    elif (response.lower() == 'ifc'):
        logger.info("User %s wishes to upload IFC", user.first_name)
        update.message.reply_text("Send a .json file to me, if you would like to cancel type 'cancel'")
        file_type = 'ifc'
        return GET_IFC
    else:
        return ConversationHandler.END

def get_image(update, context):
    #logging
    user = update.message.from_user
    logger.info('User %s is requested to send image', user.first_name)
    global file_id

    chat_id = update.message.chat_id
    try:   
        file_id = update.message.photo[-1].file_id
        base_url = 'https://api.telegram.org/bot'
        with urllib.request.urlopen(base_url + token + '/getFile?file_id=' + file_id) as obj:
            data = json.loads(obj.read())
        f = requests.get('https://api.telegram.org/file/bot' + token + '/' + data['result']['file_path'])
        open('image.jpg','wb').write(f.content)
        logger.info('Image successfully acquired from %s', user.first_name)
        update.message.reply_text("Image acquired!")
        update.message.reply_text('Please enter a short title of the file')
        return GET_NAME
    except Exception as e:
        logger.info('Failed to acquire image from %s', user.first_name)
        logger.info(e)
        update.message.reply_text("File was not an image, cancelling file upload. Type /sendfile to try again")
        return ConversationHandler.END


def get_beats(update, context):
    #logging
    user = update.message.from_user
    logger.info('User %s is requested to send beats', user.first_name)
    global file_id

    chat_id = update.message.chat_id
    file_id = update.message.document.file_id
    base_url = 'https://api.telegram.org/bot'
    with urllib.request.urlopen(base_url + token + '/getFile?file_id=' + file_id) as obj:
        data = json.loads(obj.read())
    f = requests.get('https://api.telegram.org/file/bot' + token + '/' + data['result']['file_path'])
    open('temp_beats.json','wb').write(f.content)
    logger.info('Beats received from %s', user.first_name)
    temp_json = getJson("temp_beats.json")
    valid = (validate_beats(temp_json))
    if (valid == "valid"):
        open('beats.json','wb').write(f.content)
        logger.info('Beats successfully acquired from %s', user.first_name)
        update.message.reply_text("Beats acquired!")
        update.message.reply_text('Please enter a short title of the file')
    else:
        logger.info('Beats acquired from %s were invalid. Reason %s', user.first_name, valid)
        update.message.reply_text("Invalid beats file due to " + valid + ", cancelling file upload. Type /sendfile to try again")
        return ConversationHandler.END
    return GET_NAME

def get_ifc(update, context):
    #logging
    user = update.message.from_user
    logger.info('User %s is requested to send ifc', user.first_name)
    global file_id

    chat_id = update.message.chat_id
    file_id = update.message.document.file_id
    base_url = 'https://api.telegram.org/bot'
    with urllib.request.urlopen(base_url + token + '/getFile?file_id=' + file_id) as obj:
        data = json.loads(obj.read())
    f = requests.get('https://api.telegram.org/file/bot' + token + '/' + data['result']['file_path'])
    
    open('ifc_from_user.json','wb').write(f.content)
    logger.info('IFC successfully acquired from %s', user.first_name)
    update.message.reply_text("Beats acquired!")
    update.message.reply_text('Please enter a short title of the file')
    return GET_NAME

def get_name(update, context):
    global file_type
    name = update.message.text
    user = update.message.from_user
    j = getJson('files.json')
    j[file_type].append({"name":name, "uploaded_by":user.name, "date":str(datetime.now()), 'file_id':file_id})
    with open('files.json', 'w') as outfile:
        json.dump(j, outfile, indent=4)

    update.message.reply_text('Enter a description: ')
    return GET_DESCRIPTION

def get_description(update, context):
    desc = update.message.text
    j = getJson('files.json')
    j[file_type][-1]['description'] = desc
    with open('files.json', 'w') as outfile:
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
