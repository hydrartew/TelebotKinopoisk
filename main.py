import telebot
from telebot import types
import config
import time
from time import sleep
from kinopoiskAPI import KP

bot = telebot.TeleBot(config.TOKEN)

TOKEN = 'token'
kinopoisk = KP(token=TOKEN)

input_is_allowed = False

def Mmenu(message):
    s = ''
    with open('help_menu.txt', 'r', encoding="utf8") as f:       
        for row in f:
            s += row

    mainmenu = types.InlineKeyboardMarkup(row_width=1)
    item1 = types.InlineKeyboardButton("Найти фильм/сериал", callback_data='search_films')
    item2 = types.InlineKeyboardButton("Список моих сериалов/фильмов", callback_data='list_films')
    
    mainmenu.add(item1)
    mainmenu.add(item2)

    bot.send_message(message.chat.id, s, reply_markup=mainmenu, parse_mode="HTML") 

@bot.message_handler(commands=['start', 'help'])
def start(message):
    Mmenu(message)

@bot.message_handler(content_types=['text'])
def InlineKeyboard(message):
    global input_is_allowed
    global search

    with open('log.txt', 'a+', encoding="utf8") as f:
        local_time = time.strftime("%H:%M:%S %d.%m.%Y", time.localtime())
        f.write(f'\n{local_time} \nUSER_ID: {message.from_user.id} \nNAME: {message.from_user.first_name} {message.from_user.last_name} @{message.from_user.username}\nTEXT: {message.text}')
    
    if message.chat.type == 'private' and input_is_allowed:
        search = kinopoisk.search(message.text)

        if len(search) == 0:
            bot.send_message(chat_id=message.chat.id, reply_to_message_id=message.message_id, text='Ничего не найдено🥺')
        else:
            film_spis = types.InlineKeyboardMarkup()
            for item in search:
                value = types.InlineKeyboardButton(text=f'{item.name} ({item.year})', callback_data=item.filmId)
                film_spis.add(value)
            bot.send_message(chat_id=message.chat.id, text="Парсим данные...")
            sleep(1)
            bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id+1, text='🔽Найденные фильмы🔽', reply_markup=film_spis)
            bot.send_message(chat_id=message.chat.id, text='Выберите фильм')

        input_is_allowed = False

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    global input_is_allowed
    global search
    try:
        if call.message:
            if call.data == 'mainmenu':
                Mmenu(call.message)

            elif call.data == "search_films":
                next_menu = types.InlineKeyboardMarkup()
                back = types.InlineKeyboardButton(text='Главное меню', callback_data='mainmenu')
                next_menu.add(back)
                bot.edit_message_text('Введи название фильма или сериала', call.message.chat.id, call.message.message_id,
                                    reply_markup=next_menu)
                input_is_allowed = True
                
            elif call.data == "list_films":
                next_menu2 = types.InlineKeyboardMarkup()
                back = types.InlineKeyboardButton(text='Главное меню', callback_data='mainmenu')
                next_menu2.add(back)
                bot.edit_message_text('кнопка пока не работает', call.message.chat.id, call.message.message_id,
                                    reply_markup=next_menu2)

            else:
                with open('log.txt', 'a+', encoding="utf8") as f:
                    local_time = time.strftime("%H:%M:%S %d.%m.%Y", time.localtime())
                    f.write(f'\n{local_time}\nFILM_ID: {call.data}\n')

                next_menu = types.InlineKeyboardMarkup()
                back = types.InlineKeyboardButton(text='Главное меню', callback_data='mainmenu')
                next_menu.add(back)

                film = kinopoisk.get_film(call.data)
                money = kinopoisk.money(call.data)

                if film.type == 'Сериал':
                    film.type += '\nСезонов: ' + kinopoisk.seasonsCount(call.data)

                output = f'''<a href="{film.webUrl}">{film.name} ({film.year})</a> 
                \n{film.type}
                \n{film.countries}
                \n<b>{film.rating}</b> \n{film.ratingVoteCount} оценок
                \n<b>Бюджет:</b> {money[0]} \n<b>Сборы в мире:</b> {money[1]}
                \n<b>В главных ролях:</b> \n{kinopoisk.staff(call.data)}
                \n{film.description}'''

                bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id+1)
                bot.send_photo(call.message.chat.id, film.posterUrl, caption=output, reply_markup=next_menu, parse_mode="HTML")

    except Exception as e:
        bot.send_message(call.message.chat.id, 'Возникли проблемы'.format(repr(e)))
        with open('log.txt', 'a+', encoding="utf8") as f:
            local_time = time.strftime("%H:%M:%S %d.%m.%Y", time.localtime())
            f.write(f'\n{local_time}\n{repr(e)}') 
# RUN
bot.polling(none_stop=True)