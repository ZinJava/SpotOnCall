import os
import asyncio

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
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)

sp = spotipy.Spotify(auth_manager=SpotifyOAuth( #connect to Spotify API
    client_id=os.getenv('SPOTIFY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
    redirect_uri='https://spotify.com',
    scope="user-read-currently-playing user-modify-playback-state user-read-playback-state"
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

# class View(discord.ui.View):
#     @discord.ui.button(label="Play/Pause", style=discord.ButtonStyle.green, emoji="⏯️")
#     async def button_play_pause(self, interaction: discord.Interaction, button):
#         playback = sp.current_playback()
#         if playback and playback['is_playing']:
#             sp.pause_playback()
#             await interaction.response.send_message("Paused", ephemeral=True) #ephemeral shows only to person interacting
#         else:
#             sp.start_playback()
#             await interaction.response.send_message("Playing", ephemeral=True)

#     @discord.ui.button(label="Skip", style=discord.ButtonStyle.green, emoji="⏭️")
#     async def button_skip(self, interaction: discord.Interaction, button):
#         playback = sp.current_playback()
#         if not playback or not playback.get("device") or not playback["device"].get("is_active"):
#             await interaction.response.send_message("No device found", ephemeral=True)
#             return

#         sp.next_track()
#         await interaction.response.send_message("Skip", )
#     @discord.ui.button(label="Rewind", style=discord.ButtonStyle.green, emoji="⏮️")
#     async def button_rewind(self, interaction: discord.Interaction, button):
#         sp.previous_track()
#         await self.new_embed(interaction)

#     async def new_embed(self, interaction: discord.Interaction):
#         track = sp.current_playback()
#         if not track or not track.get("item"):
#             new_embed = discord.Embed(title="Nothing is playing", color=discord.Color.red())
#         else:
#             item = track["item"]
#             title = item["name"]
#             artist = ", ".join([a["name"] for a in item["artists"]])
#             album = item["album"]["name"]
#             url = item["external_urls"]["spotify"]
#             art = item["album"]["images"][0]["url"]
#             duration_ms = item["duration_ms"]
#             duration = f"{duration_ms // 60000}:{(duration_ms // 1000) % 60:02d}"

#             new_embed = discord.Embed(title=title, description=artist, url=url, color=discord.Color.green())
#             new_embed.set_thumbnail(url=art)
#             new_embed.add_field(name="Album", value=album, inline=True)
#             new_embed.add_field(name="Duration", value=duration, inline=True)

#         await interaction.response.edit_message(embed=new_embed)

#----------------------------------Commands----------------------------------

@bot.tree.command(name="nowplaying", description="Show current track")
async def nowplaying(interaction: discord.Interaction):
    await interaction.response.defer()
    track = get_current_track()
    
    if not track:
        await interaction.followup.send("No song is currently playing")
        return
    
    embed = discord.Embed(
        title="Now Playing",
        description=track["title"],
        color=discord.Color.purple()
    )
    embed.set_author(name=track['artist'])
    embed.set_thumbnail(url=track['album_art'])
    embed.add_field(name="Album", value=track['album'], inline=True)
    embed.add_field(name="Duration", value=track['duration'], inline=True)

    await interaction.followup.send(embed=embed)

@bot.tree.command(name="pause", description="Pause the song")
async def pause(interaction: discord.Interaction):
    await interaction.response.defer()
    sp.pause_playback()
    await interaction.followup.send("Paused current track", ephemeral=True)

@bot.tree.command(name="play", description="Play the song")
async def pause(interaction: discord.Interaction):
    await interaction.response.defer()
    sp.start_playback()
    await interaction.followup.send("Playing current track", ephemeral=True)

@bot.tree.command(name="skip", description="Skip current track")
async def skip(interaction: discord.Interaction):
    await interaction.response.defer()
    sp.next_track()
    track = get_current_track()

    embed = discord.Embed(
        title="Now Playing",
        description=track["title"],
        color=discord.Color.purple()
    )
    embed.set_author(name=track['artist'])
    embed.set_thumbnail(url=track['album_art'])
    embed.add_field(name="Album", value=track['album'], inline=True)
    embed.add_field(name="Duration", value=track['duration'], inline=True)

    await interaction.followup.send(embed=embed)

@bot.tree.command(name="rewind", description="Play previous track")
async def rewind(interaction: discord.Interaction):
    await interaction.response.defer()
    sp.previous_track()
    await asyncio.sleep(0.5)
    track = get_current_track()

    embed = discord.Embed(
        title="Now Playing",
        description=track["title"],
        color=discord.Color.purple()
    )
    embed.set_author(name=track['artist'])
    embed.set_thumbnail(url=track['album_art'])
    embed.add_field(name="Album", value=track['album'], inline=True)
    embed.add_field(name="Duration", value=track['duration'], inline=True)

    await interaction.followup.send(embed=embed)

bot.run(os.getenv('DISCORD_BOT_SECRET'))