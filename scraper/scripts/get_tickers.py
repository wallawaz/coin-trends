import bs4
from datetime import datetime
import re
import requests

from ..base import Base


class TickerUpdater(Base):
    #TICKER_URL = "https://coinmarketcap.com/all/views/all/"
    TICKER_API_URL = "https://api.coinmarketcap.com/v1/ticker/?start=0&limit=2000"
    TICKER_STATS = [
        'ts',
        'last_updated',
        'symbol',
        'market_cap_usd',
        'price_usd',
        'price_btc',
        'available_supply',
        'total_supply',
        'max_supply',
        '24h_volume_usd',
        'percent_change_1h',
        'percent_change_24h',
        'percent_change_7d'
    ]
    
    def __init__(self):
        super(TickerUpdater, self).__init__()
        self.inserted = 0
        self.start_time = datetime.now()
        self.seen_symbols = set([])

    def get_tickers(self):
        response = requests.get(self.TICKER_API_URL)
        self.tickers = response.json()
        
    def insert_ticker(self, record):
        # symbol, name
        params = (record["symbol"], record["name"])

        insert_stmt = "INSERT OR REPLACE INTO tickers (symbol, name) VALUES (?, ?)"
        with self.cursor_execute(self.db, insert_stmt, params) as curr:
            inserted = curr.rowcount

    def insert_ticker_stats(self, records):
        to_insert = []
        for record in records:
            ins = [self.start_time]
            for column in self.TICKER_STATS[1:]:
                ins.append(record.get(column))
            to_insert.append(ins)

        columns = ",".join(self.TICKER_STATS)
        columns = columns.replace("24h_volume_usd", "volume_24_usd")
        qs = ",".join(["?" for i in range(len(self.TICKER_STATS))])
        insert_stmt = f"INSERT or REPLACE INTO ticker_stats ({columns}) VALUES ({qs});"
        with self.cursor_execute(self.db, insert_stmt, params=to_insert, many=True) as curr:
            inserted = curr.rowcount

    def get_latest_ticker_stats(self):
        query = "SELECT MAX(ts) FROM ticker_stats"
        with self.cursor_execute(self.db, query) as curr:
            result = curr.fetchone()
            return result[0]

    def get_db_tickers(self):
        query = "SELECT symbol FROM tickers"
        with self.cursor_execute(self.db, query) as curr:
            results = curr.fetchall()
            return set((r[0] for r in results))
    
    def _remove_duplicates(self, batch):
        query = "SELECT symbol, ts FROM ticker_stats"
        with self.cursor_execute(self.db, query) as curr:
            results = set(curr.fetchall())
        batch = [b for b in batch if (b["symbol"], self.start_time) not in results]
        return batch

    def _handle_batch(self, batch):
        batch = self._remove_duplicates(batch)
        self.insert_ticker_stats(batch)
        
    def _run(self):
        tickers_in_db = self.get_db_tickers()
        latest_ticker_stat = self.get_latest_ticker_stats()

        # set self.trs
        self.get_tickers()

        batch = []
        for record in self.tickers:
            self.inserted += 1
            batch.append(record)
            if record["symbol"] not in tickers_in_db:
                self.insert_ticker(record)
            
            if len(batch) == 100:
                self._handle_batch(batch)
                batch = []
            else:
                continue

        if batch:
            self._handle_batch(batch)

        tickers_added = self.get_db_tickers() - tickers_in_db
        if tickers_added:
            tickers_added = ",".join(tickers_added)
            print(f"Added new tickers: {tickers_added}")

        print(f"Added {self.inserted} new ticker_stats")