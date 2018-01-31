query_all_symbols = "SELECT symbol, name from tickers"

query_duplicate_symbols = (
   "SELECT symbol, count(name) "
    "FROM tickers "
    "GROUP BY symbol "
    "HAVING COUNT(name) > 1"
)
query_insert_post_stats = (
    "INSERT INTO post_sentiment (post_id, symbol, mentions, polarity, subjectivity) "
    "VALUES (?, ?, ?, ?, ?)"
)
query_insert_hourly_post_stats = (
    "INSERT INTO post_sentiment_hourly (datetime_hr, symbol, mentions_sum, polarity_sum, subjectivity_sum) "
    "VALUES (?, ?, ?, ?, ?)"
)
query_ico_threads = (
    "SELECT last_post, thread_id, subject, post_id, comment "
    "FROM threads join posts using (thread_id) "
    "WHERE UPPER(threads.subject) LIKE '%ICO%'"
)
query_min_max_post = (
    "SELECT "
        "datetime(strftime('%Y-%m-%dT%H:00:00', MIN(created_at))) as min, "
        "datetime(strftime('%Y-%m-%dT%H:00:00', MAX(created_at))) as max "
    "FROM posts join post_sentiment USING (post_id) "
    "WHERE datetime(strftime('%Y-%m-%dT%H:00:00', posts.created_at)) > ( "
        "select coalesce(max(datetime_hr), '1970-01-01') from post_sentiment_hourly "
    ")"
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

query_symbol_summary_hourly = (
    "SELECT ? as post_hour, symbol, sum(mentions), sum(sentiment), sum(polarity) "
    "FROM posts JOIN post_sentiment USING (post_id)  "
    "WHERE posts.is_parsed = 1 "
    "AND datetime(strftime('%Y-%m-%dT%H:00:00', created_at)) = ? "
    "GROUP BY post_hour, symbol "
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