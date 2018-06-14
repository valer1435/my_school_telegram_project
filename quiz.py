import json
import random

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler


# This bot a quiz bot. So, you just need to answer for a questions. Nothing special. In next bot i update it. Let's see!
# Some question may be have not right answer. Some people said it me :)

def vopros(update, user_data, q):
    answer_keyboard = [[q["A"], q["B"]], [q["C"], q["D"]]]
    markup = ReplyKeyboardMarkup(answer_keyboard)
    update.message.reply_text(q["question"], reply_markup=markup)
    user_data["quiz"].append(q)

quest = json.load(open("questions.json", mode="r"))
LENTH_QUESTION = len(quest)


def start(bot, update, user_data):
    user_data["quiz"] = []
    user_data["score"] = 0
    user_data["count"] = 0
    update.message.reply_text("Hi! I have some questions for you. Do you want to answer?")
    vopros(update, user_data, quest[random.choice(range(LENTH_QUESTION))])
    return 1


def question(bot, update, user_data):
    answer = update.message.text
    q = user_data["quiz"][-1]
    true_value = q["true"]

    if answer == q[true_value]:
        user_data["score"] += 1
    user_data["count"] += 1

    while True:
        q = quest[random.choice(range(LENTH_QUESTION))]
        if q not in user_data["quiz"]:
            print(q, user_data["quiz"])
            break

    vopros(update, user_data, q)
    if user_data["count"] == LENTH_QUESTION-1:
        return 3
    return 1


def all_sumbit(bot, update, user_data):
    answer = update.message.text
    q = user_data["quiz"][-1]
    if answer == q[q["true"]]:
        user_data["score"] += 1
    user_data["count"] += 1
    m = ReplyKeyboardMarkup([["/start"]])
    update.message.reply_text("You scored {} points. Again?".format(user_data["score"]), reply_markup=m)
    return ConversationHandler.END


def stop(bot, update):
    update.message.reply_text("Does it so hard for you? Again?", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def main():
    updater = Updater("MY_API_KEY")
    dp = updater.dispatcher

    victorine_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start, pass_user_data=True)],
        states={
            1: [MessageHandler(Filters.text, question, pass_user_data=True)],
            3: [MessageHandler(Filters.text, all_sumbit, pass_user_data=True)]
        },
        fallbacks=[CommandHandler("stop", stop)]
    )

    dp.add_handler(victorine_handler)



    print("Бот стартует")

    updater.start_polling()


    updater.idle()


if __name__ == "__main__":
    main()