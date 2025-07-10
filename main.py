import os

import discord
from discord.ext import commands

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from dotenv import load_dotenv
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv('SPOTIFY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
    redirect_uri='https://spotify.com',
    scope="user-read-currently-playing"
))

def get_current_track():
    current = sp.current_user_playing_track()
    if current is None or not current.get('is_playing'):
        return "Nothing is currently playing."

    name = current['item']['name']
    artist = current['item']['artists'][0]['name']
    return f"{name} by {artist}"

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(e)

@bot.tree.command(name="nowplaying", description="Show the current Spotify track")
async def nowplaying(interaction: discord.Interaction):
    await interaction.response.defer()
    song_info = get_current_track()
    await interaction.followup.send(song_info)

bot.run(os.getenv('BOT_SECRET'))