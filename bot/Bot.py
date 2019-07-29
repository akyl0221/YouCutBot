import re
import os
from decouple import config
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from .tasks import download_convert, cut_audio


TOKEN = config('TOKEN')
updater = Updater(token=TOKEN, request_kwargs={'read_timeout': 1000, 'connect_timeout': 1000})
dispatcher = updater.dispatcher


def startCommand(bot, update):
    text = 'Привет, я YouCut бот который вырежет для тебя видео и сконвертирует его в аудио\n' \
           'Инструкция:\n' \
           '1) Вставьте ссылку с YouTube видео и напишите промежуток\n ' \
           'который вам надо вырезать (формат 00:00-00:00 минуты секунды) \n' \
           '2) Подождите несколько минут \n' \
           'Пример: \n' \
           'https://www.youtube.com/watch?v=UYwF-jdcVjY 02:10-03:05\n' \
           'Помощь: /help'
    bot.send_message(chat_id=update.message.chat_id, text=text)


def videoMessage(bot, update):
    text = update.message.text.split()
    regex_url = re.compile(r'^(http(s)?:\/\/)?((w){3}.)?(m.youtu(be|.be))?(youtu(be|.be))?(\.com)?\/.+')
    regex_timeline = re.compile(r'((([0-5][0-9]|[0-9]):[0-5][0-9])-(([0-5][0-9]|[0-9]):[0-5][0-9]))|((([0-9][0-9]|[0-9]):([0-5][0-9]|[0-9]):[0-5][0-9])-(([0-9][0-9]|[0-9]):([0-5][0-9]|[0-9]):[0-5][0-9]))')

    if (len(text) == 1):
        bot.send_message(chat_id=update.message.chat_id, text='Неправильный ввод. '
                                                              'Пожалуйста введите ссылку '
                                                              'Youtube и временной промежуток')

    else:
        bot.send_message(chat_id=update.message.chat_id, text='Проверка введенных данных...')
        url = ''
        timeline = ''
        for i in text:
            if (re.match(regex_url, i) is not None):
                url = i
            if (re.match(regex_timeline, i) is not None):
                timeline = i

        if url != '':
            if timeline != '':
                # Определение начала и конца отрезка
                start_time, end_time, duration, name = download_convert.delay(url, download=False, timeline=timeline)

                if end_time > duration:
                    bot.send_message(chat_id=update.message.chat_id, text='Выбранный промежуток длиннее чем видео')
                else:
                    # Скачивание видео и конвертирование
                    bot.send_message(chat_id=update.message.chat_id, text='Скачивание видео...')
                    download_convert.delay(url, download=True)
                    bot.send_message(chat_id=update.message.chat_id, text='Конвертирование и обрезка...')

                    # Вырезание отрезка из аудио
                    audio, audio_output = cut_audio.delay(name, start_time, end_time)
                    bot.send_message(chat_id=update.message.chat_id, text='Отправка аудио...')
                    bot.send_audio(chat_id=update.message.chat_id, audio=audio)
                    os.remove(audio_output)
            else:
                bot.send_message(chat_id=update.message.chat_id, text='Пожалуйста введите промежуток вместе с адресом')
        else:
            bot.send_message(chat_id=update.message.chat_id, text='Неправильный адресс это не Youtube')


def helpCommand(bot, update):
    text = 'Инструкция:\n' \
           '1) Вставьте ссылку с YouTube видео и напишите промежуток ' \
           'который вам надо вырезать (формат 00:00-00:00 минуты секунды) \n' \
           '2) Подождите несколько минут \n' \
           'Пример: \n' \
           'https://www.youtube.com/watch?v=UYwF-jdcVjY 02:10-03:05'
    bot.send_message(chat_id=update.message.chat_id, text=text)


start_command_handler = CommandHandler('start', startCommand)
help_command_handler = CommandHandler('help', helpCommand)
video_message_handler = MessageHandler(Filters.text, videoMessage)

dispatcher.add_handler(start_command_handler)
dispatcher.add_handler(help_command_handler)
dispatcher.add_handler(video_message_handler)

updater.start_polling(clean=True)

updater.idle()
