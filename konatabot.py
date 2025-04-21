# ПОЛОВИНА КОДА МОЖЕТ БЫТЬ СПИЗЖЕНА, ИБО Я НЕ СОБИРАЮСЬ РАСПРОСТРАНЯТЬ ЭТОТ МОДУЛЬ, ЕСЛИ ОН КАКИМ-ТО ОБРАЗОМ ПОПАДЕТ В ЧУЖИЕ РУКИ - ЭТО НЕ МОЯ ВИНА!!! ИЗВИНИТЕ Я ГОВНОКОДЕР!!!

from telethon.tl.types import MessageService, MessageActionChatAddUser
from .. import loader, utils
from ..inline.types import InlineCall
import random as r
import time as t
import requests
from typing import Dict
import json
import aiohttp
import asyncio

@loader.tds
class KonataBotMod(loader.Module):
    """Коната-Бот!"""

    strings = {"name": "KonataBot"}


    async def client_ready(self, client, db):
        self._client = client
        self._db = db
        self.db.get("KonataBot", "stars", {}) # дб для звезд
        self.db.get("KonataBot", "timers", {}) # дб для таймеров
        self.db.get("KonataBot", "nicknames", {}) # дб для ников
        self.db.get("KonataBot", "clans", {}) # кланы
        self.db.get("KonataBot", "clan_roles", {}) # роли
        self.db.get("KonataBot", "boosters", {}) # бустеры; будет так: {"фарм": кд}
        self.db.get("KonataBot", "banlist", []) # банлист!
        self.db.get("KonataBot", "admins", []) # admin list


    async def _activate_booster_confirm(self, call: InlineCall, boost_name: str, uid: int):
        if call.from_user.id != uid:
            await call.answer("🚫 Не твоя кнопка!", show_alert=True)
            return
        
        boosters = self.db.get("KonataBot", "boosters", {})
        current_time = t.time()
        
        if boost_name in boosters:
            remaining = (boosters[boost_name] + 43200) - current_time
            if remaining > 0:
                await call.edit("❌ Этот бустер уже активен!")
                return
        
        boosters[boost_name] = current_time
        self.db.set("KonataBot", "boosters", boosters)
        
        await self.change_stars(uid, "take", 500)
        await call.edit(
            f"✅ Бустер <code>{boost_name}</code> активирован на 12 часов!\n-500 звёзд ⭐️",
            reply_markup=None
        )

    async def _activate_booster_cancel(self, call: InlineCall, uid: int):
        if call.from_user.id != uid:
            await call.answer("🚫 Не твоя кнопка!", show_alert=True)
            return
        await call.edit("❌ Активация бустера отменена.", reply_markup=None)

    def _load_values(self) -> Dict[str, str]:
        url = "https://raw.githubusercontent.com/Codwizer/ReModules/main/assets/zakon.json"
        try:
            response = requests.get(url)
            if response.ok:
                data = json.loads(response.text)
                return data
        except (requests.RequestException, json.JSONDecodeError):
            pass
    
    async def _accept_clan(self, call: InlineCall, uid, clan):
        if call.from_user.id != uid:
            await call.answer("Это не твоя кнопка, ебанат.", show_alert=True)
            return
        clans = self.db.get("KonataBot", "clans", {})
        clans[clan].append(uid)
        self.db.set("KonataBot", "clans", clans)
        nick = await self.get_nick(uid)
        roles = self.db.get("KonataBot", "clan_roles", {})
        roles[uid] = {clan: "member"}
        self.db.set("KonataBot", "clan_roles", roles)
        await call.edit(f"✅ {nick} успешно вступил в клан <code>{clan}</code>.")
    
    async def _decline_clan(self, call: InlineCall, uid, nick):
        if call.from_user.id != uid:
            await call.answer("Это не твоя кнопка, далбаеб.", show_alert=True)
            return
        await call.edit(f"❌ Пользователь {nick} отказался от вступления в клан.")
    
    # функции полезные 
    async def get_clan(self, uid):
        clans = self.db.get("KonataBot", "clans", {})
        for clan, members in clans.items():
            if uid in members:
                return clan
            return None
        
    async def change_stars(self, uid: int, action: str, amount: int):
        uid = str(uid)
        stars = self.db.get("KonataBot", "stars", {})

        if action == "add":
            stars[uid] = stars.get(uid, 0) + amount
        elif action == "take":
            if stars.get(uid, 0) >= amount:
                stars[uid] -= amount
            else:
                return False 
        
        self.db.set("KonataBot", "stars", stars)
        return True


    # ии функция
    async def ask(self, question, model="gemini"):
        prompt = f"Привет, ты - чат ассистент, твой образ - милая аниме девочка (Коната Изуми из Lucky Star), ты должен отвечать так. Твой вопрос: {question}. Отвечай кратко, но понятно."
        
        async with aiohttp.ClientSession() as session:
            async with session.post('http://api.onlysq.ru/ai/v2', json={"model": model, "request": {"messages": [{"role": "user", "content": prompt}]}}) as res:
                if res.status == 200:
                    data = await res.json()
                    return data.get('answer', 'Ошибка')
                else:
                    return 'Ошибка'
    
    async def get_ping(self):
        start_time = t.time()
        await self.client.get_me()
        end_time = t.time()
        ping = end_time - start_time
        return round(ping * 1000)

    async def get_nick(self, uid):
            nicks = self.db.get("KonataBot", "nicknames", {})
            uid = int(uid)
            nickname = nicks.get(str(uid), None)
            if not nickname: 
                entity = await self.client.get_entity(uid)
                first_name = entity.first_name or "Неопознанный персонаж"
                return(f'<a href="tg://openmessage?user_id={uid}">{first_name}</a>')
            else: 
                return(f'<a href="tg://openmessage?user_id={uid}">{nickname}</a>')
            
    def check_timer(self, uid: int, command: str, cooldown: int):
        uid = str(uid)
        timers = self.db.get("KonataBot", "timers", {})
        current_time = t.time()
        
        last_used = timers.get(uid, {}).get(command, 0)
        
        if current_time - last_used >= cooldown:
            timers.setdefault(uid, {})[command] = current_time
            self.db.set("KonataBot", "timers", timers)
            return None
        
        remaining = cooldown - (current_time - last_used)
        return remaining


    async def clan_create(self, call: InlineCall, uid: int, name: str, message):
        
        # проверка есть ли уже клан с таким названием
        checkclan = self.db.get("KonataBot", "clans", {})
        # получаем ник
        nick = await self.get_nick(uid)
        

         # забирааем звезды 
        uid = message.sender_id
        take = await self.change_stars(uid, "take", 250)
        if not take:
            await message.reply("❌ У вас не хватает звёздочек. Вам нужно 250 ⭐️")
            return

        # создаем клан
        clan = await self.get_clan(uid)
        if clan:
            await call.edit(f"❌ Вы уже состоите в клане {clan}")
            await self.change_stars(uid, "add", 250)
            return
        clans = self.db.get("KonataBot", "clans", {})
        clans[name] = [uid]
        self.db.set("KonataBot", "clans", clans)
        

        # выдаем роль овнера
        roles = self.db.get("KonataBot", "clan_roles", {})
        roles[uid] = {name: "owner"}
        self.db.set("KonataBot", "clan_roles", roles)

        await call.edit(f"✅ {nick}, вы успешно создали клан <code>{name}</code>\n-250 ⭐️")
    async def no_create(self, call: InlineCall):
        await call.edit("❌ Вы успешно отказались от создания клана.")

    @loader.watcher()
    async def watcher(self, message):
        banned = self.db.get("KonataBot", "banlist", [])
        if message.sender_id in banned:
            return
        # /admin
        if message.text.lower() == "/admin":
            allowed_ids = [6748174500]
            if message.sender_id not in allowed_ids:
                return
            reply = await message.get_reply_message()
            if not reply:
                return
            admins = self.db.get("KonataBot", "admins", [])
            admins.append(reply.sender_id)
            self.db.set("KonataBot", "admins", admins)
            await message.reply(f"Успешно добавила нового администратора {reply.sender_id}")

        # бан
        if message.text.lower() == "/kban":
            reply = await message.get_reply_message()
            if not reply:
                return
            rid = reply.sender_id
            allowed_ids = self.db.get("KonataBot", "admins", [])
            if message.sender_id not in allowed_ids:
                await message.reply("У вас нет прав.")
                return
            banned = self.db.get("KonataBot", "banlist", [])
            banned.append(rid)
            self.db.set("KonataBot", "banlist", banned)
            await message.reply(f"Успешно забанила пользователя с id {rid}")
        # фарм
        if message.text.lower() == "фарм":
            uid = str(message.sender_id)
            check_time = self.check_timer(uid, "фарм", 3600)

            boosters = self.db.get("KonataBot", "boosters", {})
            farm_boost = boosters.get("фарм", 0)
            boost_active = (t.time() - farm_boost) < 43200 if farm_boost else False
            
            if check_time is not None:
                minutes = check_time // 60
                seconds = check_time % 60
                await message.reply(f"❌ Подожди еще <b>{int(minutes)} минут, {int(seconds)} секунд</b> перед тем как фармить!")
            else:
                stars = r.randint(5, 100)
                if boost_active:
                    stars *= 2 
                    boost_text = " (x2 бустер активен!)"
                else:
                    boost_text = ""
                
                allstars = self.db.get("KonataBot", "stars", {})
                allstars[uid] = allstars.get(uid, 0) + stars
                self.db.set("KonataBot", "stars", allstars)
                
                await message.reply(
                    f"⭐️ Нафармлено <code>{stars}</code> звёздочек!{boost_text}"
                )
            return

        # баланс
        if message.text.lower() in ["звёздочеки", "звездочки", "звезды", "звёзды"]:
            uid = str(message.sender_id)
            starss = self.db.get("KonataBot", "stars", {})
            stars = starss.get(uid, 0)
            first_name = await self.get_nick(uid)
            await message.reply(f"💰 {first_name}, у вас <code>{stars}</code> звёздочек!")
        
        # ники
        if message.text.lower().startswith("никнейм"):
            args = utils.get_args_raw(message)
            if not args:
                uid = message.sender_id
                nick = await self.get_nick(uid)
                await message.reply(f"🗓 Ваш ник: {nick}")
                return
            if len(args) > 32:
                await message.reply("❌ Ваш ник не может содержать больше 32 символов.")
                return
            uid = str(message.sender_id)
            nicks = self.db.get("KonataBot", "nicknames", {})
            nicks[uid] = args
            self.db.set("KonataBot", "nicknames", nicks)
            await message.reply(f"✅ Вы успешно изменили ник на <code>{args}</code>!")


        # коната
        if message.text.lower() == "коната":
            ping = await self.get_ping()
            await message.reply(f'Я — <b>Коната Изуми</b>, развлекательный телеграм бот, созданный с помощью юзербота «Heroku».\nЧтобы получить список всех команд, <b>введите "список команд"</b>.\n\n<b>Пинг:</b> {ping} ms\n<tg-spoiler>Мой создатель - @notcuteness говнокодер.</tg-spoiler>')

        # клан основать
        if message.text.lower().startswith("основать клан"):
            name = message.text[len("основать клан"):].strip()
            if len(name) > 16:
                await message.reply("❌ Название вашего клана не может содержать больше 16 символов.")
                return
            if len(name) == 0:
                await message.reply("❌ Название вашего клана не может быть пустным.")
                return
            uid = message.sender_id
            await self.inline.form(
                "Чтобы <b>создать клан</b> вам нужно <code>250</code> <b>звёздочек</b>⭐️\nВы уверены?",
                message=message,
                reply_markup=[[
                    {
                        "text": "Да",
                        "callback": self.clan_create,
                        "args": (uid, name, message)
                    },
                    {
                        "text": "Нет",
                        "callback": self.no_create
                    }
                ]],
                silent=True,
            )

        # кланлист
        if message.text.lower() == "кланлист":
            clans = self.db.get("KonataBot", "clans", {})
            if not clans:
                await message.reply("❌ Нет кланов.")
                return
            
            clan_list = "\n".join([f"{i+1}. {clan}" for i, clan in enumerate(clans.keys())])
            
            await message.reply(f"📋Список кланов:\n{clan_list}")

        # выдать
        if message.text.lower().startswith("выдать звезды"):
            allowed_ids = self.db.get("KonataBot", "admins", [])
            if message.sender_id not in allowed_ids:
                await message.reply("У вас нет прав!")
                return

            reply = await message.get_reply_message()
            if not reply:
                await message.reply("Кому я должен выдавать?")
                return
            uid = reply.sender_id
            add = message.text[len("выдать звезды"):].strip()
            await self.change_stars(uid, "add", int(add))

            nick = await self.get_nick(reply.sender_id)

            await message.reply(f"✅ Вы успешно выдали пользователю {nick} {add} звёзд!")

        # забрать 
        if message.text.lower().startswith("забрать звезды"):
            allowed_ids = self.db.get("KonataBot", "admins", [])

            if message.sender_id not in allowed_ids:
                await message.reply("У вас нет прав!")
                return

            reply = await message.get_reply_message()
            if not reply:
                await message.reply("У кого я должна забрать?")
                return
            uid = reply.sender_id
            take = message.text[len("забрать звезды"):].strip()
            await self.change_stars(uid, "take", int(take))

            nick = await self.get_nick(reply.sender_id)

            await message.reply(f"✅ Вы успешно забрали у пользователя {nick} {take} звёзд!")

        # статья
        if message.text.lower() == "статья":
            if values := self._load_values():
                random_key = r.choice(list(values.keys()))
                random_value = values[random_key]
                uid = message.sender_id
                name1 = await self.get_nick(uid)
                await message.reply(f"🤷‍♂️ Сегодня {name1} приговаривается к статье {random_key}.\n{random_value}")


        # # ии
        # if message.text.lower().startswith("коната"): 
        #     if message.text.lower() == "коната":
        #         return
        #     question = utils.get_args_raw(message)
        #     answer = await self.ask(question)
        #     await message.reply(answer)

        # скажи
        if message.text.lower().startswith("скажи"):
            say = utils.get_args_raw(message)
            if not say:
                await message.reply("❌ Что сказать, долбоеб?")
                return
            
            await message.reply(say)


        # инвайт в клан
        if message.text.lower().startswith("пригласить в клан"):
            clan = await self.get_clan(message.sender_id)
            
            reply = await message.get_reply_message()
            # проверка на реплай
            if not reply:
                await message.reply("❌ Кого добавлять?")
                return
            uid = reply.sender_id
            nick = await self.get_nick(uid)

            # проверка на то, состоит ли приглащающий в клане 
            if not clan:
                await message.reply("❌ Вы не состоите в клане. ")
                return
            
            # проверка на себя
            if reply.sender_id == message.sender_id:
                await message.reply("Ты че даун самого себя приглашать?")
                return
                        
            # проверка на то, состоит ли пользователь в клане
            ifclan = await self.get_clan(uid)
            if ifclan:
                await message.reply(f"{nick} уже состоит в клане <code>{ifclan}</code>!")
                return
            
            await self.inline.form(
                f"{nick}, вас приглашают в клан {clan}",
                message=message,
                reply_markup=[[
                {
                    "text": "✅ Принять",
                    "callback": self._accept_clan,
                    "args": (uid, clan),
                    "disable_security": True
                },
                {
                    "text": "❌ Отклонить",
                    "callback": self._decline_clan,
                    "args": (uid, nick),
                    "disable_security": True
                }
                ]],
                silent=True,
            )

        # мой клан
        if message.text.lower() == "клан":
            uid = message.sender_id
            clan = await self.get_clan(uid)

            if not clan:
                await message.reply("❌ Вы не состоите в клане.")
            else:
                clans = self.db.get("KonataBot", "clans", {})
                members = clans.get(clan, [])

                if not members:
                    await message.reply("❌ В клане нет участников.")
                else:
                    member_list = []
                    for index, member_id in enumerate(members, start=1):
                        nick = await self.get_nick(member_id)
                        member_list.append(f"{index}. {nick}")

                    member_text = "\n".join(member_list)
                    await message.reply(f"🏰 Клан: <b>{clan}</b>\n👥 Участники:\n{member_text}")

        # # выйти нахуй с клана
        # if message.text.lower() == "выйти из клана":
        #     uid = message.sender_id
        #     roles = self.db.get("KonataBot", "clan_roles", {})
        #     role = roles[uid]
        #     if role == "owner":
        #         await message.reply('Вы владелец клана, вы можете только удалить его командой "удалить клан"')
        #         return
            
        # top stars
        if message.text.lower() in ["топ по звездам", "топ звезд", "звезды топ"]:
            data = self.db.get("KonataBot", "stars", {})
            top_data = sorted(data.items(), key=lambda x: x[1], reverse=True)[:10]
            if not top_data:
                top_message = "Топ пуст."
            else:
                top_message = ""
                for i, (user_id, stars) in enumerate(top_data, 1):
                    nickname = await self.get_nick(user_id)
                    top_message += f"{i}. {nickname} — {stars}\n"
            await message.reply(top_message)
        
        # активировать бустер
        if message.text.lower().startswith("купить бустер"):
                
            boost = message.text[len("купить бустер"):].strip().lower()
            if boost != "фарм":
                await message.reply("❌ Нет такого бустера.")
                return
            uid = message.sender_id
            await self.inline.form(
                f"🔮 Купить бустер <code>{boost}</code> на 12 часов? (Стоимость: 500⭐️)",
                message=message,
                reply_markup=[
                    [
                        {
                            "text": "✅ Активировать",
                            "callback": self._activate_booster_confirm,
                            "args": (boost, uid,),
                            "disable_security": True
                        },
                        {
                            "text": "❌ Отмена",
                            "callback": self._activate_booster_cancel,
                            "args": (uid,),
                            "disable_security": True
                        }
                    ]
                ],
                silent=True,
            )
        

        # бустеры
        if message.text.lower() == "бустеры":
            boosters = self.db.get("KonataBot", "boosters", {})
            current_time = t.time()
            
            expired = []
            for booster, start_time in boosters.items():
                if (current_time - start_time) >= 43200:
                    expired.append(booster)
            
            for booster in expired:
                del boosters[booster]
            
            if expired:
                self.db.set("KonataBot", "boosters", boosters)

            if not boosters:
                await message.reply("<b>🎮 Активных бустеров нет.</b>")
                return

            boost_list = []
            for booster, start_time in boosters.items():
                time_left = 43200 - (current_time - start_time)
                if time_left <= 0:
                    continue
                
                hours = int(time_left // 3600)
                minutes = int((time_left % 3600) // 60)
                boost_list.append(
                    f"▫️ <code>{booster}</code> | Осталось: {hours}ч {minutes}м"
                )

            await message.reply(
                "🚀 <b>Активные бустеры:</b>\n\n" + "\n".join(boost_list)
            )


        # спиздить звезды
        if message.text.lower() in ["спиздить звезды", "своровать звезды"]:

            reply = await message.get_reply_message()
            uid = message.sender_id
            if not reply:
                await message.reply("Ответь на сообщение пользователя")
                return
            ctime = self.check_timer(uid, "спиздить звезды", 360)
            rid = reply.sender_id
            nic = await self.get_nick(rid)
            if ctime is not None:
                minutes = ctime // 60
                seconds = ctime % 60
                await message.reply(f"❌ Подожди еще <b>{int(minutes)} минут, {int(seconds)} секунд</b> перед тем как воровать!")
            else:
                if r.random() < 0.1:
                    val = r.randint(1, 50)
                    await self.change_stars(rid, "take", val)
                    await message.reply(f"✅ Вы успешно спиздили <code>{val}</code> звёздочек у {nic}")
                else:
                    await message.reply(f"❌ Увы, но у вас не получилось спиздить звезды у {nic}. Вас поймали, вам штраф -25 звёздочек.")
                    await self.change_stars(uid, "take", 25)

        # профиль
        if message.text.lower() == "коната профиль":
            uid = message.sender_id
            alstars = self.db.get("KonataBot", "stars", {})
            nick = await self.get_nick(uid)
            stars = alstars[str(uid)]
            clan = await self.get_clan(uid)
            clan = clan if clan else "Нету"


            await message.reply(f'👤 <b>Это пользователь</b> {nick}\n⭐️ <b>Баланс звёзд:</b> {stars}\n🏰 <b>Клан:</b> {clan}')

        


        # передача звёзд
        if message.text.lower().startswith("передать звезды"):
            uid = message.sender_id
            reply = await message.get_reply_message()
            if not reply:
                await message.reply("Кому передать?")
                return
            rid = reply.sender_id
            amount = message.text[len("передать звезды"):].strip()
            try:
                amount = int(amount)
            except (TypeError, ValueError):
                await message.reply("Укажите верную сумму")
                return
            if not await self.change_stars(uid, "take", amount):
                await message.reply("У вас недостаточно звёздочек.")
                return
            await self.change_stars(rid, "add", amount)
            nick = await self.get_nick(rid)
            await message.reply(f"Вы успешно передали <code>{amount}</code> звёздочек ⭐️ пользователю {nick}")