from chatbot import (token, get, getBuildingFloorArea, getBuildingHeight, 
                    getBuildingVolume, getJson, getHeight, getVolume, getFloorArea)
import logging
import json
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, Defaults)
from info import *
from files import *
from AgileHelp import *
from define import *
from ifc import *

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def main():
    logger.info('Bot is started')
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    defaults = Defaults(parse_mode=ParseMode.HTML)
    updater = Updater(token, use_context=True, defaults=defaults)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler_info = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            TEAM_INFO: [MessageHandler(Filters.regex(''), team_info)],
            SEGMENT_INFO: [MessageHandler(Filters.regex(''), segments_info)],
            GIVE_INFO: [MessageHandler(Filters.regex(''), give_info)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    conv_handler_file = ConversationHandler(
        entry_points=[CommandHandler('sendfile', ask_file_type)],
        states={
            REQUEST_FILE: [MessageHandler(Filters.all, request_file)],
            GET_IMAGE: [MessageHandler(Filters.all, get_image)],
            GET_BEATS: [MessageHandler(Filters.all, get_beats)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    conv_handler_agile_help = ConversationHandler(
        entry_points=[CommandHandler('helpagile', help_agile)],
        states = {
            DEFINE: [MessageHandler(Filters.regex(''), define)],
            DEFINE_ADDITIONAL: [MessageHandler(Filters.regex(''), define_additional)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    conv_handler_define = ConversationHandler(
        entry_points=[CommandHandler('define', give_def_direct)],
        states = {},
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    conv_handler_ifc = ConversationHandler(
        entry_points=[CommandHandler('ifc', start_analysis)],
        states = {},
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler_info)
    dp.add_handler(conv_handler_file)
    dp.add_handler(conv_handler_agile_help)
    dp.add_handler(conv_handler_define)
    dp.add_handler(conv_handler_ifc)

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