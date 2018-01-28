query_all_symbols = "SELECT symbol, name from tickers"

query_duplicate_symbols = (
   "SELECT symbol, count(name) "
    "FROM tickers "
    "GROUP BY symbol "
    "HAVING COUNT(name) > 1"
)
query_insert_post_stats = (
    "INSERT INTO post_sentiment (post_id, symbol, mentions, sentiment, polarity) "
    "VALUES (?, ?, ?, ?, ?)"
)

query_ico_threads = (
    "SELECT last_post, thread_id, subject, post_id, comment "
    "FROM threads join posts using (thread_id) "
    "WHERE UPPER(threads.subject) LIKE '%ICO%'"
)

query_post_within_interval = (
    "SELECT post_id, comment "
    "FROM posts WHERE created_at > DATETIME(CURRENT_TIMESTAMP, '-{i} hour')"
)

query_symbol_mentions_within_interval = (
    "SELECT symbol, SUM(mentions)"
    "FROM posts JOIN post_sentiment USING (post_id) "
    "WHERE created_at > DATETIME(CURRENT_TIMESTAMP, '-{i} hour') "
    "GROUP BY symbol "
    "ORDER BY SUM(mentions) desc"
)

query_posts_by_thread = (
    "SELECT post_id, created_at, comment "
    "FROM posts "
    "WHERE thread_id = ?"
)

query_posts_non_parsed = (
    "SELECT post_id, comment "
    "FROM posts WHERE is_parsed = 0"
)

query_top_icos = (
    "SELECT last_post, thread_id, subject, count(post_id) as post_count "
    "FROM threads join posts using (thread_id) "
    "WHERE UPPER(threads.subject) LIKE '%ICO%' "
    "GROUP BY thread_id "
    "ORDER BY post_count desc LIMIT 10"
)

query_update_is_parsed = (
    "UPDATE posts set is_parsed = 1 WHERE post_id IN (?)"
)
