import os
import re
import youtube_dl

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from decouple import config

TOKEN = config('TOKEN')
updater = Updater(token=TOKEN, request_kwargs={'read_timeout': 1000, 'connect_timeout': 1000})
dispatcher = updater.dispatcher

media_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media')


def startCommand(bot, update):
    text = 'Бот работает просто:\n' \
           '1) Вставьте ссылку с YouTube видео и напишите промежуток\n ' \
           'который вам надо вырезать (формат 00:00-00:00 минуты секунды) \n' \
           '2) Подождите несколько минут \n' \
           'Пример: \n' \
           'https://www.youtube.com/watch?v=UYwF-jdcVjY 02:10-03:05\n'
    bot.send_message(chat_id=update.message.chat_id, text='Привет, я YouCut бот который вырежет для тебя видео\n'
                     + text + 'Помощь: /help')


def videoMessage(bot, update):
    text = update.message.text.split()
    if (len(text) == 1):
        bot.send_message(chat_id=update.message.chat_id, text="Wrong")
    else:
        url = text[0]
        regex = re.compile(r'^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+$')
        if (re.match(regex, url) is not None):
            interval = text[1].split('-')
            _from = interval[0].split(':')
            _to = interval[1].split(':')
            start_time = (int(_from[0]) * 60) + int(_from[1])
            end_time = (int(_to[0]) * 60) + int(_to[1])

            ydl_opts = {
                'format': 'best',
                'outtmpl': 'media/%(title)s.%(ext)s'
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                result = ydl.extract_info(url, download=True)

            name = result['title']
            video_input = media_dir + '/' + name + '.mp4'
            video_output = media_dir + '/' + name + "-Cut.mp4"
            ffmpeg_extract_subclip(video_input, start_time, end_time, targetname=video_output)
            video = open(video_output, 'rb')
            bot.send_video(chat_id=update.message.chat_id, video=video, supports_streaming=True)
        else:
            bot.send_message(chat_id=update.message.chat_id, text='Wrong url it is not Youtube')


def helpCommand(bot, update):
    text = 'Бот работает просто:\n' \
           '1) Вставьте ссылку с YouTube видео и напишите промежуток\n ' \
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

