from celery import Celery
from slugify import slugify
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import youtube_dl
import os
import re

app = Celery('tasks', broker='redis://localhost//',include=['bot.tasks'])

media_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media')


@app.task
def videoConverter(bot, update):
    text = update.message.text.split()
    regex_url = re.compile(r'^(http(s)?:\/\/)?((w){3}.)?(m.youtu(be|.be))?(youtu(be|.be))?(\.com)?\/.+')
    regex_timeline = re.compile(
        r'((([0-5][0-9]|[0-9]):[0-5][0-9])-(([0-5][0-9]|[0-9]):[0-5][0-9]))|((([0-9][0-9]|[0-9]):([0-5][0-9]|[0-9]):[0-5][0-9])-(([0-9][0-9]|[0-9]):([0-5][0-9]|[0-9]):[0-5][0-9]))')

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
                start_time, end_time, duration, name = download_convert(url, download=False, timeline=timeline)

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


def download_convert(url, download, timeline=0):
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
            start_time, end_time = get_interval(timeline)
            return start_time, end_time, duration, name


def cut_audio(name, start_time, end_time):
    files = os.listdir(media_dir)
    for file in files:
        for part in name.split():
            print(part)
            if part in name:
                audio_input = media_dir + '/' + file
                break
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
