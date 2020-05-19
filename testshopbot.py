import os, json, time
from DBmodul import dbbot
from Shopbot import shopbot


def init_conf():
    with open(os.path.abspath('config/config.json')) as f:
        return json.load(f)


def init_telegrambot(vd = dbbot.DbHelper(os.path.abspath('DBmodul/shopdb.db'))):
    return shopbot.Telegramshopbot(TOKENBOT = init_conf()['DEFAULT']['TOKENBOT'],
                                   databese = vd,
                                   MANAGERID = init_conf()['DEFAULT']['MANAGERID'])


def run_bot():
    shop = init_telegrambot()

    @shop.bot.message_handler(commands=['start'])
    def go_start(message):
        shop.start(message=message)

    @shop.bot.callback_query_handler(func=lambda call: call.data and call.data in ['back'])
    def get_back(call):
        return shop.back_mainmenu(call=call)

    @shop.bot.callback_query_handler(
        func=lambda call: call.data and call.data in ['category'] or call.data.startswith("back_category"))
    def get_category(call):
        return shop.category_reply(call=call)

    @shop.bot.callback_query_handler(
        func=lambda call: call.data and call.data in ['basket'] or call.data.startswith("update_info"))
    def get_basket(call):
        return shop.basket_reply(call=call)

    @shop.bot.callback_query_handler(
        func=lambda call: call.data.startswith("showacc") or call.data.startswith("showsp") or call.data.startswith("number"))
    def get_inl(call):
        shop.callback_inline_pag(call=call)

    @shop.bot.message_handler(func=lambda message: True, content_types=['text'])
    def go_acc(message):
        return shop.ans_sp(message)

    @shop.bot.callback_query_handler(func=lambda call: call.data.startswith("add_basket"))
    def add_basc(call):
        shop.add_bascet(call=call)

    @shop.bot.callback_query_handler(
        func=lambda call: call.data.startswith("buy") or call.data.startswith("delete_buy"))
    def buy_and_delete(call):
        shop.buy_and_delete(call=call)

    shop.bot.polling(none_stop=True, interval=0)



if __name__=='__main__':

    while True:
        try:
            run_bot()
        except:
            time.sleep(30)
            continue
