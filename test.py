from chatbot import (token, get, getBuildingFloorArea, getBuildingHeight, 
                    getBuildingVolume, getJson, getHeight, getVolume, getFloorArea)
import logging

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

INFO, GIVE_INFO = range(2)
TEAM = ""
TEAM_INDEX = 0
METRIC = ""

def start(update, context):
    reply_keyboard = [[]]
    json_obj = getJson('beats.json')
    for team in json_obj:
        reply_keyboard[0] += team['team']

    update.message.reply_text(
        'Hi! I am the BygBot. I will hold a conversation with you. '
        'Send /cancel to stop talking to me.\n\n'
        'Which team would you like to examine?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return INFO


def info(update, context):
    json_obj = getJson('beats.json')
    user = update.message.from_user
    TEAM = update.message.text
    for i in range(len(json_obj)):
        if json_obj[i]['team'] == TEAM:
            TEAM_INDEX=i
            break
    logger.info("Team that %s wishes to examine: %s", user.first_name, TEAM)
    reply_keyboard = [['Height','Volume','Floor Area']]
    
    update.message.reply_text(
        "What information would you like on team " + TEAM,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return GIVE_INFO

def give_info(update, context):
    json_obj = getJson('beats.json')
    user = update.message.from_user
    METRIC = update.message.text
    logger.info("Metric user %s desires: %s", user.first_name, METRIC)
    if (METRIC == 'Height'):
        update.message.reply_text('The height of the building is: ' + str(getHeight(TEAM_INDEX)),
        reply_markup=ReplyKeyboardRemove())
    elif (METRIC == 'Volume'):
        update.message.reply_text('The volume of the building is: ' + str(getVolume(TEAM_INDEX)),
        reply_markup=ReplyKeyboardRemove())
    elif (METRIC == 'Floor Area'):
        update.message.reply_text('The floor area is: ' + str(getFloorArea(TEAM_INDEX)),
        reply_markup=ReplyKeyboardRemove())


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            INFO: [MessageHandler(Filters.regex(''), info)],
            GIVE_INFO: [MessageHandler(Filters.regex(''), give_info)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()