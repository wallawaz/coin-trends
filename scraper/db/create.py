import os
import sqlite3

from scraper.utils import cursor_execute

TABLES = {
    "threads": (
        "DROP TABLE IF EXISTS threads;",
        """
        CREATE TABLE IF NOT EXISTS threads (
        thread_id INTEGER,
        last_post TIMESTAMP NOT NULL,
        subject TEXT,
        PRIMARY KEY (thread_id)
        );
        """,
    ),
    "posts": (
        "DROP TABLE IF EXISTS posts;",
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
        """
    ),
    "tickers": (
        "DROP TABLE IF EXISTS tickers;",
        """
            CREATE TABLE IF NOT EXISTS tickers (
            symbol TEXT,
            name TEXT,
            primary key (symbol, name)
        );
        """
    ),
    "post_sentiment": (
        "DROP TABLE IF EXISTS post_sentiment;",
        """
            CREATE TABLE IF NOT EXISTS post_sentiment (
            post_id INTEGER,
            symbol TEXT,
            mentions REAL,
            polarity REAL,
            subjectivity REAL,
            PRIMARY KEY (post_id, symbol),
            FOREIGN KEY (post_id) REFERENCES posts (post_id),
            FOREIGN KEY (symbol) REFERENCES tickers (symbol)
        )
        """,
    ),
    "post_sentiment_hourly": (
        "DROP TABLE IF EXISTS post_sentiment_hourly;",
        """
            CREATE TABLE IF NOT EXISTS post_sentiment_hourly ( 
            datetime_hr TIMESTAMP, 
            symbol TEXT, 
            mentions_sum REAL, 
            sentiment_sum REAL, 
            polarity_sum REAL, 
            PRIMARY KEY (datetime_hr, symbol), 
            FOREIGN KEY (symbol) REFERENCES tickers (symbol) 
        );
        """
    ),
    "ticker_stats": (
        "DROP TABLE IF EXISTS ticker_stats;",
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
        """
    ),
}

class DBCreator:
    def __init__(self, drop_first=True):
        self.drop_first = drop_first
        db_path = os.getenv("FOUR_CHAN_DB", "four_chan.sqlite")
        self.db = sqlite3.connect(db_path, check_same_thread=False)

    def run(self):
        statements = []
        for t in TABLES.keys():
            if self.drop_first:
                statements.append(tables[0])
            statements.append(tables[1])
        
        for statement in statements:
            with cursor_execute(self.db, statement) as curr:
                _ = curr.rowcount