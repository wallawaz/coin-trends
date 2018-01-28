import os
import sqlite3

from scraper.utils import cursor_execute

drop_statements = [
    "DROP TABLE IF EXISTS threads;",
    "DROP TABLE IF EXISTS posts;",
    "DROP TABLE IF EXISTS tickers;",
    "DROP TABLE IF EXISTS ticker_stats;"
]
create_statements = [
    """
        CREATE TABLE IF NOT EXISTS threads (
        thread_id INTEGER,
        last_post TIMESTAMP NOT NULL,
        subject TEXT,
        PRIMARY KEY (thread_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS posts (
        post_id INTEGER,
        thread_id INTEGER,
        created_at TIMESTAMP,
        comment TEXT,
        is_parsed BOOLEAN DEFAULT 0,
        PRIMARY KEY (post_id, thread_id),
        FOREIGN KEY (thread_id) REFERENCES threads (thread_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS post_sentiment (
        post_id INTEGER,
        symbol TEXT,
        mentions REAL,
        sentiment REAL,
        polarity REAL,
        PRIMARY KEY (post_id, symbol),
        FOREIGN KEY (post_id) REFERENCES posts (post_id),
        FOREIGN KEY (symbol) REFERENCES tickers (symbol)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS tickers (
        symbol TEXT,
        name TEXT,
        primary key (symbol, name)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS ticker_stats (
        symbol TEXT,
        ts TIMESTAMP,
        cap NUMERIC,
        price_usd NUMERIC,
        circ_supply NUMERIC,
        volume_24 NUMERIC,
        change_hr NUMERIC,
        change_day NUMERIC,
        change_week NUMERIC,
        PRIMARY KEY (symbol, ts),
        FOREIGN KEY (symbol) REFERENCES tickers (symbol)
    );
    """,
]

class DBCreator:
    def __init__(self, drop_first=True):
        self.drop_first = drop_first
        self.drop_statements = drop_statements
        self.create_statements = create_statements
        db_path = os.getenv("FOUR_CHAN_DB", "four_chan.sqlite")
        self.db = sqlite3.connect(db_path, check_same_thread=False)

    def run(self):

        if self.drop_first:
            statements = self.drop_statements + self.create_statements
        else:
            statements = self.create_statements
        
        for statement in statements:
            with cursor_execute(self.db, statement) as curr:
                _ = curr.rowcount