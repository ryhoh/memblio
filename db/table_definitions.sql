--------------------
-- Sequence Definition
--------------------

CREATE SEQUENCE public.own_own_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;

CREATE SEQUENCE public.read_book_read_book_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;

CREATE SEQUENCE public.shelf_address_shelf_address_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;

--------------------
-- Table Definition
--------------------

CREATE TABLE public.book (
	isbn13 bpchar(13) NOT NULL,
	title varchar(63) NOT NULL,
	thumbnail bytea NULL,
	CONSTRAINT book_pk PRIMARY KEY (isbn13)
);
CREATE UNIQUE INDEX book_isbn13_idx ON public.book USING btree (isbn13);

CREATE TABLE public.media (
	"name" varchar(15) NOT NULL,
	CONSTRAINT media_pk PRIMARY KEY (name)
);

CREATE TABLE public.users (
	user_name varchar(15) NOT NULL,
       hashed_password BYTEA NOT NULL,
	CONSTRAINT user_pk PRIMARY KEY (user_name)
);

CREATE TABLE public.shelf_address (
	shelf_address_id serial NOT NULL,
	address_name varchar(31),
	CONSTRAINT shelf_address_pk PRIMARY KEY (shelf_address_id)
);

CREATE TABLE public.own (
	own_id serial NOT NULL,
	isbn13 bpchar(13) NOT NULL,
	media_name varchar(15) NOT NULL,
	own_user varchar(15) NOT NULL,
	shelf_address_id int4,
	CONSTRAINT own_pk PRIMARY KEY (own_id),
	CONSTRAINT own_un UNIQUE (isbn13, media_name),
	CONSTRAINT own_fk_isbn13 FOREIGN KEY (isbn13) REFERENCES public.book(isbn13) ON DELETE RESTRICT ON UPDATE RESTRICT,
	CONSTRAINT own_fk_media FOREIGN KEY (media_name) REFERENCES public.media("name") ON DELETE RESTRICT ON UPDATE CASCADE,
	CONSTRAINT own_fk_user FOREIGN KEY (own_user) REFERENCES public.users(user_name) ON DELETE RESTRICT ON UPDATE CASCADE,
	CONSTRAINT own_fk_self_address_id FOREIGN KEY (shelf_address_id) REFERENCES public.shelf_address(shelf_address_id) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE public.read_book (
	read_book_id serial NOT NULL,
	user_name varchar(15) NOT NULL,
	own_id int4 NOT NULL,
	is_read int4 NOT NULL DEFAULT 0,
	CONSTRAINT read_book_pk PRIMARY KEY (read_book_id),
	CONSTRAINT read_book_un UNIQUE (user_name, own_id),
	CONSTRAINT read_book_fk_own FOREIGN KEY (own_id) REFERENCES public.own(own_id) ON DELETE CASCADE ON UPDATE RESTRICT,
	CONSTRAINT read_book_fk_user FOREIGN KEY (user_name) REFERENCES public.users(user_name) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE public.jwt (
       secret CHAR(64) NOT NULL
);

--------------------
-- Data Insertion
--------------------

insert into media values
	('paper'),
	('kindle'),
	('pdf'),
	('epub');

INSERT INTO public.users (user_name, hashed_password) VALUES
	('ryhoh',    '$2b$12$uWqI2KUFmu9j.FBetR0HGOiXYLeeTNWrlBq0skxYi2iHChhm35vT.'),
	('testuser', '$2b$12$uWqI2KUFmu9j.FBetR0HGOiXYLeeTNWrlBq0skxYi2iHChhm35vT.');

INSERT INTO public.shelf_address (address_name) VALUES
	('実家'),
	('TK308');

INSERT INTO public.book (isbn13,title,thumbnail) VALUES
	('9784873117584','ゼロから作るDeep Learning',NULL),
	('9784774192239','PythonユーザのためのJupyter「実践」入門',NULL),
	('9784297100919','Vue.js入門',NULL),
	('9784297100896','内部構造から学ぶPostgreSQL設計・運用計画の鉄則',NULL);

INSERT INTO public.own (isbn13,media_name,own_user,shelf_address_id) VALUES
	('9784873117584','paper','ryhoh',1),
	('9784774192239','paper','ryhoh',2),
	('9784297100896','kindle','ryhoh',NULL),
	('9784297100919','kindle','testuser',NULL);

INSERT INTO public.read_book (user_name,own_id,is_read) VALUES
	('testuser',1,1),
	('ryhoh',1,1),
	('ryhoh',2,2),
	('ryhoh',3,0),
	('testuser',4,2);

INSERT INTO public.jwt VALUES
       ('cc125635c56e2b29e842b7c520a5304eda31c3f0d409c09a911bcc5e742dcd60');
