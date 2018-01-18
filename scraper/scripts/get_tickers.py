import bs4
from datetime import datetime
import os
import re
import requests
import sqlite3


DB_PATH = os.getenv("FOUR_CHAN_DB", "four_chan.sqlite")
DB = sqlite3.connect(DB_PATH, check_same_thread=False)

from scraper.utils import cursor_execute

ticker_url = "https://coinmarketcap.com/all/views/all/"

def get_tickers_rows():
    response = requests.get(ticker_url)
    soup = bs4.BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", {"id": "currencies-all"})
    trs = table.find_all("tr")
    # remove header
    _ = trs.pop(0)
    return trs

def insert_ticker(record):
    # symbol, name
    params = (record[0], record[1])
    insert_stmt = "INSERT OR REPLACE INTO tickers (symbol, name) VALUES (?, ?)"

    with cursor_execute(DB, insert_stmt, params) as curr:
        inserted = curr.rowcount

def insert_ticker_stats(record):
    params = [record[i] for i in range(2,9)]
    params = [record[0], datetime.now()] + params

    insert_stmt = (
        "INSERT INTO ticker_stats (symbol, ts, cap, price_usd, circ_supply, "
        "volume_24, change_hr, change_day, change_week) VALUES "
        "(?, ?, ?, ?, ?, ?, ?, ?, ?); "
    )
    with cursor_execute(DB, insert_stmt, params=params) as curr:
        ins = curr.rowcount


def update(trs):

    # Each search tuple consists of:
    # target_table, target_column, bs4-html-element, bs4-html-element-class
    searches = {
        0: ("tickers", "symbol", "span", {"class": "currency-symbol"}),
        1: ("tickers", "name", "a", {"class": "currency-name-container"}),
        2: ("ticker_stats", "cap", "td", {"class": "no-wrap market-cap text-right"}),
        3: ("ticker_stats", "price_usd", "a", {"class": "price"}),
        4: ("ticker_stats", "circ_supply", "td", {"class": "no-wrap text-right circulating-supply"}),
        5: ("ticker_stats", "volume_24", "a", {"class": "volume"}),
        6: ("ticker_stats", "change_hr", "td", {}),
        7: ("ticker_stats", "change_day", "td", {}),
        8: ("ticker_stats", "change_week", "td", {}),
    }
    decimal_columns = ("price_usd", "change_hr", "change_day", "change_week")
    
    for tr in trs:

        record = dict.fromkeys(searches.keys())
        for idx in sorted(searches.keys()):
            
            table, column, elem, d = searches[idx]

            # change attributes cannot be guaranteed to always be the same class
            if idx >= 6:
                match = tr.find_all("td")

                if match:
                    match = match[-3:]
                    match = match[idx - 6]

            else:
                match = tr.find_next(elem, d)

            if match:
                match = match.text
                
                # all columns are numeric besides these
                if column not in ("symbol", "name") and "change" not in column:
                    match = re.sub("[^0-9]", "", match)

                if column in decimal_columns:
                    match = match.replace("%", "")
                    match = match.replace("$", "")
                    try:
                        match = float(match) * 0.01
                    except ValueError:
                        match = None

                record[idx] = match

        # We at least have the ticker symbol
        if record[0]:
            insert_ticker(record)
            insert_ticker_stats(record)

def get_max_ts():
    query = "SELECT MAX(ts) FROM ticker_stats"
    with cursor_execute(DB, query) as curr:
        result = curr.fetchone()
        return result[0]

def number_of_new_records(ts):
    if ts is None:
        ts = datetime(1970, 1, 1)
    query = """
        SELECT COUNT(ts) FROM ticker_stats WHERE ts > ?
    """
    with cursor_execute(DB, query, params=[ts]) as curr:
        return curr.fetchone()[0]
    
if __name__ == "__main__":
    ts_prior = get_max_ts()
    rows = get_tickers_rows()
    update(rows)
    new_records = number_of_new_records(ts_prior)
    print(f"{new_records} records inserted")
