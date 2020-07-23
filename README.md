# DTU byg chatbot
Bachelor's project on creating a chatbot/website for DTU byg by Adam Søe Beilin (s170780) and Eric Kastl Jensen (s174379)

Supervisor - Tim Pat McGinley

Co-supervisor - Andrea Burattin

# Getting started
How to run your own version of the bygchatbot
## Setting up the telegram bot
Text the botfather (https://telegram.me/botfather) in telegram the command `/newbot` and follow the instructions. Take note of the bot's token.

To add the commands into auto-suggest, ask the botfather to edit your bot, edit commands, and send the botfather the following:

```start - Get an overview of all commands
help - Get an overview of all commands (same as start)
viewbeats - Get information on beats
sendfile - Send a file to bot
agileterms - Get some definitions on agile terminology
define - Define a specific agile term
ifc - View and edit ifc file
filemanage - Manage files uploaded to the bot
teamstart - Manage your team
```

## Inserting bot token into your code
Create a json file called `token.json`, and input the json object `{"token":"[YOUR TOKEN HERE]"}`

## Running the bot
Run the main file, or write `python main.py` in the terminal
