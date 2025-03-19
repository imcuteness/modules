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

from ..inline.types import InlineCall
from .. import loader, utils
import requests

class CuteAIMod(loader.Module):
    """Module for AI text generation."""

    strings = {
        "name": "CuteAI",
        "answer": "💬 <b>Your prompt:</b> <code>{query}</code>\n\n💻 <b>AI answer:</b> {answer}",
        "model": "🔍 <b>Select the model:</b>",
        "changed": "✅ <b>Model changed to <code>{model}</code>.</b>",
        "loading": "⚡️ <b>Waiting for AI answer.</b>",
        "empty": "❌ <b>Your prompt can't be empty!</b>"
    }
    strings_ru = {
        "answer": "💬 <b>Ваш запрос:</b> <code>{query}</code>\n\n💻 <b>Ответ ИИ:</b> {answer}",
        "model": "🔍 <b>Выберите модель:</b>",
        "changed": "✅ <b>Модель изменена на <code>{model}</code>.</b>",
        "loading": "⚡️ <b>Ожидаем ответ от ИИ</b>",
        "empty": "❌ <b>Ваш запрос не может быть пустым!</b>"
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "model",
                "gpt-4",
                "Default model to ask.",
                validator=loader.validators.String(),
            )
        )

    @loader.command(
        ru_doc = "Спросить искуственный интеллект."
    )
    async def askai(self, message):
        """Ask an AI."""
        query = utils.get_args_raw(message)
        if query == "":
            await utils.answer(message, self.strings["empty"])
            return
        answer = self.ask(query, self.config["model"])
        await utils.answer(message, self.strings["loading"])
        await utils.answer(message, self.strings["answer"].format(
            query=query,
            answer=answer
        ))
    @loader.command(
            ru_doc = "Поменять модель."
    )
    async def changemodel(self, message):
        """Change the model."""
        models = ["GPT-4", "SearchGPT", "Copilot", "Gemini"]

        await self.inline.form(
            self.strings["model"],
            message=message,
            reply_markup=[[
                {
                    "text": model,
                    "callback": self.set_model,
                    "args": (model,),
                } for model in models
            ]]
        )

    async def set_model(self, call: InlineCall, model):
        self.config["model"] = model.lower()
        await call.edit(self.strings["changed"].format(model=model))


    def ask(self, question, model):
        res = requests.post('http://api.onlysq.ru/ai/v2', json={"model": model, "request": {"messages": [{"role": "user", "content": question}]}})
        return res.json().get('answer', 'Error')