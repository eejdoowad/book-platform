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
