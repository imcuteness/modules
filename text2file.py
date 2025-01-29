#meta developer: @im_cuteness


from .. import loader, utils
import os

class Text2File(loader.Module):
    """Модуль для превращения текста в файл"""
    strings = {"name": "Text2File"}

    async def text2filecmd(self, message):
        """Создает файл с текстом, на который вы ответили"""
        args = utils.get_args_raw(message)
        if not args:
            await message.edit("<b>Укажите имя файла.</b>")
            return

        reply = await message.get_reply_message()
        if not reply or not reply.text:
            await message.edit("<b>Ответьте на сообщение с текстом.</b>")
            return

        file_name = args.strip()
        file_path = os.path.join(os.getcwd(), file_name)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(reply.text)

        await message.client.send_file(message.chat_id, file_path, caption=f"<b>Файл {file_name} создан!</b>")
        os.remove(file_path)
        await message.delete()
