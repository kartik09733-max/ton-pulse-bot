import asyncio
import sqlite3
import aiohttp
import os

from aiogram import Bot, Dispatcher, executor, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# CHANNEL ID
CHANNEL_ID = -1003885809066

# DATABASE
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY
)
""")

conn.commit()

# START COMMAND
@dp.message_handler(commands=['start'])
async def start(message: types.Message):

    user_id = message.from_user.id

    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
        (user_id,)
    )

    conn.commit()

    keyboard = types.InlineKeyboardMarkup()

    button = types.InlineKeyboardButton(
        "📈 Live Chart",
        url="https://www.tradingview.com/symbols/TONUSD/"
    )

    keyboard.add(button)

    text = """
💎 TON PULSE ALERTS

✅ Alerts Activated

⚡ Live TON price every 2 minutes
📈 Real-time market updates
🚀 Automatic notifications

Stay tuned.
"""

    await message.answer(
        text,
        reply_markup=keyboard
    )

# GET TON PRICE
async def get_ton_price():

    url = "https://api.coingecko.com/api/v3/simple/price?ids=the-open-network&vs_currencies=usd"

    async with aiohttp.ClientSession() as session:

        async with session.get(url) as response:

            data = await response.json()

            return data["the-open-network"]["usd"]

# SEND ALERT
async def send_alert():

    try:

        current_price = await get_ton_price()

        text = f"""
💎 TON LIVE UPDATE

💵 Current Price: ${current_price:.2f}

⚡ Live market tracking
📈 Updated every 2 minutes
🚀 TON Pulse Alerts
"""

        # SEND TO USERS
        cursor.execute("SELECT user_id FROM users")
        users = cursor.fetchall()

        for user in users:

            try:

                await bot.send_message(
                    user[0],
                    text
                )

                await asyncio.sleep(0.05)

            except Exception as e:
                print(e)

        # SEND TO CHANNEL
        try:

            await bot.send_message(
                CHANNEL_ID,
                text
            )

        except Exception as e:
            print(e)

    except Exception as e:
        print(e)

# SCHEDULER
scheduler = AsyncIOScheduler()

scheduler.add_job(
    send_alert,
    "interval",
    minutes=2
)

async def on_startup(dp):

    scheduler.start()

    print("Bot Started")

if __name__ == "__main__":

    executor.start_polling(
        dp,
        on_startup=on_startup
    )
