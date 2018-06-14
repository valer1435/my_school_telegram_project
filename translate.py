import requests
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler


# This edication bot translate words from english on russian and from russian on english with Yandex translator API


API_KEY = "MY_API_KEY"
lang_keyboard = [["ru-en", "en-ru"]]
languages = ["ru-en", "en-ru"]
lang_dict = {"ru-en": "Русско-английский", "en-ru": "Англо-русский"}
lang_markup = ReplyKeyboardMarkup(lang_keyboard)


def start(bot, update, user_data):
    user_data["lang"] = "ru-en"
    update.message.reply_text("I'am a translator bot. Let's go! {}".format(lang_dict[user_data["lang"]]))
    return 1


def translater(bot, updater, user_data):
    accompanying_text = "Translate has made by 'Yandex Translator'  http://translate.yandex.ru/."
    translator_uri = "https://translate.yandex.net/api/v1.5/tr.json/translate"
    try:
        response = requests.get(
            translator_uri,
            params={
                "key":
                API_KEY,        # Ключ, который необходимо получить по ссылке в тексте.
                "lang": user_data["lang"],              # Направление перевода: с русскго на английский.
                "text": updater.message.text  # То, что нужно перевести.
            })
        if response:
            updater.message.reply_text("\n\n".join([response.json()["text"][0], accompanying_text]))
        else:
            updater.message.reply_text("Oooh.. we have a problem!")
    except:
        updater.message.reply_text("I don't feel internet!")
    return 1


def command_lang(bot, update):
    update.message.reply_text("Choose language", reply_markup = lang_markup)
    return 2


def change_lang(bot, update, user_data):
    print(languages)
    if update.message.text in languages:
        user_data["lang"] = update.message.text
        update.message.reply_text("Language has been changed on {}".format(lang_dict[user_data["lang"]]), reply_markup=ReplyKeyboardRemove())
        return 1
    else:
        update.message.reply_text("Choose one of them", reply_markup=lang_markup)
        return 2


def stop(bot, update):
    update.message.reply_text("Ok")
    return ConversationHandler.END


def main():
    updater = Updater("MY_API_KEY")
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start, pass_user_data=True)],
        states={
            1: [MessageHandler(Filters.text, translater, pass_user_data=True), CommandHandler("lang", command_lang)],
            2: [MessageHandler(Filters.text, change_lang, pass_user_data=True)]
        },
        fallbacks=[CommandHandler("stop", stop)]
    )

    dp.add_handler(conv_handler)
    print("Бот стартует")

    updater.start_polling()


    updater.idle()


if __name__ == "__main__":
    main()