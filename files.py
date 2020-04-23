import logging
import json
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
from chatbot import token
import requests, urllib.request
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

REQUEST_FILE, GET_IMAGE, GET_BEATS = range(3)

def ask_file_type(update, context):
    reply_keyboard = [['Image','Beats','Cancel']]
    update.message.reply_text("Please select which file type you'd like to send",
    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return REQUEST_FILE

def request_file(update, context):
    #logging
    print('there')
    user = update.message.from_user

    response = update.message.text
    chat_id = update.message.chat_id
    if (response == 'Image'):
        print('here')
        logger.info("User %s wishes to upload an image", user.first_name)
        update.message.reply_text("Send an image file to me")
        return GET_IMAGE
    elif (response.lower() == 'beats'):
        logger.info("User %s wishes to upload beats", user.first_name)
        update.message.reply_text("Send a .json file to me")
        return GET_BEATS
    else:
        return ConversationHandler.END

def get_image(update, context):
    #logging
    user = update.message.from_user
    logger.info('User %s is requested to send image', user.first_name)

    chat_id = update.message.chat_id
       
    file_id = update.message.photo[-1].file_id
    print("\n------------\n",file_id,"\n-------------------\n")
    base_url = 'https://api.telegram.org/bot'
    with urllib.request.urlopen(base_url + token + '/getFile?file_id=' + file_id) as obj:
        data = json.loads(obj.read())
    print(data)
    f = requests.get('https://api.telegram.org/file/bot' + token + '/' + data['result']['file_path'])
    open('image.jpg','wb').write(f.content)
    logger.info('Image successfully acquired from %s', user.first_name)
    update.message.reply_text("Image acquired!")
    return ConversationHandler.END

def get_beats(update, context):
    #logging
    user = update.message.from_user
    logger.info('User %s is requested to send beats', user.first_name)

    chat_id = update.message.chat_id
    print(update.message)
    file_id = update.message.document.file_id
    base_url = 'https://api.telegram.org/bot'
    print(base_url + token + '/getFile?file_id=' + file_id)
    with urllib.request.urlopen(base_url + token + '/getFile?file_id=' + file_id) as obj:
        data = json.loads(obj.read())
    print(data)
    f = requests.get('https://api.telegram.org/file/bot' + token + '/' + data['result']['file_path'])
    open('beats.json','wb').write(f.content)
    logger.info('Beats successfully acquired from %s', user.first_name)
    update.message.reply_text("Beats acquired!")
    return ConversationHandler.END