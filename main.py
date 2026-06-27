import os
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from telegram import Update
from telegram.ext import Application, ChatMemberHandler, CommandHandler, ContextTypes

# Databáze v paměti: { "Jméno": počet }
body_uzivatelu = {}

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

BOT_TOKEN = "8788896200:AAG_7tlP0TJKJ5Qvq0Ajgzo1q1k5V_MBmQc"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot běží! Napiš /tabulka pro zobrazení pořadí.")

# Funkce pro zobrazení tabulky
async def ukaz_tabulku(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not body_uzivatelu:
        await update.message.reply_text("Zatím nikdo nikoho nepozval.")
        return
    
    # Seřadí uživatele podle počtu od největšího po nejmenší
    serazeni = sorted(body_uzivatelu.items(), key=lambda x: x[1], reverse=True)
    
    vypis = "📊 **Tabulka pozvaných:**\n\n"
    for jmeno, pocet in serazeni:
        vypis += f"👤 {jmeno}: {pocet} lidí\n"
    
    await update.message.reply_text(vypis, parse_mode="Markdown")

# Funkce pro sledování
async def sledovani_pripojeni(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.chat_member
    # Kontrola, zda uživatel pozval nového člena přes svůj odkaz
    if result.new_chat_member.status == "member":
        pozvany = result.new_chat_member.user
        pozvaci = result.from_user # Kdo ho pozval
        
        jmeno_pozvace = pozvaci.full_name
        body_uzivatelu[jmeno_pozvace] = body_uzivatelu.get(jmeno_pozvace, 0) + 1
        
        print(f"{jmeno_pozvace} právě pozval {pozvany.full_name}")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("tabulka", ukaz_tabulku))
    application.add_handler(ChatMemberHandler(sledovani_pripojeni, ChatMemberHandler.CHAT_MEMBER))
    
    application.run_polling()

if __name__ == "__main__":
    main()
      
