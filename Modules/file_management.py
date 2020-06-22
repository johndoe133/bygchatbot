import logging
import json
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, File)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
from beats import token, getJson
import urllib
import requests

SHOW, SEND_FILE = range(2)

file_type = ""

def show_what(update, context):
    reply_keyboard = [['Image','Beats', 'IFC','Cancel']]
    update.message.reply_text("Please select which file type you'd like to see",
    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return SHOW

def show(update ,context):
    global file_type
    file_type = update.message.text
    file_type = file_type.lower()
    j = getJson('files.json')
    try:
        output = ""
        for file in j[file_type]:
            output += f'*{file["name"]}\n  Uploaded by {file["uploaded_by"]}\n  {file["date"]}\n  Description: {file["description"]}\n\n'
        update.message.reply_text(output)
        update.message.reply_text('Which file would you like to download? Type the name of the file')
        return SEND_FILE
    except:
        update.message.reply_text('Invalid file type!')
        return ConversationHandler.END

def send_file(update, context):
    file_name = update.message.text
    # send the file to the user
    chat_id = update.message.chat_id
    j = getJson('files.json')[file_type]
    file_id = [item['file_id'] for item in j if item['name'] == file_name][0]
    print(file_id)
    base_url = 'https://api.telegram.org/bot'
    with urllib.request.urlopen(base_url + token + '/getFile?file_id=' + file_id) as obj:
        data = json.loads(obj.read())
    update.message.reply_text('https://api.telegram.org/file/bot' + token + '/' + data['result']['file_path'])
    return ConversationHandler.END


