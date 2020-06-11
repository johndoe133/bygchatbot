from beats import (token)
import logging
import json
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
from telegram import ParseMode
from agile_help import give_definition
from uuid import uuid4

def get_word(update):
    key = str(uuid4())
    args = update.message.text.partition(' ')[2]
    return args

def give_def_direct(update, context):
    chat_id = update.message.chat_id
    word = get_word(update)
    give_definition(word, update)
