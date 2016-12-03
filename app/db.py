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

def get_all_users():
    try:
      cur.execute("SELECT * FROM account")
      users = cur.fetchall()
      return users
    except Exception as e:
        print(e, file=stderr)
        return []

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

def browse_books_query(): return '''
WITH genres AS (
		SELECT b.book_id, array_agg(bg.genre) FILTER(WHERE genre IS NOT NULL) AS genres
		FROM book b
		LEFT JOIN book_genre bg ON b.book_id = bg.book_id
		WHERE b.book_id = 1
		GROUP BY b.book_id),
	chapters AS (
		SELECT b.book_id, count(*) AS chapter_count
		FROM book b
		LEFT JOIN chapter c ON b.book_id = c.book_id
		GROUP BY b.book_id),
	ratings AS (
		SELECT b.book_id, AVG(r.rating) AS rating, COUNT(*) AS votes
		FROM book b
		LEFT JOIN book_rating r ON b.book_id = r.book_id
		GROUP BY b.book_id)
SELECT b.title, a.username, g.genres, c.chapter_count, r.rating, r.votes, b.create_time::date
FROM book b
LEFT JOIN account a ON b.author_id = a.user_id
LEFT JOIN genres g ON b.book_id = g.book_id
LEFT JOIN chapters c ON b.book_id = c.book_id
LEFT JOIN ratings r ON b.book_id = r.book_id;'''



def gen_browse_select(entity):
    select, columns = None, None
    if entity == 'book':
        columns = None
        select = '''
            SELECT
            FROM book'''
    elif entity == 'chapter':
        select = '''
            SELECT
            FROM chapter'''
    elif entity == 'author':
        select = '''
            SELECT
            FROM account'''
    else:
        raise Exception('Invalid entity made it through browse query')
    return {
        "select": select,
        "columns": columns
    }


def get_browse_data(entity, sort, order):
    select_clause = ''
    cur.execute(browse_books_query())  
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
        SELECT b.book_id, b.title, a.username, b.summary, array_agg(bg.genre) AS genres, b.create_time::date
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
# Admin Table View Queries
####################################

@functools.lru_cache(1)
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