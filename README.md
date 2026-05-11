# Fintech News Malaysia CLI

Browse [Fintech News Malaysia](https://fintechnews.my/) directly from your terminal — latest articles, category filters, keyword search, company tracking, trending topics, and more.

## Install

```bash
git clone https://github.com/shuenrui/fintechnews-malaysia-cli.git
cd fintechnews-malaysia-cli
pip3 install -r requirements.txt
```

## Commands

### `latest` — Latest articles
```bash
python3 cli.py latest
python3 cli.py latest --limit 50

# Export to CSV
python3 cli.py latest --export articles.csv
```

### `category` — Browse by topic
```bash
python3 cli.py category blockchain
python3 cli.py category payments
python3 cli.py category ai
python3 cli.py category digital-banking --limit 30 --export banking.csv
```

### `search` — Find articles by keyword
```bash
python3 cli.py search "Bank Negara"
python3 cli.py search "e-wallet" --export results.csv
```

### `open` — Open article in browser
```bash
python3 cli.py open 3    # opens article #3 from the latest list
```

### `track` — Track a company or keyword
```bash
python3 cli.py track CIMB
python3 cli.py track Maybank
python3 cli.py track "digital banking"
```
Shows total mention count, which categories they appear in most, and every article that mentions them.

### `watch` — Live auto-refreshing feed
```bash
python3 cli.py watch
python3 cli.py watch --interval 60   # refresh every 60 seconds
python3 cli.py watch --limit 20
```
Polls the feed on an interval and highlights new articles as they appear. Press `Ctrl+C` to stop.

### `digest` — Daily briefing grouped by category
```bash
python3 cli.py digest
```
Morning snapshot of the latest articles organised by topic — good for a quick daily brief.

### `trending` — Most mentioned topics right now
```bash
python3 cli.py trending
python3 cli.py trending --top 20
```
Ranks the most frequently mentioned tags and topics across the latest feed.

### `categories` — List all available categories
```bash
python3 cli.py categories
```

## Available Categories

| Category | Command |
|---|---|
| Payments & Remittance | `python3 cli.py category payments` |
| Blockchain | `python3 cli.py category blockchain` |
| Digital Banking | `python3 cli.py category digital-banking` |
| Insurtech | `python3 cli.py category insurtech` |
| Wealthtech | `python3 cli.py category wealthtech` |
| Regtech | `python3 cli.py category regtech` |
| E-Wallets | `python3 cli.py category e-wallets` |
| Lending | `python3 cli.py category lending` |
| AI | `python3 cli.py category ai` |
| Islamic Fintech | `python3 cli.py category islamic-fintech` |
| Security | `python3 cli.py category security` |

## Requirements

- Python 3.8+
- `typer`
- `rich`
- `feedparser`

## Data Source

Powered by the official RSS feed at [fintechnews.my/feed](https://fintechnews.my/feed/) — no scraping, always up to date.
