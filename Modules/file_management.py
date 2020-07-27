import logging
import json
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, File)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
from beats import token, getJson
from pathlib import Path

files_dir = Path.cwd() / 'Files'

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

SHOW, SEND_FILE, CHOOSE_FILE, DEL_FILE, DELETE = range(5)

file_type = ""

def show_all_file_type(j, file_type):
    output = ""
    for file in j[file_type]:
        output += f'\u2022 <u>Name</u>: {file["name"]}\n  Uploaded by {file["uploaded_by"]}\n  {file["date"]}\n  Description: {file["description"]}\n\n'        
    return output

def show_what(update, context):
    custom_file_categories = []
    try:
        custom_file_categories = getJson(files_dir / 'file_categories.json')
    except:
        custom_file_categories = []

    reply_keyboard = [['Image','Beats', 'IFC'] + custom_file_categories, ['Cancel']]
    update.message.reply_text("Please select which file type you'd like to see",
    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return SHOW


def show(update ,context):
    global file_type
    file_type = update.message.text
    file_type = file_type.lower()
    j = getJson(files_dir / 'files.json')
    if file_type.lower() == 'cancel':
        update.message.reply_text("Cancelling transaction. \n"
        "Try again with /filemanage or upload a new file with /sendfile", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    elif file_type not in j.keys():
        update.message.reply_text("There are currently no files stored for this format \n"
        "View other file formats with /filemanage or upload a new file with /sendfile", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    elif (j[file_type] == []):
        update.message.reply_text("There are currently no files stored for this format \n"
        "View other file formats with /filemanage or upload a new file with /sendfile", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    reply_keyboard = [['Download','Delete','Cancel']]
    update.message.reply_text("Would you like to download a file, or remove a file",
    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return CHOOSE_FILE

def choose_file(update, comtext):
    global file_type
    option = update.message.text
    option = option.lower()
    print(option)
    print(file_type)

    j = getJson(files_dir / 'files.json')


    if (option == "download"):
        pass
    elif (option == "delete"):
        pass
    elif (option ==  "cancel"):
        update.message.reply_text("You have chosen to cancel the operation")
        return ConversationHandler.END
    else: 
        update.message.reply_text("Invalid option, operation cancelled")
        return ConversationHandler.END

    try:
        update.message.reply_text(show_all_file_type(j, file_type))
        update.message.reply_text('Which file would you like to ' + option +'? Type the name of the file', reply_markup=ReplyKeyboardRemove())
        if (option == "download"):
            return SEND_FILE
        elif (option == "delete"):
            update.message.reply_text("If you do not wish to delete a file, type cancel")
            return DEL_FILE
    except Exception as e:
        logger.info(e)
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

file_name=""
def del_file(update, context):
    global file_name
    file_name = update.message.text
    file_name = file_name.lower()
    # send the file to the user
    j = getJson(files_dir / 'files.json')
    try:
        index = [index for index, item in enumerate(j[file_type]) if item['name'].lower() == file_name][0]
        reply_keyboard = [['Yes','No']]
        update.message.reply_text("Are you sure you would like to remove this file?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return DELETE
    except:
        update.message.reply_text('No file with this filename')
        
    return ConversationHandler.END


def delete(update,context):
    global file_name
    confirm = update.message.text
    confirm = confirm.lower()
    if (confirm == "yes"):
        j = getJson(files_dir / 'files.json')
        index = [index for index, item in enumerate(j[file_type]) if item['name'].lower() == file_name][0]
        del j[file_type][index]        
        with Path(files_dir / 'files.json').open(mode='w') as outfile:
            json.dump(j, outfile, indent=4)
        update.message.reply_text("file has been deleted")
    else:
        update.message.reply_text("The file has NOT been deleted")

    return ConversationHandler.END
