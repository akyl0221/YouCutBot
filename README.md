<h1>YouCutBot<h1/>
<h2>YouCutBot this bot convert and cut Youtube videos<h2/>
<h2>Requirements<h2/>
<p>Python v 3.6 <p/>
<p>Youtube-dl v 2019.7.16<p/>
<p>ffmpeg	v 1.4 <p/>
<p>ffprobe	0.5	<p/>
<p>python-decouple	3.1 <p/>
<p>python-telegram-bot	11.1.0<p/>


<h2>Install<h2/>
<p>Find in telegram @BotFather<p/>
<p>Use the /newbot command to create a new bot. The BotFather will ask you for a name and username, then generate an authorization token for your new bot.

The name of your bot is displayed in contact details and elsewhere.

The Username is a short name, to be used in mentions and telegram.me links. Usernames are 5-32 characters long and are case insensitive, but may only include Latin characters, numbers, and underscores. Your bot's username must end in ‘bot’, e.g. ‘tetris_bot’ or ‘TetrisBot’.

The token is a string along the lines of 110201543:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw that is required to authorize the bot and send requests to the Bot API. Keep your token secure and store it safely, it can be used by anyone to control your bot.
For another information see https://core.telegram.org/bots#creating-a-new-bot
<p/>
<p>git clone https://github.com/akyl0221/YouCutBot.git<p/>
<p>pip install virtualenv<p/>
<p>python3 -m venv env<p/>
<p>source env/bin/activate<p/>
<p>pip install youtube-dl<p/>
<p>pip install ffmpeg<p/>
<p>pip install ffprobe<p/>
<p>pip install python-decouple<p/>
<p>pip install python-telegram-bot<p/>
<p>cd YouCutBot
 Create file .env and add 
    TOKEN = Your TOKEN
<p/>
<p>python Bot.py<p/>
