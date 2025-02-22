from flask import Blueprint, render_template

bp = Blueprint('fcategory', __name__)

@bp.route('/fcategory')
def fcategory():
    return render_template('fcategory.html')