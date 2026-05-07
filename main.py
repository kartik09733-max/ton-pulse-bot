import asyncio
import aiohttp
import sqlite3
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# DATABASE
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY
)
""")
conn.commit()

last_price = None

# START COMMAND
@dp.message(F.text == "/start")
async def start(message: Message):
    user_id = message.from_user.id

    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
        (user_id,)
    )
    conn.commit()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📈 Live Chart",
                    url="https://www.tradingview.com/symbols/TONUSD/"
                )
            ]
        ]
    )

    text = """
╔═══ 💎 TON PULSE ═══╗

🚀 Welcome to TON Pulse

⚡ Live TON alerts
📈 Market updates
🔔 Instant price movement alerts

You will now receive alerts automatically.

╚══════════════════╝
"""

    await message.answer(text, reply_markup=keyboard)

# GET TON PRICE
async def get_ton_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=the-open-network&vs_currencies=usd"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            return data["the-open-network"]["usd"]

# BROADCAST ALERTS
async def check_price():
    global last_price

    try:
        current_price = await get_ton_price()

        if last_price is None:
            last_price = current_price
            return

        change_percent = (
            (current_price - last_price)
            / last_price
        ) * 100

        if abs(change_percent) >= 1:

            if change_percent > 0:
                emoji = "🟢"
                trend = "Bullish"
            else:
                emoji = "🔴"
                trend = "Bearish"

            text = f"""
╔═══ 💎 TON ALERT ═══╗

💵 Price: ${current_price:.2f}
📈 Change: {change_percent:.2f}%

{emoji} Market Sentiment:
{trend}

⚡ Live TON Movement

╚══════════════════╝
"""

            cursor.execute("SELECT user_id FROM users")
            users = cursor.fetchall()

            for user in users:
                try:
                    await bot.send_message(
                        user[0],
                        text
                    )
                    await asyncio.sleep(0.05)

                except:
                    pass

            last_price = current_price

    except Exception as e:
        print(e)

# SCHEDULER
scheduler = AsyncIOScheduler()
scheduler.add_job(check_price, "interval", minutes=1)

async def main():
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
