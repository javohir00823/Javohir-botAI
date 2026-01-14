import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import json

# Log sozlamalari
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Tokenlar (Render da environment variables ga qo'yiladi)
TOKEN = os.environ.get("8552411126:AAGeQDQmFBplTyz5pgIgAraMDhl56LV1h7w", "")
DEEPSEEK_API_KEY = os.environ.get("sk-0bdac265e0aa408eb63e992a68eb5d0d", "")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start komandasi"""
    user = update.effective_user
    welcome_text = f"""
👋 Assalomu alaykum {user.first_name}!

Men Javohir AI botiman. 
Sizga har qanday savolingizga javob bera olaman.

Faqat xabaringizni yuboring!
    """
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yordam komandasi"""
    help_text = """
🆘 *Yordam menyusi:*

• Har qanday savolingizni yozing, men javob beraman
• /start - Botni qayta ishga tushirish
• /help - Yordam menyusi
• /about - Bot haqida ma'lumot

📝 *Qo'llanma:*
1. Savolingizni yozing
2. Kutiling (5-10 soniya)
3. Javob oling
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot haqida"""
    about_text = """
🤖 *Javohir AI Bot*

• Versiya: 1.0
• Texnologiya: Python + DeepSeek AI
• Yaratuvchi: @javohir00823
• Manba kodi: GitHub

🎯 *Imkoniyatlar:*
• Har qanday savolga javob
• 24/7 ishlash
• Tez va aniq javoblar
    """
    await update.message.reply_text(about_text, parse_mode='Markdown')

def ask_deepseek(question: str) -> str:
    """DeepSeek API ga so'rov yuborish"""
    if not DEEPSEEK_API_KEY:
        return "❌ API kalit sozlanmagan. Iltimos, admin bilan bog'laning."
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system", 
                "content": "Siz foydali, batafsil va aniq javob beruvchi yordamchi AI assistentsiz. Javoblaringiz tushunarli va foydali bo'lsin."
            },
            {
                "role": "user",
                "content": question
            }
        ],
        "max_tokens": 2000,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            logger.error(f"API xatosi: {response.status_code} - {response.text}")
            return f"❌ API xatosi: {response.status_code}. Keyinroq urinib ko'ring."
            
    except requests.exceptions.Timeout:
        return "⏰ Javob kutish vaqti tugadi. Iltimos, qayta urinib ko'ring."
    except Exception as e:
        logger.error(f"Xatolik: {str(e)}")
        return f"⚠️ Xatolik yuz berdi: {str(e)}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi xabarlarini qayta ishlash"""
    user_message = update.message.text
    
    # Kutilayotganlik holati
    await update.message.reply_chat_action(action="typing")
    
    # DeepSeek API ga so'rov
    response = ask_deepseek(user_message)
    
    # Telegram xabar cheklovi (4096 belgi)
    if len(response) > 4000:
        response = response[:4000] + "..."
    
    await update.message.reply_text(response)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xatolarni qayta ishlash"""
    logger.error(f"Xatolik: {context.error}")
    
    try:
        await update.message.reply_text(
            "❌ Xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring yoki /start ni bosing."
        )
    except:
        pass

def main():
    """Asosiy funksiya"""
    if not TOKEN:
        print("❌ TELEGRAM_TOKEN topilmadi!")
        print("Iltimos, Render.com da environment variable qo'ying:")
        print("1. TELEGRAM_TOKEN = telegram_bot_token")
        print("2. DEEPSEEK_API_KEY = deepseek_api_key")
        return
    
    # Botni yaratish
    application = Application.builder().token(TOKEN).build()
    
    # Handlerlar
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Xato handler
    application.add_error_handler(error_handler)
    
    # Botni ishga tushirish
    logger.info("🤖 Javohir AI Bot ishga tushdi...")
    print("=" * 50)
    print("🤖 Javohir AI Bot ishga tushdi!")
    print("📞 Botga Telegram dan murojaat qilishingiz mumkin")
    print("=" * 50)
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
