import re
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from notifier.auth import login_required
from notifier.db import get_db

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, message, created, author_id, username'
        ' FROM notices p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST' and request.form['submit'] == 'Save':
        message = request.form['message']
        error = None

        if not message:
            error = 'Message is required.'

        #matched = re.match("^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])\s([01]\d|2[0-3]):?([0-5]\d)::[A-Za-z\s]+::[A-Za-z0-9\s]+::[A-Za-z0-9\s]+$", message)
        matched = re.match("^[:A-Za-z0-9\s]*$", message)

        if error is not None:
            flash(error)
        elif not matched:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO notices (message, author_id)'
                ' VALUES (?, ?)',
                (message, g.user['id'])
            )
            db.commit()

            with open('notifier/messages/raw', mode='a') as f:
                f.write(message + "\n")

            return redirect(url_for('blog.index'))
    elif request.method == 'POST' and request.form['submit'] == 'Cancel':
        return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, message, created, author_id, username'
        ' FROM notices p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        old_message = post['message']
        new_message = request.form['message']
        error = None

        if not new_message:
            error = 'Message is required.'

        matched = re.match("^[:A-Za-z0-9\s]*$", new_message)

        if error is not None:
            flash(error)
        elif not matched:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE notices SET message = ?'
                ' WHERE id = ?',
                (new_message, id)
            )
            db.commit()

            with open('notifier/messages/raw', mode='r') as f:
                content = f.read()

            content = content.replace(old_message, new_message)

            with open('notifier/messages/raw', mode='w') as f:
                f.write(content)

            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM notices WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
