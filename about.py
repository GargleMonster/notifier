from flask import (
    Blueprint, flash, redirect, render_template, url_for
)


bp = Blueprint('about', __name__)


@bp.route('/about')
def about():
    return render_template('about/about.html')
