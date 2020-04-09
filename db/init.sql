CREATE TABLE "media" (
  "id" SERIAL PRIMARY KEY,
  "name" VARCHAR(255) NOT NULL
);

CREATE TABLE "book" (
  "id" SERIAL PRIMARY KEY,
  "name" VARCHAR(255) NOT NULL,
  "isbn" CHAR(13),
  "media_id" INTEGER NOT NULL REFERENCES media(id),
  "author" VARCHAR(255) NOT NULL
);
