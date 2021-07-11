--------------------
-- Sequence Definition
--------------------

-- DROP SEQUENCE public.own_own_id_seq;
CREATE SEQUENCE public.own_own_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;

-- DROP SEQUENCE public.read_book_read_book_id_seq;
CREATE SEQUENCE public.read_book_read_book_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;-- public.book definition

--------------------
-- Table Definition
--------------------

-- DROP TABLE public.book;
CREATE TABLE public.book (
	isbn13 bpchar(13) NOT NULL,
	title varchar(63) NOT NULL,
	thumbnail bytea NULL,
	CONSTRAINT book_pk PRIMARY KEY (isbn13)
);
CREATE UNIQUE INDEX book_isbn13_idx ON public.book USING btree (isbn13);

-- DROP TABLE public.media;
CREATE TABLE public.media (
	"name" varchar(15) NOT NULL,
	CONSTRAINT media_pk PRIMARY KEY (name)
);

-- DROP TABLE public."user";
CREATE TABLE public."user" (
	user_name varchar(15) NOT NULL,
	CONSTRAINT user_pk PRIMARY KEY (user_name)
);

-- DROP TABLE public.own;
CREATE TABLE public.own (
	own_id serial NOT NULL,
	isbn13 bpchar(13) NOT NULL,
	media_name varchar(15) NOT NULL,
	own_user varchar(15) NOT NULL,
	CONSTRAINT own_pk PRIMARY KEY (own_id),
	CONSTRAINT own_un UNIQUE (isbn13, media_name),
	CONSTRAINT own_fk_isbn13 FOREIGN KEY (isbn13) REFERENCES public.book(isbn13) ON DELETE RESTRICT ON UPDATE RESTRICT,
	CONSTRAINT own_fk_media FOREIGN KEY (media_name) REFERENCES public.media("name") ON DELETE RESTRICT ON UPDATE CASCADE,
	CONSTRAINT own_fk_user FOREIGN KEY (own_user) REFERENCES public."user"(user_name) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- DROP TABLE public.read_book;
CREATE TABLE public.read_book (
	read_book_id serial NOT NULL,
	user_name varchar(15) NOT NULL,
	own_id int4 NOT NULL,
	CONSTRAINT read_book_pk PRIMARY KEY (read_book_id),
	CONSTRAINT read_book_un UNIQUE (user_name, own_id),
	CONSTRAINT read_book_fk_own FOREIGN KEY (own_id) REFERENCES public.own(own_id) ON DELETE CASCADE ON UPDATE RESTRICT,
	CONSTRAINT read_book_fk_user FOREIGN KEY (user_name) REFERENCES public."user"(user_name) ON DELETE RESTRICT ON UPDATE CASCADE
);

--------------------
-- Data Insertion
--------------------

insert into "user" values ('ryhoh');

insert into media values
	('paper'),
	('kindle'),
	('pdf'),
	('epub')
;
