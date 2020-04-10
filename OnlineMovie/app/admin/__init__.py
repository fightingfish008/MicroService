from flask import Blueprint

admin = Blueprint('admin', __name__, url_prefix='/api/admin')

from app.admin import views
