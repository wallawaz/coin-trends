from contextlib import contextmanager

@contextmanager
def cursor_execute(connection, sql, params=[]):
    curr = connection.cursor()
    curr.execute(sql, params)
    connection.commit()
    yield curr
    curr.close()