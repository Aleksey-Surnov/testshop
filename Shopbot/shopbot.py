import os, json, csv
import apiai
from telebot import types
import telebot
from datetime import datetime, timedelta


class Telegramshopbot():


    def __init__(self, TOKENBOT, databese, MANAGERID):
        self.tokenbot = TOKENBOT        # токен бота telegram
        self.bot = telebot.TeleBot(token = self.tokenbot)
        self.vd = databese              # название базы данных
        self.managerid = int(MANAGERID) # id менеджера которому отправляется заказ.


    def start(self, message):
        self.bot.send_message(message.from_user.id, 'Здравствуйте. Я тестовый магазин-бот. У меня вы можете купить: '
                                                    '\n1. Аксесуары для IPhone.'
                                                    '\n2. Запчасти для IPhone.'
                                                    '\nДля выбора товара и просмотра ассортимента нажмите *Категории*.'
                                                    '\nДля просмотра заказа и суммы покупки нажмите *Корзина*.'
                                                    '\nДля оформления заказа перейдите в корзину и нажмите *Заказать*.', parse_mode="Markdown")
        self.bot.send_message(message.chat.id, "Ваша корзина пуста", reply_markup = self.main_keybard())


    def main_keybard(self):
        keyboardmain = types.InlineKeyboardMarkup(row_width = 2)
        basket_button = types.InlineKeyboardButton(text = "Корзина", callback_data = "basket")
        category_button = types.InlineKeyboardButton(text = "Категории", callback_data = "category")
        keyboardmain.add(basket_button, category_button)
        return keyboardmain


    def category_reply(self, call):
        if call.data.startswith("back_category"):
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
        keyboardchat = types.ReplyKeyboardMarkup(resize_keyboard = True, one_time_keyboard = True)
        keyboardchat.add(*[types.KeyboardButton(name) for name in
                           ['Аксессуар для IPhone', 'Запчасти для IPhone']])
        self.bot.send_message(call.message.chat.id, text = 'Выберите категорию: ', reply_markup = keyboardchat)


    def basket_reply(self, call):
        keyboardmain = types.InlineKeyboardMarkup(row_width = 2)
        category_button = types.InlineKeyboardButton(text = "Назад", callback_data = "back")
        keyboardmain.add(category_button)
        if self.vd.verify_user(user_id = call.from_user.id):
            self.bot.edit_message_text(chat_id = call.message.chat.id,
                                       message_id = call.message.message_id,
                                       text = 'Ваша корзина пуста', reply_markup = keyboardmain)
        else:
            buy_button = types.InlineKeyboardButton(text = "Заказать", callback_data = "buy")
            delete_button = types.InlineKeyboardButton(text = "Очистить корзину", callback_data = "delete_buy")
            update_bascet = types.InlineKeyboardButton(text = "Обновить информацию в корзине", callback_data = "update_info")
            keyboardmain.add(buy_button, delete_button, update_bascet)
            bascet_info = self.vd.get_basket(user_id = call.from_user.id)
            summ_bascet = sum(self.edit_basket_for_sum(bascet_info = bascet_info))
            bascet_info = self.edit_basket_for_reading(bascet_info = bascet_info)
            bascet_info = '\n'.join([str(element)+'\n' for element in bascet_info]).strip('[]').replace('(','').replace(')','').replace(',',' ').replace("'",'')
            self.bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id,
                                       text = bascet_info+'\n'+f'*Общая сумма: {summ_bascet} руб.*',
                                       reply_markup = keyboardmain, parse_mode = "Markdown")


    def edit_basket_for_sum(self, bascet_info = []):        # генератор списка для подсчета общей суммы покупки в корзине
        return [bascet_info[i][1] for i in range(len(bascet_info))]


    def edit_basket_for_reading(self, bascet_info = []):    # редактирование для показа пользователю информации о корзине
        for i in range(len(bascet_info)):
            bascet_info[i] = (bascet_info[i][0], str(bascet_info[i][1]) + ' руб.', str(bascet_info[i][2]) + ' шт.')
        return bascet_info


    def get_keyboard(self, info_goods, position, type_category, title_bascet = "Добавить в корзину"): # клавиатура пагинации
        kb = types.InlineKeyboardMarkup()
        basket_add_button = types.InlineKeyboardButton(text = title_bascet, callback_data = "add_basket")
        back_category = types.InlineKeyboardButton(text = "Назад в категории", callback_data = "back_category")
        temp_arr = []
        if position > 0:
            temp_arr.append(types.InlineKeyboardButton(text = "←", callback_data = f"{type_category}_{position - 1}"))
        temp_arr.append(types.InlineKeyboardButton(text=f"{position + 1}", callback_data=f"number_{position}"))
        if position < len(info_goods) - 1:
            temp_arr.append(types.InlineKeyboardButton(text = "→", callback_data = f"{type_category}_{position + 1}"))
        kb.add(*temp_arr)
        kb.add(basket_add_button)
        kb.add(back_category)
        return kb


    def ans_sp(self, message):
        if message.text == 'Запчасти для IPhone':
            keyboard = types.InlineKeyboardMarkup(row_width = 2)
            info_goods = self.vd.get_category_catalog(teg = 'spareiphone')
            type_category = 'showsp'
            position = len(info_goods) - 1
            self.bot.send_message(message.chat.id,
                              f"Предлагаем Вам следующий товар:\n\n*Название*: {info_goods[0][0]}\n*Описание*: {info_goods[0][1]}."
                              f"\n"
                              f"*Цена*: {info_goods[0][2]} шт.\n\nДля просмотрa товаров используйте стрелки ниже.",
                              reply_markup = self.get_keyboard(info_goods, position, type_category), parse_mode = "Markdown")
            self.save_now(info_goods, 0, message.from_user.id)
            return info_goods[0]


        elif message.text == 'Аксессуар для IPhone':
            keyboard = types.InlineKeyboardMarkup(row_width = 2)
            info_goods = self.vd.get_category_catalog(teg = 'accessoriesiphone')
            type_category = 'showacc'
            position = len(info_goods) - 1
            self.bot.send_message(message.chat.id,
                                  f"Предлагаем Вам следующий товар:\n\n*Название*: {info_goods[0][0]}\n*Описание*: {info_goods[0][1]}."
                                  f"\n"
                                  f"*Цена*: {info_goods[0][2]} шт.\n\nДля просмотра товаров используйте стрелки ниже.",
                                  reply_markup = self.get_keyboard(info_goods, position, type_category), parse_mode= "Markdown")
            self.save_now(info_goods, 0, message.from_user.id)
            return info_goods[0]


        else:
            self.bot.send_message(message.chat.id,
                                  'Извините, я Вас не понимаю.' + '\n'+'*Пожалуйста сделайте выбор из меню*',
                                  parse_mode = "Markdown")


    def back_mainmenu(self, call):
        if call.data == 'back':
            self.bot.edit_message_reply_markup(chat_id = call.message.chat.id,
                                               message_id = call.message.message_id,
                                               reply_markup = self.main_keybard())


    def callback_inline_pag(self, call):
        if self.vd.verify_user(user_id = call.from_user.id):
            title_bascet = 'Добавить в корзину'
        else:
            title_bascet = 'Добавить еще'

        if call.data.startswith("showacc"):
            position = int(call.data.split("_")[1])
            info_goods = self.vd.get_category_catalog(teg = 'accessoriesiphone')
            type_category = 'showacc'
            self.bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id,
                                       text = f"Предлагаем Вам следующий товар:\n\n*Название*: {info_goods[position][0]}\n"
                                       f"*Описание*: {info_goods[position][1]}\n"
                                       f"*Цена*: {info_goods[position][2]} руб.\n\nДля просмотра товаров используйте стрелки ниже.",
                                       reply_markup = self.get_keyboard(info_goods, position, type_category, title_bascet), parse_mode = "Markdown")
            self.bot.answer_callback_query(call.id)
            self.save_now(info_goods, position, call.from_user.id)
            return info_goods[position]


        elif call.data.startswith("showsp"):
            position = int(call.data.split("_")[1])
            info_goods = self.vd.get_category_catalog(teg = 'spareiphone')
            type_category = 'showsp'
            self.bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id,
                                       text = f"Предлагаем Вам следующий товар:\n\n*Название*: {info_goods[position][0]}\n"
                                       f"*Описание*: {info_goods[position][1]}\n"
                                       f"*Цена*: {info_goods[position][2]} руб.\n\nДля просмотра товаров используйте стрелки ниже.",
                                       reply_markup = self.get_keyboard(info_goods, position, type_category, title_bascet),
                                       parse_mode = "Markdown")
            self.bot.answer_callback_query(call.id)
            self.save_now(info_goods, position, call.from_user.id)
            return info_goods[position]


        elif call.data.startswith("number"):
            position = int(call.data.split("_")[1])
            self.bot.answer_callback_query(callback_query_id = call.id,
                                           text = f'Вы на странице {position + 1}.',
                                           show_alert = False)


    def save_now(self, goods_file, i, user_id):
        name_file = f'now_goods_{user_id}.txt'
        with open(os.path.abspath('./files/' + name_file), 'w', encoding='UTF-8') as file_tovar:
            file_tovar.write(goods_file[i][0])
            file_tovar.write('\n')
            file_tovar.write(str(goods_file[i][2]))


    def open_now(self, user_id):
        name_file = f'now_goods_{user_id}.txt'
        with open(os.path.abspath('./files/' + name_file), 'r', encoding='UTF-8') as file_tovar:
            return file_tovar.read().split('\n')


    def add_bascet(self, call):
        try:
            order = self.open_now(user_id=call.from_user.id)
            tovar = self.vd.add_basket(user_id = call.from_user.id, name = order[0], price = int(order[1]))
            self.bot.answer_callback_query(callback_query_id = call.id,
                                           text = 'Товар добавлен в корзину. Нажмите "Обновить информацию".',
                                           show_alert = False)
        except FileNotFoundError:
            self.bot.answer_callback_query(callback_query_id = call.id,
                                           text = 'Ошибка. Нажмите "Назад в категории" или стрелки ниже.',
                                           show_alert = False)


    def buy_and_delete(self, call):
        user_id = call.from_user.id
        if call.data.startswith("buy") and self.vd.verify_user(user_id = call.from_user.id) == False:
            buy_name = f'now_goods_{user_id}.csv'
            basket_list = self.vd.get_basket(user_id = user_id)
            user_name = call.from_user.username
            with open(os.path.abspath('./files/' + buy_name), 'w', encoding='UTF-8') as file_buy:
                column = ('name', 'price', 'count')
                basket_list.insert(0, column)
                writer = csv.writer(file_buy, quoting = csv.QUOTE_NONNUMERIC)
                writer.writerows(basket_list)
            with open(os.path.abspath('./files/' + buy_name), 'r', encoding = 'UTF-8') as file_buy:
                self.bot.send_document(chat_id = self.managerid, data = file_buy,
                                       caption=f'Пользователь с id: {user_id} и username:{user_name} сделал заказ.')
            self.bot.send_message(call.message.chat.id,
                                  'Ваш заказ оформлен. В ближайшее время менеджер свяжется с Вами.')
            os.remove(os.path.abspath('./files/' + buy_name))
        elif call.data.startswith("buy") and self.vd.verify_user(user_id = call.from_user.id) == True:
            self.bot.answer_callback_query(callback_query_id=call.id,
                                           text='Ваша корзина пуста. Добавьте товар.',
                                           show_alert=False)


        elif call.data.startswith("delete_buy"):
            self.bot.answer_callback_query(callback_query_id=call.id, text='Ваша корзина пуста. Нажмите "Обновить информацию"', show_alert=False)

        try:
            name_file = f'now_goods_{user_id}.txt'
            os.remove(os.path.abspath('./files/' + name_file))
            self.vd.delete_basket(user_id = user_id)
        except FileNotFoundError:
            pass


















