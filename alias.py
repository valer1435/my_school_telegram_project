import random

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, RegexHandler

# This bot repeat game "alias" but has some differences: firstly a member of the team A try to explain his teammate
# meaning of word that bot show. f word has been guessed, word change. After 1 minute teams changes. Game has 3 rounds.
# Team that gained more points wins. That is easy!








words_keyboard = [["make new list of words"]]

game_keyboard = [["Let's go"]]

yes_keyboard = [["guessed"]]

close_keyboard = [["/close"]]

words_markup = ReplyKeyboardMarkup(words_keyboard)
game_markup = ReplyKeyboardMarkup(game_keyboard)
yes_markup = ReplyKeyboardMarkup(yes_keyboard)
close_markup = ReplyKeyboardMarkup(close_keyboard)


def set_timer(bot, update, job_queue, chat_data):
    delay = 10
    job = job_queue.run_once(task, delay, context={"id": update.message.chat_id,
                                                   "chat":chat_data, "job":job_queue, "update":update})
    chat_data['job'] = job


def start(bot, update, chat_data):
    update.message.reply_text("Let's start a game!", reply_markup=words_markup)
    chat_data["com"] = "start"


def words(bot, update, chat_data):
    if chat_data["com"] != "make new list of words":
        update.message.reply_text("Great!", reply_markup=game_markup)
        chat_data["words"] = ["rabbit", "yandex", "cat", "table"]   #this  bot is education project and i don't make huge list of words)
        chat_data["com"] = "make new list of words"
        chat_data["team"] = 0
        chat_data["A"] = 0
        chat_data["B"] = 0
        chat_data["count"] = 0


def game(bot, update, job_queue, chat_data):
    if chat_data["com"] != "Let's go":
        if chat_data["words"]:
            word = random.choice(chat_data["words"])
            del chat_data["words"][chat_data["words"].index(word)]
        else:
            end(bot, update.message.chat_id, chat_data)
            return

        update.message.reply_text("Game has started! First word is "+word, reply_markup=yes_markup)
        chat_data["team"] = "A"
        chat_data["com"] = "Let's go"
        set_timer(bot, update, job_queue, chat_data)


def yes(bot, update, chat_data):
    if chat_data["team"] != 0:
        chat_data[chat_data["team"]] += 1
        if chat_data["words"]:
            word = random.choice(chat_data["words"])
            del chat_data["words"][chat_data["words"].index(word)]
        else:
            end(bot, update.message.chat_id, chat_data)
            return
        chat_data["com"] = "guessed"
        update.message.reply_text("Next word is "+word, reply_markup=yes_markup)


def task(bot, job):
    job.context["chat"]["count"] += 1
    if job.context["chat"]["count"] != 6:
        set_timer(bot, job.context["update"], job.context["job"], job.context["chat"])
    else:
        end(bot, job.context["id"], job.context["chat"])
        return
    if job.context["chat"]["words"]:
        word = random.choice(job.context["chat"]["words"])
        del job.context["chat"]["words"][job.context["chat"]["words"].index(word)]
    else:
        end(bot, job.context["id"], job.context["chat"])
        return
    bot.send_message(job.context["id"], text="Teams are changing now! Next word is "+word)
    if job.context["chat"]["team"] == "A":
        job.context["chat"]["team"] = "B"
    elif job.context["chat"]["team"] == "B":
        job.context["chat"]["team"] = "A"


def end(bot, id,  chat_data):
    bot.send_message(id, """Result:\nTeam "А": {} points\nTeam "В": {} points""".format(chat_data["A"], chat_data["B"]), reply_markup=words_markup)
    if 'job' in chat_data:
        chat_data['job'].schedule_removal()
        del chat_data['job']
    chat_data["team"] = 0
    chat_data["A"] = 0
    chat_data["B"] = 0
    chat_data["count"] = 0


def main():
    updater = Updater("MY_API_KEY")

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start, pass_chat_data=True))
    dp.add_handler(RegexHandler("make new list of words", words, pass_chat_data=True))
    dp.add_handler(RegexHandler("Let's go", game, pass_chat_data=True, pass_job_queue=True))
    dp.add_handler(RegexHandler("guessed", yes, pass_chat_data=True))


    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()