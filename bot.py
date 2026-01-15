import os
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import httpx
from flask import Flask, request

BOT_TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 10000))

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hi! I’m AssetLog — your total capital OS.\n\n"
        "Use /add to log an asset.\n"
        "Example: /add BTC 0.5 2026-01-15"
    )

async def add_asset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if len(context.args) != 3:
            await update.message.reply_text("Usage: /add <SYMBOL> <AMOUNT> <YYYY-MM-DD>")
            return

        symbol = context.args[0].upper()
        amount = float(context.args[1])
        buy_date_str = context.args[2]
        buy_date = datetime.strptime(buy_date_str, "%Y-%m-%d")

        date_fmt = f"{buy_date.day} {buy_date.strftime('%B')[:3]} {buy_date.year}"
        url = f"https://api.coingecko.com/api/v3/coins/{symbol.lower()}/history?date={date_fmt}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10)
            if resp.status_code != 200:
                await update.message.reply_text(f"❌ Price not found for {symbol} on {buy_date_str}")
                return
            data = resp.json()
            price_usd = data["market_data"]["current_price"]["usd"]

        usd_value = amount * price_usd
        rub_value = usd_value * 90
        gold_grams = usd_value / 70

        msg = (
            f"✅ Added:\n"
            f"{amount} {symbol} bought on {buy_date_str}\n\n"
            f"= ${usd_value:,.2f}\n"
            f"= ₽{rub_value:,.0f}\n"
            f"= {gold_grams:.1f} g gold"
        )
        await update.message.reply_text(msg)

    except Exception as e:
        await update.message.reply_text("❌ Invalid input. Use: /add BTC 0.5 2026-01-15")

# --- Flask app ---
app = Flask(__name__)

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_asset))
    application.process_update(
        Update.de_json(request.get_json(force=True), application.bot)
    )
    return 'OK'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
