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

from telethon.tl.functions.contacts import AddContactRequest, DeleteContactsRequest
from .. import loader, utils


@loader.tds
class ContactsMod(loader.Module):
    """Contact manager."""

    strings = {
        "name": "Contacts"
    }

    async def client_ready(self, client, db):
        self._client = client


    @loader.command(
        ru_doc="Добавляет контакт."
    )
    async def addcont(self, message):
        """Add contact."""
        reply = await message.get_reply_message()
        if not reply:
            return
        else:
            rid = reply.sender_id
            cont = utils.get_args_raw(message)
            await self.client(AddContactRequest(
            id=rid,
            first_name=cont,
            last_name="",
            phone=""
            ))
    @loader.command(
        ru_doc="Удалить контакт"
    )
    async def delcont(self, message):
        "Удалить контакт."
        reply = message.get_reply_message()
        if not reply:
            return
        else:
            rid = reply.sender_id
        await self.client(DeleteContactsRequest(id=rid))
