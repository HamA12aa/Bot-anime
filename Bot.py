import requests
import os
import json

# وەرگرتنی زانیارییەکان لە Secrets
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def ask_gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    try:
        return data['candidates'][0]['content']['parts'][0]['text']
    except:
        return None

def get_anime_data():
    # هێنانی نوێترین ئەنیمێکان لە Jikan
    response = requests.get("https://api.jikan.moe/v4/seasons/now?limit=2")
    animes = response.json().get('data', [])
    context = ""
    for anime in animes:
        context += f"Title: {anime['title']}\nScore: {anime['score']}\nSynopsis: {anime['synopsis'][:300]}...\n\n"
    return context

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

# جێبەجێکردنی پرۆسەکە
print("Fetching Anime Data...")
anime_info = get_anime_data()

prompt = f"""تۆ ئەدمینی کەناڵی 'KURD FOREST'یت. ئەم زانیارییانەی خوارەوە وەک هەواڵ و پێشنیار بە زمانی کوردی سۆرانییەکی زۆر جوان و سەرنجڕاکێش بنووسە. 
ئیمۆجی زۆر بەکاربهێنە و لە کۆتایی بنووسە @KURD_FOREST.
زانیارییەکان:
{anime_info}"""

print("Asking Gemini to write in Kurdish...")
kurdish_post = ask_gemini(prompt)

if kurdish_post:
    print("Sending to Telegram...")
    send_to_telegram(kurdish_post)
    print("Done!")
else:
    print("Failed to generate content.")
