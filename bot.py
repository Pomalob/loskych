import discord
from discord.ext import commands, tasks
from config import DISCORD_TOKEN, YOUTUBE_API_KEY, TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET, YOUTUBE_CHANNEL_ID1, YOUTUBE_CHANNEL_ID2, DISCORD_CHANNEL_LINKS_ID
from youtube import get_youtube_service
from twitch import get_twitch_client
from links import TWITCH_LINK, TIKTOK_LINK, YOUTUBE_LINK, CUTTINGYT_LINK, TGK_SUB_LINK, TGK_SERVER_LINK, TGK_MAIN_LINK

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Инициализация YouTube и Twitch клиентов
youtube = get_youtube_service(YOUTUBE_API_KEY)
twitch = get_twitch_client(TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET)

@bot.event
async def on_ready():
    print(f'Бот {bot.user} запущен!')

    # Запуск всех фоновых задач
    check_new_video1.start()
    print('Задача по оповещениям основного канала запущена')
    check_new_video2.start()
    print('Задача по оповещениям нарезок запущена')
    check_and_notify.start()
    print('Задача по оповещениям о начале стрима запущена')


#-------------------------------Discord----------------------------------------
# Команда для вывода всех медийных ссылок
@bot.command()
async def links(ctx):
    message_TW = f"Ссылка на Twitch канал: {TWITCH_LINK}"
    await ctx.send(message_TW)
    message_YT = f"Ссылка на YouTube канал: {YOUTUBE_LINK}"
    await ctx.send(message_YT)
    message_YTC = f"Ссылка на канал с нарезками: {CUTTINGYT_LINK}"
    await ctx.send(message_YTC)
    message_TT = f"Ссылка на TikTok: {TIKTOK_LINK}"
    await ctx.send(message_TT)

# Команда для вывода ТГК каналов
@bot.command()
async def tg(ctx):
    message_TGKM = f"Ссылка на основной ТГК: {TGK_MAIN_LINK}"
    await ctx.send(message_TGKM)
    message_TGKSUB = f"Ссылка на Sub-chat: {TGK_SUB_LINK}"
    await ctx.send(message_TGKSUB)

# Команда на случайное число от 1 до n
import random
@bot.command()
async def rand(ctx, max_n: int):
    number = random.randint(0, max_n)
    await ctx.send(f"Выпавшее число от 1 до {max_n}:\n{number}")

# Приветствие новых участников и выдача начальной роли
ROLE_NAME = "Pecus"
#ROLE_NAME = "Noobik"
@bot.event
async def on_member_join(member):
    message = f"Привет {member.mention}, рады приветствовать на нашем сервере кубики лоскича!"
    channel = discord.utils.get(member.guild.text_channels, name="основной")
    # channel = discord.utils.get(member.guild.text_channels, name="╔🫣▸pr-vsem-pr")
    await channel.send(message)
    role = discord.utils.get(member.guild.roles, name=ROLE_NAME)
    await member.add_roles(role)

# Команда про maincraft
@bot.command()
async def server(ctx):
    message_TGKS = f"Сервер для подпищиков на Forge 1.20.1\nСтилистика: Frostpunk и RP\nКрупные моды: Create, TC, IE\nСсылка на ТГК сервера: {TGK_SERVER_LINK}"
    await ctx.send(message_TGKS)

@bot.command()
async def helps(ctx):
    message_ALL = f"Все доступные команды:\n!links - ссылки на YT, TW, TT\n!tg - ссылки на все ТГК\n!server - Информация о Sub-сервере\n!rand x - Случайное число до x"
    await ctx.send(message_ALL)

#-------------------------------YouTube----------------------------------------
# Переменные для хранения последнего ID видео
last_video_id1 = None
last_video_id2 = None

