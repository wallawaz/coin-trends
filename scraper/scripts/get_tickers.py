import bs4
from datetime import datetime
import re
import requests

from ..base import Base


class TickerUpdater(Base):
    TICKER_URL = "https://coinmarketcap.com/all/views/all/"

    # Each search tuple consists of:
    # target_table, target_column, bs4-html-element, bs4-html-element-class
    SEARCHES = {
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
    DECIMAL_COLUMNS = ("price_usd", "change_hr", "change_day", "change_week")


    def __init__(self):
        super(TickerUpdater, self).__init__()
        self.trs = None
        self.inserted = 0

    def get_tickers_rows(self):
        response = requests.get(self.TICKER_URL)
        soup = bs4.BeautifulSoup(response.content, "html.parser")
        table = soup.find("table", {"id": "currencies-all"})
        trs = table.find_all("tr")
        # remove header
        _ = trs.pop(0)
        self.trs = trs

    def insert_ticker(self, record):
        # symbol, name
        params = (record[0], record[1])
        insert_stmt = "INSERT OR REPLACE INTO tickers (symbol, name) VALUES (?, ?)"

        with self.cursor_execute(self.db, insert_stmt, params) as curr:
            inserted = curr.rowcount

    def insert_ticker_stats(self, record):
        params = [record[i] for i in range(2,9)]
        params = [record[0], datetime.now()] + params

        insert_stmt = (
            "INSERT INTO ticker_stats (symbol, ts, cap, price_usd, circ_supply, "
            "volume_24, change_hr, change_day, change_week) VALUES "
            "(?, ?, ?, ?, ?, ?, ?, ?, ?); "
        )
        with self.cursor_execute(self.db, insert_stmt, params=params) as curr:
            inserted = curr.rowcount

    def search_trs(self):
        if not self.trs:
            return None

        for tr in self.trs:
            record = dict.fromkeys(self.SEARCHES.keys())

            for idx in sorted(self.SEARCHES.keys()):
                table, column, elem, d = self.SEARCHES[idx]

                # change_hr|day|week attributes cannot be guaranteed to always be the same class
                if idx >= 6:
                    match = tr.find_all("td")

                    if match:
                        match = match[-3:]
                        match = match[idx - 6]

                else:
                    match = tr.find_next(elem, d)

                if match:
                    record[idx] = match.text

            yield record

    def parse_record(self, record):
        # all columns are numeric besides these

        out = {}
        for i, match in record.items():
            column = self.SEARCHES[i][1]

            if column not in ("symbol", "name") and column not in self.DECIMAL_COLUMNS:
                match = re.sub("[^0-9]", "", match)

            if column in self.DECIMAL_COLUMNS:
                match = match.replace("%", "")
                match = match.replace("$", "")
                try:
                    match = float(match)
                except ValueError:
                    match = None

                if match and "change" in column:
                    match = match * 0.01

            out[i] = match
        return out

    def get_latest_ticker_stats(self):
        query = "SELECT MAX(ts) FROM ticker_stats"
        with self.cursor_execute(self.db, query) as curr:
            result = curr.fetchone()
            return result[0]

    def get_tickers(self):
        query = "SELECT symbol FROM tickers"
        with self.cursor_execute(self.db, query) as curr:
            results = curr.fetchall()
            return set((r[0] for r in results))

    def _run(self):

        tickers_prior = self.get_tickers()
        latest_ticker_stat = self.get_latest_ticker_stats()

        # set self.trs
        self.get_tickers_rows()

        for record in self.search_trs():
            record = self.parse_record(record)

            if record[0]:
                self.insert_ticker(record)
                self.insert_ticker_stats(record)
                self.inserted += 1

        tickers_added = self.get_tickers() - tickers_prior
        if tickers_added:
            tickers_added = ",".join(tickers_added)
            print(f"Added new tickers: {tickers_added}")

        print("Added {} new ticker_stats".format(self.inserted))