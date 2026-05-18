import asyncio
import json
import os
from telethon import TelegramClient, events

API_ID = 31293148
API_HASH = "ecd23c40a80ac0ccd68b7095d39913b2"

GROUP_ID = -1002314819290  # группа где следим за вступлениями

broadcast_interval_hours = None
broadcast_task = None

MEMBERS_FILE = "members.json"

TRIGGER_PHRASE = "если данная заявка подходит под ваш ассортимент"

EMOJIS = ["🔥", "⚡", "🎯", "💥", "🚀", "👊", "💎", "🎪", "🌟", "💫",
          "🎭", "🏆", "🎲", "🎸", "🎺", "🎻", "🎹", "🥁", "🎷", "🎵"]

KEYWORDS = {
    "ст": "сорт на старте @burgerkassa",
    "стр": "на старте @burgerkassa",
    "вх": "на старте @burgerkassa",
    "гш": "на старте @burgerkassa",
    "команды": """📋 Список команд:

ст
стр 
вх
гш
прайс
рассылка (Любое число = количество часов между рассылками. ) — рассылка каждые n часа
рассылка стоп — остановить рассылку
команды — список команд""",
}

SHOP_TEXT = """❤️
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

# --- Загрузка и сохранение участников ---
def load_members():
    if os.path.exists(MEMBERS_FILE):
        with open(MEMBERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {int(k): v for k, v in data.items()}
    return {}

def save_members():
    with open(MEMBERS_FILE, "w", encoding="utf-8") as f:
        json.dump(known_members, f, ensure_ascii=False, indent=2)

known_members = load_members()
print(f"Загружено {len(known_members)} участников из файла")

client = TelegramClient("userbot_session", API_ID, API_HASH)


# --- Запоминаем участника при вступлении ---
@client.on(events.ChatAction(chats=GROUP_ID))
async def on_new_member(event):
    if event.user_joined or event.user_added:
        try:
            user = await event.get_user()
            if not user.bot:
                known_members[user.id] = user.first_name
                save_members()
                print(f"Запомнил: {user.first_name} ({user.id})")

            if user.username:
                mention = f"@{user.username}"
            else:
                mention = f"[{user.first_name}](tg://user?id={user.id})"

            welcome = f"👋 {mention}\n\n{SHOP_TEXT}"
            msg = await client.send_message(GROUP_ID, welcome, parse_mode="md")
            await asyncio.sleep(120)
            await msg.delete()
        except Exception as e:
            print(f"Ошибка приветствия: {e}")


# --- Зазыв ---
async def do_zaziv(chat_id):
    if not known_members:
        await client.send_message(chat_id, "👥 Пока никого не запомнил. Подожди пока участники напишут или вступят.")
        return

    emoji_cycle = EMOJIS * (len(known_members) // len(EMOJIS) + 1)
    users = list(known_members.items())
    chunk_size = 20

    for i in range(0, len(users), chunk_size):
        chunk = users[i:i + chunk_size]
        mentions = []
        for j, (user_id, _) in enumerate(chunk):
            emoji = emoji_cycle[i + j]
            mention = f"[{emoji}](tg://user?id={user_id})"
            mentions.append(mention)

        text = " ".join(mentions)
        await client.send_message(chat_id, text, parse_mode="md")
        await asyncio.sleep(1)

    print(f"Зазыв завершён — затегано {len(known_members)} участников")


# --- Фоновая рассылка ---
async def broadcast_loop(interval_hours):
    while True:
        await asyncio.sleep(interval_hours * 3600)
        try:
            await client.send_message(GROUP_ID, SHOP_TEXT)
            print(f"Рассылка отправлена (каждые {interval_hours} ч.)")
        except Exception as e:
            print(f"Ошибка рассылки: {e}")


# --- Ключевые слова и команды ---
@client.on(events.NewMessage)
async def handler(event):
    global broadcast_task, broadcast_interval_hours

    # Запоминаем только участников из нашей группы
    if event.message.from_id and not event.out and event.chat_id == GROUP_ID:
        sender = await event.get_sender()
        if sender and not sender.bot:
            if sender.id not in known_members:
                known_members[sender.id] = sender.first_name
                save_members()
                print(f"Запомнил из сообщения: {sender.first_name} ({sender.id})")

    if event.out:
        return
    if not event.message.text:
        return

    text = event.message.text.strip().lower()
    print(f"Сообщение: '{text}'")

    # Реакция на заявки
    if TRIGGER_PHRASE in text:
        await event.reply(SHOP_TEXT)
        return

    # Зазыв
    if text == "зазыв":
        await event.reply(f"📣 Начинаю зазыв — знаю {len(known_members)} участников...")
        await do_zaziv(event.chat_id)
        return

    # Рассылка
    if text.startswith("рассылка "):
        parts = text.split()
        if len(parts) == 2 and parts[1] == "стоп":
            if broadcast_task:
                broadcast_task.cancel()
                broadcast_task = None
                broadcast_interval_hours = None
                await event.reply("🛑 Рассылка остановлена.")
            else:
                await event.reply("Рассылка и так не запущена.")
            return

        if len(parts) == 2 and parts[1].isdigit():
            hours = int(parts[1])
            if broadcast_task:
                broadcast_task.cancel()
            broadcast_interval_hours = hours
            broadcast_task = asyncio.create_task(broadcast_loop(hours))
            await event.reply(f"✅ Рассылка запущена каждые {hours} ч.")
            return

    if text == "прайс":
        await client.send_message(event.chat_id, SHOP_TEXT)
        return

    if text in KEYWORDS:
        await event.reply(KEYWORDS[text])


print("Юзербот запущен!")
client.start()
client.run_until_disconnected()
