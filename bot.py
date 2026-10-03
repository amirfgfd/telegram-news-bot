import requests
import feedparser
import hashlib
import os
import html
from urllib.parse import quote

BOT_TOKEN = "8964282170:AAEHzp1Ixcq9G1NZajbDAZms8CxbwB6IL00"
CHAT_ID = "-1004455970098"

SEARCH_QUERIES = [
    "اخبار جهان",
    "اخبار سیاسی جهان",
    "سیاست بین الملل",
    "آمریکا جهان",
    "روسیه اوکراین",
    "خاورمیانه",
    "اسرائیل فلسطین",
    "ایران جهان",
    "چین جهان",
    "جنگ دیپلماسی"
]

STATE_FILE = "sent_news.txt"


def get_sent_news():

    if not os.path.exists(STATE_FILE):
        return set()

    with open(STATE_FILE, "r", encoding="utf-8") as file:
        return set(
            line.strip()
            for line in file
            if line.strip()
        )


def save_news(news_id):

    with open(STATE_FILE, "a", encoding="utf-8") as file:
        file.write(news_id + "\n")


def get_news():

    sent_news = get_sent_news()

    all_news = []

    for query in SEARCH_QUERIES:

        rss_url = (
            "https://news.google.com/rss/search?"
            f"q={quote(query)}"
            "&hl=fa"
            "&gl=IR"
            "&ceid=IR:fa"
        )

        try:

            feed = feedparser.parse(rss_url)

            for entry in feed.entries[:10]:

                title = entry.get("title", "").strip()
                link = entry.get("link", "").strip()

                if not title or not link:
                    continue

                news_id = hashlib.sha256(
                    (title + link).encode("utf-8")
                ).hexdigest()

                # اگر قبلاً ارسال شده، ردش کن
                if news_id in sent_news:
                    continue

                all_news.append({
                    "id": news_id,
                    "title": title,
                    "link": link
                })

        except Exception as error:

            print("RSS error:", error)


    # حذف خبرهای تکراری در همین اجرا
    unique_news = {}

    for news in all_news:
        unique_news[news["id"]] = news

    all_news = list(unique_news.values())


    if not all_news:
        print("خبر جدیدی پیدا نشد.")
        return None


    # یک خبر جدید انتخاب کن
    return all_news[0]


def send_to_telegram(news):

    title = html.escape(news["title"])
    link = html.escape(news["link"], quote=True)

    message = (
        "🌍 <b>خبر مهم جهان</b>\n\n"
        f"🔴 <b>{title}</b>\n\n"
        f"🔗 <a href=\"{link}\">مشاهده خبر</a>\n\n"
        "━━━━━━━━━━━━━━\n"
        "📢 @TIIME_NEWS | تایم نیوز"
    )

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        },
        timeout=30
    )

    response.raise_for_status()


def main():

    print("در حال بررسی خبرهای جدید...")

    news = get_news()

    if not news:
        return

    print("خبر انتخاب شد:")
    print(news["title"])

    send_to_telegram(news)

    # فقط بعد از ارسال موفق، خبر را ذخیره کن
    save_news(news["id"])

    print("خبر با موفقیت ارسال شد.")


if __name__ == "__main__":
    main()
