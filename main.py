import aiohttp
import asyncio
import os

from aiogram import Bot, Dispatcher, executor, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# BOT TOKEN FROM RAILWAY VARIABLES
BOT_TOKEN = os.getenv("BOT_TOKEN")

# BOT + DISPATCHER
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# YOUR CHANNEL ID
CHANNEL_ID = -1003885809066

# START COMMAND
@dp.message_handler(commands=["start"])
async def start(message: types.Message):

    keyboard = types.InlineKeyboardMarkup()

    button = types.InlineKeyboardButton(
        text="📈 Live TON Chart",
        url="https://www.tradingview.com/symbols/TONUSD/"
    )

    keyboard.add(button)

    text = """
💎 TON PULSE

✅ Live Alerts Activated

⚡ Real-time TON updates
📈 Professional market tracking
🚀 Automatic price feed
"""

    await message.answer(
        text,
        reply_markup=keyboard
    )

# GET TON PRICE DATA
async def get_ton_data():

    url = "https://api.coingecko.com/api/v3/coins/the-open-network"

    async with aiohttp.ClientSession() as session:

        async with session.get(url) as response:

            data = await response.json()

            price = data["market_data"]["current_price"]["usd"]

            change = data["market_data"]["price_change_percentage_24h"]

            return price, change

# SEND ALERT TO CHANNEL
async def send_alert():

    try:

        price, change = await get_ton_data()

        if change >= 0:
            sentiment = "🟢 Bullish Momentum"
        else:
            sentiment = "🔴 Bearish Pressure"

        text = f"""
💎 TON PULSE

💵 ${price:.2f}
📈 {change:.2f}% Today

{sentiment}
⚡ Live Market Feed
"""

        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=text
        )

        print("Alert Sent")

    except Exception as e:

        print("ERROR:", e)

# SCHEDULER
scheduler = AsyncIOScheduler()

scheduler.add_job(
    send_alert,
    trigger="interval",
    minutes=2
)

# BOT STARTUP
async def on_startup(dp):

    scheduler.start()

    print("Bot Started Successfully")

# RUN BOT
if __name__ == "__main__":

    executor.start_polling(
        dp,
        on_startup=on_startup,
        skip_updates=True
    )
