# DTU byg chatbot
Bachelor's project on creating a chatbot/website for DTU byg by Adam Søe Beilin (s170780) and Eric Kastl Jensen (s174379)

Supervisor - Tim Pat McGinley

Co-supervisor - Andrea Burattin

# Example files
In this repository, there is an example beats file, and an example IFC5 JSON file, called `beats.json` and `duplex_A.json`, respectively. 

# Getting started
How to run your own version of the bygchatbot

IMPORTANT NOTE: Sometimes, when running the bot in the terminal, it will "pause". This is not because of the code, is because of "quick edit" mode in the terminal. If you notice the bot not responding, simply go to the terminal and press any key to unpause it. This problem does not occur if run in visual studio code. If you wish to disable the quick edit mode, go to terminal properties and disable quick edit mode. This will stop the script from pausing. 


## Setting up the telegram bot
Text the botfather (https://telegram.me/botfather) in telegram the command `/newbot` and follow the instructions. Take note of the bot's token.

To add the commands into auto-suggest, ask the botfather to edit your bot, edit commands, and send the botfather the following:

```start - Get an overview of all commands
help - Get an overview of all commands (same as start)
viewbeats - Get information on beats
sendfile - Send a file to bot
agileterms - Get some definitions on agile terminology
agileguide - A quick guide to the core principals of agile
define - Define a specific agile term
ifc - View and edit ifc file
filemanage - Manage files uploaded to the bot
teamstart - Manage your team
```

## Inserting bot token into your code
Create a json file called `token.json` in the Root directory, and input the json object `{"token":"[YOUR TOKEN HERE]"}`

## Downloading packages
Note that downloading `open3d` might take a long time. 
```
pip install python-telegram-bot --upgrade
pip install jsonschema
pip install pytz
pip install numpy
pip install open3d
pip install plyfile
```

## Running the bot
Run the main file, or write `python main.py` in the terminal

IMPORTANT NOTE: Sometimes, when running the bot in the terminal, it will "pause". This is not because of the code, is because of "quick edit" mode in the terminal. If you notice the bot not responding, simply go to the terminal and press any key to unpause it. This problem does not occur if run in visual studio code. If you wish to disable the quick edit mode, go to terminal properties and disable quick edit mode. This will stop the script from pausing. 
