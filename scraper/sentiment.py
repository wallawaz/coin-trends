import os
import sqlite3
from textblob import TextBlob

from .utils import cursor_execute
from .db import queries


class SentimentApp:
    def __init__(self):
        self.connect_to_db()
    
    def connect_to_db(self):
        db_path = os.getenv("FOUR_CHAN_DB", "four_chan.sqlite")
        self.db = sqlite3.connect(db_path, check_same_thread=False)

    def get_all_coins(self):
        """Return list of tuples (symbol, name)"""
        with cursor_execute(self.db, queries.query_all_symbols) as curr:
            return curr.fetchall()
    
    def get_posts_within_inverval(self, interval):
        """
        Return posts within `interval` number of hours
        param: interval (int). Number of hours back from current timestamp
        """
        query = queries.query_post_within_interval.format(i=interval)
        with cursor_execute(self.db, query) as curr:
            return curr.fetchall()
    
    def merge_post_text(self, posts):
        merged = [post[-1] for post in posts]
        return " ".join(merged)
    

    def get_word_counts(self, records, text):
        tb = TextBlob(text)
        output = {record[0]: 0 for record in records}

        for record in records:
            symbol_count = tb.word_counts[record[0]]
            name_count = tb.word_counts[record[1]]
            output[record[0]] = symbol_count + name_count
        return output
        
