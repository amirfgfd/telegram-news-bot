import os
import requests
import feedparser
import hashlib
from urllib.parse import quote


# ==============================
# Telegram Settings
# ==============================

BOT_TOKEN = "8964282170:AAEHzp1Ixcq9G1NZajbDAZms8CxbwB6IL00"
CHAT_ID = "-1004455970098"


# ==============================
# News Search Topics
# ==============================

SEARCH_QUERIES = [
    "world politics",
    "international politics",
    "US politics",
    "Russia Ukraine",
    "Middle East",
    "Israel Palestine",
    "Iran politics",
    "China politics",
    "Europe politics",
    "war diplomacy",
    "international relations"
]


# ==============================
# Get news from Google News
# ==============================

def get_news():

    all_news = []

    for query in SEARCH_QUERIES:

        rss_url = (
            "https://news.google.com/rss/search?"
            f"q={quote(query)}"
            "&hl=en-US"
            "&gl=US"
            "&ceid=US:en"
        )

        feed = feedparser.parse(rss_url)

        for entry in feed.entries[:10]:

            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()

            if not title or not link:
                continue

            news_id = hashlib.sha256(
                (title + link).encode("utf-8")
            ).hexdigest()

            all_news.append({
                "id": news_id,
                "title": title,
                "link": link
            })


    # حذف خبرهای تکراری
    unique_news = {}

    for news in all_news:
        unique_news[news["id"]] = news

    all_news = list(unique_news.values())


    if not all_news:
        return None


    # اولین خبر جدید را انتخاب کن
    return all_news[0]


# ==============================
# Send news to Telegram
# ==============================

def send_telegram(title, link):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"


    text = (
        "🌍 <b>خبر مهم جهان</b>\n\n"
        f"📰 <b>{title}</b>\n\n"
        f"🔗 <a href=\"{link}\">مشاهده منبع خبر</a>\n\n"
        "━━━━━━━━━━━━━━\n"
        "📢 @TIIME_NEWS | تایم نیوز"
    )


    response = requests.post(

        url,

        data={
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        },

        timeout=30
    )


    response.raise_for_status()


# ==============================
# Main
# ==============================

def main():

    news = get_news()


    if not news:

        print("No news found.")

        return


    send_telegram(
        news["title"],
        news["link"]
    )


    print("News sent successfully.")

    print(news["title"])


# ==============================
# Run
# ==============================

if __name__ == "__main__":

    main()
