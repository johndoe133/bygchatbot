from beats import (token, get, getBuildingFloorArea, getBuildingHeight, 
                    getBuildingVolume, getJson, getHeight, getVolume, getFloorArea)
import logging
import json
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

from datetime import (datetime, timedelta)
import pytz
from queue import PriorityQueue

from info import *
from files import *
from agile_help import *
from define import *
from teamCreater import *


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

EDIT_DURATION,CHOOSE_DURATION,CHOOSE_FIRST,CHOOSE_TIME = range(40,44)

def set_duration(update, context):

    reply_keyboard = ["Yes", "No"]
    update.message.reply_text('Would you like to edit the duration of the sprint? ', 
    reply_markup=ReplyKeyboardMarkup([reply_keyboard], one_time_keyboard=True))
    return EDIT_DURATION


def edit_duration(update,context):
    with open('teams.json') as json_file:
        teams = json.load(json_file)

    user = update.message.from_user
    confirm = update.message.text


    if (confirm == "Yes"):
        update.message.reply_text("Choose the length of the sprint (number of days)")
        return CHOOSE_DURATION
    else:
        update.message.reply_text('The duration of the sprint remains at: '+ str(teams["sprint_duration"]))
        return ConversationHandler.END 

duration=0
def choose_duration(update,context):
    with open('teams.json') as json_file:
        teams = json.load(json_file)
    global duration
    user = update.message.from_user 
    duration = update.message.text

    try:
        duration = int(duration)
    except:
        update.message.reply_text("The sprint duration must be an integer")
        update.message.reply_text('The duration of the sprint remains at: '+ str(teams["sprint_duration"]))
        return ConversationHandler.END 
    
    teams["sprint_duration"] = duration
    update.message.reply_text('The duration of the sprint has been set to: '+ str(teams["sprint_duration"]))
    
    
    with open('teams.json', 'w') as outfile:
        json.dump(teams, outfile, indent = 4)
    

    update.message.reply_text("At what time should the sprint meeting begin?, Use 24 Hour format and write it as <code>hh:mm</code>")

    return CHOOSE_TIME

hour=""
minute=""
def choose_time(update, context):
    startTime = update.message.text
    global hour
    global minute
    try:
        [hour,minute] = startTime.split(":")
        hour = int(hour)
        minute = int(minute)

        if (hour<0 or hour>23 or minute <0 or minute >59):
            update.message.reply_text("Invalid time")
            return ConversationHandler.END
    except:
        update.message.reply_text("Invalid time")
        return ConversationHandler.END


    update.message.reply_text("Type the date that you want the first sprint meeting to be. Use the format <code>DD.MM.YYYY</code>")
    
    return CHOOSE_FIRST

date=datetime(1,1,1)
def choose_first(update, context):
    global hour
    global minute
    global date
    startDay = update.message.text

    try:
        [day,month,year] = startDay.split('.')
        day,month,year = int(day),int(month),int(year)
        date = datetime(year,month,day,hour,minute)
    
    except:
        update.message.reply_text("Invalid date, cancelling")
        return ConversationHandler.END 
    
    timezone = pytz.timezone("Europe/Amsterdam")
    d_aware = timezone.localize(date)

    if (date < datetime.now()):
        update.message.reply_text("The sprint meeting must be start in the future, type /teamstart to try again")
        return ConversationHandler.END


    with open('teams.json') as json_file:
        teams = json.load(json_file)

    teams["first_sprint"] = str(date)

    with open('teams.json', 'w') as outfile:
        json.dump(teams, outfile, indent = 4)
    

    if (len(context.job_queue._queue.queue)>0):
        context.job_queue._queue.queue = PriorityQueue([])

    context.job_queue.run_repeating(reminder_now, duration*24*60*60, first=d_aware, context=update.message.chat_id)
    
    if (date - timedelta(hours=24) > datetime.now()):
        context.job_queue.run_repeating(reminder_day_before, duration*24*60*60, first=d_aware-timedelta(days=1), context=update.message.chat_id)
    if (date - timedelta(hours=1) > datetime.now()):
        context.job_queue.run_repeating(reminder_hour_before, duration*24*60*60, first=d_aware-timedelta(hours=1), context=update.message.chat_id)
    
    update.message.reply_text(f'Success! Your sprint has been set to be once every {duration} days, starting on {d_aware}')

    return ConversationHandler.END


def reminder_day_before(context):
    job = context.job
    context.bot.send_message(job.context, text=f"You have a sprint meeting tomorrow at {hour:02d}:{minute:02d}")

def reminder_hour_before(context):
    job = context.job
    context.bot.send_message(job.context, text=f"You have a sprint meeting in an hour at {hour:02d}:{minute:02d}")

def reminder_now(context):
    job = context.job
    context.bot.send_message(job.context, text=f"You have a sprint meeting now")

