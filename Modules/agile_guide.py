import logging
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

from pathlib import Path

reply_keyboard = [['Continue', 'Cancel']]

index = 0

AGILE_GUIDANCE = range(1)

responses = [

    # 'To continue in the process, press the continue button. '
    # 'If you\'d like to stop at any point, simply press the cancel button.',

    'Agile is a project management structure. The agile manifesto is:\n\n'
    '    Individuals and interactions over processes and tools\n'
    '    Working software over comprehensive documentation\n'
    '    Customer collaboration over contract negotiation\n'
    '    Responding to change over following a plan',

    'In practice, Agile works as follows.\n'
    'To maximize efficiency, a project is broken down into several smaller, more manageable pieces. '
    'Each piece of the project is completed during a sprint, a pre-determined period of time where a number of '
    ' tasks are completed to have a working prototype at the end of the sprint.',

    'In order to decide on what tasks to do during a sprint, a sprint meeting is held at the beginning of each sprint. '
    'Then, at the end of a sprint, the prototype can get feedback from the client in a sprint review. Any tasks required to make changes '
    'can be added to the backlog, and worked on during the next sprint the task. ',

    'Lastly, it is common to have a daily stand-up meeting, where group members give a brief report on their progress, '
    'and any challenges they are facing.',

    'For more definitions on agile terminology, use /agileterms. '

    ''


]


def respond(update, response):
    if (update.message.text == 'Cancel'):
        update.message.reply_text('Agile walk through has been cancelled. Type /agile',
        reply_markup=ReplyKeyboardRemove())
    elif (update.message.text == 'Continue'):
        update.message.reply_text(response,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    else:
        update.message.reply_text('I didn\'t recognize that input, so I will continue the walkthrough')
        update.message.reply_text(response,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

def agile_guide_start(update, context):
    update.message.reply_text('Hi! I will guide you through how the agile process works. '
    'If you would like to define a specific term, say <code>/define term</code> and I will see if I can help you. '
    'Otherwise, use /agileterms to see all the terms I can define for you. ', reply_markup=ReplyKeyboardRemove())
    update.message.reply_text('To continue in the process, press the continue button. If you\'d like to stop at any point, simply press the cancel button.',
    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return AGILE_GUIDANCE

def agile_guidance(update, context):
    global index
    response = responses[index]
    if (index == len(responses)-1):
        index = 0
        if (update.message.text == 'Cancel'):
            update.message.reply_text('Agile walk through has been cancelled. Type /agile',
            reply_markup=ReplyKeyboardRemove())
        elif (update.message.text == 'Continue'):
            update.message.reply_text(response,
            reply_markup=ReplyKeyboardRemove())
        else:
            update.message.reply_text('I didn\'t recognize that input, so I will continue the walkthrough')
            update.message.reply_text(response,
            reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    
    respond(update, response)

    index += 1
    
    return AGILE_GUIDANCE
    
    

    



