import telebot;
import os
import youtube_dl
from decouple import config

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


bot = telebot.TeleBot(config('bot_token'));


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
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
        result = ydl.extract_info(message.text, download=False)
    name = result['title']
    video_path = MEDIA_ROOT +"/" + name + ".mp3"
    video = open(video_path, 'rb')
    bot.send_video(message.from_user.id, video)
    bot.send_video(message.from_user.id, "FILEID")


bot.polling(none_stop=True, interval=0)