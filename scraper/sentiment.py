import json
import time

from pprint import PrettyPrinter
from textblob import TextBlob
from .db import queries
from .base import Base

class SentimentApp(Base):
    def __init__(self):
        super(SentimentApp, self).__init__()

    def get_all_coins(self):
        """Return list of tuples (symbol, name)"""
        with self.cursor_execute(self.db, queries.query_all_symbols) as curr:
            return curr.fetchall()
    
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

    def get_word_counts(self, records, text):
        tb = TextBlob(text)
        words = tb.words
        
        output = {}
        for record in records:
            symbol, name = record

            # some coin symbols are just numbers: `(42, 42-coin)`
            # we should only search for the name in the case
            try:
                symbol = int(symbol)
                symbol = None
                symbol_count = 0
            except ValueError:
                continue
            if symbol:
                symbol_count = words.count(symbol)

            name_count = tb.word_counts[name]
            output[record[0]] = symbol_count + name_count
        return output

    def display(self, coin_counts):
        results = {k: v for k, v in coin_counts.items() if v > 0 }
        return json.dumps(results)


    def get_posts_by_thread(self, thread_id):
        query = queries.query_posts_by_thread
        with self.cursor_execute(self.db, query, params=[thread_id]) as curr:
            return curr.fetchall()

    def _run(self):
        pp = PrettyPrinter()
        self.connect_to_db()
        self.coins = self.get_all_coins()

        while True:
            posts = self.get_posts_within_inverval(1)
            posts_text = self.merge_post_text(posts)
            coin_counts = self.get_word_counts(self.coins, posts_text)
            print("-"*20)
            pp.pprint(self.display(coin_counts))
            print("-"*20)
            time.sleep(60)
            print("\n")