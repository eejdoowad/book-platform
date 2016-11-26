from app import app, cur, conn
from psycopg2.extensions import AsIs

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

def key_available(table, column, value):
    cur.execute('''
      SELECT DISTINCT TRUE FROM %(table)s WHERE %(column)s = %(value)s;''', {
          "table": AsIs(table),
          "column": AsIs(column),
          "value": value
      })
    return cur.fetchone() == None


# Insecure database helpers...

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