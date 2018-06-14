import requests
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler


# This bot uses Yandex.map API to find all places in the world you need

def start(bot, update):
    update.message.reply_text("You just need to write name of geo object and i find it!")
    return 1


def get_map(ll, size = "650,450", delta=0.01, l="map", pt=""):
    try:
        place_longtitude, place_lattitude = ll.split()
        map_api_server = "http://static-maps.yandex.ru/1.x/"
        response = requests.get(map_api_server, params={
            "ll": ",".join([place_longtitude, place_lattitude]),
            "size": size,
            "spn": ",".join([str(delta), str(delta)]),
            "l": l,
            "pt": pt})

        return response.url
    except:
        return 1


def get_spn(obj):
    lowerx, lowery = obj["boundedBy"]["Envelope"]["lowerCorner"].split()
    upperx, uppery = obj["boundedBy"]["Envelope"]["upperCorner"].split()
    deltax = float(upperx)- float(lowerx)
    deltay = float(uppery) - float(lowery)
    return (str(deltax/2), str(deltay/2))


def get_obj(address, format="json"):
    try:
        geocode_server = "https://geocode-maps.yandex.ru/1.x/"
        response = requests.get(geocode_server, params={
            "geocode": address,
            "format": format
        })
        j_response = response.json()["response"]
        if len(j_response["GeoObjectCollection"]["featureMember"]) != 0:
            obj = j_response["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            coords = obj["Point"]["pos"]
            return (coords, obj["metaDataProperty"]["GeocoderMetaData"]["text"], get_spn(obj)[0])
        else:
            return (1, 1, 1)
    except:
        return (2, 2, 2)


def send_map(bot, update):
    ll, adr, spn  = get_obj(update.message.text)
    if ll == 1:
        update.message.reply_text("Check what are you print")
        return 1
    elif ll == 2:
        update.message.reply_text("I don't have internet")
        return 1
    pt = ",".join(ll.split())+",pm2gnm"
    map = get_map(ll, pt=pt, delta=float(spn))
    if map == 1:
        update.message.reply_text("I don't have internet")
        return 1
    print(map, update.message.chat_id)
    bot.send_photo(update.message.chat_id, map, caption=adr)
    return 1


def stop(bot, update):
    update.message.reply_text("Ок")
    return ConversationHandler.END

def main():
    updater = Updater("MY_API_KEY")
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            1: [MessageHandler(Filters.text, send_map)],
        },
        fallbacks=[CommandHandler("stop", stop)]
    )

    dp.add_handler(conv_handler)



    print("Бот стартует")

    updater.start_polling()


    updater.idle()


if __name__ == "__main__":
    main()