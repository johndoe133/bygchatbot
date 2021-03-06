import sys
sys.path.append('../bygchatbot/Modules')

from Modules.beats import (token, getBuildingFloorArea, getBuildingHeight, 
                    getJson, getHeight, getVolume, getFloorArea)
import logging
import json
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, Defaults)
from Modules.info import *
from Modules.files import *
from Modules.agile_help import *
from Modules.define import *
from Modules.teamCreater import *
from Modules.teamJoiner import *
from Modules.team_viewer import *
from Modules.SprintDuration import *
from Modules.assignTask import *
from Modules.removeTask import *
from Modules.viewTask import *
from Modules.teamGeneral import *
from Modules.ifc import *
from Modules.file_management import *
from Modules.help import *
from Modules.agile_guide import *


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def main():
    logger.info("Bot has been started")
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    defaults = Defaults(parse_mode=ParseMode.HTML)
    updater = Updater(token, use_context=True, defaults=defaults)
    

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler_info = ConversationHandler(
        entry_points=[CommandHandler('viewbeats', view_beats)],
        states={
            OVERVIEW: [MessageHandler(Filters.regex(''), overview)],
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
            GET_A_FILE: [MessageHandler(Filters.all, get_a_file)],
            GET_NAME: [MessageHandler(Filters.all, get_name)],
            GET_DESCRIPTION: [MessageHandler(Filters.all, get_description)],
            GET_NEW_CATEGORY: [MessageHandler(Filters.all, get_new_category)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    conv_handler_agile_help = ConversationHandler(
        entry_points=[CommandHandler('agileterms', help_agile)],
        states = {
            DEFINE: [MessageHandler(Filters.regex(''), define)],
            DEFINE_ADDITIONAL: [MessageHandler(Filters.regex(''), define_additional)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # conv_handler_create_json = ConversationHandler(
    #     entry_points=[CommandHandler('createteam', create_team)],
    #     states = {
    #         NUMBER_GROUPS: [MessageHandler(Filters.regex(''), number_groups)],
    #         NAME_GROUP: [MessageHandler(Filters.regex(''), name_group)],
    #         MAKE_GROUP: [MessageHandler(Filters.regex(''), make_group)]
    #     },
    #     fallbacks=[CommandHandler('cancel', cancel)]
    # )

    # conv_handler_join_team = ConversationHandler(
    #     entry_points=[CommandHandler('jointeam', join_team)],
    #     states = {
    #         CHOOSE_TEAM: [MessageHandler(Filters.regex(''), choose_team)],
    #         ADD_TO_TEAM: [MessageHandler(Filters.regex(''), add_to_team)]
    #     },
    #     fallbacks=[CommandHandler('cancel', cancel)]
    # )

    conv_handler_define = ConversationHandler(
        entry_points=[CommandHandler('define', give_def_direct)],
        states = {},
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # conv_handler_view_teams = ConversationHandler(
    #     entry_points=[CommandHandler('view_teams', view_team)],
    #     states = {},
    #     fallbacks=[CommandHandler('cancel', cancel)]
    # )
    
    # conv_handler_sprint_duration = ConversationHandler(
    #     entry_points=[CommandHandler('sprintduration', set_duration)],
    #     states = {
    #         EDIT_DURATION: [MessageHandler(Filters.regex(''), edit_duration)],
    #         CHOOSE_DURATION: [MessageHandler(Filters.regex(''), choose_duration)]
    #     },
    #     fallbacks=[CommandHandler('cancel', cancel)]
    # )

    # conv_handler_assign_task = ConversationHandler(
    #     entry_points=[CommandHandler('assigntask', assign_task)],
    #     states = {
    #         ADD_TASK: [MessageHandler(Filters.regex(''), add_task)],
    #         ADD_DESCRIPTION: [MessageHandler(Filters.regex(''), add_description)],
    #         TO_GROUP: [MessageHandler(Filters.regex(''), to_group)]
    #     },
    #     fallbacks=[CommandHandler('cancel', cancel)]
    # )

    # conv_handler_remove_task = ConversationHandler(
    #     entry_points=[CommandHandler('removetask', remove_task)],
    #     states = {
    #         FROM_GROUP: [MessageHandler(Filters.regex(''), from_group)],
    #         CHOOSE_TASK: [MessageHandler(Filters.regex(''), choose_task)],
    #         CONFIRM: [MessageHandler(Filters.regex(''), confirm)]
    #     },
    #     fallbacks=[CommandHandler('cancel', cancel)]
    # )
    

    # conv_handler_view_task = ConversationHandler(
    #     entry_points=[CommandHandler('viewtasks', view_task)],
    #     states = {},
    #     fallbacks=[CommandHandler('cancel', cancel)]
    # )


    conv_handler_team_general = ConversationHandler(
        entry_points=[CommandHandler('teamstart', team_start)],
        states = {
            GET_RESPONSE: [MessageHandler(Filters.regex(''), get_response)],
            CHECK_OVERWRITE: [MessageHandler(Filters.regex(''), check_overwrite)],
            EDIT_GROUPS: [MessageHandler(Filters.regex(''), edit_groups)],
            CHOOSE_TEAM: [MessageHandler(Filters.regex(''), choose_team)],

            NUMBER_GROUPS: [MessageHandler(Filters.regex(''), number_groups)],
            NAME_GROUP: [MessageHandler(Filters.regex(''), name_group)],
            MAKE_GROUP: [MessageHandler(Filters.regex(''), make_group)],

            DETAILED_VIEW: [MessageHandler(Filters.regex(''), detailed_view)],

            EDIT_DURATION: [MessageHandler(Filters.regex(''), edit_duration)],
            CHOOSE_DURATION: [MessageHandler(Filters.regex(''), choose_duration)],
            CHOOSE_FIRST: [MessageHandler(Filters.regex(''), choose_first)],
            CHOOSE_TIME: [MessageHandler(Filters.regex(''), choose_time)],

            ADD_TASK: [MessageHandler(Filters.regex(''), add_task)],
            ADD_DESCRIPTION: [MessageHandler(Filters.regex(''), add_description)],
            TO_GROUP: [MessageHandler(Filters.regex(''), to_group)],

            FROM_GROUP: [MessageHandler(Filters.regex(''), from_group)],
            CHOOSE_TASK: [MessageHandler(Filters.regex(''), choose_task)],
            CONFIRM: [MessageHandler(Filters.regex(''), confirm)]            
            
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    conv_handler_ifc = ConversationHandler(
        entry_points=[CommandHandler('ifc', ifc_start)],
        states = {
            GET_IFC_RESPONSE: [MessageHandler(Filters.regex(''), get_ifc_response)],
            GET_STRETCH_PARAMETERS: [MessageHandler(Filters.regex(''), get_stretch_parameters)],
            GET_IFC_FILE: [MessageHandler(Filters.regex(''), get_ifc_file)],
            GET_STRETCHED_NAME: [MessageHandler(Filters.regex(''), get_stretched_name)],
            SAVE_STRETCHED: [MessageHandler(Filters.regex(''), save_stretched)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    conv_handler_file_management = ConversationHandler(
        entry_points=[CommandHandler('filemanage', show_what)],
        states = {
            SHOW: [MessageHandler(Filters.regex(''), show)],
            SEND_FILE: [MessageHandler(Filters.regex(''), send_file)],
            CHOOSE_FILE: [MessageHandler(Filters.regex(''), choose_file)],
            DEL_FILE: [MessageHandler(Filters.regex(''), del_file)],
            DELETE: [MessageHandler(Filters.regex(''), delete)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    conv_handler_help = ConversationHandler(
        entry_points=[CommandHandler('help', help), CommandHandler('start', help)],
        states = {},
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    conv_handler_guidance = ConversationHandler(
        entry_points=[CommandHandler('agileguide', agile_guide_start)],
        states = {
            AGILE_GUIDANCE: [MessageHandler(Filters.regex(''), agile_guidance)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )


    dp.add_handler(conv_handler_info)
    dp.add_handler(conv_handler_file)
    dp.add_handler(conv_handler_agile_help)
    dp.add_handler(conv_handler_define)
    #dp.add_handler(conv_handler_create_json)
    #dp.add_handler(conv_handler_join_team)
    # dp.add_handler(conv_handler_view_teams)
    # dp.add_handler(conv_handler_sprint_duration)
    # dp.add_handler(conv_handler_assign_task)
    # dp.add_handler(conv_handler_remove_task)
    # dp.add_handler(conv_handler_view_task)
    dp.add_handler(conv_handler_team_general)
    dp.add_handler(conv_handler_ifc)
    dp.add_handler(conv_handler_file_management)
    dp.add_handler(conv_handler_help)
    dp.add_handler(conv_handler_guidance)

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