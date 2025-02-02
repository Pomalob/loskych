# twitch.py

from twitchAPI.twitch import Twitch

def get_twitch_client(client_id, client_secret):
    return Twitch(client_id, client_secret)
