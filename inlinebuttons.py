__version__ = (1, 0, 1)

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
# The project is influenced by @hikka_mods

from .. import loader, utils
from ..inline.types import InlineCall


@loader.tds
class InlineButtonsMod(loader.Module):
    """Quick inline buttons making."""

    strings = {
        "name": "InlineButtons",
        "help": "<code>{prefix}inlinelink</code> [-g] &lt;message text&gt; / &lt;button text&gt;, &lt;link&gt; | &lt;second button text&gt;, &lt;second link&gt; | ...\n<b>Creates a message with inline button(s), each of which leads to the specified URL.</b>\n\n<code>{prefix}inlineanswer</code> [-g] &lt;message text&gt; / &lt;button text&gt;, &lt;notification&gt; | &lt;second button text&gt;, &lt;second notification&gt; | ...\n<b>Creates a message with inline button(s) that send a notification to the person who clicked it.</b>\n\n<code>{prefix}inlineedit</code> [-g] &lt;message text&gt; / &lt;button text&gt;, &lt;text after click&gt; | &lt;second button text&gt;, &lt;second text after click&gt; | ...\n<b>Creates inline buttons that change the message text after being clicked.</b>",
        "noargs": "<b>Arguments error! Please, send the {prefix}inlinehelp command to help.</b>"
               }
    strings_ru = {
        "help": "<code>{prefix}inlinelink</code> [-g] &lt;текст сообщения&gt; / &lt;текст кнопки&gt;, &lt;ссылка&gt; | &lt;текст второй кнопки&gt;, &lt;вторая ссылка&gt; | ...\n<b>Создаёт сообщение с инлайн-кнопками, каждая из которых ведёт по указанной ссылке.</b>\n\n<code>{prefix}inlineanswer</code> [-g] &lt;текст сообщения&gt; / &lt;текст кнопки&gt;, &lt;уведомление&gt; | &lt;текст второй кнопки&gt;, &lt;второе уведомление&gt; | ...\n<b>Создаёт сообщение с инлайн-кнопками, которые отправляют уведомление человеку, нажавшему на кнопку.</b>\n\n<code>{prefix}inlineedit</code> [-g] &lt;текст сообщения&gt; / &lt;текст кнопки&gt;, &lt;текст после клика&gt; | &lt;текст второй кнопки&gt;, &lt;второй текст после клика&gt; | ...\n<b>Создаёт инлайн-кнопки, которые изменяют текст сообщения после нажатия.</b>",
        "noargs": "<b>Ошибка с аргументами! Пожалуйста, напишите команду {prefix}inlinehelp для помощи.</b>"
    }


    async def inline_edit_callback(self, call: InlineCall, args):
        new_text = args[5:]
        await call.edit(new_text)
    async def inline_answer_callback(self, call: InlineCall, args):
        text = args[7:]
        await call.answer(text, show_alert=True)

    async def parse_args(self, arg_str: str):
        try:
            has_g = arg_str.startswith('-g ')
            if has_g:
                arg_str = arg_str[3:].strip()
            
            if '/' not in arg_str:
                return False
            
            message_text, buttons_str = arg_str.split('/', 1)
            message_text = message_text.strip()
            buttons_parts = [b.strip() for b in buttons_str.split('|')]
            
            buttons = []
            for part in buttons_parts:
                if ',' not in part:
                    return False
                text, link = part.split(',', 1)
                text = text.strip()
                link = link.strip()
                if not text or not link:
                    return False
                buttons.append((text, link))
            
            if not buttons:
                return False

            return has_g, message_text, buttons
        except Exception:
            return False
    async def generate_reply_markup(self, buttons, ifg: bool, mode: str = "link"):
        markup = []
        btns = []

        for text, action in buttons:
            if mode == "answer":
                btn = {"text": text, "callback": self.inline_answer_callback, "args": (f"answer:{action}",), "force_me": True, "disable_security": True,}
            elif mode == "edit":
                btn = {"text": text, "callback": self.inline_edit_callback, "args": (f"edit:{action}",), "force_me": True, "disable_security": True,}
            else:
                btn = {"text": text, "url": action}

            if ifg:
                btns.append(btn)
            else:
                markup.append([btn])

        if ifg:
            markup.append(btns)

        return markup
        
    @loader.command(
        ru_doc="Помощь по модулю"
    )
    async def inlinehelp(self, message):
        """Help with module"""
        prefix = self.get_prefix()
        await utils.answer(message, self.strings["help"].format(prefix=prefix))
    @loader.command(
        ru_doc="Создать инлайн кнопку со ссылкой."
    )
    async def inlinelink(self, message):
        """Create inline button with the link."""

        args = utils.get_args_raw(message)
        result = await self.parse_args(args)

        if result is False:
            prefix = self.get_prefix()
            await utils.answer(message, self.strings["noargs"].format(prefix=prefix))
            return
        has_g, message_text, buttons = result

        markup = await self.generate_reply_markup(buttons, ifg=has_g)

        await self.inline.form(
            message_text,
            message=message,
            reply_markup=markup
        )
    @loader.command(
        ru_doc="Создать инлайн кнопку которая вызывает уведомление."
    )
    async def inlineanswer(self, message):
        """Create inline button that makes notification."""
        args = utils.get_args_raw(message)
        result = await self.parse_args(args)

        if result is False:
            prefix = self.get_prefix()
            await utils.answer(message, self.strings["noargs"].format(prefix=prefix))
            return

        has_g, message_text, buttons = result
        markup = await self.generate_reply_markup(buttons, ifg=has_g, mode="answer")

        await self.inline.form(
            message_text,
            message=message,
            reply_markup=markup
        )
    @loader.command(
        ru_doc="Создать инлайн кнопку которая меняет сообщение."
    )
    async def inlineedit(self, message):
        """Create an inline button that edits the message."""
        args = utils.get_args_raw(message)
        result = await self.parse_args(args)

        if result is False:
            prefix = self.get_prefix()
            await utils.answer(message, self.strings["noargs"].format(prefix=prefix))
            return

        has_g, message_text, buttons = result
        markup = await self.generate_reply_markup(buttons, ifg=has_g, mode="edit")

        await self.inline.form(
            message_text,
            message=message,
            reply_markup=markup
        )
