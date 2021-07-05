import os
from typing import Dict, List, Tuple

import psycopg2


DB = os.environ.get('DATABASE_URL')
MEDIA = frozenset({'紙', 'kindle'})


def _connect():
    if DB is None:
        return psycopg2.connect(host="localhost", user="tester", password="tester", database="memblio")
    else:
        return psycopg2.connect(DB)


def select_all() -> List[Tuple]:
    order = """
    SELECT book.id, book.name, book.isbn, media.name, book.author
    FROM book
    JOIN media
    ON book.media_id = media.id;
    """

    with _connect() as sess:
        with sess.cursor() as cur:
            cur.execute(order)
            res = cur.fetchall()

    return res


def insert_book(info: Dict, media: str) -> None:
    order_media_id = """
    SELECT media.id
    FROM media
    WHERE media.name = %s;
    """

    order_insert = """
    INSERT INTO book (name, isbn, author, media_id)
    VALUES (%s, %s, %s, %s);
    """

    if media not in MEDIA:
        raise ValueError('supported media:', MEDIA, 'but given', media)

    with _connect() as sess:
        with sess.cursor() as cur:
            cur.execute(order_media_id, (media,))
            media_id = cur.fetchone()[0]  # scalar
            cur.execute(order_insert, (info['title'], info['isbn'], info['author'], media_id))
        sess.commit()
