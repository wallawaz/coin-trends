from contextlib import contextmanager

@contextmanager
def cursor_execute(connection, sql, params=[], many=False):
    curr = connection.cursor()
    if many:
        curr.executemany(sql, params)
    else:
        curr.execute(sql, params)
    connection.commit()
    yield curr
    curr.close()