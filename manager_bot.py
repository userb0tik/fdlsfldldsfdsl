import asyncio
import json
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

BOT_TOKEN = "8761488365:AAEgWoiaB-InhPuMT4WODMkkaK9KYdMN4LA"
ADMIN_ID = 665478040

SETTINGS_FILE = "settings.json"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "stop_words": ["меф", "мяу", "скорость", "ск"],
        "broadcast_hours": None,
        "shop_text": """❤️
I M
━━━━━━━━━━━━━━━
🍀 𝐈𝐂𝐄 𝐂𝐑𝐄𝐀𝐌 SRT
        ✔️  𝟏,𝟎 𝐠 𝟓𝟓$ ≥ 𝟐𝟖𝐤💳
        ✔️  𝟎,𝟓 𝐠 𝟑𝟓$ ≥ 𝟐𝟎𝐤

🍫  𝐇𝐒𝐇
        ✔️𝟏,𝟎 𝐠 𝟓𝟓$ ≥ 𝟐𝟖𝐤💳
        ✔️ 𝟐,𝟎 𝐠  𝟔𝟗$ / 𝟑𝟔𝐤
━━━━━━━━━━━━━━━
ДОСТАВКА / ФАКТ
КРИПТА / КАРТА
━━━━━━━━━━━━━━━
👤 ОПЕРАТОР: http://burgerkassir.t.me/"""
    }


def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)


def is_admin(message: types.Message):
    return message.from_user.id == ADMIN_ID


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if not is_admin(message):
        return
    await message.answer(
        "🤖 <b>Панель управления юзерботом</b>\n\n"
        "/стоп_список — список стоп-слов\n"
        "/стоп_добавить [слово] — добавить стоп-слово\n"
        "/стоп_удалить [слово] — удалить стоп-слово\n\n"
        "/прайс — показать текущий прайс\n"
        "/прайс_изменить — изменить прайс\n\n"
        "/участники — сколько участников запомнено\n\n"
        "/рассылка [часы] — запустить рассылку\n"
        "/рассылка_стоп — остановить рассылку\n"
        "/статус — текущий статус",
        parse_mode="HTML"
    )


@dp.message(Command("стоп_список"))
async def cmd_stop_list(message: types.Message):
    if not is_admin(message):
        return
    settings = load_settings()
    words = settings.get("stop_words", [])
    if not words:
        await message.answer("Стоп-слов нет.")
        return
    text = "🚫 <b>Стоп-слова:</b>\n\n" + "\n".join(f"• {w}" for w in words)
    await message.answer(text, parse_mode="HTML")


@dp.message(Command("стоп_добавить"))
async def cmd_stop_add(message: types.Message):
    if not is_admin(message):
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Напиши слово: /стоп_добавить кокс")
        return
    word = parts[1].strip().lower()
    settings = load_settings()
    if word in settings["stop_words"]:
        await message.answer(f"Слово «{word}» уже есть в списке.")
        return
    settings["stop_words"].append(word)
    save_settings(settings)
    await message.answer(f"✅ Слово «{word}» добавлено в стоп-список.")


@dp.message(Command("стоп_удалить"))
async def cmd_stop_remove(message: types.Message):
    if not is_admin(message):
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Напиши слово: /стоп_удалить кокс")
        return
    word = parts[1].strip().lower()
    settings = load_settings()
    if word not in settings["stop_words"]:
        await message.answer(f"Слова «{word}» нет в списке.")
        return
    settings["stop_words"].remove(word)
    save_settings(settings)
    await message.answer(f"✅ Слово «{word}» удалено из стоп-списка.")


@dp.message(Command("прайс"))
async def cmd_price(message: types.Message):
    if not is_admin(message):
        return
    settings = load_settings()
    await message.answer(f"📋 <b>Текущий прайс:</b>\n\n{settings['shop_text']}", parse_mode="HTML")


@dp.message(Command("прайс_изменить"))
async def cmd_price_change(message: types.Message):
    if not is_admin(message):
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Напиши новый прайс после команды:\n/прайс_изменить текст прайса")
        return
    new_text = parts[1].strip()
    settings = load_settings()
    settings["shop_text"] = new_text
    save_settings(settings)
    await message.answer("✅ Прайс обновлён!")


@dp.message(Command("участники"))
async def cmd_members(message: types.Message):
    if not is_admin(message):
        return
    if os.path.exists("members.json"):
        with open("members.json", "r", encoding="utf-8") as f:
            members = json.load(f)
        await message.answer(f"👥 Запомнено участников: <b>{len(members)}</b>", parse_mode="HTML")
    else:
        await message.answer("Файл участников не найден.")


@dp.message(Command("рассылка"))
async def cmd_broadcast(message: types.Message):
    if not is_admin(message):
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip().isdigit():
        await message.answer("Напиши количество часов: /рассылка 2")
        return
    hours = int(parts[1].strip())
    settings = load_settings()
    settings["broadcast_hours"] = hours
    save_settings(settings)
    await message.answer(f"✅ Рассылка каждые <b>{hours}</b> ч. запущена.", parse_mode="HTML")


@dp.message(Command("рассылка_стоп"))
async def cmd_broadcast_stop(message: types.Message):
    if not is_admin(message):
        return
    settings = load_settings()
    settings["broadcast_hours"] = None
    save_settings(settings)
    await message.answer("🛑 Рассылка остановлена.")


@dp.message(Command("статус"))
async def cmd_status(message: types.Message):
    if not is_admin(message):
        return
    settings = load_settings()
    hours = settings.get("broadcast_hours")
    words = settings.get("stop_words", [])
    members_count = 0
    if os.path.exists("members.json"):
        with open("members.json", "r", encoding="utf-8") as f:
            members_count = len(json.load(f))

    broadcast_status = f"каждые {hours} ч." if hours else "выключена"
    await message.answer(
        f"📊 <b>Статус:</b>\n\n"
        f"👥 Участников: {members_count}\n"
        f"📢 Рассылка: {broadcast_status}\n"
        f"🚫 Стоп-слов: {len(words)}",
        parse_mode="HTML"
    )


async def main():
    print("Бот-управлялка запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())