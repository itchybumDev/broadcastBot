import configparser
import csv
import logging
import pickle
import sys
import time
from datetime import datetime

import telegram
from telegram.ext import MessageHandler, Filters
from telegram.ext import Updater, CommandHandler
from telegram.ext.dispatcher import run_async

from model.Job import Job

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read('config.ini')

class authorize:
    def __init__(self, f):
        self._f = f

    def __call__(self, *args):
        if str(args[0].effective_chat.id) in dev_team:
            return self._f(*args)
        else:
            raise Exception('Alpaca does not want to you use this command.')


@run_async
def unknown(update, context):
    send_plain_text(update, context, "Sorry, I didn't understand that command.\nRun /help to see available options")

groupChatId = {}

dev_team = []

def log(message):
    print("********************************")
    print("{} : {}".format(datetime.today(), message))
    print("********************************")

def saveUserDict():
    global groupChatId
    with open("./db/groupChatId.pickle", 'wb') as handle:
        pickle.dump(groupChatId, handle, protocol=pickle.HIGHEST_PROTOCOL)
    return True


def loadUserDict():
    global groupChatId
    try:
        with open("./db/groupChatId.pickle", 'rb') as handle:
            groupChatId = pickle.load(handle)
    except IOError:
        log("User Dict data is not found, initialize to empty")

def loadDevTeam():
    with open("./db/dev_team.csv", newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            dev_team.append(str(row[0]))


def saveDevTeam():
    with open("./db/dev_team.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        for v in dev_team:
            writer.writerow([v])
    return True

@run_async
def start(update, context):
    chatId = update.effective_chat.id
    type = update.effective_chat.type
    title = update.effective_chat.title
    print("ChatId: {} - type: {} - title: {}".format(chatId, type, title))
    if chatId not in groupChatId.keys():
        groupChatId[chatId] = Job(chatId, type, title, "", 20)
        saveUserDict()


@run_async
def hi(update, context):
    chatId = update.effective_chat.id
    type = update.effective_chat.type
    title = update.effective_chat.title
    print("ChatId: {} - type: {} - title: {}".format(chatId, type, title))
    if chatId not in groupChatId.keys():
        groupChatId[chatId] = Job(chatId, type, title, "", 20)
        saveUserDict()


@run_async
def activate(update, context):
    while True:
        for k in groupChatId.keys():
            tmpJob = groupChatId.get(k)
            if tmpJob.chatId < 0:
                keepSending(update, context, tmpJob)

        time.sleep(10)

@run_async
def addDev(update, context):
    dev_team.append(update.effective_chat.id)
    saveDevTeam()


@authorize
@run_async
def show(update, context):
    for k in groupChatId.keys():
        tmpJob = groupChatId.get(k)
        if tmpJob.chatId < 0:
            send_plain_text(update, context, tmpJob.toString())

@authorize
@run_async
def updateGroup(update, context):
    id = int(context.args[0])
    frequency = int(context.args[1])
    msg = ' '.join(context.args[2:])
    msg = msg.replace('*n','\n')
    msg = msg.replace('*b', '*')
    msg = msg.replace('*i', '_')
    tmpJob = groupChatId[id]
    tmpJob.set_message(msg)
    tmpJob.set_frequency(frequency)
    saveUserDict()

    context.bot.send_message(update.effective_chat.id, text=tmpJob.toString(), parse_mode=telegram.ParseMode.MARKDOWN)

@authorize
@run_async
def delete(update, context):
    id = int(context.args[0])
    tmpJob  = groupChatId.get(id)
    if id in groupChatId.keys():
        del groupChatId[id]
        saveUserDict()
    send_plain_text(update,context, 'Removed this group \n{}'.format(tmpJob.toString()))

@authorize
@run_async
def help_me(update, context):
    HELP_TEXT = """--<i>Here is a list of commands</i>--

/hi
Register the group after added bot to group

/activate
Start sending after the bot reset

/show
Show all Groups that the bot is active

/update [chatId] [frequency in seconds] [message]
Update the message sending to the group
*b -- *bBold*b
*i -- *iItalic*i
*n -- newline

/delete [chatId]
Delete the group from the bot
    """
    context.bot.send_message(update.effective_chat.id, text=HELP_TEXT, parse_mode=telegram.ParseMode.HTML)


# Emoticon table: https://apps.timwhitlock.info/emoji/tables/unicode
def keepSending(update, context, job):
    print("{} :: Last sent - {} at {}".format(datetime.today(), job.groupName, job.lastSent))
    if (isinstance(job.lastSent, int)
        or (datetime.today() - job.lastSent).total_seconds() > job.frequency) \
            and job.msg != ''\
            and job.frequency != -1:
        context.bot.send_message(job.chatId, text=job.msg, parse_mode=telegram.ParseMode.MARKDOWN)
        notifyAdmin(("Just sent to *{}* \n\n" +u'\U0001F4EA' + " Message: \n{}").format(job.groupName, job.msg), context)
        job.lastSent = datetime.today()


def notifyAdmin(text, context):
    for dev in dev_team:
        context.bot.send_message(dev, text=text, parse_mode=telegram.ParseMode.MARKDOWN)


def error_handler(update, context):
    send_plain_text(update, context, str("Something is missing! Please try again"))
    logger.error(" Error in Telegram Module has Occurred:", exc_info=True)

def send_plain_text(update, context, text):
    context.bot.send_message(update.effective_chat.id, text=text)

def main():
    # ad.startAdmin()
    updater = Updater(config['telegram']['token_dev'], use_context=True)
    dp = updater.dispatcher
    loadUserDict()
    loadDevTeam()

    commands = [
        ["start", start],
        ["hi", hi],
        ["iamadmin", addDev],
    ]
    for command, function in commands:
        updater.dispatcher.add_handler(CommandHandler(command, function))

    admin_commands = [
        ["activate", activate],
        ["show", show],
        ["update", updateGroup],
        ["delete", delete],
        ["help", help_me],
    ]
    #
    for command, function in admin_commands:
        updater.dispatcher.add_handler(CommandHandler(command, function))

    dp.add_handler(MessageHandler(Filters.command, unknown))
    dp.add_handler(MessageHandler(Filters.text, unknown))

    dp.add_error_handler(error_handler)
    updater.start_polling(poll_interval=1.0, timeout=20)
    updater.idle()


if __name__ == '__main__':
    logger.info("Starting Bot")
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Terminated using Ctrl + C")
    logger.info("Exiting Bot")
    sys.exit()
