from app import app, cur, conn
from psycopg2.extensions import AsIs
import functools



####################################
# Helper Queries
####################################

def key_available(table, column, value):
    cur.execute('''
      SELECT DISTINCT TRUE FROM %(table)s WHERE %(column)s = %(value)s;''', {
          "table": AsIs(table),
          "column": AsIs(column),
          "value": value
      })
    return cur.fetchone() == None



####################################
# Authentication Queries
####################################

def register_user(form):
    try:
        admin = form.admin.data == app.config['ADMIN_SECRET']
        cur.execute('''
            INSERT INTO account
                (username, email, password, is_admin, first_name, last_name)
            VALUES
                (%s, %s, %s, %s, %s, %s);''',
            (form.username.data, form.email.data, form.password.data, admin, form.first_name.data, form.last_name.data))
        conn.commit()
    except Exception as e:
        print(e, file=stderr)

def get_user(username):
    cur.execute("SELECT * FROM account WHERE username = %s", (username,))
    return cur.fetchone()

def get_account(**kwargs):
    if len(kwargs) != 1:
        raise Exception('Only one arg must be specified')
    key, value = kwargs.popitem()
    if key not in ['username', 'email', 'user_id']:
        raise Exception('Invalid column into table account')
    cur.execute('''
      SELECT * FROM account WHERE %(column)s = %(value)s;''', {
          "column": AsIs(key),
          "value": value
      })
    return cur.fetchone()



####################################
# General Queries
####################################



def gen_browse_query(entity, sort, order):
    order = 'ASC' if order == 'increasing' else 'DESC'
    if entity == 'book':
        popularity = '(r.votes + v.book_views) * (COALESCE(r.rating, 0) + 1)'
        sort = 'create_time' if sort == 'new' else popularity
        query = cur.mogrify('''
            WITH genres AS (
                    SELECT b.book_id, array_agg(bg.genre) FILTER(WHERE genre IS NOT NULL) AS genres
                    FROM book b
                    LEFT JOIN book_genre bg ON b.book_id = bg.book_id
                    GROUP BY b.book_id),
                chapters AS (
                    SELECT b.book_id, count(*) AS chapter_count
                    FROM book b
                    LEFT JOIN chapter c ON b.book_id = c.book_id
                    GROUP BY b.book_id),
                ratings AS (
                    SELECT b.book_id, AVG(r.rating) AS rating, COUNT(r.user_id) AS votes
                    FROM book b
                    LEFT JOIN book_rating r ON b.book_id = r.book_id
                    GROUP BY b.book_id),
                book_views AS (
                    WITH chapter_views as (
                        SELECT c.book_id, c.chapter_id, COUNT(v.user_id) AS chapter_views
                        FROM chapter c
                        LEFT JOIN chapter_view v ON c.chapter_id = v.chapter_id
                        GROUP BY c.chapter_id)
                    SELECT b.book_id, COALESCE(SUM(cv.chapter_views), 0) AS book_views
                    FROM book b
                    LEFT JOIN chapter_views cv ON b.book_id = cv.book_id
                    GROUP BY b.book_id)
            SELECT b.book_id, b.title, a.username AS author, g.genres, c.chapter_count AS chapters, v.book_views AS views, r.rating, r.votes, %s, b.create_time::date
            FROM book b
            LEFT JOIN account a ON b.author_id = a.user_id
            LEFT JOIN genres g ON b.book_id = g.book_id
            LEFT JOIN chapters c ON b.book_id = c.book_id
            LEFT JOIN ratings r ON b.book_id = r.book_id
            LEFT JOIN book_views v ON b.book_id = v.book_id
            ORDER BY %s %s''', (AsIs(popularity + ' AS popularity'), AsIs(sort), AsIs(order)))
    elif entity == 'chapter':
        sort = 'c.create_time' if sort == 'new' else 'c.view_count'
        query = cur.mogrify('''
            SELECT c.book_id, c.chapter_id, c.title, b.title AS book,
                row_number() over(PARTITION BY c.book_id ORDER BY chapter_id) AS chapter,
                c.view_count, c.create_time
            FROM chapter c
            LEFT JOIN book b ON c.book_id = b.book_id
            ORDER BY %s %s;''', (AsIs(sort), AsIs(order)))
    elif entity == 'author':
        sort = 'a.create_time' if sort == 'new' else 'follow_count.follow_count'
        query = cur.mogrify('''
            WITH user_book_count AS (
                SELECT a.user_id, COUNT(book_id) AS count
                FROM account a
                LEFT JOIN book b ON a.user_id = b.author_id
                GROUP BY a.user_id),
            follow_count AS (
                SELECT a.user_id, COUNT(f.follower_id) AS follow_count
                FROM account a
                LEFT JOIN follow f ON a.user_id = f.followee_id
                GROUP BY a.user_id)
            SELECT username, first_name, last_name, create_time AS joined, website, follow_count.follow_count AS followers, user_book_count.count AS books
            FROM account a
            LEFT JOIN user_book_count ON a.user_id = user_book_count.user_id
            LEFT JOIN follow_count ON a.user_id = follow_count.user_id
            ORDER BY %s %s;''', (AsIs(sort), AsIs(order)))
    else:
        raise Exception('Invalid entity made it through browse query')
    return query


