# Fintech News Malaysia CLI

Browse [Fintech News Malaysia](https://fintechnews.my/) directly from your terminal — latest articles, category filters, keyword search, and open in browser.

## Install

```bash
git clone https://github.com/shuenrui/fintechnews-malaysia-cli.git
cd fintechnews-malaysia-cli
pip3 install -r requirements.txt
```

## Usage

```bash
# Latest news
python3 cli.py latest

# Limit number of results
python3 cli.py latest --limit 50

# Browse by category
python3 cli.py category blockchain
python3 cli.py category payments
python3 cli.py category ai

# See all available categories
python3 cli.py categories

# Search by keyword
python3 cli.py search "Bank Negara"
python3 cli.py search "e-wallet"

# Open article #3 in your browser
python3 cli.py open 3
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
