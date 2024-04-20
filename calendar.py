import re, sys
from . import db as evt
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, make_response
)
from werkzeug.exceptions import abort

from datetime import datetime
from notifier.auth import login_required
from notifier.db import get_db

bp = Blueprint('calendar', __name__)


@bp.route('/calendar', methods=["GET", "POST"])
def calendar():
    return render_template('calendar/calendar.html', datetime = str(datetime.now().strftime('%B %d, %Y %H:%M')))


@bp.route('/calendar/get/', methods=["POST"])
def get():
    data = dict(request.form)
    events = evt.get(int(data["month"]), int(data["year"]))
    return "{}" if events is None else events


@bp.route("/calendar/save/", methods=["POST"])
@login_required
def save():
    data = dict(request.form)
    ok = evt.save(data["s"], data["e"], data["t"], data["c"], data["b"], data["id"] if "id" in data else None)
    msg = "OK" if ok else sys.last_value
    
    return make_response(msg, 200)


@bp.route("/calendar/delete/", methods=["POST"])
@login_required
def delete():
    data = dict(request.form)
    ok = evt.delete(data["id"])
    msg = "OK" if ok else sys.last_value

    return make_response(msg, 200)
