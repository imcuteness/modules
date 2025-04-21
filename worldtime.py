from .. import loader, utils
from datetime import datetime, timedelta

@loader.tds
class TimeZonesMod(loader.Module):
    """Показывает текущее время в двух часовых поясах с кастомным шаблоном"""

    strings = {
        "name": "TimeZones",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            "TZ1", "+0", lambda: "Первый часовой пояс (например, +3, -5)",
            "TZ2", "None", lambda: "Второй часовой пояс или None, если не нужен",
            "TEMPLATE", "🕒 Время:\nЧасы 1 (UTC{tz1}): {time1}\n{time2_line}",
            lambda: "Шаблон вывода. Можно использовать {time1}, {time2}, {tz1}, {tz2}, {time2_line}",
        )

    @loader.command()
    async def timecmd(self, message):
        """Показывает текущее время в заданных часовых поясах"""
        tz1 = self.config["TZ1"]
        tz2 = self.config["TZ2"]
        template = self.config["TEMPLATE"]

        def parse_timezone(tz_str):
            try:
                return int(tz_str)
            except:
                return 0

        def format_time(offset):
            now = datetime.utcnow() + timedelta(hours=offset)
            return now.strftime("%H:%M:%S")

        tz1_offset = parse_timezone(tz1)
        time1 = format_time(tz1_offset)

        if tz2 and tz2.lower() != "none":
            tz2_offset = parse_timezone(tz2)
            time2 = format_time(tz2_offset)
            time2_line = f"Часы 2 (UTC{('+' if tz2_offset >= 0 else '')}{tz2_offset}): {time2}"
            tz2_fmt = ("+" if tz2_offset >= 0 else "") + str(tz2_offset)
        else:
            time2 = ""
            time2_line = ""
            tz2_fmt = ""

        tz1_fmt = ("+" if tz1_offset >= 0 else "") + str(tz1_offset)

        result = template.format(
            time1=time1,
            time2=time2,
            time2_line=time2_line,
            tz1=tz1_fmt,
            tz2=tz2_fmt
        )

        await utils.answer(message, result)
