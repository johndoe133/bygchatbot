from beats import (token, getJson)
import logging
import json
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
from beats import getJson

DETAILED_VIEW = 8

def view_team(update, context):
    teams = getJson('teams.json')
    view_string = "<code>"
    view_string += f"{'Sprint duration':<18}: {teams['sprint_duration']}\n"
    view_string += f'{"Groups":<18}:\n'
    view_string += '-'*25
    for team_no, team in enumerate(teams['teams']):
        view_string += f'\n{"  Group number":<18}: {team_no+1}\n'
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


    reply_keyboard = [[str(i+1) for i in range(len(teams["teams"]))], ["All","Cancel"]]
    update.message.reply_text("Would you like to view a team with more detail?", 
    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return DETAILED_VIEW 

def detailed_view(update,context):

    choice = update.message.text
    teams = getJson('teams.json')

    if (choice == "All"):
        view_string = "<code>"
        view_string += f"{'Sprint duration':<18}: {teams['sprint_duration']}\n"
        view_string += f'{"Groups":<18}:\n'
        view_string += '-'*25
        for team_no, team in enumerate(teams['teams']):
            view_string += f'\n{"  Group number":<18}: {team_no+1}\n'
            view_string += f'{"  Group name":<18}: {team["group_name"]}\n'
            view_string += f'{"  Group members":<18}:\n'
            if (len(team['group_members']) == 0):
                view_string += f'    Empty\n'
            for member in team['group_members']:
                view_string += f'    @{member}\n'
            view_string += f'{"  Group tasks":<18}:\n'
            if (len(team['tasks'])==0):
                view_string += f'    Empty\n'
            
            for i in range(len(team['tasks'])):
                if (i>0):
                    view_string+="\n"
                task = team["tasks"][i]
                description = team["descriptions"][i]
                view_string += "    "+task + "\n"
                view_string += "     "+description + "\n"
            view_string += '  ' + '-'*10
        view_string = view_string.strip('-')
        view_string = view_string.strip(' ')
        view_string += '-' * 25
        
        view_string += '</code>'
        update.message.reply_text(view_string)
    
    elif (choice in [str(i) for i in range(1,1+len(teams["teams"]))]):
        choice = int(choice) - 1
        team = teams["teams"][choice]
        view_string = "<code>"
        view_string += f"{'Sprint duration':<18}: {teams['sprint_duration']}\n"
        view_string += f'\n{"Group number":<18}: {choice+1}\n'
        view_string += f'{"Group name":<18}: {teams["teams"][choice]["group_name"]}\n'
        view_string += '-'*25

        view_string += f'\n{"  Group members":<18}:\n'
        if (len(team['group_members']) == 0):
            view_string += f'    Empty\n'
        for member in team['group_members']:
            view_string += f'    @{member}\n'
        view_string += f'{"  Group tasks":<18}:\n'
        if (len(team['tasks'])==0):
            view_string += f'    Empty\n'
        
        for i in range(len(team['tasks'])):
            if (i>0):
                view_string+="\n"
            task = team["tasks"][i]
            description = team["descriptions"][i]
            view_string += "    "+task + "\n"
            view_string += "     "+description + "\n"
        view_string += '  ' + '-'*10

        view_string = view_string.strip('-')
        view_string = view_string.strip(' ')
        view_string += '-' * 25
        
        view_string += '</code>'
        update.message.reply_text(view_string)

    elif choice.lower() == 'cancel':
        update.message.reply_text('Cancelling view team. Type /teamstart to try again. ', reply_markup=ReplyKeyboardRemove())
    else:
        update.message.reply_text('Invalid team. Type /teamstart to try again. ', reply_markup=ReplyKeyboardRemove())



    return ConversationHandler.END 
