import base64
import os
from typing import List, Optional, Tuple

import psycopg2
from psycopg2.errors import ForeignKeyViolation, UniqueViolation

from src import scraper


DB = os.environ.get('DATABASE_URL') or 'postgres://web:web@127.0.0.1:5432/memblio'

with open('static/no_image.jpg', 'rb') as f:
    no_image = f.read()

with psycopg2.connect(DB) as sess:
    with sess.cursor() as cur:
        cur.execute("SELECT name FROM media;")
        media_names = sorted(elm[0] for elm in cur.fetchall())
        cur.execute("SELECT user_name FROM users;")
        user_names = sorted(elm[0] for elm in cur.fetchall())
        cur.execute("SELECT address_name FROM shelf_address;")
        address_names = sorted(elm[0] for elm in cur.fetchall())


def encode_thumbnail(table):
    res = []
    for row in table:
        binary = no_image if row[5] is None else row[5]
        res.append(
            list(row[:5]) + [base64.b64encode(binary).decode('utf-8')] + list(row[6:])
        )
    return res


#######################
# SELECT Statements
#######################

def read_JWT_secret() -> str:
    """
    Read JWT secret

    :return: JWT secret
    """
    with psycopg2.connect(DB) as conn:
        with conn.cursor() as cur:
            cur.execute("select secret from jwt;")
            res: list[str] = cur.fetchone()
            return res[0]


def select_existing_books() -> List[Tuple]:
    """
    
    :return: title, isbn13, media_name, own_id, is_read, thumbnail, address_name
    """
    with psycopg2.connect(DB) as sess:
        with sess.cursor() as cur:
            cur.execute("""
SELECT book.title, own.isbn13, own.media_name, own.own_id, NULL AS is_read, book.thumbnail, sa.address_name
  FROM own
  JOIN book ON own.isbn13 = book.isbn13
  LEFT OUTER JOIN shelf_address sa ON own.shelf_address_id = sa.shelf_address_id 
 ORDER BY book.title ASC, own.isbn13 ASC;
            """)
            res = cur.fetchall()
    return encode_thumbnail(res)


def select_existing_books_with_user(user_name: str) -> List[Tuple]:
    """
    特定ユーザの読書状況を付与して書架全体をセレクトする
    
    :return: title, isbn13, media_name, own_id, is_read, thumbnail, address_name
    """
    with psycopg2.connect(DB) as sess:
        with sess.cursor() as cur:
            cur.execute("""
SELECT book.title, own.isbn13, own.media_name, own.own_id,
       COALESCE(is_read, 0) AS is_read, book.thumbnail, sa.address_name
  FROM book
  JOIN own ON book.isbn13 = own.isbn13
  LEFT OUTER JOIN (
       SELECT own_id, user_name, is_read
         FROM read_book
        WHERE user_name = %s
       ) AS rb 
    ON own.own_id = rb.own_id
  LEFT OUTER JOIN shelf_address sa ON own.shelf_address_id = sa.shelf_address_id 
 ORDER BY is_read ASC, book.title ASC, own.isbn13 ASC;
            """, (user_name,))
            res = cur.fetchall()
    return encode_thumbnail(res)


def read_password_from_users(name: str) -> bytes:
    """
    Read user's password

    :return: Hashed password if user exists.
    """
    with psycopg2.connect(DB) as conn:
        with conn.cursor() as cur:
            cur.execute("""
SELECT hashed_password
  FROM users
 WHERE user_name = %s;
            """, (name,))
            res = cur.fetchone()
            if res is None:
                raise ValueError("User not exist:", name)
            return res[0].tobytes()


#################################
# UPDATE and INSERT Statements
#################################

def register_book(isbn13: str) -> bool:
    """

    :param isbn13: isbn to register
    :return: True if registered
    """
    with psycopg2.connect(DB) as sess:
        with sess.cursor() as cur:
            cur.execute("SELECT isbn13 FROM book WHERE isbn13 = %s;", (isbn13,))
            if len(cur.fetchall()):
                return False  # Already registered
        
        book_info = scraper.request_book_info(isbn13)
        with sess.cursor() as cur:
            cur.execute("""
INSERT INTO book (isbn13, title, thumbnail)
VALUES (%s, %s, %s);
            """, (book_info['isbn13'], book_info['title'], book_info['thumbnail']))


def register_own(isbn13: str, media_name: str, own_user: str, address: Optional[str]):
    with psycopg2.connect(DB) as sess:
        with sess.cursor() as cur:
            try:
                if address is None:
                    cur.execute("""
INSERT INTO own (isbn13, media_name, own_user)
VALUES (%s, %s, %s);
                    """, (isbn13, media_name, own_user))
                else:
                    cur.execute("""
INSERT INTO own (isbn13, media_name, own_user, shelf_address_id)
VALUES (%s, %s, %s,
              (SELECT shelf_address_id FROM shelf_address WHERE address_name = %s)
       );
                    """, (isbn13, media_name, own_user, address))
            except UniqueViolation:
                raise ValueError("UniqueViolation with", (isbn13, media_name, own_user))
            except ForeignKeyViolation:
                raise ValueError("ForeignKeyViolation with", (isbn13, media_name, own_user))


def upsert_read_book(user_name: str, own_id: int, is_read: int):
    with psycopg2.connect(DB) as sess:
        with sess.cursor() as cur:
            cur.execute("""
INSERT INTO read_book (user_name, own_id, is_read)
VALUES (%s, %s, %s)
    ON CONFLICT ON CONSTRAINT read_book_un
    DO
UPDATE SET is_read = %s;
            """, (user_name, own_id, is_read, is_read))


if __name__ == '__main__':
    import scraper
    register_book('9784873117584')
    register_own('9784873117584', 'paper', 'ryhoh')