def get_browse_data(entity, sort, order):
    cur.execute(gen_browse_query(entity, sort, order))  
    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    return {
        "table": entity,
        "columns": columns,
        "rows": rows
    }

####################################
# Book Queries
####################################

def add_rating(book_id, user_id, rating):
    cur.execute('''
        INSERT INTO book_rating (book_id, user_id, rating)
        VALUES (%s, %s, %s)
        ON CONFLICT (book_id, user_id) DO UPDATE
        SET rating = %s;''', (book_id, user_id, rating, rating))
    conn.commit()

def get_rating(book_id, user_id):
    cur.execute('''
        SELECT rating
        FROM book_rating
        WHERE book_id = %s AND user_id = %s;''', (book_id, user_id))
    row = cur.fetchone()
    if row: return row[0]
    return None

def get_genres():
    cur.execute(''' SELECT * FROM genre ORDER BY genre ASC;''')
    genres = [e[0] for e in cur.fetchall()]
    return genres

def get_book(book_id):
    cur.execute('''
        SELECT *
        FROM book
        WHERE book_id = %s''',
        (book_id,))    
    return cur.fetchone()

def get_book_plus(book_id):
    cur.execute('''
        SELECT b.book_id, b.title, a.username, b.author_id, b.summary, array_agg(bg.genre) AS genres, b.create_time::date
        FROM book b
        LEFT JOIN account a ON b.author_id = a.user_id
        LEFT JOIN book_genre bg ON b.book_id = bg.book_id
        WHERE b.book_id = %s
        GROUP BY b.book_id, a.username;''',
        (book_id,))    
    return cur.fetchone()

def add_book(author_id, title, summary=None):
    '''Inserts book and returns book_id'''
    cur.execute('''
        INSERT INTO book(author_id, title, summary)
        VALUES (%s, %s, %s)
        RETURNING book_id;''',
        (author_id, title, summary))
    return cur.fetchone()[0]

def add_book_genre(book_id, genre):
    cur.execute('''
        INSERT INTO book_genre(book_id, genre)
        VALUES (%s, %s);''',
        (book_id, genre))

def delete_book_genre(book_id, genre):
    cur.execute('''
        DELETE FROM book_genre
        WHERE book_id = %s AND genre = %s''',
        (book_id, genre))

def add_book_with_genres(author_id, title, genres, summary=None):
    book_id = add_book(author_id, title, summary)
    for genre in genres:
        add_book_genre(book_id, genre)
    conn.commit()
    return book_id

def edit_book_with_genres(book_id, title, new_genres, summary, old_genres):
    print(book_id, title, new_genres, summary, old_genres)
    print('asf')
    edit_book(book_id, title, summary)

    add_genres = [genre for genre in new_genres if genre not in old_genres]
    delete_genres = [genre for genre in old_genres if genre not in new_genres]
    
    for genre in add_genres:
        add_book_genre(book_id, genre)
    for genre in delete_genres:
        delete_book_genre(book_id, genre)

    conn.commit()

def edit_book(book_id, title, summary=None):
    cur.execute('''
        UPDATE book
        SET title = %s, summary = %s
        WHERE book_id = %s''',
        (title, summary, book_id))

def remove_book(book_id):
    cur.execute('''
        DELETE FROM book
        WHERE book_id = %s''',
        (book_id,))

def get_books_by_author(author_id):
    cur.execute('''
        SELECT *
        FROM book
        WHERE author_id = %s''',
        (author_id,))    
    return cur.fetchall()

def get_books_with_genre_by_author(author_id):
    cur.execute('''
        SELECT b.book_id, b.title, b.create_time::date, array_agg(bg.genre) as genres        
        FROM book b LEFT JOIN book_genre bg ON b.book_id = bg.book_id
        WHERE b.author_id = %s
        GROUP BY b.book_id;''',
        (author_id,))
    return cur.fetchall()

####################################
# Chapter Queries
####################################

def update_chapter_views(chapter_id, user_id):
    cur.execute('''
        INSERT INTO chapter_view (chapter_id, user_id)
        VALUES (2, 1);''', (chapter_id, user_id))
    conn.commit()

