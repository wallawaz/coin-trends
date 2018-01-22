import basc_py4chan
from datetime import datetime, timedelta
import os
import time
import random
from requests.exceptions import HTTPError

from .base import Base


def utc_to_datetime(x):
    try:
        x = datetime.utcfromtimestamp(int(x))
    except ValueError:
        x = datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
    return x

class FourChanBoardScraper(Base):

    THREAD_THRESHOLD = 210
    CACHE_THRESHOLD = 1200

    def __init__(self, board):
        super(FourChanBoardScraper, self).__init__()
        self.board = basc_py4chan.Board(board)
        self.threads = []
        self.last_clear_cache = datetime.now()
        self.idx = None
    
    def reset(self):
        self.board.clear_cache()
        self.threads = self.board.get_all_threads()
        self.last_clear_cache = datetime.now()
        self.idx = None

    def update_idx(self):
        """Update the index in self.threads"""
        if not self.idx:
            self.idx = len(self.threads) - 1
            return

        self.idx = self.idx - 1
        if self.idx < 0:
            self.idx = len(self.threads) - 1

    def get_thread(self, thread_id):
        query = "SELECT thread_id, last_post from threads where thread_id = ?"
        with self.cursor_execute(self.db, query, params=[thread_id]) as curr:
            thread = curr.fetchone()
            if thread:
                return (thread[0], utc_to_datetime(thread[1]))
            
        return None

    def update_thread(self):
        self.update_idx()
        thread = self.threads[self.idx]
        
        existing_thread = self.get_thread(thread.id)
        if existing_thread:
            if ((datetime.now() - existing_thread[-1]).seconds
                > self.THREAD_THRESHOLD):
                self.threads[self.idx] = thread
                ins = self._insert_posts(
                    thread,
                    last_post=existing_thread[-1]
                )
        else:
            print("new thread: ", thread.id)
            self.threads[self.idx] = thread
            updated_thread = self._insert_new_thread(thread)
            if updated_thread:
                ins = self._insert_posts(updated_thread)
            
    
    def _insert_new_thread(self, thread):
        try:
            thread.update()
        except HTTPError as e:
            print(e)
            time.sleep(3)
            return None

        last_post = sorted(
            (p.timestamp for p in thread.posts),
            reverse=True
        )
        last_post = last_post[0]
        subject = thread.topic.subject

        insert_stmt = (
            "INSERT OR REPLACE INTO threads (thread_id, last_post, subject) "
            "VALUES (?, ?, ?);"
        )
        params = [thread.id, last_post, subject]
        with self.cursor_execute(self.db, insert_stmt, params=params) as curr:
            _ = curr.rowcount

        return thread


    def _insert_posts(self, thread, last_post=None):
        records = []
        max_fetched_post = datetime(1970, 1, 1)
        ins = 0
            
        insert_posts_stmt = (
            "INSERT INTO posts (post_id, thread_id, created_at, comment) "
            "VALUES (?, ?, ?, ?);" 
        )
        if last_post:
            print ("{}: posts must be > {}".format(thread.id, last_post))
            try:
                thread.update()
            except HTTPError as e:
                print(e)
                time.sleep(3)
                return 0
        
        for post in thread.posts:
            utc_dt = utc_to_datetime(post.timestamp)
            if utc_dt > max_fetched_post:
                max_fetched_post = utc_dt

            # post for this thread we have not seen before
            if not last_post or (last_post and utc_dt > last_post):
                records.append(
                    (post.number, thread.id, utc_dt, post.text_comment)
                )

        for record in records:
            with self.cursor_execute(self.db, insert_posts_stmt, params=record) as curr:
                ins = curr.rowcount

        if last_post and max_fetched_post > last_post:
            update_stmt = "UPDATE threads SET last_post = ? WHERE thread_id = ?"
            params = [max_fetched_post, thread.id]
            with self.cursor_execute(self.db, update_stmt, params=params) as curr:
                _ = curr.rowcount

        return ins

    def _run(self):
        
        while True:
            if not self.threads:
                print("reset: no threads")
                self.reset()

            if (datetime.now() - self.last_clear_cache).seconds > self.CACHE_THRESHOLD:
                print("reset: CACHE_THRESHOLD")
                self.reset()

            self.update_thread()
            time.sleep(1.5)
