drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  title text not null,
  'text' text not null
);


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

INSERT INTO account(email, username, password, is_admin, first_name, last_name)
VALUES ('cat@novelcat.com', 'cat', 'cat', TRUE, 'Cat', 'Nip');

DROP TABLE IF EXISTS book;
CREATE TABLE book(
    book_id         SERIAL NOT NULL UNIQUE,
    author_id       SERIAL NOT NULL UNIQUE,
    title           VARCHAR(255) NOT NULL UNIQUE,
    create_time     TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc'),
    PRIMARY KEY (book_id),
    FOREIGN KEY (author_id) REFERENCES account(user_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);


DROP TABLE IF EXISTS chapter;
CREATE TABLE chapter(
    chapter_id      SERIAL NOT NULL UNIQUE,
    book_id         SERIAL NOT NULL UNIQUE,
    number          INT NOT NULL,
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
	comment_id      SERIAL NOT NULL UNIQUE,
	content         TEXT NOT NULL,
	create_time     TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc'),
	update_time     TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc'),
	PRIMARY KEY (comment_id)
);

