import os

import psycopg2


DB = os.environ.get('DATABASE_URL')


def connect():
    if DB is None:
        return psycopg2.connect(host="localhost", user="tester", password="tester", database="memblio")
    else:
        return psycopg2.connect(DB)


def query_all():
    order = """
    SELECT book.id, book.name, book.isbn, media.name, book.author
    FROM book
    JOIN media
    ON book.media_id = media.id;
    """

    with connect() as sess:
        with sess.cursor() as cur:
            cur.execute(order)
            res = cur.fetchall()

    return res
