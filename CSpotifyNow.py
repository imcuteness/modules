#    _____ _    _ _______ ______ _   _ ______  _____ _____        
#   / ____| |  | |__   __|  ____| \ | |  ____|/ ____/ ____|       
#  | |    | |  | |  | |  | |__  |  \| | |__  | (___| (___         
#  | |    | |  | |  | |  |  __| | . ` |  __|  \___ \\___ \        
#  | |____| |__| |  | |  | |____| |\  | |____ ____) |___) |       
#   \_____|\____/_  |_| _|______|_|_\_|______|_____/_____/ ______ 
#   / ____|/ __ \ \    / / \ | |/ __ \ / ____/ __ \|  __ \|  ____|
#  | |  __| |  | \ \  / /|  \| | |  | | |   | |  | | |  | | |__   
#  | | |_ | |  | |\ \/ / | . ` | |  | | |   | |  | | |  | |  __|  
#  | |__| | |__| | \  /  | |\  | |__| | |___| |__| | |__| | |____ 
#   \_____|\____/   \/   |_| \_|\____/ \_____\____/|_____/|______|
#    
#meta developer: @im_cuteness

import asyncio
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from telethon import events
from .. import loader, utils

class CSpotifyNow(loader.Module):
    """Динмаическое обновление прослушиваемой песни в спотифае."""

    strings = {
        "name": "CSpotifyNow",
        "need_auth": "🚫 Сначала используй `.csauth` для входа в Spotify.",
        "auth": "🔐 <a href='{}'>Авторизуйся здесь</a>, затем используй `.cscode <URL>` с полученной ссылкой.",
        "authed": "✅ Авторизация успешна!",
        "error": "❌ Ошибка: {}",
        "waiting": "🎵 Ожидание данных из Spotify...",
        "playing": "<emoji document_id=5379631616970726681>🎵</emoji> <b>SpotifyNow</b> <b>by cuteness</b>\n<emoji document_id=5891249688933305846>🎵</emoji> Сейчас играет: <b>{}</b>",
        "no_music": "<b><emoji document_id=5379631616970726681>🎵</emoji> SpotifyNow by cuteness</b>\n<b><emoji document_id=5026027728290185861>😌</emoji> Музыка не играет.</b>",
        "stopped": "⏹ Мониторинг Spotify остановлен."
    }

    def __init__(self):
        self.running = False
        self.sp = None
        self.msg_id = None
        self.chat_id = None
        self.auth_manager = SpotifyOAuth(
            client_id="45282ddda62b496c9f0fe3e5fbeb2e20",
            client_secret="b8aaf932a6dc4e658824025bdc6102ed",
            redirect_uri="https://imcuteness.github.io/spotifynow/",
            scope="user-read-currently-playing user-read-playback-state",
            cache_path=".spotify_cache"
        )

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        try:
            self.sp = spotipy.Spotify(auth_manager=self.auth_manager)
        except Exception:
            self.sp = None

    async def csauthcmd(self, message):
        """Первый этап авторизации"""

        auth_url = self.auth_manager.get_authorize_url()
        await utils.answer(message, self.strings("auth").format(auth_url))

    async def scodecmd(self, message):
        """Второй этап авторизации (введи ссылку после авторизации)"""
        args = utils.get_args_raw(message)
        if not args:
            await message.reply("🚫 Введи ссылку после авторизации!")
            return

        try:
            code = self.auth_manager.parse_auth_response_url(args)
            self.auth_manager.get_access_token(code, as_dict=False)
            self.sp = spotipy.Spotify(auth_manager=self.auth_manager)
            await utils.answer (message, self.strings("authed"))
        except Exception as e:
            await utils.answer(message, self.strings("error").format(e))

    async def csnowcmd(self, message):
        """Запускает динамическое обновление прослушиваемой музыки"""
        if self.running:
            await utils.answer(message, "🔄 Мониторинг уже запущен!")
            return

        if not self.sp:
            await utils.answer(message, self.strings("need_auth"))
            return

        msg = await utils.answer(message, self.strings("waiting"))
        self.msg_id = msg.id
        self.chat_id = msg.chat_id
        self.running = True

        asyncio.create_task(self.update_spotify_status())

    async def update_spotify_status(self):
        last_track = None

        while self.running:
            try:
                track = self.get_current_track()
                if track and track != last_track:
                    last_track = track
                    await self.client.edit_message(self.chat_id, self.msg_id, self.strings("playing").format(track))
                elif not track:
                    await self.client.edit_message(self.chat_id, self.msg_id, self.strings("no_music"))
            except Exception as e:
                print(f"⚠ Ошибка в обновлении Spotify: {e}")
                await asyncio.sleep(10)

            await asyncio.sleep(1)

    def get_current_track(self):
        if not self.sp:
            return None
        try:
            track = self.sp.currently_playing()
            if track and track["is_playing"]:
                artist = track["item"]["artists"][0]["name"]
                title = track["item"]["name"]
                return f"{artist} - {title}"
        except Exception:
            return None

    async def cstopcmd(self, message):
        """Останавливает обновление"""
        self.running = False
        await utils.answer(message, self.strings("stopped"))
