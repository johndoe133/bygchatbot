from beats import (token)
import logging
import json
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
from telegram import ParseMode
from info import cancel

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

DEFINE, DEFINE_ADDITIONAL = range(2)
terms = ['Manifesto', 'Overall', 'Sprint', 'Scrum', 'Roles', 
    'User Stories']
additional_terms = ['Product Backlog', 'Sprint Backlog', 'Minimum Viable Product', 'Sprint Planning Meeting', 
'Daily Scrum', 'Sprint Review', 'Sprint Retrospective']
def help_agile(update, context):
    logger.info('user %s would like some agile definitions', update.message.from_user.name)
    update.message.reply_text(
        'I can see you would like some help with understanding the agile process.'
        'What would you like to know more about?',
        reply_markup=ReplyKeyboardMarkup([terms[0:4],terms[4:] + ['Additional Terms']], one_time_keyboard=True))
    return DEFINE

def define(update, context):
    user = update.message.from_user
    term = update.message.text
    
    if (term == 'Additional Terms'):
        update.message.reply_text(
        'Which of the following additional terms would you like to know more about?',
        reply_markup=ReplyKeyboardMarkup([additional_terms[0:2],additional_terms[2:4], 
        additional_terms[4:]], one_time_keyboard=True))
        return DEFINE_ADDITIONAL
    give_definition(term, update)
    return ConversationHandler.END

def define_additional(update, context):
    user = update.message.from_user
    term = update.message.text
    give_definition(term, update)
    return ConversationHandler.END