def add_chapter(book_id, title, content, status):
    '''Inserts chapter into given book and returns chapter_id'''
    cur.execute('''
        INSERT INTO chapter(book_id, title, content, status)
        VALUES (%s, %s, %s, %s)
        RETURNING chapter_id;''',
        (book_id, title, content, status))
    conn.commit()
    return cur.fetchone()[0]

def get_chapters_by_book(book_id):
    cur.execute('''
        WITH chapter_number AS (
            SELECT c.chapter_id, row_number() over(ORDER BY chapter_id) AS number
            FROM chapter c
            WHERE c.book_id = %s
            ORDER BY c.chapter_id ASC)
        SELECT *, row_number() over() AS number
        FROM chapter
        NATURAL JOIN chapter_number
        WHERE book_id = %s
        ORDER BY chapter_id ASC''',
        (book_id, book_id))    
    return cur.fetchall()

def get_chapter(book_id, chapter_id):
    cur.execute('''
        WITH chapter_number AS (
            SELECT c.chapter_id, row_number() over(ORDER BY chapter_id) AS number
            FROM chapter c
            WHERE c.book_id = %s
            ORDER BY c.chapter_id ASC)
        SELECT *
        FROM chapter NATURAL JOIN chapter_number
        WHERE chapter_id = %s;''',
        (book_id, chapter_id))    
    return cur.fetchone()

def edit_book_chapter(book_id, chapter_id, title, content, status):
    cur.execute('''
        UPDATE chapter
        SET title = %s, content = %s, status = %s
        WHERE book_id = %s AND chapter_id = %s''',
        (title, content, status, book_id, chapter_id))

def remove_book_chapter(book_id, chapter_id):
    cur.execute('''
        DELETE FROM chapter
        WHERE book_id = %s AND chapter_id = %s''',
        (book_id, chapter_id))



####################################
# Comment Queries
####################################

def add_book_comment(book_id, comment, user_id):
    cur.execute('''
        INSERT INTO comment (content, user_id)
        VALUES (%s, %s)
        RETURNING comment_id;''',
        (comment, user_id))
    comment_id = cur.fetchone()[0]
    cur.execute('''
        INSERT INTO book_comment (comment_id, book_id)
        VALUES (%s, %s)''',
        (comment_id, book_id))
    conn.commit()
    return comment_id


def get_comments_by_book(book_id):
    cur.execute('''
        SELECT comment.create_time, comment.content, a.username
        FROM book_comment NATURAL JOIN comment
        LEFT JOIN account a ON comment.user_id = a.user_id
        WHERE book_id = %s;''', (book_id,))
    return cur.fetchall()

def add_chapter_comment(chapter_id, comment, user_id):
    cur.execute('''
        INSERT INTO comment (content, user_id)
        VALUES (%s, %s)
        RETURNING comment_id;''',
        (comment, user_id))
    comment_id = cur.fetchone()[0]
    cur.execute('''
        INSERT INTO chapter_comment (comment_id, chapter_id)
        VALUES (%s, %s)''',
        (comment_id, chapter_id))
    conn.commit()
    return comment_id


def get_comments_by_chapter(chapter_id):
    cur.execute('''
        SELECT comment.create_time, comment.content, a.username
        FROM chapter_comment NATURAL JOIN comment
        LEFT JOIN account a ON comment.user_id = a.user_id
        WHERE chapter_id = %s;''', (chapter_id,))
    return cur.fetchall()

def get_comments_plus():
    cur.execute('''
    SELECT c.create_time, c.content, a.username, 
	    CASE WHEN bc.book_id IS NULL THEN FALSE ELSE TRUE END is_book_comment, COALESCE(b.title, chapter.title) AS title, COALESCE(bc.book_id, cc.chapter_id) AS fk_id, c2.book_id
    FROM comment c
    LEFT JOIN account a ON c.user_id = a.user_id
    LEFT JOIN chapter_comment cc ON c.comment_id = cc.comment_id
    LEFT JOIN book_comment bc ON c.comment_id = bc.comment_id
    LEFT JOIN book b ON bc.book_id = b.book_id
    LEFT JOIN chapter ON cc.chapter_id = chapter.chapter_id
    LEFT JOIN chapter c2 ON c2.chapter_id = chapter.chapter_id
    ORDER BY c.create_time DESC;''')
    return cur.fetchall()

def get_comments_plus_table():
    rows = get_comments_plus()
    columns = [desc[0] for desc in cur.description]
    return {
        "table": 'comments',
        "columns": columns,
        "rows": rows
    }

####################################
# Admin Table View Queries
####################################

def get_tables():
    '''returns the names of all database tables as a list'''
    cur.execute('''
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name ASC;''')
    return [r[0] for r in cur.fetchall()]

def get_table_columns(table):
    '''returns the column names of the given table as a list'''
    cur.execute('''
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name   = '%s';''',
        (AsIs(table),))
    return [r[0] for r in cur.fetchall()]

