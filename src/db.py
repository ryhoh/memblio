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
SELECT book.title, own.isbn13, own.media_name, NULL AS is_read, book.thumbnail
FROM own
JOIN book
ON own.isbn13 = book.isbn13
ORDER BY book.title ASC, own.isbn13 ASC;
            """)
            res = cur.fetchall()
    return [list(row[:4]) + [base64.b64encode(row[4]).decode('utf-8')] for row in res]


def select_existing_books_with_user(user_name: str) -> List[Tuple]:
    """
    
    :return: title, isbn13, media_name, thumbnail
    """
    with psycopg2.connect(DB) as sess:
        with sess.cursor() as cur:
            cur.execute("""
SELECT book.title, own.isbn13, own.media_name,
	CASE
		WHEN EXISTS
			(SELECT read_book.read_book_id 
			FROM read_book
			WHERE read_book.user_name = %s AND own.own_id = read_book.own_id) THEN true
		ELSE false
	END AS is_read,
    book.thumbnail
FROM own
JOIN book ON own.isbn13 = book.isbn13
ORDER BY book.title ASC, own.isbn13 ASC;
            """, (user_name,))
            res = cur.fetchall()
    return [list(row[:4]) + [base64.b64encode(row[4]).decode('utf-8')] for row in res]


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


if __name__ == '__main__':
    import scraper
    register_book('9784873117584')
    register_own('9784873117584', 'paper', 'ryhoh')
