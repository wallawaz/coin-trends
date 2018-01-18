query_all_symbols = "SELECT symbol, name from tickers"

query_post_within_interval = (
    "SELECT post_id, comment "
    "FROM posts WHERE created_at > DATETIME(CURRENT_TIMESTAMP, '-{i} hour')"
)