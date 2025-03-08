__version__ = (1, 0, 0)

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
import aiohttp


async def get_creation_date(user_id: int) -> str:
    url = "https://restore-access.indream.app/regdate"
    headers = {
        "accept": "*/*",
        "content-type": "application/x-www-form-urlencoded",
        "user-agent": "Nicegram/92 CFNetwork/1390 Darwin/22.0.0",
        "x-api-key": "e758fb28-79be-4d1c-af6b-066633ded128",
        "accept-language": "en-US,en;q=0.9",
    }
    data = {"telegramId": user_id}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 200 and "data" in await response.json():
                return (await response.json())["data"]["date"]
            else:
                return "Ошибка получения данных"
    
@loader.tds
class UserInfoMod(loader.Module):
    """Sends info about the user."""
    strings = {
        "name": "UserInfo",
        "loading": "⏳ <b>Loading... Please wait.</b>",
        "no_args": "❌ <b>Usage: .userinfo &lt;id&gt; or reply to the message.</b>",
        "info": "👤 <b>User Information:</b>\n🆔 <b>ID:</b> <code>{id}</code>\n🌟 <b>First Name:</b> <code>{name}</code>\n💫 <b>Last Name:</b> <code>{last_name}</code>\n📆 <b>Account Creation Date:</b> <code>{date_of_creation}</code>\n🌍 <b>Data Center:</b> <code>{dc}</code> ({country})\n🤖 <b>Bot:</b> <code>{is_bot}</code>\n⚡️ <b>Premium:</b> <code>{is_premium}</code>",
        "unknown": "❌ <b>Unknown</b>",
        "true": "✅",
        "false": "❌",
        "usa": "USA",
        "europe": "Europe",
        "asia": "Asia",
        "anth": "Another country"
    }
    strings_ru = {
        "loading": "⏳ <b>Загрузка... Пожалуйста подождите.</b>",
        "no_args": "❌ <b>Использование: .userinfo &lt;айди&gt; или ответ на сообщение.</b>",
        "info": "👤 <b>Информация о пользователе:</b>\n🆔 <b>Айди:</b> <code>{id}</code>\n🌟 <b>Имя:</b> <code>{name}</code>\n💫 <b>Фамилия:</b> <code>{last_name}</code>\n📆 <b>Дата создания аккаунта:</b> <code>{date_of_creation}</code>\n🌍 <b>Датацентр:</b> <code>{dc}</code> ({country})\n🤖 <b>Бот:</b> <code>{is_bot}</code>\n⚡️ <b>Премиум:</b> <code>{is_premium}</code>",
        "unknown": "❌ <b>Неизвестно</b>",
        "true": "✅",
        "false": "❌",
        "usa": "США",
        "europe": "Европа",
        "asia": "Азия",
        "anth": "Другая страна"
    }
    
    async def client_ready(self, client, db):
        self._client = client

    async def userinfocmd(self, message):
        """Sends info about the user."""
        await utils.answer(message, self.strings["loading"])
        reply = await message.get_reply_message()
        
        if reply:
            user_id = reply.sender_id
        if not reply:
            args = utils.get_args_raw(message)
            if not args:
                await utils.answer(message, self.strings["no_args"])
                return
            try: 
                user_id = int(args)
            except ValueError:
                await utils.answer(message, self.strings["no_args"])
                return
        try:
            user_entity = await self._client.get_entity(user_id)
        except ValueError:
            await utils.answer(message, self.strings["no_args"])
            return
        
        id = user_id
        first_name = user_entity.first_name or self.strings["unknown"]
        last_name = user_entity.last_name or self.strings["false"]
        date_of_creation = await get_creation_date(user_id)
        dc = user_entity.photo.dc_id if user_entity.photo else self.strings["unknown"]
        countries = {
            1: self.strings["usa"],
            2: self.strings["europe"],
            3: self.strings["asia"],
            4: self.strings["anth"],
            5: self.strings["anth"],
        }
        country = countries.get(dc, self.strings["unknown"])
        is_bot = self.strings["true"] if user_entity.bot else self.strings["false"]
        is_premium = self.strings["true"] if user_entity.premium else self.strings["false"]
        
        info_message = self.strings["info"].format(
            id=id,
            name=first_name,
            last_name=last_name,
            date_of_creation=date_of_creation,
            dc=dc,
            country=country,
            is_bot=is_bot,
            is_premium=is_premium,
        )
        await utils.answer(message, info_message)