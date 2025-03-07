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
# meta developer: @cuteness_modules
from .. import loader, utils
from ..inline.types import InlineCall

@loader.tds
class WhisperMod(loader.Module):
    """Allows you to whisper to the user and no one else can read your message"""
    strings = {
        "name": "Whisper",
        "not_your": "It's not your message.",
        "your_message": "Your message: {args}",
        "no_reply": "Reply to a message to whisper to that user.",
        "no_text": "No text provided to whisper.",
        "user_not_found": "User not found.",
        "whisper": "🔒 <b>Whisper to {user}</b>\n\n<i>Click the button below to read the message</i>",
        "read": "Read the message"
    }
    strings_ru = {
        "not_your": "Это не ваше сообщение.",
        "your_message": "Ваше сообщение: {args}",
        "no_reply": "Ответьте на сообщение пользователя, которому хотите прошептать.",
        "no_text": "Не указан текст сообщения.",
        "user_not_found": "Пользователь не найден.",
        "whisper": "🔒 <b>Шепот для {user}</b>\n\n<i>Нажмите на кнопку ниже, чтобы прочитать сообщение</i>",
        "read": "Прочитать сообщение"
    }

    async def client_ready(self, client, db):
        self._client = client

    async def read(self, call: InlineCall, user_id: int, args: str):
        if call.from_user.id != user_id:
            await call.answer(self.strings["not_your"], show_alert=True)
            return
        await call.answer(self.strings["your_message"].format(args=args), show_alert=True)
        
    async def whispercmd(self, message):
        """Whispers to user"""
        args = utils.get_args_raw(message)
        
        if not args:
            await message.edit(self.strings["no_text"])
            return
            
        reply = await message.get_reply_message()
        if not reply:
            await message.edit(self.strings["no_reply"])
            return
            
        sender_id = message.sender_id
        sender = await self._client.get_entity(sender_id)
        sender_name = sender.first_name
        
        user_id = reply.sender_id
        fulluser = await self._client.get_entity(user_id)
        user = fulluser.first_name
        
        await self.inline.form(
            self.strings["whisper"].format(user=user),
            message=message,
            reply_markup=[[
                {
                    "text": self.strings[read],
                    "callback": self.read,
                    "args": (user_id, args),
                    "force_me": True,
                    "disable_security": True
                }
            ]]
        )

    @loader.inline_handler()
    async def whisper(self, event):
        """Inline whisper"""
        args = event.args.split(maxsplit=1)
        if len(args) < 2:
            return
            
        username, message = args
        username = username.replace("@", "")
        
        try:
            user = await self._client.get_entity(username)
            user_id = user.id
            first_name = user.first_name
            
            return [{
                "title": "🔒 Whisper",
                "description": f"Send whisper to {first_name}",
                "message": self.strings["inline_whisper"].format(user=first_name),
                "reply_markup": [[
                    {
                        "text": self.strings[read],
                        "callback": self.read,
                        "args": (user_id, message),
                        "force_me": True,
                        "disable_security": True
                    }
                ]]
            }]
        except Exception:
            return [{
                "title": "❌ Error",
                "description": Exception,
                "message": Exception
            }] 
