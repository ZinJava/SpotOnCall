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

@bot.event
async def on_ready(): #runs when bot starts
    print(f'Logged in as {bot.user}')
    try:
        synced = bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)

sp = spotipy.Spotify(auth_manager=SpotifyOAuth( #connect to Spotify API
    client_id=os.getenv('SPOTIFY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
    redirect_uri='https://spotify.com',
    scope="user-read-currently-playing"
))

def get_current_track():
    song = sp.current_user_playing_track()
    if song is None or not song.get('is_playing'): #if no song playing, return None
        return None

    item = song['item']
    title = item['name']
    artist = item['artists'][0]['name']
    album = item['album']['name']
    url = item['external_urls']['spotify']
    album_art = item['album']['images'][0]['url']
    duration_ms = item['duration_ms']
    minutes = duration_ms // 60000
    seconds = (duration_ms % 60000) // 1000
    duration = f"{minutes}:{seconds:02d}"

    #return dictionary(key:value)
    return {
        "title": title,
        "artist": artist,
        "album": album,
        "url": url,
        "album_art": album_art,
        "duration": duration
    }

@bot.tree.command(name="nowplaying", description="Show the current playing Spotify track")
async def nowplaying(interaction: discord.Interaction):
    await interaction.response.defer()
    song_info = get_current_track()
    
    if not song_info:
        await interaction.followup.send("No song is currently playing")
        return
    
    embed = discord.Embed(
        title="Now Playing",
        description=f"[{song_info['title']}]({song_info['url']})",
        color=discord.Color.purple()
    )
    embed.set_author(name=song_info['artist'])
    embed.set_thumbnail(url=song_info['album_art'])
    embed.add_field(name="Album", value=song_info['album'], inline=True)
    embed.add_field(name="Duration", value=song_info['duration'], inline=True)

    await interaction.followup.send(embed=embed)

bot.run(os.getenv('DISCORD_BOT_SECRET'))