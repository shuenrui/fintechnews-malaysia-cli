import feedparser
import csv
from collections import Counter
from datetime import datetime
from email.utils import parsedate_to_datetime

FEED_URL = "https://fintechnews.my/feed/"

CATEGORY_FEEDS = {
    "payments": "https://fintechnews.my/category/payments-remittance/feed/",
    "blockchain": "https://fintechnews.my/category/blockchain/feed/",
    "digital-banking": "https://fintechnews.my/category/digital-banking/feed/",
    "insurtech": "https://fintechnews.my/category/insurtech/feed/",
    "wealthtech": "https://fintechnews.my/category/wealthtech/feed/",
    "regtech": "https://fintechnews.my/category/regtech/feed/",
    "e-wallets": "https://fintechnews.my/category/e-wallets/feed/",
    "lending": "https://fintechnews.my/category/lending/feed/",
    "ai": "https://fintechnews.my/category/artificial-intelligence/feed/",
    "islamic-fintech": "https://fintechnews.my/category/islamic-fintech/feed/",
    "security": "https://fintechnews.my/category/security/feed/",
}


def parse_date(entry) -> str:
    try:
        dt = parsedate_to_datetime(entry.get("published", ""))
        return dt.strftime("%d %b %Y")
    except Exception:
        return "Unknown date"


def parse_datetime(entry) -> datetime:
    try:
        return parsedate_to_datetime(entry.get("published", "")).replace(tzinfo=None)
    except Exception:
        return datetime.min


def fetch_articles(limit: int = 20, category: str = None) -> list[dict]:
    url = CATEGORY_FEEDS.get(category, FEED_URL) if category else FEED_URL
    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries[:limit]:
        categories = [tag.term for tag in entry.get("tags", [])]
        articles.append({
            "title": entry.get("title", "No title"),
            "link": entry.get("link", ""),
            "date": parse_date(entry),
            "datetime": parse_datetime(entry),
            "author": entry.get("author", "Fintech News Malaysia"),
            "summary": entry.get("summary", "")[:200].strip(),
            "categories": categories,
        })
    return articles


def search_articles(keyword: str, limit: int = 20) -> list[dict]:
    feed = feedparser.parse(FEED_URL)
    keyword_lower = keyword.lower()
    results = []
    for entry in feed.entries:
        title = entry.get("title", "")
        summary = entry.get("summary", "")
        categories = [tag.term for tag in entry.get("tags", [])]
        if keyword_lower in title.lower() or keyword_lower in summary.lower():
            results.append({
                "title": title,
                "link": entry.get("link", ""),
                "date": parse_date(entry),
                "datetime": parse_datetime(entry),
                "author": entry.get("author", "Fintech News Malaysia"),
                "summary": summary[:200].strip(),
                "categories": categories,
            })
        if len(results) >= limit:
            break
    return results


def track_keyword(keyword: str) -> dict:
    feed = feedparser.parse(FEED_URL)
    keyword_lower = keyword.lower()
    matches = []
    for entry in feed.entries:
        title = entry.get("title", "")
        summary = entry.get("summary", "")
        categories = [tag.term for tag in entry.get("tags", [])]
        if keyword_lower in title.lower() or keyword_lower in summary.lower():
            matches.append({
                "title": title,
                "link": entry.get("link", ""),
                "date": parse_date(entry),
                "categories": categories,
            })
    category_counts = Counter(
        cat for article in matches for cat in article["categories"]
    )
    return {
        "keyword": keyword,
        "mention_count": len(matches),
        "articles": matches,
        "top_categories": category_counts.most_common(5),
    }


def get_digest() -> dict:
    feed = feedparser.parse(FEED_URL)
    today = datetime.utcnow().strftime("%d %b %Y")
    grouped = {}
    for entry in feed.entries:
        date_str = parse_date(entry)
        categories = [tag.term for tag in entry.get("tags", [])]
        primary = categories[0] if categories else "General"
        article = {
            "title": entry.get("title", "No title"),
            "link": entry.get("link", ""),
            "date": date_str,
        }
        grouped.setdefault(primary, []).append(article)
    return {"date": today, "sections": grouped}


def get_trending(top_n: int = 10) -> list[tuple]:
    feed = feedparser.parse(FEED_URL)
    tag_counter = Counter()
    for entry in feed.entries:
        tags = [tag.term for tag in entry.get("tags", [])]
        # skip generic tags
        filtered = [t for t in tags if t.lower() not in ("various", "featured")]
        tag_counter.update(filtered)
    return tag_counter.most_common(top_n)


def export_articles(articles: list[dict], filepath: str):
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "date", "categories", "link", "summary"])
        writer.writeheader()
        for a in articles:
            writer.writerow({
                "title": a["title"],
                "date": a["date"],
                "categories": ", ".join(a["categories"]),
                "link": a["link"],
                "summary": a.get("summary", ""),
            })


def list_categories() -> list[str]:
    return list(CATEGORY_FEEDS.keys())
