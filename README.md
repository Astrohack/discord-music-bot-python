# Discord Music Bot

Welcome to the Discord Music Bot repository! This bot allows you to search for music and play radio stations directly in your Discord server.

## Features

- **Music Search**: Search for your favorite tracks and play them.
- **Music Queue**: Add multilple songs to queue.
- **Radio Streaming**: Play live radio stations directly in your Discord voice channels.

## Prerequisites

Before you can run the bot, you need to have the following installed:

- [Python 3.8+](https://www.python.org/downloads/)
- [FFmpeg](https://ffmpeg.org/download.html) - Download FFmpeg and place the executable in the root directory of the application.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/Astrohack/discord-music-bot-python
    cd discord-music-bot-python
    ```

2. Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

3. Download [FFmpeg](https://ffmpeg.org/download.html) and place the executable in the root directory of the application.

## Configuration

1. Create a `.env` file in the root directory of the application and add your Discord bot token:

    ```env
    DISCORD_TOKEN=your_discord_bot_token_here
    VCCHANEL_ID=your_voice_channel_id
    GUILD_ID=your_guild_id_for_command_sync
    RADIO_API_URL=your_radio_stream_url
    FFMPEG=location_of_your_ffmpeg_file
    ```

## Usage

To start the bot, run:

```bash
python discord_music_player.py
```
