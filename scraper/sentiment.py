from datetime import datetime
import json
import re
import time


from textblob import TextBlob
from .db import queries
from .base import Base
from .utils.constants import SKIP_TICKERS

class SentimentApp(Base):

    REFRESH_COIN_THRESHOLD = 3600

    def __init__(self):
        super(SentimentApp, self).__init__()

        # XXX Skip these ticker-symbols as they are too common
        self.skip_tickers = SKIP_TICKERS

        self.skip_names = set([
            "REAL",
            "FOR",
            "FORCE",
        ])
        self.printed_coins = set([])
        self.posts_to_update = []
        self.post_sentiments = []

    def set_duplicate_tickers(self):
        """Fetch a set of all ticker symbols with more than 1 name"""
        self.duplicate_tickers = dict()
        with self.cursor_execute(self.db, queries.query_duplicate_symbols) as curr:
            for result in curr.fetchall():
                self.duplicate_tickers[result[0]] = result[1]
            
            
    def set_all_coins(self):
        """Return list of tuples (symbol, name)"""
        with self.cursor_execute(self.db, queries.query_all_symbols) as curr:
            self.coins = curr.fetchall()

        self.coins_last_refreshed = datetime.utcnow()
    
    def get_posts_within_inverval(self, interval):
        """
        Return posts within `interval` number of hours
        param: interval (int). Number of hours back from current timestamp
        """
        query = queries.query_post_within_interval.format(i=interval)
        with self.cursor_execute(self.db, query) as curr:
            return curr.fetchall()
    
    def merge_post_text(self, posts):
        merged = [post[-1] for post in posts]
        if not merged:
            print("no posts!")
        return " ".join(merged)

    def get_top_ico_threads(self):
        """
        Return thread_ids with `ICO` mentioned
        """
        query = queries.query_top_icos
        with self.cursor_execute(self.db, query) as curr:
            return curr.fetchall()
    
    def clean_coins(self, coins):
        out_coins = []
        for coin in coins:
            symbol, name = coin

            skip = False # skip searching for this `symbol`.

            if symbol in self.skip_tickers:
                skip = True
            
            # some coin symbols are just numbers: `(42, 42-coin)`
            # we should only search for the name in this case
            if not skip:
                try:
                    skip = int(symbol)
                    skip = True
                except ValueError:
                    skip = False

            if skip and name in self.skip_names:
                continue
            factor = 1
            if symbol in self.duplicate_tickers:
                factor = self.duplicate_tickers[symbol]
            out_coins.append((skip, symbol, name, factor))

        return out_coins
            

    def parse(self, coins, text):

        tb = TextBlob(text)
        words = tb.words
        
        output = {}
        for record in coins:
            skip, symbol, name, factor = record

            if not skip:
                # note - words.count() is case-insensitive
                symbol_count = words.count(symbol)

            name_count = words.count(name)
            total_count = symbol_count + name_count
            if total_count > 0:
                output[symbol] = (
                    total_count / factor,
                    tb.sentiment.polarity,
                    tb.sentiment.subjectivity,
                )
        return output

    def display(self, coin_counts):
        results = {k: v for k, v in coin_counts.items() if v > 0 }
        return json.dumps(results)

    def get_posts_by_thread(self, thread_id):
        query = queries.query_posts_by_thread
        with self.cursor_execute(self.db, query, params=[thread_id]) as curr:
            return curr.fetchall()

    def get_posts_non_parsed(self):
        query = queries.query_posts_non_parsed
        with self.cursor_execute(self.db, query) as curr:
            return curr.fetchall()

    def update_post(self, post_id, parsed):

        self.posts_to_update.append(post_id)
        if len(self.posts_to_update) % 100 == 0:
            self._update_posts_is_parsed()

        if parsed:
            for symbol, stats in parsed.items():
                record = [post_id, symbol] + [*stats]
                self.post_sentiments.append(record)

            if symbol not in self.printed_coins:
                self.printed_coins.add(symbol)
                print(f"{symbol}: {stats}")
            
            if len(self.post_sentiments) % 100 == 0:
                self._insert_post_sentiments()
                
    def _update_posts_is_parsed(self):
        query = queries.query_update_is_parsed
        post_ids = "({})".format(",".join(str(p) for p in self.posts_to_update))
        with self.cursor_execute(self.db, query, params=[post_ids]) as curr:
            updated = curr.fetchall()
        self.posts_to_update = []

    def _insert_post_sentiments(self):
        insert_query = queries.query_insert_post_stats
        with self.cursor_execute(self.db, insert_query, params=self.post_sentiments, many=True) as curr:
            inserted = curr.fetchall()
        self.post_sentiments = []

    def _run(self):
        self.start_time = datetime.utcnow()

        def refresh():
            self.set_all_coins()
            self.set_duplicate_tickers()
            self.coins = self.clean_coins(self.coins)
            
        self.connect_to_db()
        refresh()
            
        while True:
            total_parsed = 0
            for post_id, post_comment in self.get_posts_non_parsed():
                parsed = self.parse(self.coins, post_comment)
                total_parsed += 1

                # if parsed in non-empty dict - insert into post_sentiment
                self.update_post(post_id, parsed)
                if total_parsed  % 1000 == 0:
                    print(f"total_parsed: {total_parsed}, last post_id: {post_id}")

            if (datetime.utcnow() - self.coins_last_refreshed).seconds > self.REFRESH_COIN_THRESHOLD:
                refresh()

            if self.posts_to_update:
                self._update_posts_is_parsed()
            if self.post_sentiments:
                self._insert_post_sentiments()
            
            print("done parsing - sleep 15")
            time.sleep(15)