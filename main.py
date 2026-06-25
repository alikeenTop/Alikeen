import os
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from telegram import Update
from telegram.ext import Application, ChatMemberHandler, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

MOJE_CHAT_ID = int(os.environ.get("MOJE_CHAT_ID", "8952168418"))
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8788896200:AAGTwSs9YP4Agbx_cNLcCVSdl2j7sVESmJU")

class HealthCheckServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckServer)
    server.serve_forever()

async def sledovani_pripojeni(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.chat_member
    if result.old_chat_member.status in ["left", "kicked"] and result.new_chat_member.status == "member":
        uzivatel = result.new_chat_member.user
        skupina = result.chat
        invite_link = result.invite_link
        
        if invite_link:
            nazev_odkazu = invite_link.name if invite_link.name else "Bez nazvu / No name"
            vytvoril = invite_link.creator.full_name if invite_link.creator else "Neznamy / Unknown"
            zprava = (
                f"📩 **Nový člen ve skupině! / New member in the group!**\n\n"
                f"👤 **Uživatel / User:** {uzivatel.full_name}\n"
                f"👥 **Skupina / Group:** {skupina.title}\n"
                f"🔗 **Odkaz / Link:** {nazev_odkazu}\n"
                f"👨‍💻 **Vytvořil / Created by:** {vytvoril}\n"
                f"📊 **Použití odkazu / Link uses:** {invite_link.member_count}x\n"
                f"----------------------------------------"
            )
        else:
            zprava = f"📩 **Nový člen! / New member!**\n\n👤 **{uzivatel.full_name}** přišel přes veřejný odkaz."
        
        try:
            await context.bot.send_message(chat_id=MOJE_CHAT_ID, text=zprava, parse_mode="Markdown")
        except Exception as e:
            print(f"Chyba: {e}")

def main():
    threading.Thread(target=run_health_server, daemon=True).start()
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(ChatMemberHandler(sledovani_pripojeni, ChatMemberHandler.CHAT_MEMBER))
    print("Bot bezi...")
    application.run_polling(allowed_updates=[Update.CHAT_MEMBER])

if __name__ == "__main__":
    main()
