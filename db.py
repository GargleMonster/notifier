import sqlite3

import click
from flask import current_app, g
from werkzeug.security import generate_password_hash
from calendar import monthrange


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

    usernames = [ ]
    passwords = [ ]

    for user, passwd in zip(usernames, passwords):
        try:
            db.execute(
                "INSERT INTO user (username, password) VALUES (?, ?)",
                (user, generate_password_hash(passwd, method='scrypt'),)
            )
            db.commit()
        except Exception as e:
            print(e)


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


@click.command('start-dat-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def save(start, end, txt, color, bg, id=None):
    db = get_db()

    if id is None:
        db.execute(
            "INSERT INTO events (start, end, text, color, bg) VALUES (?, ?, ?, ?, ?)",
            (start, end, txt, color, bg,)
        )
    else:
        db.execute(
            "UPDATE events SET start=?, end=?, text=?, color=?, bg=? WHERE id=?",
            (start, end, txt, color, bg, id,)
        )

    db.commit()

    return True


def delete(id):
    db = get_db()

    db.execute(
        "DELETE FROM events WHERE id=?",
        (id,)
    )
    db.commit()

    return True


def get(month, year):
    days_in_month = str(monthrange(year, month)[1])
    month = month if month > 10 else "0" + str(month)
    date_y_m = str(year) + "-" + str(month) + "-"
    start = date_y_m + "01 00:00:00"
    end = date_y_m + days_in_month + " 23:59:59"

    rows = get_db().execute(
        "SELECT * FROM events WHERE (( start BETWEEN ? AND ?) OR (end BETWEEN ? AND ?) OR (start <= ? AND end >= ?))",
        (start, end, start, end, start, end,)
    ).fetchall()
    
    if len(rows) == 0:
        return None

    data = {}
    for r in rows:
        data[r[0]] = {
            "s" : r[1], "e" : r[2],
            "c" : r[4], "b" : r[5],
            "t" : r[3]
        }

    return data     