def get_all_rows(table):
    '''returns all rows of the given table'''
    cur.execute('''
        SELECT *
        FROM %s;''',
        (AsIs(table),))
    return cur.fetchall()

def get_table_data(table):
    '''returns dict containing table data'''
    return {
        "table": table,
        "columns": get_table_columns(table),
        "rows": get_all_rows(table)
    }



####################################
# Admin Report Queries
####################################

def get_interval(when):
    if when == 'hour':
        return '1 hours'
    elif when == 'day':
        return '24 hours'
    elif when == 'week':
        return '1 weeks'
    elif when == 'month':
        return '1 months'
    else:
        raise Exception('unaccepted time interval')

def wrap_report(rows):
    columns = [desc[0] for desc in cur.description]
    return {
        "columns": columns,
        "rows": rows
    }  

def report_new_users(when):
    cur.execute('''
        SELECT *
        FROM account
        WHERE create_time >  NOW() AT TIME ZONE 'utc' - INTERVAL %s
        ORDER BY create_time DESC;''', (get_interval(when),))
    return wrap_report(cur.fetchall())

def report_new_books(when):
    cur.execute('''
        SELECT *
        FROM book
        WHERE create_time >  NOW() AT TIME ZONE 'utc' - INTERVAL %s
        ORDER BY create_time DESC;''', (get_interval(when),))
    return wrap_report(cur.fetchall())

def report_most_followers(when):
    cur.execute('''
        SELECT a.user_id, a.username, COUNT(f.follower_id) AS new_followers
        FROM account a
        LEFT JOIN follow f ON a.user_id = f.followee_id
        WHERE f.follow_time >  NOW() AT TIME ZONE 'utc' - INTERVAL %s
        GROUP BY a.user_id
        ORDER BY new_followers DESC;''', (get_interval(when),))
    return wrap_report(cur.fetchall())

def report_most_popular_books(when):
    cur.execute('''
        WITH chapter_views as (
            SELECT c.book_id, c.chapter_id, COUNT(v.user_id) AS chapter_views
            FROM chapter c
            LEFT JOIN chapter_view v ON c.chapter_id = v.chapter_id
            WHERE v.view_time >  NOW() AT TIME ZONE 'utc' - INTERVAL %s
            GROUP BY c.chapter_id)
        SELECT b.book_id, b.title, COALESCE(SUM(cv.chapter_views), 0) AS book_views
        FROM book b
        LEFT JOIN chapter_views cv ON b.book_id = cv.book_id
        GROUP BY b.book_id
        HAVING COALESCE(SUM(cv.chapter_views), 0) > 0;''', (get_interval(when),))
    return wrap_report(cur.fetchall())

def report_most_commented_chapters(when):
    cur.execute('''
    SELECT *
    FROM (
        SELECT c.chapter_id, COALESCE(array_length(array_agg(cc.chapter_id) FILTER (WHERE cc.chapter_id IS NOT NULL), 1), 0) AS comments
        FROM chapter c
        LEFT JOIN chapter_comment cc ON c.chapter_id = cc.chapter_id
        GROUP BY c.chapter_id) x
    WHERE x.comments > 0
    ORDER BY x.comments DESC;''', (get_interval(when),))
    return wrap_report(cur.fetchall())



####################################
# Insecure Stackoverflow SQL Helpers
####################################

def read(table, **kwargs):
    """ Generates SQL for a SELECT statement matching the kwargs passed. """
    sql = list()
    sql.append("SELECT * FROM %s " % table)
    if kwargs:
        sql.append("WHERE " + " AND ".join("%s = %s" % (AsIs(k), v) for k, v in kwargs.iteritems()))
    sql.append(";")
    return "".join(sql)


def upsert(table, **kwargs):
    """ update/insert rows into objects table (update if the row already exists)
        given the key-value pairs in kwargs """
    keys = ["%s" % k for k in kwargs]
    values = ["'%s'" % v for v in kwargs.values()]
    sql = list()
    sql.append("INSERT INTO %s (" % table)
    sql.append(", ".join(keys))
    sql.append(") VALUES (")
    sql.append(", ".join(values))
    sql.append(") ON DUPLICATE KEY UPDATE ")
    sql.append(", ".join("%s = '%s'" % (k, v) for k, v in kwargs.iteritems()))
    sql.append(";")
    return "".join(sql)


def delete(table, **kwargs):
    """ deletes rows from table where **kwargs match """
    sql = list()
    sql.append("DELETE FROM %s " % table)
    sql.append("WHERE " + " AND ".join("%s = '%s'" % (k, v) for k, v in kwargs.iteritems()))
    sql.append(";")
    return "".join(sql)