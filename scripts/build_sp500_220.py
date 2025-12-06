"""Build a 220-ticker list from the S&P 500 Wikipedia page and write
`stock_symbols_220.py` in the project root.

This script is robust: it tries to use pandas.read_html first, and falls
back to a regex extraction if pandas is not available.
"""
import requests
import re
import os
from html import unescape

WIKI_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
OUT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "stock_symbols_220.py")


def fetch_tickers_via_pandas(html):
    try:
        import pandas as pd
        from io import StringIO
    except Exception:
        return None
    try:
        tables = pd.read_html(StringIO(html))
        # first table on the page is the component list
        df = tables[0]
        if 'Symbol' in df.columns:
            return df['Symbol'].astype(str).str.strip().tolist()
    except Exception:
        return None


def fetch_tickers_via_regex(html):
    # Fallback HTML table parsing: find the first wikitable and extract
    # the first column from each row (the symbol). This avoids depending
    # on pandas/bs4 in the environment.
    symbols = []
    # find first wikitable
    tbl_match = re.search(r"<table[^>]*class=[\"'][^\"']*wikitable[^\"']*[\"'][^>]*>(.*?)</table>", html, re.S | re.I)
    if not tbl_match:
        return []
    tbl = tbl_match.group(1)
    # find rows
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", tbl, re.S | re.I):
        # find first cell (th or td)
        cell_match = re.search(r"<(?:th|td)[^>]*>(.*?)</(?:th|td)>", row, re.S | re.I)
        if not cell_match:
            continue
        cell_html = cell_match.group(1)
        # strip tags
        cell_text = re.sub(r"<.*?>", "", cell_html).strip()
        cell_text = re.sub(r"\s+", " ", cell_text)
        # symbol is usually uppercase alnum / . / - up to 6 chars
        if re.fullmatch(r"[A-Z0-9\.\-]{1,6}", cell_text):
            symbols.append(cell_text)
    # dedupe while preserving order
    seen = set()
    out = []
    for s in symbols:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def main():
    print("Fetching S&P 500 list from Wikipedia...")
    r = requests.get(WIKI_URL, timeout=20)
    txt = r.text
    txt = unescape(txt)

    tickers = fetch_tickers_via_pandas(txt)
    if not tickers:
        print("pandas not available or parsing failed, falling back to regex")
        tickers = fetch_tickers_via_regex(txt)

    if not tickers:
        print("Failed to extract tickers from page")
        return

    # take first 220 tickers
    tickers = tickers[:220]

    # write out file
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write("# Auto-generated S&P500-derived 220-ticker list\n")
        f.write("STOCK_SYMBOLS = [\n")
        for s in tickers:
            f.write(f"    \"{s}\",\n")
        f.write("]\n")

    print(f"Wrote {len(tickers)} tickers to: {OUT_PATH}")


if __name__ == '__main__':
    main()
