import logging
import json
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, File)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
from beats import token, getJson
import urllib
import requests
from pathlib import Path

files_dir = Path.cwd() / 'Files'


SHOW, SEND_FILE = range(2)

file_type = ""

def show_all_file_type(j, file_type):
    output = ""
    for file in j[file_type]:
        output += f'*{file["name"]}\n  Uploaded by {file["uploaded_by"]}\n  {file["date"]}\n  Description: {file["description"]}\n\n'
    return output

def show_what(update, context):
    reply_keyboard = [['Image','Beats', 'IFC','Cancel']]
    update.message.reply_text("Please select which file type you'd like to see",
    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return SHOW

def show(update ,context):
    global file_type
    file_type = update.message.text
    file_type = file_type.lower()
    j = getJson(files_dir / 'files.json')

    if j[file_type] == []:
        update.message.reply_text('There is currently no files stored for this format \nView other file formats with /filemanage or upload a new file with /sendfile')
        return ConversationHandler.END

    try:
        update.message.reply_text(show_all_file_type(j, file_type))
        update.message.reply_text('Which file would you like to download? Type the name of the file')
        return SEND_FILE
    except:
        update.message.reply_text('Invalid file type!')
        return ConversationHandler.END

def send_file(update, context):
    file_name = update.message.text
    file_name = file_name.lower()
    # send the file to the user
    chat_id = update.message.chat_id
    j = getJson(files_dir / 'files.json')[file_type]
    try:
        index = [index for index, item in enumerate(j) if item['name'].lower() == file_name][0]
    except:
        update.message.reply_text('No file with this filename')
        return ConversationHandler.END
    # base_url = 'https://api.telegram.org/bot'
    # with urllib.request.urlopen(base_url + token + '/getFile?file_id=' + file_id) as obj:
    #     data = json.loads(obj.read())
    # update.message.reply_text('https://api.telegram.org/file/bot' + token + '/' + data['result']['file_path'])
    bot = context.bot
    if (file_type == 'image'):
        bot.send_photo(chat_id=chat_id, photo=Path(files_dir / j[index]['file_name']).open(mode='rb'), filename=j[index]['name'])
    else:
        bot.send_document(chat_id=chat_id, document=Path(files_dir / j[index]['file_name']).open(mode='rb'), 
        filename=j[index]['name']+ '.' + j[index]['file_name'].split('.')[-1])
    return ConversationHandler.END


