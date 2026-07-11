import telebot
import requests
import os
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# ================= وەرگرتنی نهێنییەکان لە سێرڤەر/گیت هەب =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ADMIN_ID = os.getenv("ADMIN_ID") # ئایدی تێلیگرامی خۆت وەک سکرێت دابنێ
# ==========================================================

bot = telebot.TeleBot(BOT_TOKEN)

# دڵنیابوونەوە لەوەی هەموو نهێنییەکان هەن
if not all([BOT_TOKEN, CHANNEL_ID, GEMINI_API_KEY, ADMIN_ID]):
    print("❌ هەڵە: یەکێک لە نهێنییەکان (Secrets) لە گیت هەب دانەنراوە!")
    exit()

# گۆڕینی ئایدی ئەدمین بۆ ژمارە
ADMIN_ID = int(ADMIN_ID)

# ================= فەنکشنی زیرەکی دەستکرد =================
def format_with_gemini(raw_data, post_type):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    if post_type == "search":
        prompt = f"تۆ ئەدمینی KURD FORESTیت. ئەم زانیارییە فەرمییانەی خوارەوە بە کوردییەکی سۆرانی شاز و پڕۆفیشناڵ دابڕێژەوە. کورت و پوخت بێت و ئیمۆجی بەکاربهێنە. لە کۆتایی بنووسە @KURD_FOREST.\n\n{raw_data}"
    else:
        prompt = f"ئەمە خشتەی ئەنیمێکانی ئەمڕۆیە. بە کوردییەکی زۆر جوان و ئیمۆجییەوە ڕێکی بخە بۆ کەناڵی KURD FOREST. لە کۆتایی بنووسە @KURD_FOREST.\n\n{raw_data}"

    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload).json()
        return response['candidates'][0]['content']['parts'][0]['text']
    except:
        return "❌ هەڵە لە دروستکردنی دەقەکە."

# ================= مینۆی سەرەکی =================
def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(KeyboardButton("🔍 گەڕان بەدوای ئەنیمێ"), KeyboardButton("📅 خشتەی ئەمڕۆ"))
    markup.add(KeyboardButton("📖 ڕێنمایی بەکارهێنان"))
    return markup

# ================= فەرمانەکان =================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.id != ADMIN_ID: return
    bot.send_message(message.chat.id, "🌳 بەخێربێیت بۆ پانێڵی بەڕێوەبردنی KURD FOREST\nتکایە هەڵبژێرە:", reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.chat.id == ADMIN_ID)
def handle_text(message):
    if message.text == "📖 ڕێنمایی بەکارهێنان":
        tutorial = "💡 **ڕێنمایی:**\n1. کلیک لە گەڕان بکە.\n2. ناوی ئەنیمێ بنووسە.\n3. کاتێک وێنە و دەقەکە هات، کلیک لە 'بڵاوکردنەوە' بکە تا بچێتە کەناڵ."
        bot.send_message(message.chat.id, tutorial, parse_mode="Markdown")

    elif message.text == "🔍 گەڕان بەدوای ئەنیمێ":
        msg = bot.send_message(message.chat.id, "✏️ ناوی ئەنیمێیەکە بنووسە:")
        bot.register_next_step_handler(msg, process_search)

    elif message.text == "📅 خشتەی ئەمڕۆ":
        bot.send_message(message.chat.id, "⏳ خەریکی هێنانی خشتەی ئەمڕۆم...")
        process_schedule(message.chat.id)

# ================= پرۆسەکان =================
def process_search(message):
    try:
        res = requests.get(f"https://api.jikan.moe/v4/anime?q={message.text}&limit=1").json()
        anime = res['data'][0]
        img = anime['images']['jpg']['large_image_url']
        data = f"Title: {anime['title']}\nStatus: {anime['status']}\nBroadcast: {anime['broadcast']['string']}\nScore: {anime['score']}\nSynopsis: {anime['synopsis'][:300]}..."
        
        kurdish = format_with_gemini(data, "search")
        send_preview(message.chat.id, kurdish, img)
    except:
        bot.send_message(message.chat.id, "❌ نەدۆزرایەوە.")

def process_schedule(chat_id):
    try:
        res = requests.get("https://api.jikan.moe/v4/schedules?filter=today&limit=10").json()
        raw = "\n".join([f"- {a['title']}" for a in res['data']])
        kurdish = format_with_gemini(raw, "schedule")
        send_preview(chat_id, kurdish, None)
    except:
        bot.send_message(chat_id, "❌ کێشەیەک لە خشتەدا هەیە.")

def send_preview(chat_id, text, img):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📢 بڵاوکردنەوە", callback_data="post"), InlineKeyboardButton("❌ سڕینەوە", callback_data="del"))
    
    if img:
        bot.send_photo(chat_id, img, caption=text, reply_markup=markup)
    else:
        bot.send_message(chat_id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "post":
        if call.message.content_type == 'photo':
            bot.send_photo(CHANNEL_ID, call.message.photo[-1].file_id, caption=call.message.caption)
        else:
            bot.send_message(CHANNEL_ID, call.message.text)
        bot.answer_callback_query(call.id, "✅ بڵاوکرایەوە!")
    elif call.data == "del":
        bot.delete_message(call.message.chat.id, call.message.message_id)

bot.infinity_polling()
