INSERT INTO account(email, username, password, is_admin, first_name, last_name)
VALUES ('cat@novelcat.com', 'cat', 'cat', TRUE, 'Cat', 'Nip');

INSERT INTO genre
VALUES ('adventure');

SELECT * FROM genre;

INSERT INTO book(author_id, title)
VALUES (1, 'a mystery');

INSERT INTO book_genre(book_id, genre)
VALUES (1, 'drama');

SELECT genre
FROM book NATURAL JOIN book_genre
WHERE book.title = 'a mystery'

SELECT column_name
FROM information_schema.columns
WHERE table_name   = 'book';

ALTER TABLE book
ADD summary TEXT;

select * from information_schema.table_constraints WHERE constraint_name like 'book_title%';

ALTER TABLE book DROP CONSTRAINT book_title_key;

ALTER TABLE chapter DROP COLUMN number;

UPDATE book
SET title = 'jungle book'
WHERE book_id = 1;


DROP TABLE IF EXISTS account, book, chapter, comment, follow, genre, book_genre, book_review, book_rating, book_save, book_comment, chapter_comment, chapter_view;

DROP TABLE IF EXISTS account;
CREATE TABLE account(
    user_id         SERIAL,
    email           VARCHAR(255) UNIQUE,
    username        VARCHAR(30) NOT NULL UNIQUE,
    password        VARCHAR(30) NOT NULL,
    is_admin        BOOLEAN NOT NULL DEFAULT FALSE,
    first_name      VARCHAR(30) NOT NULL,
    last_name       VARCHAR(30) NOT NULL,
    create_time     TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc'),
    website         VARCHAR(255),
    picture         BYTEA,
    PRIMARY KEY(user_id)
);


DROP TABLE IF EXISTS book;
CREATE TABLE book(
    book_id         SERIAL,
    author_id       SERIAL NOT NULL,
    title           VARCHAR(255) NOT NULL,
    summary         TEXT,
    create_time     TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc'),
    PRIMARY KEY (book_id),
    FOREIGN KEY (author_id) REFERENCES account(user_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);


DROP TABLE IF EXISTS chapter;
CREATE TABLE chapter(
    chapter_id      SERIAL,
    book_id         SERIAL NOT NULL,
    title           VARCHAR(30),
    view_count      INT NOT NULL DEFAULT 0,
    create_time     TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc'),
    update_time     TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc'),
    status          VARCHAR(30) NOT NULL DEFAULT 'draft',
    content         text,
    PRIMARY KEY (chapter_id),
    UNIQUE (book_id, chapter_id),
    FOREIGN KEY (book_id) REFERENCES book(book_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);


DROP TABLE IF EXISTS comment;
CREATE TABLE comment(
	comment_id      SERIAL,
	content         TEXT NOT NULL,
	create_time     TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc'),
	update_time     TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc'),
	PRIMARY KEY (comment_id)
);

DROP TABLE IF EXISTS follow;
CREATE TABLE follow(
	follower_id     SERIAL,
	followee_id     SERIAL,
	follow_time     TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc'),
	PRIMARY KEY (follower_id, followee_id),
	FOREIGN KEY (follower_id) REFERENCES account(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
	FOREIGN KEY (followee_id) REFERENCES account(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

DROP TABLE IF EXISTS genre;
CREATE TABLE genre(
	genre VARCHAR(30) PRIMARY KEY
);


DROP TABLE IF EXISTS book_genre;
CREATE TABLE book_genre(
	book_id SERIAL,
	genre VARCHAR(30),
	PRIMARY KEY (book_id, genre),
	FOREIGN KEY (book_id) REFERENCES book(book_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
	FOREIGN KEY (genre) REFERENCES genre(genre)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);


DROP TABLE IF EXISTS book_review;
CREATE TABLE book_review(
	book_id         SERIAL,
	user_id         SERIAL,
	title           VARCHAR(30) NOT NULL,
	content         TEXT NOT NULL,
	create_time     TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc'),
	update_time     TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc'),
	PRIMARY KEY (book_id, user_id),
	FOREIGN KEY (book_id) REFERENCES book(book_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
	FOREIGN KEY (user_id) REFERENCES account(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);


DROP TABLE IF EXISTS book_rating;
CREATE TABLE book_rating(
	book_id SERIAL,
	user_id SERIAL,
	rating DECIMAL(3,1) NOT NULL CHECK (rating >= 0.0 AND rating <= 10.0),
	PRIMARY KEY (book_id, user_id),
	FOREIGN KEY (book_id) REFERENCES book(book_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
	FOREIGN KEY (user_id) REFERENCES account(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);


DROP TABLE IF EXISTS book_save;
CREATE TABLE book_save(
	book_id SERIAL,
	user_id SERIAL,
	PRIMARY KEY (book_id, user_id),
	FOREIGN KEY (book_id) REFERENCES book(book_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
	FOREIGN KEY (user_id) REFERENCES account(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

DROP TABLE IF EXISTS book_comment;
CREATE TABLE book_comment(
	comment_id SERIAL,
	book_id SERIAL NOT NULL,
	user_id SERIAL NOT NULL,
	PRIMARY KEY (comment_id),
	FOREIGN KEY (comment_id) REFERENCES comment(comment_id)
		ON DELETE CASCADE
		ON UPDATE CASCADE,
	FOREIGN KEY (book_id) REFERENCES book(book_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
	FOREIGN KEY (user_id) REFERENCES account(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);


DROP TABLE IF EXISTS chapter_comment;
CREATE TABLE chapter_comment(
	comment_id SERIAL,
	chapter_id SERIAL NOT NULL,
	user_id SERIAL NOT NULL,
	PRIMARY KEY (comment_id),
	FOREIGN KEY (comment_id) REFERENCES comment(comment_id)
		ON DELETE CASCADE
		ON UPDATE CASCADE,
	FOREIGN KEY (chapter_id) REFERENCES chapter(chapter_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
	FOREIGN KEY (user_id) REFERENCES account(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

DROP TABLE IF EXISTS chapter_view;
CREATE TABLE chapter_view(
	chapter_id SERIAL,
	user_id SERIAL,
	view_time     TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc'),
	PRIMARY KEY (chapter_id, user_id, view_time),
	FOREIGN KEY (chapter_id) REFERENCES chapter(chapter_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
	FOREIGN KEY (user_id) REFERENCES account(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);