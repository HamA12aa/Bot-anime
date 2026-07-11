import requests
import os

# وەرگرتنی نهێنییەکان لە گیت هەب
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

def ask_gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    res = requests.post(url, json=payload)
    try:
        return res.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "هەڵە لە دروستکردنی دەقەکە ڕوویدا."

def get_anime_news():
    # وەرگرتنی ٢ ئەنیمێی بەناوبانگی ئێستا لە MyAnimeList (Jikan)
    res = requests.get("https://api.jikan.moe/v4/top/anime?filter=airing&limit=2")
    animes = res.json().get('data', [])
    info = ""
    for a in animes:
        info += f"Title: {a['title']}\nScore: {a['score']}\nStory: {a['synopsis'][:200]}...\n\n"
    return info

def send_post():
    data = get_anime_news()
    prompt = f"تۆ ئادمینێکی زیرەکی کەناڵی ئەنیمێی 'KURD FOREST'یت. ئەم زانیارییانەی خوارەوەم بۆ بکە بە پۆستێکی کوردی سۆرانی زۆر جوان و سەرنجڕاکێش. ئیمۆجی بەکاربهێنە و لە کۆتایی بنووسە @KURD_FOREST. زانیارییەکان:\n{data}"
    
    kurdish_text = ask_gemini(prompt)
    
    # ناردن بۆ تێلیگرام
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": kurdish_text, "parse_mode": "Markdown"})

if __name__ == "__main__":
    send_post()
