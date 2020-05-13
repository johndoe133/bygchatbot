from chatbot import (token, get, getBuildingFloorArea, getBuildingHeight, 
                    getBuildingVolume, getJson, getHeight, getVolume, getFloorArea)
import logging
import json
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
from chatbot import getJson

def view_team(update, context):
    teams = getJson('teams.json')
    view_string = "<code>"
    view_string += f"{'Sprint duration':<18}: {teams['sprint_duration']}\n"
    view_string += f'{"Groups":<18}:\n'
    view_string += '-'*25
    for team_no, team in enumerate(teams['teams']):
        view_string += f'\n{"  Group number":<18}: {team_no}\n'
        view_string += f'{"  Group name":<18}: {team["group_name"]}\n'
        view_string += f'{"  Group members":<18}:\n'
        if (len(team['group_members']) == 0):
            view_string += f'    Empty\n'
        for member in team['group_members']:
            view_string += f'    @{member}\n'
        view_string += '  ' + '-'*10
    view_string = view_string.strip('-')
    view_string = view_string.strip(' ')
    view_string += '-' * 25
    
    view_string += '</code>'
    update.message.reply_text(view_string)