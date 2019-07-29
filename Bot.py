import os
import re

import youtube_dl
from decouple import config
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from slugify import slugify
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

TOKEN = config('TOKEN')
updater = Updater(token=TOKEN, request_kwargs={'read_timeout': 1000, 'connect_timeout': 1000})
dispatcher = updater.dispatcher

media_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media')


def download_convert(url, download):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'media/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        if download:
            ydl.download([url])
        else:
            result = ydl.extract_info(url, download=False)
            duration = result['duration']
            name = result['title'].replace('?', '').replace('"', '\'')
            return duration, name


def cut_audio(name, start_time, end_time):
    audio_input = media_dir + '/' + name + '.mp3'
    audio_output = media_dir + '/' + slugify(name) + '-Cut.mp3'

    ffmpeg_extract_subclip(audio_input, start_time, end_time, targetname=audio_output)
    audio = open(audio_output, 'rb')
    os.remove(audio_input)
    return audio, audio_output


def get_interval(timeline):
    interval = timeline.split('-')
    _from = interval[0].split(':')
    _to = interval[1].split(':')
    if len(_from) == 3:
        start_time = ((int(_from[0]) * 60) + int(_from[1])) * 60 + int(_from[2])
        end_time = ((int(_to[0]) * 60) + int(_to[1])) * 60 + int(_to[2])
    else:
        start_time = (int(_from[0]) * 60) + int(_from[1])
        end_time = (int(_to[0]) * 60) + int(_to[1])

    if end_time < start_time:
        current = start_time
        start_time = end_time
        end_time = current
    return start_time, end_time


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
    regex_timeline = re.sub(r'(([0-5][0-9]|[0-9]):[0-5][0-9])-(([0-5][0-9]|[0-9]):[0-5][0-9])'
                            r'(([0-9][0-9]|[0-9]):([0-5][0-9]|[0-9]):[0-5][0-9])-(([0-9][0-9]|[0-9]):([0-5][0-9]|[0-9]):[0-5][0-9])')

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
                start_time, end_time = get_interval(timeline)
                duration, name = download_convert(url, download=False)

                if end_time > duration:
                    bot.send_message(chat_id=update.message.chat_id, text='Выбранный промежуток длиннее чем видео')
                else:
                    # Скачивание видео и конвертирование
                    bot.send_message(chat_id=update.message.chat_id, text='Скачивание видео...')
                    download_convert(url, download=True)
                    bot.send_message(chat_id=update.message.chat_id, text='Конвертирование и обрезка...')

                    # Вырезание отрезка из аудио
                    audio, audio_output = cut_audio(name, start_time, end_time)
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
