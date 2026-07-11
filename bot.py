import telebot
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ================= زانیارییەکانی تۆ =================
BOT_TOKEN = "8963794119:AAHntWTn_Rc_EUbgdhwaBYXwtwMqw_xiu2Q"
CHANNEL_ID = "-1002127529797"
GEMINI_API_KEY = "کلیلی_جیمینای_لێرە_دابنێ"
ADMIN_ID = 123456789 # ئایدی تێلیگرامی خۆت لێرە دابنێ (لە @userinfobot وەریگرە)
# ====================================================

bot = telebot.TeleBot(BOT_TOKEN)

# فەنکشنی پەیوەندیکردن بە جیمینای
def format_with_gemini(raw_data, post_type):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    if post_type == "search":
        prompt = f"""تۆ ڕۆژنامەنووسێکی کەناڵی 'KURD FOREST'یت. 
پابەند بە بەم مەرجانەوە:
1. زانیارییەکان لە خۆتەوە مەهێنە، تەنها ئەم زانیارییانە بەکاربهێنە کە پێت دەدەم.
2. بە زمانی کوردی سۆرانییەکی زۆر پڕۆفیشناڵ و جوان بینووسە.
3. ئیمۆجی گونجاو بەکاربهێنە.
4. با ڕۆژ و کاتی پەخشکردنەکە بە ڕوونی دیار بێت.
5. لە کۆتایی بنووسە 🌳 @KURD_FOREST

زانیارییەکان (دروستکراوی MyAnimeList):
{raw_data}"""
    else:
        prompt = f"ئەمە هەواڵی ئەمڕۆیە، بیکە بە پۆستێکی کوردی شاز بۆ کەناڵی KURD FOREST بە هەمان مەرجەکانی پێشوو:\n{raw_data}"

    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload).json()
        return response['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return "❌ هەڵە لە دروستکردنی دەقەکە ڕوویدا."

# دڵنیابوونەوە لەوەی تەنها ئەدمین دەتوانێت فەرمان بدات
def is_admin(message):
    return message.chat.id == ADMIN_ID

# ١. فەرمانی ستارت
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not is_admin(message): return
    text = """👋 سڵاو گەورەم! بەخێربێیت بۆ سیستەمی بەڕێوەبردنی KURD FOREST.
    
فەرمانەکان:
/anime [ناوی ئەنیمێ] 👈 بۆ دۆزینەوەی زانیاری و کاتی پەخشی هەر ئەنیمێیەک.
/daily 👈 بۆ ئامادەکردنی پۆستی هەواڵەکانی ئەمڕۆ."""
    bot.reply_to(message, text)

# ٢. فەرمانی گەڕان بەدوای ئەنیمێ و کاتی پەخش
@bot.message_handler(commands=['anime'])
def search_anime(message):
    if not is_admin(message): return
    
    anime_name = message.text.replace('/anime', '').strip()
    if not anime_name:
        bot.reply_to(message, "❌ تکایە ناوی ئەنیمێیەکە بنووسە، نموونە:\n/anime One Piece")
        return

    msg = bot.reply_to(message, "⏳ خەریکی هێنانی زانیارییە دروستەکانم لە MyAnimeList...")
    
    # هێنانی زانیاری ڕاستەقینە لە Jikan API
    try:
        res = requests.get(f"https://api.jikan.moe/v4/anime?q={anime_name}&limit=1").json()
        if not res['data']:
            bot.edit_message_text("❌ هیچ ئەنیمێیەک بەم ناوەوە نەدۆزرایەوە.", message.chat.id, msg.message_id)
            return
            
        anime = res['data'][0]
        raw_data = f"""
        Title: {anime['title']}
        Status: {anime['status']}
        Airing Date/Time: {anime['broadcast']['string'] if anime['broadcast']['string'] else 'Unknown'}
        Score: {anime['score']}
        Episodes: {anime['episodes']}
        Synopsis: {anime['synopsis'][:300]}...
        """
        
        bot.edit_message_text("🧠 خەریکی داڕشتنەوەیم بە کوردییەکی نایاب لەلایەن Gemini...", message.chat.id, msg.message_id)
        
        # ناردنی بۆ جیمینای بۆ وەرگێڕان و ڕێکخستن
        kurdish_post = format_with_gemini(raw_data, "search")
        
        # دروستکردنی دوگمە بۆ ناردن بۆ کەناڵ
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton("📢 بڵاوکردنەوە لە کەناڵ", callback_data="post_channel"))
        markup.row(InlineKeyboardButton("❌ پەشیمان بوونەوە", callback_data="cancel"))
        
        bot.send_message(message.chat.id, kurdish_post, reply_markup=markup)
        bot.delete_message(message.chat.id, msg.message_id)
        
    except Exception as e:
        bot.edit_message_text(f"❌ کێشەیەک ڕوویدا: {e}", message.chat.id, msg.message_id)

# ٣. وەڵامدانەوەی دوگمەکان (کاتێک کلیک لە بڵاوکردنەوە دەکەیت)
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "post_channel":
        try:
            bot.send_message(CHANNEL_ID, call.message.text)
            bot.answer_callback_query(call.id, "✅ بە سەرکەوتوویی لە کەناڵ پۆست کرا!")
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            bot.send_message(call.message.chat.id, "✅ پۆستەکە چوو بۆ کەناڵ.")
        except Exception as e:
            bot.answer_callback_query(call.id, "❌ هەڵە لە ناردن بۆ کەناڵ.")
    elif call.data == "cancel":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id, "پۆستەکە سڕایەوە.")

# کارپێکردنی بۆتەکە
print("Bot is running...")
bot.infinity_polling()
