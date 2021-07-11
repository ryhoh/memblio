import base64
import os
from typing import List, Tuple

import psycopg2
from psycopg2.errors import ForeignKeyViolation, UniqueViolation

from src import scraper


DB = os.environ.get('DATABASE_URL') or 'postgres://web:web@127.0.0.1:5432/memblio'


def select_existing_books() -> List[Tuple]:
    """
    
    :return: title, isbn13, media_name, thumbnail
    """
    with psycopg2.connect(DB) as sess:
        with sess.cursor() as cur:
            cur.execute("""
SELECT book.title, own.isbn13, own.media_name, book.thumbnail
FROM own
JOIN book
ON own.isbn13 = book.isbn13;
            """)
            res = cur.fetchall()


    return [list(row[:3]) + [base64.b64encode(row[3]).decode('utf-8')] for row in res]


# def select_books() -> pd.DataFrame:
#     book_df = pd.read_csv(os.path.join('db/', 'book.csv'))
#     media_df = pd.read_csv(os.path.join('db/', 'media.csv'))
#     own_df = pd.read_csv(os.path.join('db/', 'own.csv'))

#     own_book_df = own_df \
#         .merge(book_df, how='inner', on='isbn13') \
#         .merge(media_df, how='inner', left_on='media_name', right_on='media_name')

#     return own_book_df


def register_book(isbn13: str) -> bool:
    """

    :param isbn13: isbn to register
    :return: True if registered
    """
    with psycopg2.connect(DB) as sess:
        with sess.cursor() as cur:
            cur.execute("""SELECT isbn13 FROM book WHERE isbn13 = %s;""", (isbn13,))
            if len(cur.fetchall()):
                return False  # Already registered
        
        book_info = scraper.request_book_info(isbn13)
        with sess.cursor() as cur:
            cur.execute("""
INSERT INTO book (isbn13, title, thumbnail)
VALUES (%s, %s, %s);
            """, (book_info['isbn13'], book_info['title'], book_info['thumbnail']))


def register_own(isbn13: str, media_name: str, own_user: str):
    with psycopg2.connect(DB) as sess:
        with sess.cursor() as cur:
            try:
                cur.execute("""
INSERT INTO own (isbn13, media_name, own_user)
VALUES (%s, %s, %s);
                """, (isbn13, media_name, own_user))
            except UniqueViolation:
                raise ValueError("UniqueViolation with", (isbn13, media_name, own_user))
            except ForeignKeyViolation:
                raise ValueError("ForeignKeyViolation with", (isbn13, media_name, own_user))


# def insert_book(info: Dict, media: str) -> None:
#     order_media_id = """
#     SELECT media.id
#     FROM media
#     WHERE media.name = %s;
#     """

#     order_insert = """
#     INSERT INTO book (name, isbn, author, media_id)
#     VALUES (%s, %s, %s, %s);
#     """

#     if media not in MEDIA:
#         raise ValueError('supported media:', MEDIA, 'but given', media)

#     with _connect() as sess:
#         with sess.cursor() as cur:
#             cur.execute(order_media_id, (media,))
#             media_id = cur.fetchone()[0]  # scalar
#             cur.execute(order_insert, (info['title'], info['isbn'], info['author'], media_id))
#         sess.commit()


if __name__ == '__main__':
    import scraper
    register_book('9784873117584')
    register_own('9784873117584', 'paper', 'ryhoh')