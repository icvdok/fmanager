from flask import Blueprint, render_template

bp = Blueprint('fsearch', __name__)

@bp.route('/fsearch')
def fsearch():
    return render_template('fsearch.html')