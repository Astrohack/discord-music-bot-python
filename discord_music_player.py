import discord
import asyncio
from discord import app_commands
from yt_dlp import YoutubeDL
from discord.ui import Button, View, Select
from dotenv import load_dotenv
import os

load_dotenv()

# Bot token
TOKEN: str = os.environ.get("DISCORD_TOKEN", "")

FFMPEG: str = os.environ.get("FFMPEG", "")

# Voicechannel ID
VCCHANEL_ID: int = int(os.environ.get("VCCHANEL_ID", ""))

GUILD_ID: int = int(os.environ.get("GUILD_ID", ""))

# URL of an .m3u8 file aka radio stream
RADIO_API_URL = os.environ.get("RADIO_API_URL", "https://radio.stream.smcdn.pl/timeradio-p/3990-1.aac/playlist.m3u8")

# FFMPEG option for streaming 
FFMPEG_OPTIONS = {
        'before_options': ' -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 ',
        'options': ' -vn'
        }

YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'extractaudio': True,
    'audioformat': 'mp3',
    'outtmpl': '%(extractor)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0',
}

class Song:
    def __init__(self, url, name):
        self.url = url
        self.name = name

class Music(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.voice: discord.VoiceClient = None
        self.tree = app_commands.CommandTree(self)
        self.queue = list()
        self.mode = None
        self.currently_playing = None

    async def setup_hook(self):
        self.tree.copy_global_to(guild=discord.Object(id=GUILD_ID))
        print("Command sync started")
        await self.tree.sync()
        print("Command sync finished")


    async def join(self):
        if not self.voice:
            self.voice = await client.get_channel(VCCHANEL_ID).connect()

    async def search_for_songs(self, query):
        with YoutubeDL(YDL_OPTIONS) as ytdl:
            query = query if query.startswith('https://y') else f"ytsearch4:{query}"
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, lambda: ytdl.extract_info(query, download=False))
            return [Song(url=entry['url'],name=entry['title']) for entry in info['entries']]

    def add_to_queue(self, song: tuple):
        self.queue.append(song)

    def play_radio(self):
        if self.currently_playing or self.mode == "radio":
            self.voice.stop()
        self.mode = "radio"
        source = discord.FFmpegPCMAudio(RADIO_API_URL, **FFMPEG_OPTIONS, executable=FFMPEG)
        self.voice.play(source)

    def play_yt(self):
        if self.currently_playing:
            return
        if self.mode == "radio":
            self.voice.stop()
        if not self.queue:
            self.play_radio()
            return
        self.mode = "yt"
        self.currently_playing = self.queue.pop(0)
        source = discord.FFmpegPCMAudio(self.currently_playing.url, **FFMPEG_OPTIONS, executable=FFMPEG)
        self.voice.play(source, after=lambda e: self.on_track_end())

    def skip(self):
        if self.mode == "radio": return
        if self.mode == "yt":
            self.voice.stop()
            self.currently_playing = None
            self.play_yt()

    def on_track_end(self) -> None:
        self.voice.stop()
        self.currently_playing = None
        self.mode = None
        if not self.queue: self.play_radio()
        else: self.play_yt()

    async def selectSong(self, songs, interaction):
        if not songs: return
        if len(songs) == 1: return songs[0]
        select = Select(options=[discord.SelectOption(label=song.name, value=i) for i, song in enumerate(songs)])
        view = View().add_item(select)
        await interaction.edit_original_response(view=view)
        try:
            await client.wait_for('interaction', timeout=30)
            return songs[int(select.values[0])]
        except asyncio.TimeoutError:
            pass

client = Music()


@client.tree.command(name='play', description="Rozpocznij koncert")
async def play(interaction: discord.Interaction, query: str):
    await interaction.response.send_message("Teraz sobie chwilę poczekasz")
    songs = await client.search_for_songs(query)
    song = await client.selectSong(songs, interaction)
    if not song:
        return await interaction.edit_original_response(content=f'Nie znaleziono')
    client.add_to_queue(song)
    await interaction.edit_original_response(content=f'Do kolejki leci utwór: {song.name}', view=None)
    await client.join()
    client.play_yt()


@client.tree.command(name='skip', description="Pomiń to")
async def skip(interaction: discord.Interaction):
    client.skip()
    await interaction.response.defer()
    await interaction.delete_original_response()


@client.tree.command(name='radio', description="Brak pomysłów na piosenke? Posłuchaj radia.")
async def radio(interaction: discord.Interaction):
    await client.join()
    client.play_radio()
    await interaction.response.defer()
    await interaction.delete_original_response()



client.run(TOKEN)
