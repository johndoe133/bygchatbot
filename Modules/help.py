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


def help(update, context):


    helpstring = "Here is an overview of all callable commands:  \n \n"

    helpstring += "/Teamstart: \n"
    helpstring += "This feature lets you create groups, for any user to join, as well as add or remove tasks to each of the groups. Sprint durations can be set and changed here as well, which provides reminders for upcoming meetings \n"

    helpstring += "/Agilehelp: \n"
    helpstring += "This feature can provide you with definitions of key agile terminology \n"

    helpstring += "/Sendfile: \n"
    helpstring += "This feature allows you to send files, such as images, beats.json, and IFC.json, to be stored by the chatbot \n"

    helpstring += "/Filemanage: \n"
    helpstring += "This feature lets you access all files stored by the chatbot \n"

    helpstring += "/IFC: \n"
    helpstring += "This feature allows you to get an analysis of any stored IFC.json file, along with giving an option to view a 3D model of this file. An option to stretch a 3D model is also available here.\n"

    helpstring += "/Viewbeats: \n"
    helpstring += "This feature allows you to view and get an analysis of any stored beats.json file \n"


    update.message.reply_text(helpstring)


    return ConversationHandler.END