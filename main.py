# lib
import json

from pycqbot_core.cqApi import cqHttpApi, cqLog, Message
from logging import INFO

# 启用日志 默认日志等级 DEBUG
cqLog(INFO)

cqapi = cqHttpApi()

bot = cqapi.create_bot()


def help_proc(commandData, message: Message):

    with open('help.json', "rb") as tipsjson:
        help_dict = json.loads(tipsjson.read().decode('utf-8'))

    if not bool(commandData):

        message.reply("\n".join(help_dict['commands']))

    else:

        for key in commandData:

            if key in help_dict:
                message.reply(
                    help_dict[key]
                )


bot.command(help_proc, 'help', {"type": "all"})

bot.plugin_load(
    [
        "sdapi"
    ]
)

bot.start()
