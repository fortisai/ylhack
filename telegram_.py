from logging import basicConfig, DEBUG
import requests
from requests import post, get
from telegram.ext import MessageHandler, Filters, CommandHandler, ConversationHandler, Updater
from database import *
from random import randint

TIME = 30
# basicConfig(level=DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
TOKEN = "886061585:AAGqa4VAePyMctx6NA9uPr7JJaWA7Z3b1Oc"

codes = {}


def authentication(bot, update, args, chat_data):
    if len(args) == 2:
        login, passw = args
        print(login, passw)
        response = post('http://localhost:5000/api/auth',
                 data={"login": login, "password": passw}).json()
        print(response)
        if response["token"]:
            new_id = TID(login=login, tid=update.message.chat_id)
            db.session.add(new_id)
            db.session.commit()
            chat_data["token"] = response["token"]
            update.message.reply_text('Успешно')
        return
    update.message.reply_text(
        "Неверный формат ввода"
    )


def send_code(tid):
    bot_token = TOKEN
    bot_chatID = tid.tid
    codes[tid.tid] = randint(10000, 99999)
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + str(codes[tid.tid])
    response = requests.get(send_text)
    return response.json()


def get_valid(tid):
    print(codes)
    return str(codes[tid])


if __name__ == "__main__":
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    j = updater.job_queue
    auth = CommandHandler(
        'auth', authentication, pass_args=1, pass_chat_data=1
    )
    # task = CommandHandler('task', get_task, pass_args=1, pass_chat_data=1)

    dp.add_handler(auth)
    updater.start_polling()
    updater.idle()