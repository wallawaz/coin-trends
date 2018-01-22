query_all_symbols = "SELECT symbol, name from tickers"

query_post_within_interval = (
    "SELECT post_id, comment "
    "FROM posts WHERE created_at > DATETIME(CURRENT_TIMESTAMP, '-{i} hour')"
)

query_ico_threads = (
    "SELECT last_post, thread_id, subject, post_id, comment "
    "FROM threads join posts using (thread_id) "
    "WHERE UPPER(threads.subject) LIKE '%ICO%'"
)

query_top_icos = (
    "SELECT last_post, thread_id, subject, count(post_id) as post_count "
    "FROM threads join posts using (thread_id) "
    "WHERE UPPER(threads.subject) LIKE '%ICO%' "
    "GROUP BY thread_id "
    "ORDER BY post_count desc LIMIT 10"
)

query_posts_by_thread = (
    "SELECT post_id, created_at, comment "
    "FROM posts "
    "WHERE thread_id = ?"
)