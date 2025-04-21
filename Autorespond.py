#    _____ _    _ _______ ______ _   _ ______  _____ _____        
#   / ____| |  | |__   __|  ____| \ | |  ____|/ ____/ ____|       
#  | |    | |  | |  | |  | |__  |  \| | |__  | (___| (___         
#  | |    | |  | |  | |  |  __| | . ` |  __|  \___ \___ \        
#  | |____| |__| |  | |  | |____| |\  | |____ ____) |___) |       
#   \_____|___/_  |_| _|______|_|_\_|______|_____/_____/ ______ 
#   / ____|/ __ \ \    / / \ | |/ __ \ / ____/ __ \|  __ \|  ____|
#  | |  __| |  | \ \  / /|  \| | |  | | |   | |  | | |  | | |__   
#  | | |_ | |  | |\ \/ / | . ` | |  | | |   | |  | | |  | |  __|  
#  | |__| | |__| | \  /  | |\  | |__| | |___| |__| | |__| | |____ 
#   \_____|\____/   \/   |_| \_|\____/ \_____\____/|_____/|______|
# 
# meta developer: @cuteness_modules

from .. import loader, utils
import asyncio

@loader.tds
class AutoRespondMod(loader.Module):
    """автоответчик"""

    strings = {"name": "AutoRespond"}

    async def client_ready(self, client, db):
        self._client = client
        self._db = db
        self.db.get("AutoResp", "blist", [])
        self.db.get("AutoResp", "ifon", False)
        self.db.get("AutoResp", "message", None)


    
    async def autorespondcmd(self, message):
        args = str(utils.get_args_raw(message))
        self.db.set("AutoResp", "message", args)
        await utils.answer(message, f"Успешно пососал!! {args}")
    async def startcmd(self, message):
        self.db.set("AutoResp", "ifon", True)
        await utils.answer(message, "Начал сосать хуй успешно")
    async def stopcmd(self, message):
        self.db.set("AutoResp", "ifon", False)
        await utils.answer(message, "Перестал сосать успешно")
    @loader.watcher()
    async def venom(self, message):
        asyncio.sleep(10)
        if not self.db.get("AutoResp", "ifon", False):
            return
        if message.sender_id in self.db.get("AutoResp", "blist", []):
            return
        await self.client.send_message(message.peer_id, self.db.get("AutoResp", "message", None))
        old = self.db.get("AutoResp", "blist", [])
        old.append(message.sender_id)
        self.db.set("AutoResp", "blist", old)