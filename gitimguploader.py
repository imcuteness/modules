# meta developer: @im_cuteness


from hikka import loader, utils
import requests
import base64
import os

class GitHubUploader(loader.Module):
    """Модуль для загрузки изображений на GitHub"""
    strings = {"name": "GitHubUploader"}

    def __init__(self):
        self.config = loader.ModuleConfig(
            "GITHUB_TOKEN", None, "Персональный токен GitHub"
        )

    async def client_ready(self, client, db):
        self.client = client

    async def githubuploadcmd(self, message):
        """Загружает изображение на GitHub и возвращает raw ссылку."""
        args = utils.get_args_raw(message)
        if not args:
            await message.edit("<b>Укажите репозиторий. Пример:\ngithubupload myuser/myrepo</b>")
            return

        token = self.config["GITHUB_TOKEN"]
        if not token:
            await message.edit("<b>Токен GitHub не настроен. Настройте его в конфиге</b>")
            return

        repo_path = args.strip()
        reply = await message.get_reply_message()
        if not reply or not reply.media:
            await message.edit("<b>Ответьте на сообщение с изображением.</b>")
            return

        file = await reply.download_media()
        if not os.path.exists(file):
            await message.edit("<b>Ошибка загрузки изображения.</b>")
            return

        file_name = os.path.basename(file)
        ext = os.path.splitext(file_name)[1]
        if not ext:
            await message.edit("<b>Не удалось определить расширение файла.</b>")
            return

        with open(file, "rb") as f:
            content = base64.b64encode(f.read()).decode("utf-8")

        api_url = f"https://api.github.com/repos/{repo_path}/contents/{file_name}"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }
        data = {
            "message": "Добавлено через модуль GitHubUploader",
            "content": content,
        }

        response = requests.put(api_url, json=data, headers=headers)
        if response.status_code == 201:
            raw_url = response.json()["content"]["download_url"]
            await message.edit(f"<b>Изображение загружено: Raw:({raw_url})</b>", link_preview=False)
        else:
            await message.edit(f"Ошибка загрузки: {response.json().get('message', 'Неизвестная ошибка')}")
