from bot import server #Импорт сервера Flack
from bot import bot # Импортируем объект бота
from messages import * # Инмпортируем все с файла сообщений
import random
import utils
from SQLighter import SQLighter
from telebot import types
import config


@bot.message_handler(commands=['game'])
def game(message):
    # Подключаемся к БД
    db_worker = SQLighter(config.database_name)
    # Получаем случайную строку из БД
    row = db_worker.select_single(random.randint(1, utils.get_rows_count()))
    # Формируем разметку
    markup = utils.generate_markup(row[2], row[3])

    # Отправляем аудиофайл с вариантами ответа
    bot.send_voice(message.chat.id, row[1], reply_markup=markup, duration=20)
    # Включаем "игровой режим"
    utils.set_user_game(message.chat.id, row[2])
    # Отсоединяемся от БД
    db_worker.close()


@bot.message_handler(func=lambda message: True, content_types=['text'])
def check_answer(message):
    markup2 = types.ReplyKeyboardMarkup()
    markup2.add('/game')
    # Если функция возвращает None -> Человек не в игре
    answer = utils.get_answer_for_user(message.chat.id)
    # Как Вы помните, answer может быть либо текст, либо None
    # Если None:
    if not answer:
        bot.send_message(message.chat.id, 'Чтобы начать игру, выберите команду /game')
    else:
        # Уберем клавиатуру с вариантами ответа.
        keyboard_hider = types.ReplyKeyboardRemove()
        # Если ответ правильный/неправильный
        if message.text == answer:
            bot.send_message(message.chat.id, 'Верно!', reply_markup=keyboard_hider)
        else:
            bot.send_message(message.chat.id, 'Увы, Вы не угадали. Попробуйте ещё раз!', reply_markup=keyboard_hider)
            bot.send_message(message.chat.id, 'Чтобы начать новую игру, выберите команду /game', reply_markup=markup2)
        # Удаляем юзера из хранилища (игра закончена)
        utils.finish_user_game(message.chat.id)

@bot.message_handler(commands=['start']) # Выполняется, когда пользователь нажимает на start
def send_welcome(message):
    bot.send_message(message.chat.id, HELLO_MESSAGE)


@bot.message_handler(content_types=["text"]) # Любой текст
def repeat_all_messages(message):
    bot.send_message(message.chat.id, message.text)

if __name__ == '__main__':
    utils.count_rows()
    random.seed()
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))