# Функция для получения последнего видео на канале
def get_latest_video(a):
    if a == 1:
        try:
            request = youtube.search().list(
                channelId = YOUTUBE_CHANNEL_ID1,
                part = 'snippet',
                order = 'date',
                maxResults = 1,
                type = 'video'
            )
            response = request.execute()
            #print("Ответ от YouTube API:", response)  # Отладочный вывод
            if response['items']:
                item = response['items'][0]
                if item['id']['kind'] == 'youtube#video':  # Проверяем, что это видео
                    return item
            return None
        except Exception as e:
            print(f"Ошибка при запросе к YouTube API: {e}")
            return None
    elif a == 2:
        try:
            request = youtube.search().list(
                channelId = YOUTUBE_CHANNEL_ID2,
                part = 'snippet',
                order = 'date',
                maxResults = 1,
                type = 'video'
            )
            response = request.execute()
            # print("Ответ от YouTube API:", response)  # Отладочный вывод
            if response['items']:
                item = response['items'][0]
                if item['id']['kind'] == 'youtube#video':  # Проверяем, что это видео
                    return item
            return None
        except Exception as e:
            print(f"Ошибка при запросе к YouTube API: {e}")
            return None

# Первый таск на выход видео на основном канале
@tasks.loop(minutes=5)
async def check_new_video1():
    try:
        # print("Проверка новых видео...")
        global last_video_id1

        latest_video = get_latest_video(1)
        if latest_video:
            # print(f"Найдено видео: {latest_video['snippet']['title']}")
            video_id = latest_video['id']['videoId']
            if video_id != last_video_id1:
                last_video_id1 = video_id

                video_title = latest_video['snippet']['title']
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                message = f"**Новое видео на канале loskych!**\n{video_title}\n{video_url}"

                channel = bot.get_channel(DISCORD_CHANNEL_LINKS_ID)
                if channel:
                    # print(f"Отправка сообщения в канал {DISCORD_CHANNEL_LINKS_ID}...")
                    await channel.send(message)
                #else:
                    # print(f"Канал с ID {DISCORD_CHANNEL_LINKS_ID} не найден.")
    except Exception as e:
        print(f"Ошибка в фоновой задаче: {e}")

# Второй таск на выход нарезок
@tasks.loop(minutes=5)
async def check_new_video2():
    try:
        # print("Проверка новых видео...")
        global last_video_id2

        latest_video = get_latest_video(2)
        if latest_video:
            # print(f"Найдено видео: {latest_video['snippet']['title']}")
            video_id = latest_video['id']['videoId']
            if video_id != last_video_id2:
                last_video_id2 = video_id

                video_title = latest_video['snippet']['title']
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                message = f"**Новое видео на канале нарезок!**\n{video_title}\n{video_url}"

                channel = bot.get_channel(DISCORD_CHANNEL_LINKS_ID)
                if channel:
                    # print(f"Отправка сообщения в канал {DISCORD_CHANNEL_LINKS_ID}...")
                    await channel.send(message)
                #else:
                    # print(f"Канал с ID {DISCORD_CHANNEL_LINKS_ID} не найден.")
    except Exception as e:
        print(f"Ошибка в фоновой задаче: {e}")

#-------------------------------Twitch----------------------------------------

import requests
# Получение OAuth токена для Twitch
def get_twitch_oauth_token():
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    response = requests.post(url, params=params)
    data = response.json()
    return data['access_token']
# Проверка, активен ли стрим на Twitch
def check_stream_status(oauth_token):
    url = f"https://api.twitch.tv/helix/streams?user_login=sclkoma"
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {oauth_token}"
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    if data['data']:
        stream_info = data['data'][0]
        # print(f"Стрим начался: {stream_info['title']}")
        return True, stream_info['title']
    else:
        # print(f"Стрим не активен.")
        return False, None
# Отправка сообщения в Discord
async def send_discord_notification(channel_id):
    channel = bot.get_channel(channel_id)
    if channel:
        await channel.send(f"Стрим начался на Twitch! Ссылка: {TWITCH_LINK}")
        # print(f"Сообщение отправлено в Discord канал: {channel_id}")
    else:
        print(f"Канал с ID {channel_id} не найден!")
# Главная функция проверки и оповещения
status = False
@tasks.loop(minutes=1)
async def check_and_notify():
    global status
    oauth_token = get_twitch_oauth_token()
    stream_active, stream_title = check_stream_status(oauth_token)

    if stream_active and status == False:
        status = True
        channel = DISCORD_CHANNEL_LINKS_ID
        await send_discord_notification(channel)
    elif stream_active == 0:
        status = False

bot.run(DISCORD_TOKEN)