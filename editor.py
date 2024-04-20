import re, sys, time
from . import db as evt
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, make_response
)

from notifier.auth import login_required
from notifier.db import get_db

bp = Blueprint('editor', __name__)


@bp.route('/editor', methods=["GET", "POST"])
@login_required
def editor():
    if g.user['username'] == 'matthew':
        raw_message = open('notifier/messages/raw', mode='r').read()
       
        if request.method == 'POST' and request.form['submit'] == 'Save':
            filtered_message = request.form['messages']
            error = None
            success = "Successfully updated!"

            matched = re.match("\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])\s([01]\d|2[0-3]):?([0-5]\d)::[A-Za-z\s]+::[A-Za-z0-9\s]+::[A-Za-z0-9\s]+", filtered_message)

            if not filtered_message:
                error = "Message is required"

            if error is not None:
                flash(error)
            elif not matched:
                flash(error)
            else:
                with open('notifier/messages/complete', mode='wt') as f:
                    f.write(filtered_message)
                
                flash(success)

                open('notifier/messages/raw', mode='w').close()

                return redirect(url_for('blog.index'))
        elif request.method == 'POST' and request.form['submit'] == 'Cancel':
            return redirect(url_for('blog.index'))
    else:
        return redirect(url_for('blog.index'))
            
    return render_template('editor/editor.html', message=raw_message)