def give_definition(word, update):
    if (word.lower() == terms[0].lower()): # manifesto
        update.message.reply_text('Individuals and interactions over processes and tools\n'
        'Working software over comprehensive documentation\n'
        'Customer collaboration over contract negotiation\n'
        'Responding to change over following a plan\n'
        'That is, while there is value in the items on '
        'the right, we value the items on the left more.'
        )
        update.message.reply_text('For more information, click on the following link\n'
        'https://agilemanifesto.org/')

    elif (word.lower() == terms[1].lower()): # overall
        update.message.reply_text('The Agile methodology is a type of project management approach. '
        'The practices stem from the Agile Manifesto, and works by breaking large tasks into smaller '
        'more manageable ones, while always working on the most important element of a project at any '
        'given time. The focus is to at all times have a minimal viable product available, and during '
        'each sprint, iteratively add onto this product.')
        update.message.reply_text('For more information, click on the following link\n'
        'https://en.wikipedia.org/wiki/Agile_software_development#Overview')

    elif (word.lower() == terms[2].lower()): # sprint
        update.message.reply_text('A sprint is an iterative pre planned time-box in which tasks '
        'are completed in order to add to project. The sprint duration is decided by the scrum '
        'master. Each sprint focuses on removing the highest prioritised items off of the product '
        'backlog, typically defined in user stories. During the sprint daily "stand up" meetings '
        'are held to manage team progress. At the end of a sprint a review is held where work is '
        'shown to the product owner.'
        )
        update.message.reply_text('For more information, click on the following link\n'
        'https://en.wikipedia.org/wiki/Scrum_Sprint')

    elif (word.lower() == terms[3].lower()): # scrum
        update.message.reply_text('Scrum is a subset of the Agile methodology. '
        'Scrum is typically applied by teams of 10 or fewer members. It works by breaking larger'
        'elements of a project into smaller tasks which each can be autonomously completed '
        'during the sprint. Before a sprint, a sprint planning meeting is held to organize '
        'the upcoming sprint, daily scrum meetings are held to track progress of the sprints, '
        'and after the sprint is completed a sprint retrospective meeting is held to find out '
        'what worked well and what did not.')
        update.message.reply_text('For more information, click the following link\n'
        'https://en.wikipedia.org/wiki/Scrum_(software_development)')

    elif (word.lower() == terms[4].lower()): # roles
        update.message.reply_text('Scrum Master - '
        'The Scrum master is the facilitator of the project\'s '
        'development team. They are in charge of the all scrum meetings. '
        'This person is in responsible for removing obstacles for the team '
        'and guide the team to stay on track.\n\n'

        'Product Owner - The product owner is a person '
        'who represents the client or user community and '
        'is in charge of communication between the development '
        'team and the customer. This person is responsible for '
        'leading the group in defining, adjusting and prioritizing '
        'features to include in the product\n\n'

        'Scrum Team - '
        'This group of people is responsible for executing the work '
        'agreed upon during the sprints. The team is self managing and '
        'are individually responsible for working on their task for each '
        'sprint and collectively responsible for managing how to reach '
        'the goals for the sprint.')
        update.message.reply_text('For more information, click the following link\n'
        'https://en.wikipedia.org/wiki/Scrum_(software_development)#Roles')


    elif (word.lower() == terms[5].lower()): # user stories
        update.message.reply_text('User stories are a description of a feature or requirement, '
        'expressed in natural language\. They are usually \(but not always\) written from the '
        'perspective of the end\-user\. The format is usually:\n'
        'As a `role` I can `capability`, so that `receive benefit`', parse_mode = ParseMode.MARKDOWN_V2)
        update.message.reply_text('For more information, click the following link\n'
        'https://en.wikipedia.org/wiki/User_story')
    
    elif (word.lower() == additional_terms[0].lower()): # Product backlog
        update.message.reply_text(
            'A product backlog is a breakdown of work to be done, often '
            'sorted by priority or necessity. The list is typically '
            'formatted in user stories, or use cases, and includes '
            'product features, bug-fixes or non functional requirements. '
            'The backlog is the single authoritative source for what the '
            'team works on, meaning nothing is done that is not listed. '
            'This also means that new features are decided upon, their '
            'priority is determined and they are added to the backlog.'
        )
        update.message.reply_text('For more information, click the following link\n'
        'https://en.wikipedia.org/wiki/Scrum_(software_development)#Product_backlog')
    elif (word.lower() == additional_terms[2].lower()): # minimum viable product
        update.message.reply_text(
            'The minimal Viable Product (MVP) is the current version of a '
            'product consisting of completed and tested features. This means '
            'that features that are yet to be completely done are not included '
            'in the MVP. The MVP allows the team to be able to at all times '
            'present a functioning prototype, which can help ensure customer '
            'satisfaction before further development is done.'
        )
        update.message.reply_text('For more information, click the following link\n'
        'https://en.wikipedia.org/wiki/User_story')

    elif (word.lower() == additional_terms[3].lower()): # sprint planning meeting
        update.message.reply_text('The sprint planning meeting initiates '
        'the following sprint. It is attended by all members of the scrum, and '
        'occasionally outside stakeholders by invitation of the team. During this '
        'meeting the product owner defines the most important features for the team. '
        'The team can then ask questions in order to be able to turn high-level user '
        'stories from the product backlog into more detailed tasks for the sprint backlog')
        update.message.reply_text('For more information, click the following link\n'
        'https://en.wikipedia.org/wiki/Scrum_Sprint#Process_Flow')
    
    elif (word.lower() == additional_terms[1].lower()): # sprint backlog
        update.message.reply_text('A sprint backlog is a highly detailed list of '
        'tasks to be completed. Each tasks in the sprint backlog has been taken '
        'from the product backlog, based on priority, and elaborated upon. All '
        'tasks within the sprint backlog is expected to be completed within the '
        'current sprint.')
        update.message.reply_text('For more information, click the following link\n'
        'https://en.wikipedia.org/wiki/Scrum_(software_development)#Sprint_backlog')

    elif (word.lower() == additional_terms[4].lower()): #daily scrum
        update.message.reply_text('In the beginning of each new day of the sprint, '
        'a daily scrum is held. The meetings are often strictly time boxed, and '
        'are done standing up, in order to keep them short and relevant. Typically '
        'every development team member answers the three questions: "What did I '
        'complete yesterday?", "What do I plan on completing today?" and "Do I see '
        'any impediment that could prevent me or the team from meeting our sprint goal?"')
        update.message.reply_text('For more information, click the following link\n'
        'https://en.wikipedia.org/wiki/Scrum_(software_development)#Daily_scrum')

    elif (word.lower() == additional_terms[5].lower()): # Sprint Review
        update.message.reply_text(' At the end of each sprint, the entire scrum team '
        'holds a sprint review meeting. During this meeting the team reviews and '
        'presents what has been completed, sometimes in form of a demo. A discussion '
        'of what was not completed is had, as well as figuring out with the product '
        'owner on what to work on next.')
        update.message.reply_text('For more information, click the following link\n'
        'https://en.wikipedia.org/wiki/Scrum_(software_development)#Sprint_review')
    
    elif (word.lower() == additional_terms[6].lower()): # sprint retrospective
        update.message.reply_text('The sprint retrospective is a meeting held in order '
        'to allow the team to continue to improve based on the last completed sprint. '
        'The focus is to review what practices the team should continue to use, which '
        'they should stop using and what they should start doing to allow optimal '
        'performance during the next sprint.')
        update.message.reply_text('For more information, click the following link\n'
        'https://en.wikipedia.org/wiki/Scrum_(software_development)#Sprint_Retrospective')
    else:
        update.message.reply_text("Oops! Looks like I don't recognize that word...")

