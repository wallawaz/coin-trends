import os
import sqlite3

from scraper.utils import cursor_execute


class Base:

    def __init__(self):
        self.db_path = os.getenv("FOUR_CHAN_DB", "four_chan.sqlite")
        self.cursor_execute = cursor_execute
    
    def connect_to_db(self):
        self.db = sqlite3.connect(self.db_path, check_same_thread=False)
        self.db_safe = sqlite3.connect(self.db_path, check_same_thread=True)


    def reset(self):
        pass

    def run(self):
        self.connect_to_db()
        self._run()
        pass

    def _run(self):
        pass