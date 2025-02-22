from flask import Blueprint, render_template

bp = Blueprint('fcreate', __name__)

@bp.route('/fcreate')
def fcreate():
    return render_template('fcreate.html')