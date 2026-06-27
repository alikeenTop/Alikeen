import os
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from telegram import Update
from telegram.ext import Application, ChatMemberHandler, CommandHandler, ContextTypes

# Nastavení logování
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Tvoje údaje (v Renderu si v Environment Variables nastav MOJE_CHAT_ID a BOT_TOKEN)
MOJE_CHAT_ID = os.environ.get("MOJE_CHAT_ID", "8952168418")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8788896200:AAGTwSs9YP4Agbx_cNLcCVSdl2j7sVESmJU")

# Web server pro Render (aby bot „nespal“)
class HealthCheckServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckServer)
    server.serve_forever()

# Funkce pro příkaz /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot je připraven a funguje!")

# Funkce pro sledování nových členů
async def sledovani_pripojeni(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.chat_member
    if result.old_chat_member.status in ["left", "kicked"] and result.new_chat_member.status == "member":
        uzivatel = result.new_chat_member.user
        zprava = f"📩 Nový člen: {uzivatel.full_name}"
        
        try:
            # Pošle zprávu na tvoje ID
            await context.bot.send_message(chat_id=MOJE_CHAT_ID, text=zprava)
        except Exception as e:
            print(f"Chyba při posílání: {e}")

def main():
    # Spustí server na pozadí
    threading.Thread(target=run_health_server, daemon=True).start()
    
    # Inicializace bota
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Handlery
    application.add_handler(CommandHandler("start", start))
    application.add_handler(ChatMemberHandler(sledovani_pripojeni, ChatMemberHandler.CHAT_MEMBER))
    
    print("Bot bezi...")
    application.run_polling()

if __name__ == "__main__":
    main()
          
