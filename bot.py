import os
import requests
import feedparser
import hashlib

# Telegram settings
BOT_TOKEN = "8964282170:AAEHzp1Ixcq9G1NZajbDAZms8CxbwB6IL00"
CHAT_ID = "-1004455970098"

# Google News RSS
RSS_URL = (
    "https://news.google.com/rss/search?"
    "q=world+news&hl=en-US&gl=US&ceid=US:en"
)

STATE_FILE = "last_news.txt"


def get_last_news():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()

    return ""


def save_last_news(news_id):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        f.write(news_id)


def get_news():
    feed = feedparser.parse(RSS_URL)

    if not feed.entries:
        return None

    for entry in feed.entries:
        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()

        if not title or not link:
            continue

        news_id = hashlib.sha256(
            (title + link).encode("utf-8")
        ).hexdigest()

        return {
            "id": news_id,
            "title": title,
            "link": link
        }

    return None


def send_telegram(title, link):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    text = (
        "🌍 <b>مهم‌ترین خبر جهان</b>\n\n"
        f"📰 {title}\n\n"
        f"🔗 <a href=\"{link}\">مشاهده خبر</a>"
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


def main():
    news = get_news()

    if not news:
        print("No news found.")
        return

    last_news = get_last_news()

    if news["id"] == last_news:
        print("This news was already sent.")
        return

    send_telegram(
        news["title"],
        news["link"]
    )

    save_last_news(news["id"])

    print("News sent successfully.")


if __name__ == "__main__":
    main()
