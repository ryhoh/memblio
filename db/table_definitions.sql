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
	is_read bool NOT NULL DEFAULT false,
	CONSTRAINT read_book_pk PRIMARY KEY (read_book_id),
	CONSTRAINT read_book_un UNIQUE (user_name, own_id),
	CONSTRAINT read_book_fk_own FOREIGN KEY (own_id) REFERENCES public.own(own_id) ON DELETE CASCADE ON UPDATE RESTRICT,
	CONSTRAINT read_book_fk_user FOREIGN KEY (user_name) REFERENCES public."user"(user_name) ON DELETE RESTRICT ON UPDATE CASCADE
);

--------------------
-- Data Insertion
--------------------

insert into media values
	('paper'),
	('kindle'),
	('pdf'),
	('epub');

INSERT INTO public."user" (user_name) VALUES
	('ryhoh'),
	('testuser');

INSERT INTO public.book (isbn13,title,thumbnail) VALUES
	('9784873117584','ゼロから作るDeep Learning',NULL),
	('9784774192239','PythonユーザのためのJupyter「実践」入門',NULL),
	('9784297100919','Vue.js入門',NULL),
	('9784297100896','内部構造から学ぶPostgreSQL設計・運用計画の鉄則',NULL);

INSERT INTO public.own (isbn13,media_name,own_user) VALUES
	('9784873117584','paper','ryhoh'),
	('9784774192239','paper','ryhoh'),
	('9784297100896','kindle','ryhoh'),
	('9784297100919','kindle','testuser');

INSERT INTO public.read_book (user_name,own_id,is_read) VALUES
	('testuser',1,true),
	('ryhoh',1,true),
	('ryhoh',2,true),
	('ryhoh',3,false),
	('testuser',4,true);
