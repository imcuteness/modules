from .. import loader, utils
import random as r
import time

@loader.tds
class IrisMod(loader.Module):
    """Iris imitation"""
    strings = {"name": "Iris"}

    async def client_ready(self, client, db):
        self.db = db
        if not self.db.get("Iris", "farm_timestamps", None):
            self.db.set("Iris", "farm_timestamps", {})
        if not self.db.get("Iris", "ic", None):
            self.db.set("Iris", "ic", {})
        if not self.db.get("Iris", "cooldowns", None):
            self.db.set("Iris", "cooldowns", {})

    @loader.watcher(chat_id=2192007423)
    async def mainwatcher(self, message):
        if message.text.lower() == "1фарма":
            user_id = str(message.sender_id)
            timestamps = self.db.get("Iris", "farm_timestamps", {})
            last_farm = timestamps.get(user_id, 0)
            current_time = time.time()
            
            if current_time - last_farm < 14400:
                remaining_time = int((14400 - (current_time - last_farm)) / 60)
                hours = remaining_time // 60
                minutes = remaining_time % 60
                return await message.reply(f"❌ НЕЗАЧЁТ! Фармить можно раз в 4 часа. Следующая добыча через {hours} час {minutes} мин")
            
            offline_hours = (current_time - last_farm) / 3600 if last_farm else 0
            multiplier = min(1 + max(0, offline_hours - 4) * 0.3, 3) if offline_hours >= 5 else 1
            ic_base = r.randint(5, 50)
            ic = int(ic_base * multiplier)
            timestamps[user_id] = current_time
            self.db.set("Iris", "farm_timestamps", timestamps)
            
            old = self.db.get("Iris", "ic", {})
            old[user_id] = old.get(user_id, 0) + ic
            self.db.set("Iris", "ic", old)
            
            if multiplier > 1:
                return await message.reply(f"✅ <b>ЗАЧЁТ!</b> ☢️ +{ic} i¢ = {ic_base}×{round(multiplier, 2)}\n\n✨ Сила звёздности: 0\n⏳ Урожайность: {round(multiplier, 2)}")
            else:
                return await message.reply(f"✅ <b>ЗАЧЁТ!</b> ☢️ +{ic} i¢\n\n✨ Сила звёздности: 0")

        if message.text.lower() == "1мешок":
            id = str(message.sender_id)
            entity = await self.client.get_entity(int(id))
            firstname = entity.first_name
            data = self.db.get("Iris", "ic", {})
            ic = data.get(id, 0)
            await message.reply(f"💰 <b>В мешке </b><a href='tg://user?id={id}'><b>{firstname}</b></a><b>:</b>\n🍬 0 ирисок 🟡 0 ирис-голд\n☢️ {ic} i¢ звёзд ✨ 0 звёздочек\n\n 💬 Запасы можно пополнить, введя команду 'купить <число>'")       
        if message.text.lower() == "1заразить":
            reply = await message.get_reply_message()
            if not reply:
                return
            else:
                sid = message.sender_id
                rid = reply.sender_id
                sentity = await self.client.get_entity(sid)
                rentity = await self.client.get_entity(rid)
                sfirst = sentity.first_name
                rfirstname = rentity.first_name
                sender = f'<a href=tg://openmessage?user_id={sid}>{sfirst}</a>'
                receiver = f'<a href=tg://openmessage?user_id={rid}>{rfirstname}</a>'

                await message.reply(message, f"🦠 {sender} подверг заражению неизвестным патогеном {receiver} \n☠️ Горячка на 1 минуту\n🤒 Заражение на 1 день\n☣️ +1 био-опыта")
    def check_cooldown(self, user_id: str, command: str, cooldown: int) -> int:
        cooldowns = self.db.get("Iris", "cooldowns", {})
        last_used = cooldowns.get(user_id, {}).get(command, 0)
        current_time = time.time()

        if current_time - last_used < cooldown:
            return int(cooldown - (current_time - last_used))

        if user_id not in cooldowns:
            cooldowns[user_id] = {}
        cooldowns[user_id][command] = current_time
        self.db.set("Iris", "cooldowns", cooldowns)
        
        return 0