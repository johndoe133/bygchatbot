from telegram.ext import (Updater, CommandHandler)
import requests
import json
import re
from uuid import uuid4
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

token = '1123323323:AAG5kydgweesrh71QXW_J4CmwVxJTSsken4'

def get_url():
    contents = requests.get('https://random.dog/woof.json').json()
    return contents['url']

def get_image_url():
    allowed_extensions = ['jpg','jpeg','png']
    file_extension = ''
    while file_extension not in allowed_extensions:
        url = get_url()
        file_extension = re.search("([^.]*)$",url).group(1).lower()
    return url

def bop(bot, update):
    url = get_image_url()
    chat_id = update.message.chat_id
    bot.send_photo(chat_id=chat_id, photo=url)

def getArgs(update):
    key = str(uuid4())
    args = update.message.text.partition(' ')[2].split(' ')
    return args

def get(bot, update):
    chat_id = update.message.chat_id
    # bot.send_message(chat_id=chat_id, text=getAllInfo())
    # sent = bot.send_message(chat_id=chat_id, text="Input an integer:")
    # bot.register_next_step_handler(sent, getAllInfo)
    # print(update.message.text)
    args = getArgs(update)
    bot.send_message(chat_id=chat_id, text=getInfo(args))

def getInfo(args):
    
    json_obj = getJson('beats.json')
    if args[0] == '':
        return json.dumps(json_obj, indent=2)
    prev = json_obj
    for item in args:
        try:
            prev = prev[int(item)]
        except:
            prev = prev[item]
    return json.dumps(prev, indent=2)

def getAllInfo():
    json_obj = getJson('beats.json')
    return json.dumps(json_obj, indent=2)

def getJson(filename):
    with open(filename) as json_file:
        json_obj = json.load(json_file)
    return json_obj

def getHeight(index):
    json_obj = getJson('beats.json')
    f2f = float(json_obj[0]['segments'][0]['f2f'])
    flrs = int(json_obj[0]['segments'][0]['flrs'])
    return f2f * flrs

def getFloorArea(index):
    json_obj = getJson('beats.json')
    flrs = int(json_obj[0]['segments'][0]['flrs'])
    gfa = float(json_obj[0]['segments'][0]['gfa'])
    return gfa / flrs

def getVolume(index):
    json_obj = getJson('beats.json')
    return getFloorArea(index) * getHeight(index)


def getBuildingHeight(bot, update):
    chat_id = update.message.chat_id
    args = getArgs(update)
    bot.send_message(chat_id=chat_id, text=getHeight(int(args[0])))

def getBuildingFloorArea(bot, update):
    chat_id = update.message.chat_id
    args = getArgs(update)
    bot.send_message(chat_id=chat_id, text=getFloorArea(int(args[0])))

def getBuildingVolume(bot, update):
    chat_id = update.message.chat_id
    args = getArgs(update)
    bot.send_message(chat_id=chat_id, text=getVolume(int(args[0])))

def main():
    updater = Updater(token)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('bop', bop))
    dp.add_handler(CommandHandler('get', get))
    dp.add_handler(CommandHandler('getHeight', getBuildingHeight))
    dp.add_handler(CommandHandler('getFloorArea', getBuildingFloorArea))
    dp.add_handler(CommandHandler('getVolume', getBuildingVolume))
    updater.start_polling()
    updater.idle()
    
if __name__ == '__main__':
    main()